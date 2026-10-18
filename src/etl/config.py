"""Configurações compartilhadas pelas etapas do ETL.

Os caminhos podem ser sobrescritos por variáveis de ambiente, definidas no
arquivo .env (veja .env.example).
"""

import os
from pathlib import Path

# Raiz do repositório (dois níveis acima deste arquivo: src/etl/config.py)
RAIZ_PROJETO = Path(__file__).resolve().parents[2]

# Pasta dos dados brutos e intermediários. Fica fora do Git.
DATA_DIR = Path(os.getenv("DATA_DIR", RAIZ_PROJETO / "data"))

# Arquivo publicado pelo Inep e seu tamanho em bytes, usado para checar
# se o download terminou por completo.
URL_MICRODADOS = "https://download.inep.gov.br/microdados/microdados_enem_2020.zip"
TAMANHO_ZIP_BYTES = 620_776_982
CAMINHO_ZIP = DATA_DIR / "microdados_enem_2020.zip"

# Arquivos extraídos do zip que o pipeline usa
ARQUIVOS_EXTRAIDOS = (
    "DADOS/MICRODADOS_ENEM_2020.csv",
    "DICIONÁRIO/Dicionário_Microdados_Enem_2020.xlsx",
    "LEIA-ME E DOCUMENTOS TÉCNICOS/Leia_Me_Enem_2020.pdf",
)
CAMINHO_CSV = DATA_DIR / "DADOS" / "MICRODADOS_ENEM_2020.csv"

# O servidor do Inep não envia o certificado intermediário da cadeia TLS.
# Este arquivo público (emitido pela GlobalSign) completa a cadeia sem
# desligar a verificação do certificado.
CERTIFICADO_INTERMEDIARIO = (
    RAIZ_PROJETO / "docker" / "certs" / "rnp_icpedu_gr46_ov_tls_ca_2025.pem"
)

# Formato do CSV, conforme o Leia-me do Inep
SEPARADOR_CSV = ";"
ENCODING_CSV = "latin-1"
