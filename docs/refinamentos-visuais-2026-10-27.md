# Refinamentos de leitura e portfólio — 27/10/2026

## Alterações

- Três diagramas SVG localizados, com cores adaptadas aos modos claro e escuro,
  nos cartões de projetos. Diagramas e tendência de crescimento são identificados
  como representações simplificadas, sem métricas de produção inventadas.
- Cabeçalhos de artigos com título em primeiro plano e capa reduzida. Os três
  trabalhos selecionados recebem um resumo de problema, contribuição, decisão
  e resultado/limitações. A tradução do artigo Ceph também recebe o resumo.
- Texto pequeno elevado para pelo menos 12 px nas regras personalizadas;
  controles de tema e menu com área de 44 px e seletor de idioma mais espaçado.
  Os cartões usam duas colunas em tablets e uma em celulares.
- About/Sobre com retrato, apresentação, quatro áreas de atuação, certificações
  já declaradas no conteúdo original e contatos GitHub/LinkedIn. URLs de currículo
  e verificação de credenciais são opcionais; não foram inventadas.
- Índice móvel nativo do Stack com apresentação revisada e fechamento ao escolher
  uma seção. O índice também foi ativado no artigo Terraform selecionado.
- Blocos de código com linguagem e título opcional; arquivos incluídos mostram
  nome, número de linhas, download e expansão nativa a partir de 60 linhas.
  O código completo permanece no HTML, inclusive para copiar quando recolhido.
  A cópia usa a área de ferramentas para não cobrir o exemplo.
- Shortcode de notas, decisões e restrições, aplicado a trechos existentes dos
  artigos selecionados sem alterar as conclusões técnicas.

## Manutenção

O README documenta os novos campos e componentes. Os resumos ficam em
`data/case_studies.yaml`, o perfil em `data/profile.json` e as credenciais em
`data/credentials.yaml`. Os textos longos do perfil continuam nos bundles About.

## Validação

Build de produção, 14 testes dos exemplos e verificação de 247 páginas HTML
aprovados. Preservadas as 44 rotas e datas originais do inventário. O verificador
também confere IDs duplicados, os componentes dos artigos selecionados e os dois
perfis. Os recursos locais, downloads e âncoras são verificados no site gerado.

A revisão visual foi retomada no Chrome após as interrupções de acesso ao
navegador. Foram conferidos os cartões de projetos em desktop e no viewport móvel
de 400 × 591 pixels, o perfil em inglês nos modos claro/escuro e o perfil em
português no celular. O artigo Ceph em português foi revisado em desktop e celular,
incluindo visão geral, código expansível, confirmação de cópia e navegação pelo
índice móvel com fechamento automático.

A revisão identificou e corrigiu três detalhes: contraste das tags no rodapé em
modo escuro, padding duplicado no cabeçalho dos artigos e navegação para âncoras
sem descontar o cabeçalho fixo. O scroll agora respeita esse espaço e a preferência
por movimento reduzido. O build e a verificação do site foram repetidos após os
ajustes. Lighthouse e testes em outros navegadores não foram executados.

Os links públicos de verificação das certificações serão fornecidos pelo autor
em uma segunda etapa. A prévia local permanece disponível em localhost:1313.

Alterações locais, sem commit, push ou publicação nesta etapa.
