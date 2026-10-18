# ADR-0004: Carga no MySQL com LOAD DATA LOCAL INFILE

- Data: 18/10/2026
- Status: Aceito

## Contexto

Inserir cerca de 5,8 milhões de linhas com `DataFrame.to_sql` gera um volume grande de comandos `INSERT` e pode levar horas. O MySQL tem um caminho próprio de carga em lote a partir de arquivos.

## Decisão

A etapa de transformação grava um CSV limpo por tabela do modelo. A etapa de carga usa `LOAD DATA LOCAL INFILE` para cada arquivo, primeiro as dimensões e depois o fato. O servidor sobe com `local_infile=1` e a conexão Python habilita a opção do lado do cliente.

O MySQL do container sobe sem log binário (`--skip-log-bin`), com redo log de 2 GB e `innodb_flush_log_at_trx_commit=2`. É um banco analítico local, sem replicação, e o log binário duplicava as escritas da carga.

## Consequências

- Num Codespace de 4 núcleos, a carga das seis tabelas levou 317 segundos (88 s para o questionário e 229 s para o fato). Antes desses ajustes do servidor, a carga do fato ainda não tinha terminado depois de 319 segundos; com eles, terminou em 229.
- Os ajustes trocam durabilidade por velocidade: uma queda do servidor no meio da carga pode perder a última transação. Como a carga é refeita do zero a cada execução, essa perda não afeta o resultado.
- Os CSVs intermediários ficam em `data/`, fora do Git, e permitem reprocessar só a carga.
- A carga é idempotente: cada execução esvazia as tabelas antes de carregar.
