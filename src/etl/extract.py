"""Extração: download e descompactação dos microdados do ENEM 2020.

As duas operações são idempotentes. O download só acontece se o zip não
existir ou estiver incompleto, e a descompactação só extrai os arquivos
que ainda não estão na pasta de dados.

Uso:
    python -m src.etl.extract
"""

import logging
import shutil
import ssl
import time
import urllib.request
import zipfile
from pathlib import Path

from src.etl import config

log = logging.getLogger(__name__)

TAMANHO_BLOCO = 1024 * 1024  # 1 MB por leitura no download
TENTATIVAS_DOWNLOAD = 3
ESPERA_SEGUNDOS = 10


def _contexto_ssl() -> ssl.SSLContext:
    """Cria um contexto TLS com as CAs do sistema mais o intermediário do Inep."""
    contexto = ssl.create_default_context()
    contexto.load_verify_locations(cafile=config.CERTIFICADO_INTERMEDIARIO)
    return contexto


def baixar_zip(destino: Path = config.CAMINHO_ZIP) -> Path:
    """Baixa o zip dos microdados, se ainda não estiver completo em disco.

    Args:
        destino: caminho onde o zip será salvo.

    Returns:
        O caminho do zip baixado.

    Raises:
        RuntimeError: se o arquivo baixado não tiver o tamanho esperado.
    """
    if destino.exists() and destino.stat().st_size == config.TAMANHO_ZIP_BYTES:
        log.info("Zip já existe e está completo: %s", destino)
        return destino

    destino.parent.mkdir(parents=True, exist_ok=True)
    temporario = destino.with_suffix(".part")

    # O servidor do Inep às vezes derruba a conexão. Cada falha de rede
    # gera uma nova tentativa, até o limite.
    for tentativa in range(1, TENTATIVAS_DOWNLOAD + 1):
        try:
            log.info("Baixando %s (tentativa %d)", config.URL_MICRODADOS, tentativa)
            with urllib.request.urlopen(
                config.URL_MICRODADOS, context=_contexto_ssl(), timeout=60
            ) as resposta:
                with open(temporario, "wb") as arquivo:
                    shutil.copyfileobj(resposta, arquivo, TAMANHO_BLOCO)
            break
        except OSError as erro:
            if tentativa == TENTATIVAS_DOWNLOAD:
                raise
            log.warning("Falha no download (%s). Nova tentativa em %ds", erro, ESPERA_SEGUNDOS)
            time.sleep(ESPERA_SEGUNDOS)

    tamanho = temporario.stat().st_size
    if tamanho != config.TAMANHO_ZIP_BYTES:
        raise RuntimeError(
            f"Download incompleto: {tamanho} bytes, esperado {config.TAMANHO_ZIP_BYTES}"
        )

    temporario.replace(destino)
    log.info("Download concluído: %s bytes", tamanho)
    return destino


FLAG_NOME_UTF8 = 0x800  # bit 11 do cabeçalho zip: nome gravado em UTF-8


def _nome_real(info: zipfile.ZipInfo) -> str:
    """Devolve o nome do arquivo no zip com os acentos corretos.

    Sem o bit de UTF-8, o Python lê o nome como CP437. O zip do Inep foi
    gerado em CP850 (padrão do Windows em português), e os dois diferem em
    letras como "Á". Por isso o nome é recodificado.
    """
    if info.flag_bits & FLAG_NOME_UTF8:
        return info.filename
    return info.filename.encode("cp437").decode("cp850")


def descompactar(zip_path: Path = config.CAMINHO_ZIP, pasta: Path = config.DATA_DIR) -> None:
    """Extrai do zip apenas os arquivos usados pelo pipeline.

    Cada arquivo é procurado pelo final do caminho, já com o nome
    recodificado, e gravado direto em `pasta`.

    Args:
        zip_path: caminho do zip baixado.
        pasta: pasta de destino dos arquivos extraídos.
    """
    with zipfile.ZipFile(zip_path) as zf:
        nomes = {_nome_real(info): info for info in zf.infolist()}
        for relativo in config.ARQUIVOS_EXTRAIDOS:
            alvo = pasta / relativo
            if alvo.exists():
                log.info("Já extraído: %s", alvo)
                continue

            origem = next(info for nome, info in nomes.items() if nome.endswith(relativo))
            alvo.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(origem) as entrada, open(alvo, "wb") as saida:
                shutil.copyfileobj(entrada, saida, TAMANHO_BLOCO)
            log.info("Extraído: %s", alvo)


def executar() -> Path:
    """Roda a extração completa e devolve o caminho do CSV de microdados."""
    descompactar(baixar_zip())
    return config.CAMINHO_CSV


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    executar()
