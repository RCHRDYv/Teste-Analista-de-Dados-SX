# Indicadores

Gerado por `python -m src.analise.indicadores_sql` a partir de [`sql/02_indicadores.sql`](../sql/02_indicadores.sql). Definições no [ADR-0006](adr/0006-definicoes-das-metricas.md).

## 1. Escola com a maior média (grupo município x dependência x localização, top 10)

| municipio_escola        | uf_escola   | dependencia_adm   | localizacao   | participantes   | media   |
|:------------------------|:------------|:------------------|:--------------|:----------------|:--------|
| Viçosa                  | MG          | Federal           | Urbana        | 153             | 688,60  |
| Vila Velha              | ES          | Federal           | Urbana        | 40              | 679,78  |
| Vitória                 | ES          | Federal           | Urbana        | 242             | 656,15  |
| Divinópolis             | MG          | Federal           | Urbana        | 81              | 654,05  |
| Belo Horizonte          | MG          | Federal           | Urbana        | 649             | 649,86  |
| Cachoeiro de Itapemirim | ES          | Federal           | Rural         | 68              | 648,55  |
| Timóteo                 | MG          | Federal           | Urbana        | 73              | 641,00  |
| Holambra                | SP          | Privada           | Urbana        | 47              | 639,99  |
| Pato Branco             | PR          | Federal           | Urbana        | 32              | 639,98  |
| Betim                   | MG          | Federal           | Urbana        | 121             | 636,60  |

## 2. Aluno com a maior média

| nu_inscricao   | media   | nu_nota_cn   | nu_nota_ch   | nu_nota_lc   | nu_nota_mt   |
|:---------------|:--------|:-------------|:-------------|:-------------|:-------------|
| 200001357436   | 830,95  | 795,80       | 839,50       | 713,50       | 975,00       |

## 3. Média geral

| media_das_medias   | participantes_quatro_provas   | media_de_todas_as_notas   |
|:-------------------|:------------------------------|:--------------------------|
| 512,89             | 2.588.681                     | 511,66                    |

## 4. Percentual de ausentes

| pct_ausente_algum_dia   | pct_ausente_dia_1   | pct_ausente_dia_2   | pct_ausente_dois_dias   | pct_ausente_cn   | pct_ausente_ch   | pct_ausente_lc   | pct_ausente_mt   |
|:------------------------|:--------------------|:--------------------|:------------------------|:-----------------|:-----------------|:-----------------|:-----------------|
| 55,21                   | 52,30               | 55,06               | 52,15                   | 55,06            | 52,30            | 52,30            | 55,06            |

## 5. Total de inscritos

| total_inscritos   |
|:------------------|
| 5.783.109         |

## 6. Média por disciplina

| disciplina           | media   | participantes   |
|:---------------------|:--------|:----------------|
| Ciências da Natureza | 490,41  | 2.597.440       |
| Ciências Humanas     | 511,15  | 2.754.140       |
| Linguagens e Códigos | 523,80  | 2.754.140       |
| Matemática           | 520,58  | 2.597.440       |
| Redação              | 573,41  | 2.754.140       |

## 7. Média por sexo

| sexo      | participantes   | media   |
|:----------|:----------------|:--------|
| Masculino | 1.024.630       | 528,58  |
| Feminino  | 1.564.051       | 502,61  |

## 8. Média por cor/raça (etnia)

| cor_raca      | participantes   | media   |
|:--------------|:----------------|:--------|
| Branca        | 984.621         | 539,92  |
| Não declarado | 50.000          | 522,08  |
| Amarela       | 57.449          | 511,22  |
| Parda         | 1.169.331       | 496,35  |
| Preta         | 313.315         | 490,58  |
| Indígena      | 13.965          | 467,16  |
