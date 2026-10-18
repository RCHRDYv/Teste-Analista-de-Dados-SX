"""Executa as consultas de sql/02_indicadores.sql e grava as respostas.

Cada consulta do arquivo começa com "-- name: <nome>". O resultado de cada
uma vira uma tabela em docs/indicadores.md.

Uso:
    python -m src.analise.indicadores_sql
"""

import logging
import re
from decimal import Decimal
from pathlib import Path

import pandas as pd

from src.etl import config
from src.etl.load import conectar

log = logging.getLogger(__name__)

ARQUIVO_SQL = config.RAIZ_PROJETO / "sql" / "02_indicadores.sql"
ARQUIVO_SAIDA = config.RAIZ_PROJETO / "docs" / "indicadores.md"

TITULOS = {
    "q1_escola_maior_media": "1. Escola com a maior média (grupo município x dependência x localização, top 10)",
    "q2_aluno_maior_media": "2. Aluno com a maior média",
    "q3_media_geral": "3. Média geral",
    "q4_percentual_ausentes": "4. Percentual de ausentes",
    "q5_total_inscritos": "5. Total de inscritos",
    "q6_media_por_disciplina": "6. Média por disciplina",
    "q7_media_por_sexo": "7. Média por sexo",
    "q8_media_por_cor_raca": "8. Média por cor/raça (etnia)",
}


def ler_consultas(caminho: Path = ARQUIVO_SQL) -> dict:
    """Separa o arquivo SQL em consultas nomeadas, na ordem do arquivo."""
    texto = caminho.read_text(encoding="utf-8")
    partes = re.split(r"^-- name: (\w+)\s*$", texto, flags=re.MULTILINE)
    # partes = [preâmbulo, nome1, corpo1, nome2, corpo2, ...]
    return {nome: corpo.strip() for nome, corpo in zip(partes[1::2], partes[2::2])}


def executar_consultas() -> dict:
    """Roda todas as consultas e devolve um DataFrame por indicador."""
    resultados = {}
    conexao = conectar()
    try:
        with conexao.cursor() as cursor:
            for nome, consulta in ler_consultas().items():
                cursor.execute(consulta)
                colunas = [descricao[0] for descricao in cursor.description]
                resultados[nome] = pd.DataFrame(cursor.fetchall(), columns=colunas)
                log.info("%s: %d linha(s)", nome, len(resultados[nome]))
    finally:
        conexao.close()
    return resultados


def _formatar(valor) -> str:
    """Formata um valor no padrão brasileiro: vírgula decimal e ponto de milhar.

    A inscrição é um código, não uma quantidade, e fica sem separador.
    """
    if isinstance(valor, (Decimal, float)):
        texto = f"{float(valor):,.2f}"
    elif isinstance(valor, int) and valor < 10**11:
        texto = f"{valor:,}"
    else:
        return str(valor)
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def gravar_markdown(resultados: dict, caminho: Path = ARQUIVO_SAIDA) -> None:
    """Grava os resultados como tabelas Markdown, uma seção por pergunta."""
    linhas = [
        "# Indicadores",
        "",
        "Gerado por `python -m src.analise.indicadores_sql` a partir de "
        "[`sql/02_indicadores.sql`](../sql/02_indicadores.sql). "
        "Definições no [ADR-0006](adr/0006-definicoes-das-metricas.md).",
        "",
    ]
    for nome, df in resultados.items():
        texto = df.map(_formatar).to_markdown(index=False, disable_numparse=True)
        linhas += [f"## {TITULOS.get(nome, nome)}", "", texto, ""]
    caminho.write_text("\n".join(linhas), encoding="utf-8")
    log.info("Resultados gravados em %s", caminho)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    gravar_markdown(executar_consultas())
