"""Orquestra o ETL completo: extração, transformação e carga.

Uso:
    docker compose run --rm app python -m src.etl.main
"""

import logging
import time

from src.etl import extract, load, transform

log = logging.getLogger("etl")


def executar() -> None:
    """Roda as três etapas em sequência e registra tempo e linhas de cada uma."""
    inicio = time.perf_counter()

    etapa = time.perf_counter()
    caminho_csv = extract.executar()
    log.info("Extração concluída em %.0fs: %s", time.perf_counter() - etapa, caminho_csv)

    etapa = time.perf_counter()
    resumo = transform.executar(caminho_csv)
    log.info(
        "Transformação concluída em %.0fs: %d linhas lidas, %d linhas no fato",
        time.perf_counter() - etapa, resumo.linhas_lidas, resumo.linhas_fato,
    )

    etapa = time.perf_counter()
    contagens = load.executar(resumo.arquivos)
    log.info("Carga concluída em %.0fs", time.perf_counter() - etapa)

    if contagens["fato_participacao"] != resumo.linhas_lidas:
        raise RuntimeError(
            f"Fato com {contagens['fato_participacao']} linhas, "
            f"mas o CSV tem {resumo.linhas_lidas}"
        )
    log.info("ETL concluído em %.0fs", time.perf_counter() - inicio)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    executar()
