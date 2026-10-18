# ADR-0005: Agrupamento de escola sem CO_ESCOLA

- Data: 18/10/2026
- Status: Proposto (confirmar no Leia-me e no dicionário do Inep)

## Contexto

A primeira pergunta do teste é qual escola tem a maior média de notas. A partir do ENEM 2020, o Inep passou a publicar os microdados num modelo simplificado e retirou a variável `CO_ESCOLA`, que identificava a escola onde o participante declarou concluir o ensino médio. Sem ela, não há como identificar uma escola individual no arquivo público.

## Decisão

Respondo a pergunta no nível mais fino disponível no arquivo: o grupo formado por município da escola, dependência administrativa e localização. Só entram grupos com pelo menos 30 participantes presentes nas quatro provas, para que um grupo com poucos alunos não fique no topo por acaso. A resposta traz o grupo, a média e o número de participantes.

## Consequências

- A resposta deixa claro que não se trata de uma escola individual e explica o motivo.
- A maior parte dos inscritos não informa escola, porque esses campos costumam vir preenchidos só para quem concluía o ensino médio no ano. O número de participantes com escola informada aparece junto da resposta.
