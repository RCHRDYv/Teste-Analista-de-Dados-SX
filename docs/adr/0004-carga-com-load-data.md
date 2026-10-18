# ADR-0004: Carga no MySQL com LOAD DATA LOCAL INFILE

- Data: 18/10/2026
- Status: Aceito

## Contexto

Inserir cerca de 5,8 milhões de linhas com `DataFrame.to_sql` gera um volume grande de comandos `INSERT` e pode levar horas. O MySQL tem um caminho próprio de carga em lote a partir de arquivos.

## Decisão

A etapa de transformação grava um CSV limpo por tabela do modelo. A etapa de carga usa `LOAD DATA LOCAL INFILE` para cada arquivo, primeiro as dimensões e depois o fato. O servidor sobe com `local_infile=1` e a conexão Python habilita a opção do lado do cliente.

## Consequências

- A carga do fato fica na ordem de minutos.
- Os CSVs intermediários ficam em `data/`, fora do Git, e permitem reprocessar só a carga.
- A carga é idempotente: cada execução esvazia as tabelas antes de carregar.
