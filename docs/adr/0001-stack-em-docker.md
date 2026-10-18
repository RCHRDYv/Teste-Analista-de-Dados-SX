# ADR-0001: Stack em Docker com MySQL 8 e imagem Python com Java

- Data: 18/10/2026
- Status: Aceito

## Contexto

O teste exige que o ETL carregue os dados num MySQL rodando em container, e Docker é um dos critérios avaliados. O pipeline também tem uma etapa em PySpark, que depende de uma JVM. Quem avaliar precisa reproduzir tudo sem instalar Python, Java ou MySQL na própria máquina.

## Decisão

Uso um `docker-compose.yml` com dois serviços:

- `mysql`: imagem oficial `mysql` na linha 8.0, com versão fixa, healthcheck, volume nomeado e `local_infile` habilitado para a carga em lote.
- `app`: imagem própria a partir de `python:3.11-slim-bookworm`, com OpenJDK 17 headless e as dependências Python em versões fixas. A mesma imagem roda o ETL, o job PySpark, o QA e o notebook.

As credenciais ficam num `.env` fora do Git. O repositório versiona apenas o `.env.example`.

O repositório também traz um `.devcontainer/devcontainer.json` com Docker habilitado, para abrir o projeto num GitHub Codespaces e rodar a mesma sequência de comandos.

## Consequências

- Uma única imagem de aplicação evita divergência de versões entre ETL, Spark e notebook.
- A imagem fica maior por causa do Java, mas o build acontece uma vez só.
- Todas as versões são fixas, então o resultado não muda se uma biblioteca lançar versão nova.
