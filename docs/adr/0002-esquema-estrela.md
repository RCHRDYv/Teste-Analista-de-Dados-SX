# ADR-0002: Esquema estrela com grão de uma linha por inscrição

- Data: 18/10/2026
- Status: Aceito

## Contexto

O arquivo `MICRODADOS_ENEM_2020.csv` tem uma linha por inscrição e reúne, na mesma linha, perfil do participante, dados da escola, local de prova, presença, notas, redação e as 25 questões do questionário socioeconômico. As perguntas do teste cruzam notas com perfil, escola, redação e questionário.

## Decisão

Modelo em esquema estrela com o grão do fato declarado como **uma linha por inscrição**.

- `fato_participacao`: chaves das dimensões, `nu_inscricao` como dimensão degenerada, presença por prova, as quatro notas objetivas, a nota da redação, as cinco competências, o status da redação e a média das quatro provas objetivas.
- `dim_perfil`: dimensão junk com atributos de baixa cardinalidade do participante (sexo, faixa etária, cor/raça, estado civil, nacionalidade, treineiro), já decodificados em texto. A combinação desses atributos gera poucas centenas de linhas.
- `dim_escola`: atributos da escola declarada (município e UF da escola, dependência administrativa, localização, situação de funcionamento), com chave substituta.
- `dim_local_prova`: município e UF de aplicação da prova.
- `dim_questionario`: mini-dimensão 1:1 com as questões Q001 a Q025, ligada ao fato pela inscrição.

## Consequências

- O fato fica estreito e as consultas de indicadores não precisam ler as 25 colunas do questionário.
- O questionário separado evita uma dimensão junk com quase uma linha por participante.
- Como a relação fato x questionário é 1:1, o join não multiplica linhas. O QA confere isso.
