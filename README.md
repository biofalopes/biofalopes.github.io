# Fabio Lopes — blog e portfólio

Blog técnico e seleção de trabalhos em Cloud, Platform Engineering e SRE,
publicados em <https://fabiolopes.page/> com Hugo e Stack.

## Versões do projeto

| Componente | Versão | Fonte de configuração |
|---|---|---|
| Hugo Extended | 0.168.0 | `.hugo-version` |
| Stack | 4.0.3 | `go.mod` e `go.sum` |
| Go | 1.27.3 | `go.mod` e `.go-version` |
| Dart Sass | 1.106.1 | `.sass-version` |
| Python para validação no CI | 3.15.2 | `.python-version` |

O Hugo compila TypeScript e o Sass processa os estilos. Não é necessário
instalar Node.js ou npm. Go resolve o tema como Hugo Module. Downloads de
ferramentas usam os hashes fixados em `scripts/tool-checksums.json`.

## Desenvolvimento no Windows

Primeira configuração, no PowerShell, com acesso à internet:

```powershell
.\scripts\install-tools.ps1
```

O instalador baixa Hugo, Go e Sass para `.tools/`, sem alterar a instalação
global ou o PATH do sistema. Python precisa estar disponível para os checks;
a versão do CI está em `.python-version`.

```powershell
.\scripts\blog.ps1 serve   # preview local, incluindo rascunhos
.\scripts\blog.ps1 check   # testes, build de produção, rotas e assets
.\scripts\blog.ps1 build   # somente build de produção
```

Abra o endereço informado pelo servidor, normalmente <http://localhost:1313/>.
A prévia usa `.tools/preview/`; a produção usa `public/`. Analytics e comentários
ficam desabilitados no ambiente de desenvolvimento. O build de produção limpa
arquivos antigos de `public/`, evitando publicar saídas de rascunhos anteriores.
Não mantenha arquivos manuais nesse diretório gerado.

Em Linux x64, instale Go e Python nas versões indicadas e execute:

```bash
bash scripts/install-tools.sh
bash scripts/blog.sh serve   # preview local, incluindo rascunhos (padrão)
bash scripts/blog.sh check   # testes, build de produção, rotas e assets
bash scripts/blog.sh build   # somente build de produção
```

## Conteúdo e personalização

- `content/post/<artigo>/`: artigo e seus recursos, incluindo exemplos executáveis.
- `content/page/`: Sobre, busca, arquivo e trabalhos selecionados.
- `data/work.yaml`: curadoria, resumos e links dos trabalhos destacados.
- `data/interface.yaml`: textos da interface EN/PT.
- `assets/scss/custom.scss`: identidade visual, responsividade e modo escuro.
- `assets/img/`: avatar, favicon e fontes vetoriais da identidade.
- `layouts/`: homepage, navegação e overrides do Stack v4.
- `layouts/_shortcodes/`: renderização de código e downloads compartilhados.
- `static/`: arquivos publicados diretamente, incluindo a imagem social.

O tema vem de `github.com/CaiJimmy/hugo-theme-stack/v4`, com versão fixa e
checksums. Os arquivos upstream não são editados nem copiados para `themes/`.
Personalizações ficam na raiz, nos caminhos do Hugo atual (`_partials` e
`_shortcodes`).

Inglês é o idioma padrão: `index.md` ou `index.en.md`. Para uma tradução,
use `index.pt-br.md` no mesmo bundle. Trabalhos sem tradução apontam para o
artigo em inglês com a indicação EN.

Novos artigos devem conter título, descrição, slug estável, data e `draft`:

```yaml
---
title: "Título do artigo"
description: "O problema, a abordagem e o que o leitor vai encontrar."
slug: exemplo-de-artigo
date: 2026-10-27
draft: true
categories: [Platform Engineering]
tags: [kubernetes]
image: cover.jpg
---
```

Coloque a imagem no mesmo bundle ou remova o campo. Valide o exemplo e o
preview, revise o PR e altere `draft` para `false` ao publicar. Use `lastmod`
para uma revisão substancial, preservando a data original. Datas sem offset
continuam interpretadas em UTC para preservar os metadados históricos.

As URLs dos artigos seguem `/p/:slug/`; português usa `/pt-br/`. O check de
migração preserva as 44 rotas do inventário original. Uma mudança deliberada
de rota exige alias e revisão desse contrato, sem perder os links publicados.

## Componentes editoriais e perfil

### Preservação de autoria e contexto

Artigos de portfólio documentam o trabalho realizado pelo autor, com as decisões,
restrições e ferramentas da época. Revisões editoriais devem preservar esse
contexto e o código original. Uma implementação alternativa ou reescrita não pode
substituir o trabalho apresentado nem ser atribuída ao autor sem sua concordância
explícita. Esclarecimentos posteriores ficam identificados e separados do relato;
melhorias propostas não devem parecer entregas já realizadas.

### Componentes disponíveis

- `data/work.yaml` controla os três trabalhos selecionados. Os diagramas SVG
  são gerados por `layouts/_partials/portfolio/diagram.html`, com rótulos
  localizados em `data/interface.yaml` e cores compartilhadas com o tema.
- `data/case_studies.yaml` fornece a visão geral opcional dos artigos. A chave
  é o nome do diretório do bundle; cada idioma contém `problem`, `contribution`,
  `decision` e `outcome`. Separe resultados observados de propostas ou limitações.
- `data/profile.json` contém a apresentação e as áreas de atuação EN/PT.
  Os textos mais longos continuam em `content/page/about/`.
- `data/credentials.yaml` reúne os nomes já declarados no perfil. Inclua `url`
  em uma credencial somente quando houver um endereço público de verificação.
  Para mostrar um currículo, adicione `profile.resume` dentro de `params` em
  `hugo.yaml`, apontando para o arquivo ou URL público real.

Blocos de código Markdown recebem um cabeçalho com linguagem. Um título
opcional pode identificar o arquivo:

````markdown
```python {title="example.py"}
print("hello")
```
````

O shortcode `code-file` mostra nome, linguagem, contagem de linhas e download.
Arquivos com 60 linhas ou mais ficam recolhidos em um elemento nativo `details`.
Use `collapse="false"` para mantê-los abertos ou `collapse="true"` para recolher
um arquivo menor. O código completo permanece no HTML e no download.

Use destaques editoriais para decisões, restrições e notas:

```text
{{< callout type="constraint" >}}
Explique a restrição operacional e sua consequência.
{{< /callout >}}
```

Os tipos aceitos são `decision`, `constraint` e `note`; `title` é opcional.
O índice móvel reutiliza o componente nativo do Stack e fecha ao escolher uma
seção. Ative-o no artigo com `toc: true` (YAML) ou `toc = true` (TOML).

## CI e publicação

Pull requests executam testes dos exemplos, build de produção e checagens de
rotas, assets, idiomas, headings e metadados. O artefato `blog-preview` permite
baixar o resultado para revisão; ele não é um site de preview hospedado.

Pushes em `main` passam pelos mesmos checks e publicam exatamente o artefato
validado no GitHub Pages. O deploy usa um grupo de concorrência único e
permissões restritas ao job de publicação. Actions estão fixadas por SHA;
Dependabot propõe atualizações das Actions e do tema mensalmente.

Configure Pages com origem **GitHub Actions** e domínio `fabiolopes.page`.
O domínio canônico vem de `baseURL` em `hugo.yaml`. Os arquivos `robots.txt`
e `sitemap.xml` publicados são gerados pelo Hugo; arquivos homônimos na raiz
não são a fonte da publicação. Rollback: reverta o commit problemático e
publique novamente pelo mesmo workflow.

## Atualizações

1. Verifique as releases oficiais e a compatibilidade Hugo/Stack.
2. Atualize as versões fixadas e os checksums das ferramentas correspondentes.
3. Para o tema, use `hugo mod get github.com/CaiJimmy/hugo-theme-stack/v4@<versão>`
   e versione `go.mod`/`go.sum`.
4. Reinstale as ferramentas locais, execute `blog.ps1 check` e confira o preview
   em desktop/celular e nos modos claro/escuro antes do merge.

As versões permanecem fixas entre atualizações para que local e CI usem a
mesma base. Detalhes da migração e limites de validação estão em
[docs/modernizacao-2026-10-27.md](docs/modernizacao-2026-10-27.md).
