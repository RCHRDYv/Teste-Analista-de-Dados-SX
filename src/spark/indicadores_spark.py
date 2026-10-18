"""Recalcula os oito indicadores em PySpark a partir do CSV original do Inep.

Este caminho não usa o MySQL nem o modelo dimensional: lê o arquivo bruto
e aplica as mesmas definições do ADR-0006. O QA (src/qa/qa_carga.py)
compara estes números com os do SQL para detectar perda ou duplicação de
dados no ETL.

Uso:
    python -m src.spark.indicadores_spark
"""

import json
import logging

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

from src.etl import config, dominios

log = logging.getLogger(__name__)

ARQUIVO_SAIDA = config.DATA_DIR / "indicadores_spark.json"
PROVAS = ["CN", "CH", "LC", "MT"]
MINIMO_PARTICIPANTES_GRUPO = 30


def criar_sessao() -> SparkSession:
    """Cria uma sessão Spark local usando todos os núcleos do container."""
    return (
        SparkSession.builder.master("local[*]")
        .appName("indicadores-enem-2020")
        .config("spark.driver.memory", "6g")
        .config("spark.sql.shuffle.partitions", "16")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )


def ler_microdados(spark: SparkSession) -> DataFrame:
    """Lê o CSV bruto e converte para número só as colunas usadas."""
    bruto = (
        spark.read.option("header", True)
        .option("sep", config.SEPARADOR_CSV)
        .option("encoding", "ISO-8859-1")
        .csv(str(config.CAMINHO_CSV))
    )
    inteiros = [f"TP_PRESENCA_{p}" for p in PROVAS] + [
        "TP_COR_RACA", "TP_DEPENDENCIA_ADM_ESC", "TP_LOCALIZACAO_ESC", "CO_MUNICIPIO_ESC",
        "TP_STATUS_REDACAO",
    ]
    df = bruto.withColumn("NU_INSCRICAO", F.col("NU_INSCRICAO").cast("long"))
    for coluna in inteiros:
        df = df.withColumn(coluna, F.col(coluna).cast("int"))
    for coluna in [f"NU_NOTA_{p}" for p in PROVAS] + ["NU_NOTA_REDACAO"]:
        df = df.withColumn(coluna, F.col(coluna).cast("double"))

    presente_nas_quatro = F.lit(True)
    for prova in PROVAS:
        presente_nas_quatro = presente_nas_quatro & (F.col(f"TP_PRESENCA_{prova}") == 1)
    media = sum(F.col(f"NU_NOTA_{p}") for p in PROVAS) / 4
    return df.withColumn("MEDIA", F.when(presente_nas_quatro, F.round(media, 3)))


def calcular(df: DataFrame) -> dict:
    """Calcula os indicadores e devolve um dicionário serializável em JSON."""
    df = df.cache()
    resultado = {}

    # Pergunta 5: total de inscritos
    resultado["total_inscritos"] = df.count()

    # Pergunta 4: ausentes (código 0); eliminados não contam
    falta = {p: (F.col(f"TP_PRESENCA_{p}") == 0).cast("int") for p in PROVAS}
    dia_1 = F.greatest(falta["LC"], falta["CH"])
    dia_2 = F.greatest(falta["CN"], falta["MT"])
    linha = df.agg(
        F.avg(F.greatest(dia_1, dia_2)).alias("algum_dia"),
        F.avg(dia_1).alias("dia_1"),
        F.avg(dia_2).alias("dia_2"),
    ).first()
    resultado["pct_ausente_algum_dia"] = round(100 * linha["algum_dia"], 2)
    resultado["pct_ausente_dia_1"] = round(100 * linha["dia_1"], 2)
    resultado["pct_ausente_dia_2"] = round(100 * linha["dia_2"], 2)

    # Pergunta 3: média geral (média das médias dos presentes nas quatro)
    linha = df.agg(F.avg("MEDIA").alias("media"), F.count("MEDIA").alias("n")).first()
    resultado["media_das_medias"] = round(linha["media"], 2)
    resultado["participantes_quatro_provas"] = linha["n"]

    # Pergunta 2: maior média individual e inscrições empatadas
    maior = df.agg(F.max("MEDIA")).first()[0]
    resultado["maior_media"] = maior
    resultado["inscricoes_maior_media"] = sorted(
        r["NU_INSCRICAO"] for r in df.filter(F.col("MEDIA") == maior).select("NU_INSCRICAO").collect()
    )

    # Pergunta 6: média por disciplina entre os presentes em cada prova
    resultado["media_por_disciplina"] = {
        prova: round(
            df.filter(F.col(f"TP_PRESENCA_{prova}") == 1).agg(F.avg(f"NU_NOTA_{prova}")).first()[0], 2
        )
        for prova in PROVAS
    }
    resultado["media_por_disciplina"]["REDACAO"] = round(
        df.filter(F.col("TP_STATUS_REDACAO").isNotNull()).agg(F.avg("NU_NOTA_REDACAO")).first()[0], 2
    )

    # Perguntas 7 e 8: média por sexo e por cor/raça
    com_media = df.filter(F.col("MEDIA").isNotNull())
    resultado["media_por_sexo"] = {
        dominios.descrever(r["TP_SEXO"], dominios.SEXO): round(r["media"], 2)
        for r in com_media.groupBy("TP_SEXO").agg(F.avg("MEDIA").alias("media")).collect()
    }
    resultado["media_por_cor_raca"] = {
        dominios.descrever(r["TP_COR_RACA"], dominios.COR_RACA): round(r["media"], 2)
        for r in com_media.groupBy("TP_COR_RACA").agg(F.avg("MEDIA").alias("media")).collect()
    }

    # Pergunta 1: grupo de escola com a maior média (ADR-0005)
    grupo = (
        com_media.filter(F.col("CO_MUNICIPIO_ESC").isNotNull())
        .groupBy("CO_MUNICIPIO_ESC", "TP_DEPENDENCIA_ADM_ESC", "TP_LOCALIZACAO_ESC")
        .agg(F.count("*").alias("participantes"), F.avg("MEDIA").alias("media"))
        .filter(F.col("participantes") >= MINIMO_PARTICIPANTES_GRUPO)
        .orderBy(F.desc("media"))
        .first()
    )
    resultado["escola_maior_media"] = {
        "co_municipio_esc": grupo["CO_MUNICIPIO_ESC"],
        "dependencia_adm": dominios.descrever(grupo["TP_DEPENDENCIA_ADM_ESC"], dominios.DEPENDENCIA_ADM),
        "localizacao": dominios.descrever(grupo["TP_LOCALIZACAO_ESC"], dominios.LOCALIZACAO),
        "participantes": grupo["participantes"],
        "media": round(grupo["media"], 2),
    }
    df.unpersist()
    return resultado


def executar() -> dict:
    """Roda o job, grava o JSON em DATA_DIR e devolve os indicadores."""
    spark = criar_sessao()
    try:
        resultado = calcular(ler_microdados(spark))
    finally:
        spark.stop()
    ARQUIVO_SAIDA.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
    log.info("Indicadores Spark gravados em %s", ARQUIVO_SAIDA)
    return resultado


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    print(json.dumps(executar(), ensure_ascii=False, indent=2))
