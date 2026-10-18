# ADR-0003: pandas no ETL principal e PySpark no recálculo dos indicadores

- Data: 18/10/2026
- Status: Aceito

## Contexto

O teste pede o ETL em Python e lista PySpark como desejável. O CSV tem cerca de 5,8 milhões de linhas e cabe em memória quando lido em blocos com tipos explícitos.

## Decisão

- O ETL principal (extração, transformação e carga no MySQL) usa pandas, lendo o CSV em chunks com `usecols` e `dtype` definidos.
- O PySpark roda um job separado que lê o CSV bruto e recalcula os oito indicadores sem passar pelo MySQL.
- O script de QA compara os indicadores calculados em SQL sobre o modelo com os indicadores calculados em PySpark sobre o arquivo original.

## Consequências

- O ETL fica simples de ler e depurar.
- O PySpark tem papel próprio: serve de verificação independente da carga e da modelagem. Se SQL e Spark divergirem, algum passo do ETL perdeu ou duplicou dados.
- O pipeline tem duas bibliotecas de processamento, cada uma com responsabilidade separada.
