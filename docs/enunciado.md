# Enunciado do teste de Analista de Dados

Texto original do repositório [dheiver/Teste-Analista-de-Dados-SX](https://github.com/dheiver/Teste-Analista-de-Dados-SX), mantido sem alterações abaixo desta nota.

---

# Teste de Analista de Dados
Critérios avaliadas:
- Docker;
- SQL;
- Python;
- Organização do Código
- Documentação
- ETL
- Modelagem dos dados

### Desejáveis
- PySpark
- Esquema Estrela


### Steps:

1. Realizar um Fork desse projeto
2. Realizar a modelagem dimensional da base
    - A base está disponível para download [clicando aqui](https://download.inep.gov.br/microdados/microdados_enem_2020.zip).
    - Após descompactar a paste, o Arquivo com a base encontra-se no diretório microdados_enem_2020/DADOS/MICRODADOS_ENEM_2020.csv
    - A documentação necessária sobre os campos da base está disponível nos demais diretórios dentro da pasta descompactada.
3. Realizar o ETL dessa base em Python para o MySQL no container
4. Disponibilizar o link do seu repositório para posterior avaliação


### Levantar Indicadores
#### Responder às seguintes perguntas:
1. Qual a escola com a maior média de notas?
2. Qual o aluno com a maior média de notas e o valor dessa média?
3. Qual a média geral?
4. Qual o % de Ausentes?
5. Qual o número total de Inscritos?
6. Qual a média por disciplina?
7. Qual a média por Sexo?
8. Qual a média por Etnia?

### Levantar Visões
1. Gere visualizações gráficas que demonstrem a nota como indicador, trazendo as dimensões e os gráficos que melhor possam representar 
a informação para avaliação da performance.
2. Analisar correlações de variáveis que identificar dentro do dataset com a variável dependente nota total (NU_NOTA_CN
NU_NOTA_CH, NU_NOTA_LC, NU_NOTA_M.T).
3. Gerar visualizações (Data viz) que melhor estratifiquem e demonstremos dados do bloco de DADOS DA REDAÇÃO, verificando o comportamento
das notas 4 provas vs. estes dados.
4. Gerar visualizações (Data viz) que melhor estratifiquem e demonstremos dados do bloco de DADOS DO QUESTIONÁRIO SOCIOECONÔMICO, verificando
o comportamento das notas 4 provas vs. estes dados.
5. Faça um resumo em 10 bullets de Conclusões e Insights.

### sugestões
1. Tableau.
2. Power BI.
3. Qlik.
4. Power Point.
5. Excel.
6. Colab.





