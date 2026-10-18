# Modelo dimensional

## Base de origem

| Item | Valor | Fonte |
|---|---|---|
| Arquivo | `DADOS/MICRODADOS_ENEM_2020.csv`, dentro de `microdados_enem_2020.zip` (620.776.982 bytes) | Portal de microdados do Inep |
| Formato | CSV separado por `;`, encoding latin-1, com cabeçalho | Leia-me, seção 3 |
| Linhas de dados | 5.783.109 (uma por inscrição) | Contagem no arquivo: 5.783.110 linhas menos o cabeçalho |
| Colunas | 76 | Cabeçalho do arquivo, igual ao dicionário |
| Inscritos com escola informada | 904.569 (15,6%) | `CO_MUNICIPIO_ESC` preenchido |
| Presentes nas quatro provas objetivas | 2.588.681 | `TP_PRESENCA_*` igual a 1 nas quatro |
| Faltaram ao dia 1 (LC, CH e redação) | 3.024.590 | `TP_PRESENCA_LC` igual a 0 |
| Faltaram ao dia 2 (CN e MT) | 3.184.243 | `TP_PRESENCA_MT` igual a 0 |

O modelo simplificado de 2020 excluiu `CO_ESCOLA`, trocou `NU_IDADE` por `TP_FAIXA_ETARIA` e retirou os municípios de nascimento e residência (Leia-me, seção 3). As colunas `TX_RESPOSTAS_*` e `TX_GABARITO_*` (vetores de respostas e gabaritos) e `CO_PROVA_*` (cor do caderno) não entram no modelo, porque nenhuma pergunta do teste depende delas.
