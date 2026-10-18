# ADR-0006: Definições das métricas

- Data: 18/10/2026
- Status: Aceito

## Contexto

As perguntas do teste usam termos que admitem mais de uma leitura, como "média geral" e "% de ausentes". Sem definição explícita, dois analistas chegam a números diferentes a partir da mesma base.

O dicionário do Enem 2020 define a presença em cada prova objetiva (`TP_PRESENCA_CN`, `_CH`, `_LC`, `_MT`) com três códigos: 0 (faltou à prova), 1 (presente na prova) e 2 (eliminado na prova). O Leia-me (seção 2, página 6) informa que, em 2020, o primeiro dia teve Linguagens, Redação e Ciências Humanas, e o segundo teve Ciências da Natureza e Matemática.

## Decisão

- **Média do participante**: média aritmética das quatro provas objetivas (CN, CH, LC, MT), que o enunciado chama de nota total. Só é calculada para quem teve presença igual a 1 nas quatro provas. A redação é analisada à parte.
- **Média geral**: média das médias dos participantes. A média simples de todas as notas objetivas aparece ao lado, para comparação.
- **Média por disciplina**: média de cada prova entre os presentes naquela prova.
- **% de ausentes**: o indicador principal é o percentual de inscritos que faltaram (código 0) a pelo menos um dos dois dias de prova. Ao lado vêm o percentual por dia (dia 1: LC, CH e redação; dia 2: CN e MT) e por prova. Eliminados (código 2) não contam como ausentes.
- **Total de inscritos**: número de linhas do arquivo, uma por inscrição.
- **Aluno com maior média**: o `NU_INSCRICAO` (máscara sequencial gerada pelo Inep, que não identifica a pessoa) com a maior média do participante. Em caso de empate, a resposta lista todas as inscrições empatadas.
- **Média por sexo e por cor/raça**: média do participante agrupada por `TP_SEXO` e `TP_COR_RACA`. Uso o termo "cor/raça" do dicionário do Inep, com a "etnia" do enunciado entre parênteses.

## Consequências

- Todos os números do README podem ser refeitos a partir destas regras.
- O job PySpark e o SQL seguem as mesmas definições, então o QA compara números equivalentes.
