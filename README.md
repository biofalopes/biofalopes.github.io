# Fabio Lopes — blog

Blog pessoal sobre Cloud, Platform Engineering, SRE e automação, publicado em
<https://fabiolopes.page/> com Hugo e o tema Stack.

## Requisitos

- **Hugo Extended 0.144.1**, versão fixada em `.hugo-version` e usada pelo CI.
- Git.

O projeto usa SCSS via Hugo Extended. Não precisa de Node.js, npm ou uma
instalação separada do Dart Sass.

## Desenvolvimento local

No PowerShell, usando o executável local (ignorado pelo Git):

```powershell
.\hugo.exe version
.\hugo.exe server --buildDrafts
```

Com Hugo no PATH, use `hugo` no lugar de `.\hugo.exe`.
Abra o endereço informado pelo servidor, normalmente <http://localhost:1313/>.
Rascunhos aparecem quando `--buildDrafts` está habilitado.

Para reproduzir a validação de produção:

```powershell
.\hugo.exe --environment production --gc --minify --printPathWarnings --panicOnWarning
```

O resultado fica em `public/`. Esse diretório e o cache `resources/` são gerados
e não devem ser editados nem versionados.

## Estrutura e conteúdo

- `hugo.yaml`: configuração, idiomas, navegação e integrações.
- `content/post/<artigo>/`: artigo e suas imagens (page bundle).
- `content/page/`: páginas Sobre, Busca e Arquivos.
- `static/`: arquivos copiados diretamente para o site.
- `themes/hugo-theme-stack/`: cópia versionada do tema Stack.
- `.github/workflows/hugo.yaml`: validação e publicação.

O idioma padrão é inglês: `index.md` ou `index.en.md`. Para uma tradução em
português, use `index.pt-br.md` no mesmo bundle. Preserve nomes de bundles e
slugs ao revisar artigos para evitar alterações nas URLs existentes.
Os artigos seguem `/p/:slug/`; o português usa o prefixo `/pt-br/`.

Exemplo de front matter para um novo bundle:

```yaml
---
title: "Título do artigo"
description: "Resumo objetivo para leitores e compartilhamento."
date: 2026-10-26
slug: exemplo-de-artigo
draft: true
categories: [Platform Engineering]
tags: [kubernetes]
image: cover.jpg
---
```

Coloque `cover.jpg` no mesmo diretório ou remova o campo `image`.
Antes de publicar, revise o artigo e altere `draft` para `false`.

## Personalização

Crie overrides em `layouts/` e estilos em `assets/scss/custom.scss` na raiz,
usando os pontos de extensão do Stack. Prefira isso a alterar o tema diretamente.
A cópia atual do tema está versionada como arquivos comuns, sem submódulo ou
Hugo Module.

## Publicação

Pull requests para `main` executam o build de produção e falham em caso de
avisos. Pushes em `main` executam o mesmo build e publicam no GitHub Pages.
O workflow também aceita execução manual; publica somente na referência `main`.

O domínio canônico vem de `baseurl` em `hugo.yaml`. Configure o Pages para usar
**GitHub Actions** como origem e `fabiolopes.page` como domínio personalizado.

Para atualizar Hugo, altere `.hugo-version`, instale a mesma versão Extended
localmente e valide o build antes de integrar a alteração.

`robots.txt`, `sitemap.xml` e `CNAME` na raiz não são copiados automaticamente
pelo Hugo. O sitemap e o robots são gerados pelo Hugo; o domínio personalizado
é configurado no GitHub Pages.
