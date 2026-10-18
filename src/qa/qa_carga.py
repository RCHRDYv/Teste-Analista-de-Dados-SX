"""QA da carga: confere o modelo no MySQL por caminhos independentes do ETL.

Verificações:
1. Grão: linhas do CSV bruto (contadas lendo o arquivo) = linhas do fato
   = linhas do questionário, sem inscrição repetida.
2. Integridade: nenhuma chave do fato sem correspondente na dimensão, e o
   join com todas as dimensões não multiplica linhas (fan-out).
3. Valores: notas objetivas e da redação entre 0 e 1000, competências
   entre 0 e 200, nota preenchida só para quem esteve presente, média
   preenchida só para quem esteve presente nas quatro provas.
4. Indicadores: os números do SQL sobre o modelo batem com os do PySpark
   sobre o CSV bruto (src/spark/indicadores_spark.py).

O resultado vai para docs/qa.md. O script termina com código 1 se alguma
verificação falhar.

Uso:
    python -m src.qa.qa_carga
"""

import json
import logging
import sys
from decimal import Decimal

from src.analise.indicadores_sql import executar_consultas
from src.etl import config
from src.etl.load import conectar
from src.spark import indicadores_spark

log = logging.getLogger(__name__)

ARQUIVO_SAIDA = config.RAIZ_PROJETO / "docs" / "qa.md"
TOLERANCIA = 0.01  # diferença máxima aceita entre SQL e Spark, em pontos


def contar_linhas_csv() -> int:
    """Conta as linhas de dados do CSV lendo o arquivo em blocos binários."""
    total = 0
    with open(config.CAMINHO_CSV, "rb") as arquivo:
        while bloco := arquivo.read(16 * 1024 * 1024):
            total += bloco.count(b"\n")
    return total - 1  # desconta o cabeçalho


def _valor(cursor, consulta: str):
    cursor.execute(consulta)
    return cursor.fetchone()[0]


def verificar_modelo() -> list:
    """Roda as verificações de grão, integridade e valores no MySQL."""
    checagens = []

    def registrar(nome, obtido, esperado):
        checagens.append((nome, obtido, esperado, obtido == esperado))

    linhas_csv = contar_linhas_csv()
    conexao = conectar()
    try:
        with conexao.cursor() as c:
            linhas_fato = _valor(c, "SELECT COUNT(*) FROM fato_participacao")
            registrar("Linhas do fato = linhas do CSV", linhas_fato, linhas_csv)
            registrar("Linhas do questionário = linhas do CSV",
                      _valor(c, "SELECT COUNT(*) FROM dim_questionario"), linhas_csv)
            registrar("Inscrições distintas no fato",
                      _valor(c, "SELECT COUNT(DISTINCT nu_inscricao) FROM fato_participacao"),
                      linhas_csv)

            for dimensao, chave in [
                ("dim_perfil", "sk_perfil"), ("dim_escola", "sk_escola"),
                ("dim_local_prova", "sk_local_prova"),
                ("dim_status_redacao", "tp_status_redacao"),
                ("dim_questionario", "nu_inscricao"),
            ]:
                orfaos = _valor(c, f"""
                    SELECT COUNT(*) FROM fato_participacao f
                    LEFT JOIN {dimensao} d ON d.{chave} = f.{chave}
                    WHERE d.{chave} IS NULL""")
                registrar(f"Chaves do fato sem {dimensao}", orfaos, 0)

            registrar("Linhas após join com todas as dimensões (fan-out)", _valor(c, """
                SELECT COUNT(*) FROM fato_participacao f
                JOIN dim_perfil p ON p.sk_perfil = f.sk_perfil
                JOIN dim_escola e ON e.sk_escola = f.sk_escola
                JOIN dim_local_prova l ON l.sk_local_prova = f.sk_local_prova
                JOIN dim_status_redacao s ON s.tp_status_redacao = f.tp_status_redacao
                JOIN dim_questionario q ON q.nu_inscricao = f.nu_inscricao"""), linhas_fato)

            registrar("Notas objetivas fora de 0 a 1000", _valor(c, """
                SELECT COUNT(*) FROM fato_participacao
                WHERE nu_nota_cn NOT BETWEEN 0 AND 1000 OR nu_nota_ch NOT BETWEEN 0 AND 1000
                   OR nu_nota_lc NOT BETWEEN 0 AND 1000 OR nu_nota_mt NOT BETWEEN 0 AND 1000"""), 0)
            registrar("Notas da redação fora de 0 a 1000", _valor(c, """
                SELECT COUNT(*) FROM fato_participacao
                WHERE nu_nota_redacao NOT BETWEEN 0 AND 1000"""), 0)
            registrar("Competências fora de 0 a 200", _valor(c, """
                SELECT COUNT(*) FROM fato_participacao
                WHERE nu_nota_comp1 NOT BETWEEN 0 AND 200 OR nu_nota_comp2 NOT BETWEEN 0 AND 200
                   OR nu_nota_comp3 NOT BETWEEN 0 AND 200 OR nu_nota_comp4 NOT BETWEEN 0 AND 200
                   OR nu_nota_comp5 NOT BETWEEN 0 AND 200"""), 0)

            for prova in ("cn", "ch", "lc", "mt"):
                registrar(f"Nota de {prova.upper()} sem presença (ou presença sem nota)", _valor(c, f"""
                    SELECT COUNT(*) FROM fato_participacao
                    WHERE (tp_presenca_{prova} = 1) <> (nu_nota_{prova} IS NOT NULL)"""), 0)

            registrar("Média preenchida fora da regra das quatro presenças", _valor(c, """
                SELECT COUNT(*) FROM fato_participacao
                WHERE (tp_presenca_cn = 1 AND tp_presenca_ch = 1
                       AND tp_presenca_lc = 1 AND tp_presenca_mt = 1)
                      <> (nu_media_objetivas IS NOT NULL)"""), 0)
    finally:
        conexao.close()
    return checagens


def _numero(valor) -> float:
    return float(valor) if isinstance(valor, Decimal) else valor


def comparar_com_spark(spark: dict) -> list:
    """Compara os indicadores do SQL com os do PySpark."""
    sql = executar_consultas()
    pares = []

    def comparar(nome, valor_sql, valor_spark):
        valor_sql, valor_spark = _numero(valor_sql), _numero(valor_spark)
        if isinstance(valor_sql, (int, float)) and isinstance(valor_spark, (int, float)):
            ok = abs(valor_sql - valor_spark) <= TOLERANCIA
        else:
            ok = valor_sql == valor_spark
        pares.append((f"SQL x Spark: {nome}", valor_sql, valor_spark, ok))

    comparar("total de inscritos", sql["q5_total_inscritos"].iloc[0, 0], spark["total_inscritos"])

    ausentes = sql["q4_percentual_ausentes"].iloc[0]
    comparar("% ausente em algum dia", ausentes["pct_ausente_algum_dia"], spark["pct_ausente_algum_dia"])
    comparar("% ausente no dia 1", ausentes["pct_ausente_dia_1"], spark["pct_ausente_dia_1"])
    comparar("% ausente no dia 2", ausentes["pct_ausente_dia_2"], spark["pct_ausente_dia_2"])

    geral = sql["q3_media_geral"].iloc[0]
    comparar("média geral", geral["media_das_medias"], spark["media_das_medias"])
    comparar("presentes nas quatro provas", geral["participantes_quatro_provas"],
             spark["participantes_quatro_provas"])

    aluno = sql["q2_aluno_maior_media"]
    comparar("maior média individual", aluno["media"].iloc[0], spark["maior_media"])
    comparar("inscrições com a maior média", sorted(aluno["nu_inscricao"].tolist()),
             spark["inscricoes_maior_media"])

    nomes_provas = {
        "Ciências da Natureza": "CN", "Ciências Humanas": "CH",
        "Linguagens e Códigos": "LC", "Matemática": "MT", "Redação": "REDACAO",
    }
    for _, linha in sql["q6_media_por_disciplina"].iterrows():
        sigla = nomes_provas[linha["disciplina"]]
        comparar(f"média de {linha['disciplina']}", linha["media"], spark["media_por_disciplina"][sigla])

    for _, linha in sql["q7_media_por_sexo"].iterrows():
        comparar(f"média sexo {linha['sexo']}", linha["media"], spark["media_por_sexo"][linha["sexo"]])
    for _, linha in sql["q8_media_por_cor_raca"].iterrows():
        comparar(f"média cor/raça {linha['cor_raca']}", linha["media"],
                 spark["media_por_cor_raca"][linha["cor_raca"]])

    escola = sql["q1_escola_maior_media"].iloc[0]
    comparar("grupo de escola com maior média: participantes", escola["participantes"],
             spark["escola_maior_media"]["participantes"])
    comparar("grupo de escola com maior média: média", escola["media"],
             spark["escola_maior_media"]["media"])
    return pares


def gravar_relatorio(checagens: list) -> None:
    """Grava o resultado do QA em Markdown."""
    linhas = [
        "# QA da carga",
        "",
        "Gerado por `python -m src.qa.qa_carga`. Cada linha compara o valor obtido "
        "com o esperado; as comparações SQL x Spark aceitam diferença de até "
        f"{TOLERANCIA} ponto por arredondamento.",
        "",
        "| Verificação | Obtido | Esperado | Resultado |",
        "|---|---|---|---|",
    ]
    for nome, obtido, esperado, ok in checagens:
        linhas.append(f"| {nome} | {obtido} | {esperado} | {'OK' if ok else 'FALHA'} |")
    ARQUIVO_SAIDA.write_text("\n".join(linhas) + "\n", encoding="utf-8")


def executar() -> bool:
    """Roda todas as verificações e devolve True se todas passaram."""
    if indicadores_spark.ARQUIVO_SAIDA.exists():
        spark = json.loads(indicadores_spark.ARQUIVO_SAIDA.read_text(encoding="utf-8"))
    else:
        spark = indicadores_spark.executar()

    checagens = verificar_modelo() + comparar_com_spark(spark)
    gravar_relatorio(checagens)
    for nome, obtido, esperado, ok in checagens:
        log.info("%s %s: obtido=%s esperado=%s", "OK   " if ok else "FALHA", nome, obtido, esperado)
    return all(ok for *_, ok in checagens)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    sys.exit(0 if executar() else 1)
