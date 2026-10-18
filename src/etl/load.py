"""Carga: arquivos TSV do modelo para o MySQL com LOAD DATA LOCAL INFILE.

A carga é idempotente: cada tabela é esvaziada antes de receber os dados.
As checagens de chave estrangeira ficam desligadas só durante a carga, e a
integridade é conferida depois pelo QA (src/qa/qa_carga.py).

Uso:
    python -m src.etl.load
"""

import logging
import os
from pathlib import Path

import pymysql

from src.etl import transform

log = logging.getLogger(__name__)

# Ordem de carga: dimensões antes do fato. As colunas seguem a ordem dos
# arquivos gerados em transform.py e do DDL em sql/01_schema.sql.
TABELAS = {
    "dim_status_redacao": ["tp_status_redacao", "ds_status_redacao"],
    "dim_perfil": [
        "sk_perfil", "tp_faixa_etaria", "ds_faixa_etaria", "tp_sexo", "ds_sexo",
        "tp_estado_civil", "ds_estado_civil", "tp_cor_raca", "ds_cor_raca",
        "tp_nacionalidade", "ds_nacionalidade", "tp_st_conclusao", "ds_st_conclusao",
        "tp_escola", "ds_escola", "in_treineiro", "ds_treineiro", "tp_lingua", "ds_lingua",
    ],
    "dim_escola": [
        "sk_escola", "co_municipio_esc", "no_municipio_esc", "co_uf_esc", "sg_uf_esc",
        "tp_dependencia_adm_esc", "ds_dependencia_adm_esc", "tp_localizacao_esc",
        "ds_localizacao_esc", "tp_sit_func_esc", "ds_sit_func_esc",
    ],
    "dim_local_prova": [
        "sk_local_prova", "co_municipio_prova", "no_municipio_prova", "co_uf_prova", "sg_uf_prova",
    ],
    "dim_questionario": ["nu_inscricao", *[f"q{n:03d}" for n in range(1, 26)]],
    "fato_participacao": [c.lower() for c in transform.COLUNAS_FATO],
}


def conectar() -> pymysql.connections.Connection:
    """Abre a conexão com o MySQL usando as variáveis do .env."""
    return pymysql.connect(
        host=os.environ["MYSQL_HOST"],
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.environ["MYSQL_USER"],
        password=os.environ["MYSQL_PASSWORD"],
        database=os.environ["MYSQL_DATABASE"],
        charset="utf8mb4",
        local_infile=True,
        autocommit=False,
    )


def carregar_tabela(cursor, tabela: str, colunas: list, arquivo: Path) -> int:
    """Esvazia a tabela e carrega o arquivo TSV correspondente.

    Returns:
        Número de linhas na tabela depois da carga.
    """
    cursor.execute(f"TRUNCATE TABLE {tabela}")
    cursor.execute(
        f"LOAD DATA LOCAL INFILE %s INTO TABLE {tabela} "
        "CHARACTER SET utf8mb4 "
        "FIELDS TERMINATED BY '\\t' ESCAPED BY '\\\\' "
        "LINES TERMINATED BY '\\n' "
        f"({', '.join(colunas)})",
        (str(arquivo),),
    )
    cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
    return cursor.fetchone()[0]


def executar(arquivos: dict | None = None) -> dict:
    """Carrega todas as tabelas do modelo.

    Args:
        arquivos: caminho do TSV de cada tabela. Sem ele, usa a pasta
            padrão da transformação.

    Returns:
        Número de linhas carregadas por tabela.
    """
    if arquivos is None:
        arquivos = {t: transform.PASTA_SAIDA / f"{t}.tsv" for t in TABELAS}

    contagens = {}
    conexao = conectar()
    try:
        with conexao.cursor() as cursor:
            cursor.execute("SET foreign_key_checks = 0")
            cursor.execute("SET unique_checks = 0")
            for tabela, colunas in TABELAS.items():
                contagens[tabela] = carregar_tabela(cursor, tabela, colunas, arquivos[tabela])
                log.info("%s: %d linhas", tabela, contagens[tabela])
            cursor.execute("SET unique_checks = 1")
            cursor.execute("SET foreign_key_checks = 1")
        conexao.commit()
    finally:
        conexao.close()
    return contagens


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    executar()
