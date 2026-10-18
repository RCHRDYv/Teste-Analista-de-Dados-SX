# ADR-0005: Agrupamento de escola sem CO_ESCOLA

- Data: 18/10/2026
- Status: Aceito

## Contexto

A primeira pergunta do teste é qual escola tem a maior média de notas. O Leia-me dos Microdados do Enem 2020 (Inep, fevereiro de 2022, seção 3, página 7) informa que, com a adoção do modelo simplificado de microdados por causa da LGPD, a variável `CO_ESCOLA` foi excluída da tabela `MICRODADOS_ENEM_2020`. Sem ela, não há como identificar uma escola individual no arquivo público. O dicionário da mesma edição confirma que o bloco "Dados da escola" traz apenas município, UF, dependência administrativa, localização e situação de funcionamento.

## Decisão

Respondo a pergunta no nível mais fino disponível no arquivo: o grupo formado por município da escola, dependência administrativa e localização. Só entram grupos com pelo menos 30 participantes presentes nas quatro provas, para que um grupo com poucos alunos não fique no topo por acaso. A resposta traz o grupo, a média e o número de participantes.

## Consequências

- A resposta deixa claro que não se trata de uma escola individual e explica o motivo, citando o Leia-me.
- Só 904.569 dos 5.783.109 inscritos (15,6%) têm escola informada (`CO_MUNICIPIO_ESC` preenchido). Esse número aparece junto da resposta.
