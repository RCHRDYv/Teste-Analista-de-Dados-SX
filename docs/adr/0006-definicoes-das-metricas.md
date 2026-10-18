# ADR-0006: Definições das métricas

- Data: 18/10/2026
- Status: Proposto (confirmar os códigos de presença no dicionário do Inep)

## Contexto

As perguntas do teste usam termos que admitem mais de uma leitura, como "média geral" e "% de ausentes". Sem definição explícita, dois analistas chegam a números diferentes a partir da mesma base.

## Decisão

- **Média do participante**: média aritmética das quatro provas objetivas (CN, CH, LC, MT), que o enunciado chama de nota total. Só é calculada para quem esteve presente nas quatro provas. A redação é analisada à parte.
- **Média geral**: média das médias dos participantes. A média simples de todas as notas objetivas aparece ao lado, para comparação.
- **Média por disciplina**: média de cada prova entre os presentes naquela prova.
- **% de ausentes**: o indicador principal é o percentual de inscritos que faltaram a pelo menos um dos dois dias de prova. Ao lado vêm o percentual por dia (dia 1: LC, CH e redação; dia 2: CN e MT) e por prova. Eliminados não contam como ausentes.
- **Total de inscritos**: número de linhas do arquivo, uma por inscrição.
- **Aluno com maior média**: o `NU_INSCRICAO` (mascarado pelo Inep) com a maior média do participante. Em caso de empate, a resposta lista todas as inscrições empatadas.
- **Média por sexo e por cor/raça**: média do participante agrupada por `TP_SEXO` e `TP_COR_RACA`. Uso o termo "cor/raça" do dicionário do Inep, com a "etnia" do enunciado entre parênteses.

## Consequências

- Todos os números do README podem ser refeitos a partir destas regras.
- O job PySpark e o SQL seguem as mesmas definições, então o QA compara números equivalentes.
