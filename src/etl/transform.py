"""Transformação: do CSV do Inep para os arquivos das tabelas do modelo.

O CSV é lido em blocos. Para cada bloco, as combinações de atributos de
perfil, escola e local de prova recebem uma chave substituta (sk), mantida
num catálogo em memória que cresce entre os blocos. O fato e o questionário
são gravados bloco a bloco; as dimensões são gravadas no final, com as
descrições do dicionário do Inep.

Os arquivos de saída são TSV sem cabeçalho, com \\N para nulos, no formato
que o LOAD DATA do MySQL espera (ADR-0004).

Uso:
    python -m src.etl.transform
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from src.etl import config, dominios

log = logging.getLogger(__name__)

LINHAS_POR_BLOCO = 500_000
SEM_VALOR = -1  # substitui nulos nas colunas que formam chave de dimensão
PASTA_SAIDA = config.DATA_DIR / "modelo"

# Colunas lidas do CSV e seus tipos. Vetores de respostas, gabaritos e
# códigos de caderno não entram no modelo.
QUESTOES = [f"Q{n:03d}" for n in range(1, 26)]
TIPOS_COLUNAS = {
    "NU_INSCRICAO": "int64",
    "TP_FAIXA_ETARIA": "Int16", "TP_SEXO": "string", "TP_ESTADO_CIVIL": "Int16",
    "TP_COR_RACA": "Int16", "TP_NACIONALIDADE": "Int16", "TP_ST_CONCLUSAO": "Int16",
    "TP_ESCOLA": "Int16", "IN_TREINEIRO": "Int16", "TP_LINGUA": "Int16",
    "CO_MUNICIPIO_ESC": "Int64", "NO_MUNICIPIO_ESC": "string", "CO_UF_ESC": "Int16",
    "SG_UF_ESC": "string", "TP_DEPENDENCIA_ADM_ESC": "Int16",
    "TP_LOCALIZACAO_ESC": "Int16", "TP_SIT_FUNC_ESC": "Int16",
    "CO_MUNICIPIO_PROVA": "int64", "NO_MUNICIPIO_PROVA": "string",
    "CO_UF_PROVA": "int16", "SG_UF_PROVA": "string",
    "TP_PRESENCA_CN": "int8", "TP_PRESENCA_CH": "int8",
    "TP_PRESENCA_LC": "int8", "TP_PRESENCA_MT": "int8",
    "NU_NOTA_CN": "float64", "NU_NOTA_CH": "float64",
    "NU_NOTA_LC": "float64", "NU_NOTA_MT": "float64",
    "TP_STATUS_REDACAO": "Int16",
    "NU_NOTA_COMP1": "Int16", "NU_NOTA_COMP2": "Int16", "NU_NOTA_COMP3": "Int16",
    "NU_NOTA_COMP4": "Int16", "NU_NOTA_COMP5": "Int16", "NU_NOTA_REDACAO": "Int16",
    **{q: "string" for q in QUESTOES},
    "Q005": "Int16",
}

# Atributos que definem cada dimensão (a chave natural da combinação)
CHAVE_PERFIL = [
    "TP_FAIXA_ETARIA", "TP_SEXO", "TP_ESTADO_CIVIL", "TP_COR_RACA",
    "TP_NACIONALIDADE", "TP_ST_CONCLUSAO", "TP_ESCOLA", "IN_TREINEIRO", "TP_LINGUA",
]
CHAVE_ESCOLA = [
    "CO_MUNICIPIO_ESC", "TP_DEPENDENCIA_ADM_ESC", "TP_LOCALIZACAO_ESC", "TP_SIT_FUNC_ESC",
]
# Atributos que dependem do município e são guardados junto da chave
ATRIBUTOS_MUNICIPIO_ESC = ["NO_MUNICIPIO_ESC", "CO_UF_ESC", "SG_UF_ESC"]
ATRIBUTOS_LOCAL_PROVA = ["NO_MUNICIPIO_PROVA", "CO_UF_PROVA", "SG_UF_PROVA"]

PROVAS = ["CN", "CH", "LC", "MT"]

# Ordem das colunas nos arquivos de saída. Precisa bater com o LOAD DATA.
COLUNAS_FATO = [
    "NU_INSCRICAO", "sk_perfil", "sk_escola", "sk_local_prova", "TP_STATUS_REDACAO",
    *[f"TP_PRESENCA_{p}" for p in PROVAS], *[f"NU_NOTA_{p}" for p in PROVAS],
    *[f"NU_NOTA_COMP{n}" for n in range(1, 6)], "NU_NOTA_REDACAO", "nu_media_objetivas",
]
COLUNAS_QUESTIONARIO = ["NU_INSCRICAO", *QUESTOES]


@dataclass
class Catalogos:
    """Chaves substitutas atribuídas até o momento, por dimensão."""

    perfil: dict = field(default_factory=dict)
    escola: dict = field(default_factory=dict)
    atributos_escola: dict = field(default_factory=dict)
    local_prova: dict = field(default_factory=dict)


@dataclass
class ResumoTransformacao:
    """Contagens usadas no log e no QA."""

    linhas_lidas: int = 0
    linhas_fato: int = 0
    arquivos: dict = field(default_factory=dict)


def _atribuir_chaves(bloco: pd.DataFrame, colunas: list, catalogo: dict, nome_sk: str,
                     primeira_chave: int = 1) -> pd.DataFrame:
    """Atribui uma chave substituta a cada combinação de `colunas`.

    Combinações novas recebem a próxima chave livre. O catálogo é alterado
    no lugar, para que o próximo bloco reaproveite as chaves já criadas.

    Returns:
        O bloco com a coluna `nome_sk` acrescentada, sem alterar o número
        de linhas.
    """
    for combinacao in bloco[colunas].drop_duplicates().itertuples(index=False, name=None):
        if combinacao not in catalogo:
            catalogo[combinacao] = primeira_chave + len(catalogo)

    mapa = pd.DataFrame(list(catalogo.keys()), columns=colunas).astype(bloco[colunas].dtypes)
    mapa[nome_sk] = list(catalogo.values())
    resultado = bloco.merge(mapa, on=colunas, how="left", validate="many_to_one")

    if len(resultado) != len(bloco) or resultado[nome_sk].isna().any():
        raise ValueError(f"Falha ao atribuir {nome_sk}: linhas perdidas ou sem chave")
    return resultado


def _preparar_bloco(bloco: pd.DataFrame, catalogos: Catalogos) -> pd.DataFrame:
    """Aplica as regras de negócio e as chaves de dimensão a um bloco."""
    # Nulos nas colunas de chave viram -1 para entrar no catálogo
    for coluna in CHAVE_PERFIL:
        valor_ausente = "N" if coluna == "TP_SEXO" else SEM_VALOR
        bloco[coluna] = bloco[coluna].fillna(valor_ausente)
    bloco = _atribuir_chaves(bloco, CHAVE_PERFIL, catalogos.perfil, "sk_perfil")

    # Escola: sem município informado, a linha aponta para sk_escola = 0
    tem_escola = bloco["CO_MUNICIPIO_ESC"].notna()
    com_escola = bloco.loc[tem_escola].copy()
    for coluna in CHAVE_ESCOLA[1:]:
        com_escola[coluna] = com_escola[coluna].fillna(SEM_VALOR)
    com_escola = _atribuir_chaves(com_escola, CHAVE_ESCOLA, catalogos.escola, "sk_escola")
    for linha in com_escola[["CO_MUNICIPIO_ESC", *ATRIBUTOS_MUNICIPIO_ESC]] \
            .drop_duplicates("CO_MUNICIPIO_ESC").itertuples(index=False, name=None):
        catalogos.atributos_escola.setdefault(linha[0], linha[1:])
    sem_escola = bloco.loc[~tem_escola].assign(sk_escola=0)
    bloco = pd.concat([com_escola, sem_escola], ignore_index=True)

    # Local de prova: um município por chave; os atributos vão no catálogo
    for linha in bloco[["CO_MUNICIPIO_PROVA", *ATRIBUTOS_LOCAL_PROVA]] \
            .drop_duplicates("CO_MUNICIPIO_PROVA").itertuples(index=False, name=None):
        if linha[0] not in catalogos.local_prova:
            catalogos.local_prova[linha[0]] = (len(catalogos.local_prova) + 1, *linha[1:])
    bloco["sk_local_prova"] = bloco["CO_MUNICIPIO_PROVA"].map(
        {codigo: valores[0] for codigo, valores in catalogos.local_prova.items()}
    )

    # Sem redação corrigida, o status vira 0 ("Sem redação")
    bloco["TP_STATUS_REDACAO"] = bloco["TP_STATUS_REDACAO"].fillna(0)

    # Média das quatro objetivas, só para quem esteve presente nas quatro
    presente_nas_quatro = (bloco[[f"TP_PRESENCA_{p}" for p in PROVAS]] == 1).all(axis=1)
    media = bloco[[f"NU_NOTA_{p}" for p in PROVAS]].mean(axis=1, skipna=False).round(3)
    bloco["nu_media_objetivas"] = media.where(presente_nas_quatro)
    return bloco


def _gravar(df: pd.DataFrame, caminho: Path, anexar: bool) -> None:
    """Grava um DataFrame em TSV no formato do LOAD DATA."""
    df.to_csv(caminho, sep="\t", header=False, index=False, na_rep="\\N",
              mode="a" if anexar else "w", encoding="utf-8", lineterminator="\n")


def _montar_dim_perfil(catalogo: dict) -> pd.DataFrame:
    """Monta a dimensão de perfil com as descrições do dicionário."""
    dim = pd.DataFrame(list(catalogo.keys()), columns=CHAVE_PERFIL)
    dim.insert(0, "sk_perfil", list(catalogo.values()))
    descricoes = {
        "TP_FAIXA_ETARIA": dominios.FAIXA_ETARIA, "TP_SEXO": dominios.SEXO,
        "TP_ESTADO_CIVIL": dominios.ESTADO_CIVIL, "TP_COR_RACA": dominios.COR_RACA,
        "TP_NACIONALIDADE": dominios.NACIONALIDADE, "TP_ST_CONCLUSAO": dominios.ST_CONCLUSAO,
        "TP_ESCOLA": dominios.TIPO_ESCOLA, "IN_TREINEIRO": dominios.TREINEIRO,
        "TP_LINGUA": dominios.LINGUA,
    }
    colunas = ["sk_perfil"]
    for codigo, dominio in descricoes.items():
        nome_ds = "ds_" + codigo.split("_", 1)[1].lower()
        dim[nome_ds] = dim[codigo].map(lambda c, d=dominio: dominios.descrever(c, d))
        colunas += [codigo, nome_ds]
    return dim[colunas]


def _montar_dim_escola(catalogos: Catalogos) -> pd.DataFrame:
    """Monta a dimensão de escola, com a linha 0 para "não informada"."""
    linhas = [(0, None, "Não informada", None, None, None, "Não informada",
               None, "Não informada", None, "Não informada")]
    for (municipio, dependencia, localizacao, situacao), sk in catalogos.escola.items():
        nome, co_uf, sg_uf = catalogos.atributos_escola[municipio]
        linhas.append((
            sk, municipio, nome, co_uf, sg_uf,
            None if dependencia == SEM_VALOR else dependencia,
            dominios.descrever(dependencia, dominios.DEPENDENCIA_ADM),
            None if localizacao == SEM_VALOR else localizacao,
            dominios.descrever(localizacao, dominios.LOCALIZACAO),
            None if situacao == SEM_VALOR else situacao,
            dominios.descrever(situacao, dominios.SIT_FUNCIONAMENTO),
        ))
    return pd.DataFrame(linhas).astype(
        {0: "int64", 1: "Int64", 3: "Int16", 5: "Int16", 7: "Int16", 9: "Int16"}
    )


def _montar_dim_local_prova(catalogo: dict) -> pd.DataFrame:
    """Monta a dimensão de local de prova a partir do catálogo."""
    return pd.DataFrame(
        [(sk, codigo, nome, co_uf, sg_uf) for codigo, (sk, nome, co_uf, sg_uf) in catalogo.items()]
    )


def executar(caminho_csv: Path = config.CAMINHO_CSV, pasta: Path = PASTA_SAIDA) -> ResumoTransformacao:
    """Transforma o CSV do Inep nos arquivos das tabelas do modelo.

    Returns:
        Resumo com o número de linhas lidas, de linhas do fato e o caminho
        de cada arquivo gerado.
    """
    pasta.mkdir(parents=True, exist_ok=True)
    arquivos = {nome: pasta / f"{nome}.tsv" for nome in (
        "fato_participacao", "dim_questionario", "dim_perfil",
        "dim_escola", "dim_local_prova", "dim_status_redacao",
    )}
    catalogos = Catalogos()
    resumo = ResumoTransformacao(arquivos=arquivos)

    leitor = pd.read_csv(
        caminho_csv, sep=config.SEPARADOR_CSV, encoding=config.ENCODING_CSV,
        usecols=list(TIPOS_COLUNAS), dtype=TIPOS_COLUNAS, chunksize=LINHAS_POR_BLOCO,
    )
    for numero, bloco in enumerate(leitor):
        resumo.linhas_lidas += len(bloco)
        bloco = _preparar_bloco(bloco, catalogos)
        _gravar(bloco[COLUNAS_FATO], arquivos["fato_participacao"], anexar=numero > 0)
        _gravar(bloco[COLUNAS_QUESTIONARIO], arquivos["dim_questionario"], anexar=numero > 0)
        resumo.linhas_fato += len(bloco)
        log.info("Bloco %d: %d linhas (acumulado %d)", numero + 1, len(bloco), resumo.linhas_lidas)

    _gravar(_montar_dim_perfil(catalogos.perfil), arquivos["dim_perfil"], anexar=False)
    _gravar(_montar_dim_escola(catalogos), arquivos["dim_escola"], anexar=False)
    _gravar(_montar_dim_local_prova(catalogos.local_prova), arquivos["dim_local_prova"], anexar=False)
    _gravar(pd.DataFrame(list(dominios.STATUS_REDACAO.items())),
            arquivos["dim_status_redacao"], anexar=False)

    log.info(
        "Dimensões: perfil=%d, escola=%d (+1 não informada), local_prova=%d",
        len(catalogos.perfil), len(catalogos.escola), len(catalogos.local_prova),
    )
    return resumo


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    executar()
