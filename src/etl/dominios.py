"""Domínios das variáveis categóricas, copiados do dicionário do Inep.

Fonte: DICIONÁRIO/Dicionário_Microdados_Enem_2020.xlsx, dentro do zip dos
microdados. O código -1 representa valor ausente no arquivo e não existe
no dicionário original.
"""

NAO_INFORMADO = "Não informado"

FAIXA_ETARIA = {
    1: "Menor de 17 anos", 2: "17 anos", 3: "18 anos", 4: "19 anos",
    5: "20 anos", 6: "21 anos", 7: "22 anos", 8: "23 anos", 9: "24 anos",
    10: "25 anos", 11: "Entre 26 e 30 anos", 12: "Entre 31 e 35 anos",
    13: "Entre 36 e 40 anos", 14: "Entre 41 e 45 anos",
    15: "Entre 46 e 50 anos", 16: "Entre 51 e 55 anos",
    17: "Entre 56 e 60 anos", 18: "Entre 61 e 65 anos",
    19: "Entre 66 e 70 anos", 20: "Maior de 70 anos",
}

SEXO = {"M": "Masculino", "F": "Feminino"}

ESTADO_CIVIL = {
    0: "Não informado", 1: "Solteiro(a)",
    2: "Casado(a)/Mora com companheiro(a)",
    3: "Divorciado(a)/Desquitado(a)/Separado(a)", 4: "Viúvo(a)",
}

COR_RACA = {
    0: "Não declarado", 1: "Branca", 2: "Preta", 3: "Parda",
    4: "Amarela", 5: "Indígena",
}

NACIONALIDADE = {
    0: "Não informado", 1: "Brasileiro(a)",
    2: "Brasileiro(a) Naturalizado(a)", 3: "Estrangeiro(a)",
    4: "Brasileiro(a) Nato(a), nascido(a) no exterior",
}

ST_CONCLUSAO = {
    1: "Já concluí o Ensino Médio",
    2: "Estou cursando e concluirei o Ensino Médio em 2020",
    3: "Estou cursando e concluirei o Ensino Médio após 2020",
    4: "Não concluí e não estou cursando o Ensino Médio",
}

TIPO_ESCOLA = {1: "Não respondeu", 2: "Pública", 3: "Privada", 4: "Exterior"}

TREINEIRO = {0: "Não", 1: "Sim"}

LINGUA = {0: "Inglês", 1: "Espanhol"}

DEPENDENCIA_ADM = {1: "Federal", 2: "Estadual", 3: "Municipal", 4: "Privada"}

LOCALIZACAO = {1: "Urbana", 2: "Rural"}

SIT_FUNCIONAMENTO = {
    1: "Em atividade", 2: "Paralisada", 3: "Extinta",
    4: "Escola extinta em anos anteriores.",
}

# O código 0 não existe no dicionário: representa quem não tem redação
# corrigida (faltou ao primeiro dia ou foi eliminado).
STATUS_REDACAO = {
    0: "Sem redação",
    1: "Sem problemas", 2: "Anulada", 3: "Cópia texto motivador",
    4: "Em branco", 6: "Fuga ao tema", 7: "Não atendimento ao tipo textual",
    8: "Texto insuficiente", 9: "Parte desconectada",
}


def descrever(codigo, dominio: dict) -> str:
    """Devolve a descrição de um código, ou "Não informado" se não houver."""
    return dominio.get(codigo, NAO_INFORMADO)
