# QA da carga

Gerado por `python -m src.qa.qa_carga`. Cada linha compara o valor obtido com o esperado; as comparações SQL x Spark aceitam diferença de até 0.01 ponto por arredondamento.

| Verificação | Obtido | Esperado | Resultado |
|---|---|---|---|
| Linhas do fato = linhas do CSV | 5783109 | 5783109 | OK |
| Linhas do questionário = linhas do CSV | 5783109 | 5783109 | OK |
| Inscrições distintas no fato | 5783109 | 5783109 | OK |
| Chaves do fato sem dim_perfil | 0 | 0 | OK |
| Chaves do fato sem dim_escola | 0 | 0 | OK |
| Chaves do fato sem dim_local_prova | 0 | 0 | OK |
| Chaves do fato sem dim_status_redacao | 0 | 0 | OK |
| Chaves do fato sem dim_questionario | 0 | 0 | OK |
| Linhas após join com todas as dimensões (fan-out) | 5783109 | 5783109 | OK |
| Notas objetivas fora de 0 a 1000 | 0 | 0 | OK |
| Notas da redação fora de 0 a 1000 | 0 | 0 | OK |
| Competências fora de 0 a 200 | 0 | 0 | OK |
| Nota de CN sem presença (ou presença sem nota) | 0 | 0 | OK |
| Nota de CH sem presença (ou presença sem nota) | 0 | 0 | OK |
| Nota de LC sem presença (ou presença sem nota) | 0 | 0 | OK |
| Nota de MT sem presença (ou presença sem nota) | 0 | 0 | OK |
| Média preenchida fora da regra das quatro presenças | 0 | 0 | OK |
| SQL x Spark: total de inscritos | 5783109 | 5783109 | OK |
| SQL x Spark: % ausente em algum dia | 55.21 | 55.21 | OK |
| SQL x Spark: % ausente no dia 1 | 52.3 | 52.3 | OK |
| SQL x Spark: % ausente no dia 2 | 55.06 | 55.06 | OK |
| SQL x Spark: média geral | 512.89 | 512.89 | OK |
| SQL x Spark: presentes nas quatro provas | 2588681 | 2588681 | OK |
| SQL x Spark: maior média individual | 830.95 | 830.95 | OK |
| SQL x Spark: inscrições com a maior média | [200001357436] | [200001357436] | OK |
| SQL x Spark: média de Ciências da Natureza | 490.41 | 490.41 | OK |
| SQL x Spark: média de Ciências Humanas | 511.15 | 511.15 | OK |
| SQL x Spark: média de Linguagens e Códigos | 523.8 | 523.8 | OK |
| SQL x Spark: média de Matemática | 520.58 | 520.58 | OK |
| SQL x Spark: média de Redação | 573.41 | 573.41 | OK |
| SQL x Spark: média sexo Masculino | 528.58 | 528.58 | OK |
| SQL x Spark: média sexo Feminino | 502.61 | 502.61 | OK |
| SQL x Spark: média cor/raça Branca | 539.92 | 539.92 | OK |
| SQL x Spark: média cor/raça Não declarado | 522.08 | 522.08 | OK |
| SQL x Spark: média cor/raça Amarela | 511.22 | 511.22 | OK |
| SQL x Spark: média cor/raça Parda | 496.35 | 496.35 | OK |
| SQL x Spark: média cor/raça Preta | 490.58 | 490.58 | OK |
| SQL x Spark: média cor/raça Indígena | 467.16 | 467.16 | OK |
| SQL x Spark: grupo de escola com maior média: participantes | 153 | 153 | OK |
| SQL x Spark: grupo de escola com maior média: média | 688.6 | 688.6 | OK |
