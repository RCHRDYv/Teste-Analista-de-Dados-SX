# ADR-0007: Visualizações em notebook com imagens estáticas no README

- Data: 18/10/2026
- Status: Aceito

## Contexto

O teste sugere ferramentas como Power BI, Tableau ou Colab para as visões. Quem avalia precisa ver os gráficos sem instalar software e, de preferência, conseguir reproduzi-los. O visualizador de notebooks do GitHub não renderiza gráficos interativos do Plotly.

## Decisão

As visões ficam num notebook Jupyter que roda no container `app`, consulta o MySQL e gera os gráficos com matplotlib e seaborn. Cada gráfico é exportado como PNG com fundo branco em `docs/img/` e embutido no README.

## Consequências

- Os gráficos aparecem direto no GitHub, nos temas claro e escuro.
- O notebook pode ser reexecutado dentro do Docker para regenerar as imagens.
- Não há filtros interativos. As visões trazem os recortes já escolhidos.
