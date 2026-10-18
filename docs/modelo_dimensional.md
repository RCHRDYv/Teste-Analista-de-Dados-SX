# Modelo dimensional

Esquema estrela com um fato e cinco dimensões (ADR-0002). O DDL está em [`sql/01_schema.sql`](../sql/01_schema.sql).

**Grão do fato:** uma linha por inscrição no ENEM 2020.

```mermaid
erDiagram
    fato_participacao }o--|| dim_perfil : sk_perfil
    fato_participacao }o--|| dim_escola : sk_escola
    fato_participacao }o--|| dim_local_prova : sk_local_prova
    fato_participacao }o--|| dim_status_redacao : tp_status_redacao
    fato_participacao ||--|| dim_questionario : nu_inscricao

    fato_participacao {
        bigint nu_inscricao PK
        int sk_perfil FK
        int sk_escola FK
        int sk_local_prova FK
        tinyint tp_status_redacao FK
        tinyint tp_presenca_cn_ch_lc_mt
        decimal nu_nota_cn_ch_lc_mt
        smallint nu_nota_comp1_a_comp5
        smallint nu_nota_redacao
        decimal nu_media_objetivas
    }
    dim_perfil {
        int sk_perfil PK
        tinyint tp_faixa_etaria
        char tp_sexo
        tinyint tp_estado_civil
        tinyint tp_cor_raca
        tinyint tp_nacionalidade
        tinyint tp_st_conclusao
        tinyint tp_escola
        tinyint in_treineiro
        tinyint tp_lingua
    }
    dim_escola {
        int sk_escola PK
        int co_municipio_esc
        varchar no_municipio_esc
        char sg_uf_esc
        tinyint tp_dependencia_adm_esc
        tinyint tp_localizacao_esc
        tinyint tp_sit_func_esc
    }
    dim_local_prova {
        int sk_local_prova PK
        int co_municipio_prova
        varchar no_municipio_prova
        char sg_uf_prova
    }
    dim_status_redacao {
        tinyint tp_status_redacao PK
        varchar ds_status_redacao
    }
    dim_questionario {
        bigint nu_inscricao PK
        char q001_a_q025
    }
```

## Tabelas

| Tabela | Tipo | Chave | Conteúdo |
|---|---|---|---|
| `fato_participacao` | Fato | `nu_inscricao` | Presença nas quatro provas objetivas, notas, competências e nota da redação, média das objetivas e as chaves das dimensões |
| `dim_perfil` | Dimensão junk | `sk_perfil` | Combinações de faixa etária, sexo, estado civil, cor/raça, nacionalidade, situação de conclusão, tipo de escola, treineiro e língua estrangeira, com código e descrição |
| `dim_escola` | Dimensão | `sk_escola` | Município, UF, dependência administrativa, localização e situação de funcionamento da escola declarada. A linha 0 é "não informada" |
| `dim_local_prova` | Dimensão | `sk_local_prova` | Município e UF de aplicação da prova |
| `dim_status_redacao` | Dimensão | `tp_status_redacao` | Situação da redação. O código 0 ("sem redação") não existe no dicionário e cobre quem não teve redação corrigida |
| `dim_questionario` | Mini-dimensão 1:1 | `nu_inscricao` | Respostas Q001 a Q025 do questionário socioeconômico, com os códigos do dicionário |

Regras de transformação:

- Os atributos de perfil sem valor no arquivo recebem o código -1 (ou `N` no sexo), descrito como "Não informado".
- Quem não informou o município da escola aponta para `sk_escola = 0`.
- `nu_media_objetivas` é a média das quatro provas objetivas, só para quem teve presença igual a 1 nas quatro (ADR-0006).
- `nu_inscricao` é a máscara sequencial do Inep e não identifica o participante.

## Base de origem

| Item | Valor | Fonte |
|---|---|---|
| Arquivo | `DADOS/MICRODADOS_ENEM_2020.csv`, dentro de `microdados_enem_2020.zip` (620.776.982 bytes) | Portal de microdados do Inep |
| Formato | CSV separado por `;`, encoding latin-1, com cabeçalho | Leia-me, seção 3 |
| Linhas de dados | 5.783.109 (uma por inscrição) | Contagem no arquivo: 5.783.110 linhas menos o cabeçalho |
| Colunas | 76 | Cabeçalho do arquivo, igual ao dicionário |
| Inscritos com escola informada | 904.569 (15,6%) | `CO_MUNICIPIO_ESC` preenchido |
| Presentes nas quatro provas objetivas | 2.588.681 | `TP_PRESENCA_*` igual a 1 nas quatro |
| Faltaram ao dia 1 (LC, CH e redação) | 3.024.590 | `TP_PRESENCA_LC` igual a 0 |
| Faltaram ao dia 2 (CN e MT) | 3.184.243 | `TP_PRESENCA_MT` igual a 0 |

O modelo simplificado de 2020 excluiu `CO_ESCOLA`, trocou `NU_IDADE` por `TP_FAIXA_ETARIA` e retirou os municípios de nascimento e residência (Leia-me, seção 3). As colunas `TX_RESPOSTAS_*` e `TX_GABARITO_*` (vetores de respostas e gabaritos) e `CO_PROVA_*` (cor do caderno) não entram no modelo, porque nenhuma pergunta do teste depende delas.
