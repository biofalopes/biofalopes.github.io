# Restauração do artigo de previsão Ceph — 27/10/2026

A revisão anterior substituiu a implementação do autor por um exemplo novo e
transformou o relato de um projeto entregue em documentação desse exemplo.
Essa alteração não preservava a autoria nem o contexto do portfólio e foi desfeita.

## Origem e alterações

- Recuperados os artigos EN/PT e o código Python do commit `218eb63`, anterior
  às revisões automatizadas do conteúdo. O código nas duas línguas era idêntico.
- O código original está em `content/post/jupyter-forecast/forecast.py`, exibido
  integralmente e aberto por padrão nos dois artigos. Sua lógica não foi alterada.
  A comparação com o bloco original é exata após normalizar finais de linha,
  inclusive preservando os espaços do código histórico.
- O contexto que estava em “Melhorias futuras” foi trazido para o início:
  urgência na aquisição de hardware, colaboração na lógica de previsão, Jupyter,
  integração com Mimir, agendamento, gráficos e Teams.
- Mantidos os títulos, data de publicação, imagem, idiomas e URLs. Headings foram
  adaptados à hierarquia atual e o índice permanece habilitado.
- Cartão Selected Work e visão geral agora descrevem o projeto original. Foram
  removidas as atribuições de testes e funcionalidades do exemplo substituto.
- Removida a amostra sintética e os 11 testes da implementação substituta. Eles
  não validavam o código do autor. Os testes de ordenação e Fibonacci permanecem.
- Notas editoriais ao final distinguem o código histórico de uma nova implantação
  e esclarecem a terminologia sem modificar o algoritmo.

O código histórico não foi executado: ele faz chamadas ao Mimir e ao Teams e
depende do ambiente original. A validação compara o arquivo recuperado com o
bloco Python do histórico, verifica sua sintaxe e confere a saída HTML nas duas
línguas. Isso não é uma alegação de correção estatística ou segurança atual.

As demais alterações pendentes, incluindo o novo post PHP2Shell e sua seleção
para Selected Work, foram preservadas. Nenhum commit ou deploy foi realizado.
