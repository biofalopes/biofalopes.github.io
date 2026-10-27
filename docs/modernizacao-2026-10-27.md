# Modernização visual e técnica — 27/10/2026

## Identidade visual

O blog passa a apresentar Fabio Lopes e seus trabalhos antes do arquivo cronológico. A identidade usa azul profundo, verde, fundo claro e tipografia do sistema, sem downloads de fontes externas. O monograma `fl.` aparece na navegação, nos ícones e na imagem de compartilhamento.

A homepage tem apresentação curta, uma representação das etapas de engenharia, três trabalhos selecionados e artigos recentes. A página de trabalhos amplia a mesma curadoria. Navegação, busca, arquivo e artigos compartilham o cabeçalho; os artigos apresentam título principal, publicação, revisão técnica, tempo de leitura e traduções.

Os textos da interface e a curadoria estão separados em `data/interface.yaml` e `data/work.yaml`. O seletor de idioma aponta para a tradução existente; trabalhos disponíveis apenas em inglês recebem a indicação EN. O modo escuro segue a preferência do sistema e permite escolha manual.

Foram incluídos foco visível, link para saltar ao conteúdo, menu móvel nativo, fechamento do menu por Escape, redução de movimento e rótulos acessíveis. Os estilos foram revisados no Chrome em desktop e em viewport móvel de 400 × 596 pixels.

## Atualizações de componentes

Versões estáveis verificadas nas fontes oficiais em 27/10/2026:

| Componente | Versão adotada | Referência |
|---|---|---|
| Hugo Extended | 0.168.0 | [Release oficial](https://github.com/gohugoio/hugo/releases/tag/v0.168.0) |
| Stack | 4.0.3 | [Release oficial](https://github.com/CaiJimmy/hugo-theme-stack/releases/tag/v4.0.3) |
| Go | 1.27.3 | [Downloads oficiais](https://go.dev/dl/) |
| Dart Sass | 1.106.1 | [Release oficial](https://github.com/sass/dart-sass/releases/tag/1.106.1) |
| Python do CI | 3.15.2 | [Release oficial](https://www.python.org/downloads/release/python-3152/) |
| PhotoSwipe | 5.4.4 | [Release oficial](https://github.com/dimsemenov/PhotoSwipe/releases/tag/v5.4.4) |
| KaTeX | 0.19.1 | [Release oficial](https://github.com/KaTeX/KaTeX/releases/tag/v0.19.1) |
| Mermaid | 12.2.0 | [Pacote oficial](https://www.npmjs.com/package/mermaid/v/12.2.0) |

Actions: checkout 7.0.1, setup-go 7.0.0, setup-python 7.1.0, upload-artifact 7.0.2, upload-pages-artifact 5.0.0, configure-pages 6.0.0 e deploy-pages 5.0.1. Os SHAs foram resolvidos pelas referências das tags oficiais e fixados no workflow.

A cópia antiga do Stack foi removida. O tema é um Hugo Module fixado por `go.mod`/`go.sum`, e os overrides usam a organização do v4. As configurações de idiomas usam `locale`/`label`; avatar, favicon e processamento de imagens seguem a API atual. O Sass usa Dart Sass explicitamente. As advertências de importação e funções antigas conhecidas do SCSS upstream são silenciadas por nome; os avisos do Hugo continuam fazendo o build falhar.

As atualizações se aplicam à plataforma do blog e às suas ferramentas. Versões históricas descritas em tutoriais, como os charts Loki/Mimir, continuam identificadas como históricas; não foram convertidas em alegações de novos deployments.

## Workflow e manutenção

- Ferramentas Windows ficam em `.tools/`, com hashes verificados e sem instalação global.
- `scripts/blog.ps1 serve`, `check` e `build` documentam o ciclo local. Preview e produção têm destinos separados.
- CI usa ferramentas fixadas, valida módulos e exemplos, gera o site e confere referências, idiomas e metadados.
- Um grupo de concorrência exclusivo serializa os deployments de produção.
- Pull requests recebem um artefato de revisão; somente `main` publica no Pages.
- Dependabot monitora Actions e o módulo do tema. Novas versões de ferramentas exigem atualização explícita dos pins e hashes.
- A paginação mantém três artigos por página para preservar a estrutura existente. O parsing de datas continua em UTC, preservando os metadados originais; datas são exibidas conforme o idioma.
- Analytics e comentários ficam desabilitados no desenvolvimento. Em produção, o suporte de consentimento do Stack controla o carregamento das integrações configuradas.

## Verificação e limites

O build de produção passou com Hugo 0.168.0 e Sass 1.106.1, sem avisos do Hugo. Os 14 testes dos artigos passaram com Python 3.15.2. As 44 rotas e datas de publicação do inventário foram preservadas, e a saída foi conferida quanto a referências locais, traduções, downloads, metadados e exclusão de rascunhos.

Os scripts PowerShell e Bash passaram em análise de sintaxe. A imagem social e os ícones foram exportados dos SVGs do projeto; a imagem social foi inspecionada visualmente.

A revisão no Chrome confirmou a homepage, a alternância EN/PT, os modos claro e escuro, a busca em português (consulta Ceph), a abertura do artigo correspondente e o menu móvel com fechamento por Escape. Foram corrigidos o contraste dos textos introdutórios no modo escuro, o tamanho de legendas, os cantos do campo de busca, a decoração do rodapé e a disposição dos metadados dos artigos. O build e as verificações automatizadas foram repetidos com sucesso após os ajustes.

Galeria, consentimento, matemática e diagramas opcionais ainda precisam de testes interativos específicos. Não foi executado Lighthouse. O workflow Linux precisa executar no GitHub para confirmar a integração completa das novas Actions. Nenhuma publicação foi realizada nesta etapa.
