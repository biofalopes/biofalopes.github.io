# Auditoria do blog e plano de modernização

Data: 26/10/2026. Base: workspace em `29f6057`, incluindo as alterações locais anteriores em CI, README, `.gitignore` e `.hugo-version`.

## Objetivo e conclusão

Transformar o blog em um portfólio técnico para entrevistas de Senior/Staff Platform Engineer, Cloud Infrastructure Engineer e SRE, com conteúdo confiável, leitura clara, publicação reproduzível e manutenção simples.

A recomendação é manter Hugo e GitHub Pages, atualizar Hugo e Stack em conjunto e criar uma homepage que apresente trabalhos selecionados. A prioridade imediata é a correção técnica de conteúdo e a preservação das URLs. Uma reformulação visual sobre os exemplos atuais deixaria problemas relevantes de credibilidade sem solução.

Esta auditoria é um diagnóstico e um backlog. Os posts ainda não foram corrigidos e a atualização do tema ainda não foi executada.

## Escopo e evidências

- Inventário de todos os 44 arquivos de artigos em 38 bundles: 39 versões publicáveis, correspondentes a 33 assuntos, e 5 rascunhos. Entre as versões publicáveis, 33 são em inglês e 6 em português.
- Inspeção de configuração, tema, workflow, templates, metadados e trechos de conteúdo; revisão aprofundada de uma seleção de artigos prioritários. O inventário não equivale a uma revisão linha a linha de todos os artigos.
- Build de produção em Hugo 0.144.1 com `--gc --minify --printPathWarnings --panicOnWarning`: passou, usando cache e destino temporários.
- Varredura de 243 HTMLs gerados, incluindo redirecionamentos: nenhum destino local ausente nos atributos `href`/`src` inspecionados e nenhuma âncora local quebrada. Não cobre URLs em CSS, execução de JavaScript nem disponibilidade dos links externos.
- Os blocos explicitamente marcados como Python passaram na análise de sintaxe. Testes pequenos de funções selecionadas encontraram erros lógicos, descritos abaixo.
- Homepage EN/PT, About e artigo Loki inspecionados no HTML: idioma presente, mas sem `hreflang` ou JSON-LD.
- 44/44 arquivos de artigos sem `slug` explícito e sem `lastmod` explícito. Todos têm campo `description`; a qualidade e o tamanho variam.
- 37/39 versões publicáveis desabilitam o sumário com `toc = false`, apesar de o site habilitá-lo globalmente.
- Não houve auditoria visual em navegador: a ferramenta de browser não disponibilizou nenhum navegador. Não há medição Lighthouse, avaliação de contraste, navegação por teclado ou teste móvel concluídos.
- Configuração remota de Pages, proteção de branch, DNS/HTTPS e execução do workflow no GitHub não foram verificadas. A página obtida por busca estava em cache e não serve para confirmar o estado atual do deploy.

O inventário com as URLs calculadas pelo Hugo está em [inventario-posts-2026-10-26.json](inventario-posts-2026-10-26.json). Ele será a referência para verificar regressões de rotas durante a migração.

## Achados prioritários nos artigos

P0 significa corrigir antes de promover o artigo como demonstração técnica. P1 significa corrigir durante a primeira rodada editorial. P2 representa manutenção ou aprofundamento posterior. Um achado não invalida toda a experiência documentada no artigo.

### P0 — Loki: arquitetura, autenticação e comandos

Arquivo: `content/post/grafana-loki/index.md`.

- O texto apresenta Mimir como backend de armazenamento de logs do Loki. O próprio YAML usa S3/Rook Ceph; Mimir é destinado a métricas. Corrigir texto e conferir o diagrama SVG.
- `auth_enabled` é apresentado como mecanismo que habilita autenticação. Ele controla multi-tenancy; autenticação precisa de uma camada apropriada, como proxy autenticador. [Documentação de autenticação do Loki](https://grafana.com/docs/loki/latest/operations/authentication/).
- O comando `helm install --namespace loki grafana/loki loki ...` inverte release e chart. A sintaxe é `helm install NAME CHART`. [Referência do Helm](https://v3.helm.sh/docs/helm/helm_install/).
- A criação de buckets não informa o endpoint Ceph. Sem configuração externa não documentada, a AWS CLI não estará necessariamente operando no storage descrito. Explicitar endpoint, credenciais de exemplo e CA.
- O dimensionamento iguala réplicas de componentes a número de nós sem justificar carga ou requisitos dos componentes. Fixar versões de Loki/chart e revisar particularmente compactor, disponibilidade e recursos.
- A coleta usa Promtail 2.9.9. Promtail chegou ao fim de suporte em 02/03/2026; atualizar o guia com Alloy ou marcar claramente o procedimento como histórico. [Status oficial do Promtail](https://grafana.com/docs/loki/latest/send-data/promtail/).

Referência sobre a finalidade do Mimir: [retenção de métricas](https://grafana.com/docs/mimir/latest/configure/configure-metrics-storage-retention/).

### P0 — Mimir: exemplo de instalação inconsistente

Arquivo: `content/post/grafana-mimir/index.md`.

- O comando de leitura do Secret aponta para o usuário `loki`, embora a seção crie `mimir`.
- O comando Helm também inverte release/chart e usa `grafana/mimir`; a instalação documentada utiliza `grafana/mimir-distributed`. Fixar uma versão e validar o values correspondente. [Instalação oficial](https://grafana.com/docs/helm-charts/mimir-distributed/latest/get-started-helm-charts/).
- Os comandos S3 também omitem o endpoint Ceph.
- Rever endpoint de remote write, autenticação, replicas e alegação de HA. Um YAML parcial e não versionado não sustenta sozinho a conclusão de alta disponibilidade.
- A seção de segurança chama placeholders de credenciais vazadas; reformular para explicar o tratamento correto de Secrets, sem afirmar um vazamento não demonstrado.

### P0 — IBB Kids: corrigir fundamentos e sustentar resultados

Arquivo: `content/post/ibb-kids/index.md`.

- SQLite aceita múltiplos processos no mesmo host, com um escritor por vez. A afirmação de que SQLite exige um processo único e que múltiplos workers causam corrupção do WAL está incorreta como regra geral. Contenção e arquitetura da aplicação devem ser explicadas separadamente. [SQLite WAL](https://sqlite.org/wal.html).
- A Online Backup API produz uma cópia consistente; não deve ser descrita como um mecanismo que descarrega transações não confirmadas no backup. Diferenciar dados confirmados no WAL de transações ainda não confirmadas. [Online Backup API](https://sqlite.org/backup.html).
- A restauração descrita suspende e reinicia o processo. O texto não demonstra como isso mantém atendimento contínuo. A troca de um symlink também não redireciona automaticamente um upstream HTTP do Nginx nem substitui o código de um processo em execução.
- Tratar “zero downtime” como uma propriedade a demonstrar: portas/upstreams, sobreposição entre versões, drenagem de conexões, compatibilidade de schema e medição de requisições durante o deploy. A documentação do PM2 associa reload sem interrupção ao modo cluster; outros desenhos precisam de evidência própria. [PM2](https://pm2.keymetrics.io/docs/usage/cluster-mode/).
- Compilar módulos no host ARM de destino é compilação nativa; usar “cross-compilation” somente se houve toolchain gerando para outra arquitetura.
- Um host único permanece um domínio único de falha. Separar recuperação, disponibilidade observada e alta disponibilidade arquitetural.
- Confirmar as métricas de 48 testes/74 regras com evidências do projeto antes de usá-las como resultado de portfólio. Não inventar resultados ou substituir retrospectiva real por uma narrativa idealizada.

Este é um forte candidato a case de portfólio após revisão: restrição de custo, operação real, backup, identidade cloud e trade-offs são bons temas para entrevista.

### P0 — Previsão Ceph: método e código divergem

Arquivos: `content/post/jupyter-forecast/index.en.md` e `index.pt-br.md`.

- O texto descreve desvio padrão móvel; o código usa um desvio global.
- O filtro compara `abs(delta)` ao desvio, sem centralizar no crescimento típico. Reprodução mínima da mesma regra: deltas `[10, 10, 10, 10, 10]` têm desvio zero, são substituídos por zero e geram mediana zero. Uma série de crescimento constante pode virar previsão sem crescimento.
- A projeção usa incrementos medianos, não regressão linear ajustada; harmonizar nomes e explicação.
- O primeiro dia futuro começa com o último valor observado, sem incremento. Rever deslocamento temporal, quantidade de passos e cálculo da taxa.
- `abs((capacidade - uso_atual) / taxa)` não trata taxa zero, crescimento negativo ou limite já excedido. Definir explicitamente cada caso.
- Chamadas HTTP usam `verify=False`, desabilitam warnings e não definem timeout. Adotar CA confiável, timeout, tratamento de indisponibilidade e de dataset vazio. [Requests](https://requests.readthedocs.io/en/stable/user/advanced/).
- Validar com séries sintéticas e backtesting temporal antes de apresentar precisão ou robustez. Capacidade adicionada, rebalanceamento e remoção de dados podem ser mudanças reais, não outliers a apagar.

### P0 — Algoritmos: falhas reproduzidas

Arquivo: `content/post/python-sort/index.md`.

Executadas apenas funções inspecionadas e imports da biblioteca padrão, sem executar o benchmark de 5.000 itens:

| Função | Entrada | Saída obtida | Problema |
|---|---|---|---|
| `mergeSort` | `[4, 3, 2, 1]` | `[2, 1, 4, 3]` | Decorator impede a execução das chamadas recursivas. |
| `selectionSort` | `[4, 3, 2, 1]` | `[4, 3, 2, 1]` | Troca está fora do laço externo. |
| `bubbleSort` | `[4, 3, 2, 1]` | `[1, 2, 3, 4]` | Funcionou nesse caso de controle. |

Os tempos publicados para algoritmos que não ordenam corretamente não são uma comparação válida. Corrigir a lógica e medir novamente, registrando ambiente e entradas.

Arquivo: `content/post/dp/index.md`: `fibonacci_tabulation(0)` reproduziu `IndexError`. Tratar casos base; revisar também argumento mutável padrão da versão memoizada e limites de entrada.

### P0 — Terraform ASG: subnets fora da VPC

Arquivo: `content/post/terraform-2/index.md`.

- VPC `10.0.0.0/16` com subnets `10.10.1.0/24` e `10.10.2.0/24`: subnets não pertencem ao intervalo da VPC declarada.
- O exemplo usa Launch Configuration e provider AWS `~> 3.0`. Modernizar para Launch Template e validar o provider escolhido; contas AWS criadas desde 01/10/2024 não podem criar novas launch configurations. [AWS Auto Scaling](https://docs.aws.amazon.com/autoscaling/ec2/userguide/launch-configurations.html).
- Rever security groups, autenticação, cleanup e custos do laboratório; registrar quais partes foram realmente testadas.

### P1 — Outros problemas e candidatos à revisão

| Artigo/grupo | Evidência ou tarefa |
|---|---|
| `ansible-1` | Copia `authorized_keys` antes de criar `.ssh`; pode falhar em um usuário novo. Validar sudoers e sshd antes de aplicar; revisar handlers, acesso de recuperação e opções antigas. |
| `eks-outpost` | Texto diz AL2023, mas user data usa `/etc/eks/bootstrap.sh`. AL2023 usa `nodeadm`. Determinar qual AMI foi usada e separar procedimento histórico de atualização. [AWS](https://docs.aws.amazon.com/eks/latest/userguide/al2023.html). |
| `rook-2` | Expande OSD como “Object Storage Devices”; corrigir a terminologia. `wipefs` é chamado de apagamento seguro, embora remova assinaturas e não os dados do dispositivo. Tornar seleção de discos explícita e revisar RGW único versus HA alegada. [util-linux](https://kernel.googlesource.com/pub/scm/utils/util-linux/util-linux/+/refs/tags/v2.41.1/misc-utils/wipefs.8.adoc). |
| `ceph-cluster` | Há `--remove-signatures` anexado a valores de imagens no arquivo de configuração; conferir artefato original e comando de origem. Marcar dependências de registry privado e diferenças entre upstream e distribuição comercial. |
| `kubespray` EN/PT | Separar inventário ilustrativo de inventário executável; alinhar checkout do repositório e imagem de execução; registrar versões testadas. |
| `python-sorting-2` | Metodologia menciona 1.000 itens e resultados 5.000. Revisar texto sobre complexidade do MergeSort; explicitar repetição, seed, ambiente e verificação de saída. |
| `terraform-3` | Bom texto sobre ownership, mas descreve propostas em avaliação. Classificar como análise arquitetural; não apresentar como resultado operacional já entregue. Identificar snippets parciais. |
| `terraform-4` | Rascunho sobre tema próximo ao anterior. Consolidar ou transformar em continuação com resultados reais, evitando duas versões concorrentes da mesma história. |
| `jenkins-1` EN/PT | Imagem/plugins flutuantes, instalador legado e Compose 1.29.2. Revisar a reprodução e limites do uso de Docker socket. |
| Guias AWS/GCP/Terraform | Registrar edição do exame e data da revisão. Revalidar objetivos e materiais oficiais antes de se apresentar como guia atual. A trilha Terraform atual consultada é Associate 004. [HashiCorp](https://developer.hashicorp.com/terraform/tutorials/certification-004/associate-study-004). |
| `solutions-arch-pro` EN/PT | Versões muito diferentes em extensão e escopo; a tradução PT tem cerca de 20 mil palavras incluindo código, enquanto EN tem cerca de 3 mil. Decidir entre equivalência editorial e guias independentes. |
| `python-scrapper`, `ansible-intro`, `ceph-features-*` | Manter valor histórico, mas indicar versões/contexto. Rever escrita, exemplos e links antes de atualizar a data editorial. |

## Plataforma e deployment

### Atualização coordenada

O Hugo local 0.144.1 foi alinhado ao CI na etapa anterior; isso é uma base de comparação, não a versão final desejada. A página oficial consultada lista Hugo 0.168.0. O tema local identifica módulo v3, mas não há referência explícita à tag upstream da cópia. A página de releases consultada apresenta Stack v4.0.3. [Hugo releases](https://gohugo.io/news/), [Stack releases](https://github.com/CaiJimmy/hugo-theme-stack/releases).

Stack v4 exige Hugo pelo menos 0.157.0 e muda opções e caminhos de templates. Migrar primeiro a base e só depois construir overrides visuais. Avatar/favicon, `imageProcessing`, opções removidas e localização dos layouts precisam de conferência. [Guia de migração](https://stack.cai.im/guide/upgrade-to-v4).

Proposta: usar Hugo Modules com versão fixada do tema e `go.mod`/`go.sum` na raiz; instalar Go com versão controlada no CI e documentar localmente. Isso adiciona uma dependência explícita, mas torna atualizações rastreáveis. Se a prioridade for dispensar Go local, um submódulo fixado é alternativa; não manter uma cópia sem identificação de origem.

### Revisão do workflow anterior

Aspectos úteis já presentes: PRs compilam, produção usa build minificado, permissões de Pages ficam no deploy e rascunhos não entram no build normal.

Ainda falta:

1. Atualizar Actions para versões verificadas e fixar por SHA completo; automatizar atualizações via Dependabot. Tags maiores atuais e requisitos de runtime devem ser conferidos no momento da implementação. [GitHub Actions](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository).
2. Verificar checksum do binário Hugo e adaptar nome/formato do pacote à release escolhida. Não assumir que o URL antigo com `hugo_extended_` continua correto após atualização.
3. Corrigir concorrência de produção: o grupo atual inclui `event_name`, permitindo que execução manual e push para `main` ocupem grupos diferentes. Usar um grupo único no job de deploy; manter cancelamento separado para PRs.
4. Incluir timeout de jobs e desativar persistência de credenciais de checkout quando desnecessária.
5. Validar workflow, metadados, links internos, assets e os exemplos selecionados. Build Hugo sozinho não detectou os erros acima.
6. Produzir artefato de preview em PR, com rascunhos quando apropriado. Explicar como executar localmente; GitHub Pages de produção não deve ser reutilizado como preview de cada PR.
7. Publicar exatamente o artefato validado. Após deploy, conferir homepage EN/PT, um post, busca e sitemap.
8. Documentar rollback por revert do commit e redeploy. Confirmar regras de branch/environment e check obrigatório no GitHub; esses ajustes remotos ainda não estão auditados.
9. Preservar `baseURL` canônica em produção e usar URL local em previews. Desabilitar analytics/comentários no ambiente de preview.

GitHub Pages continua adequado: o conteúdo é estático e não há requisito de backend. Não há motivo demonstrado para migrar para Next.js, adicionar CMS ou contratar outra hospedagem. [Hugo no Pages](https://gohugo.io/host-and-deploy/deploy-to-github-pages/).

## URLs, SEO, leitura e identidade

- **Congelar rotas antes de editar títulos:** adicionar slugs que reproduzam exatamente as rotas atuais do inventário. Não usar o nome do diretório como novo slug em massa. Se uma rota mudar deliberadamente, incluir alias e testar.
- **Distinguir datas:** preservar `date` original, usar `lastmod` para revisão significativa e `reviewedAt` para revisão técnica. Não fazer todo artigo parecer novo por causa de uma migração ou formatação.
- **Idiomas:** manter inglês como entrada principal, dado o objetivo internacional; tradução seletiva com o mesmo nível de revisão. Adicionar `hreflang` apenas para traduções existentes e testar seletor, busca, arquivos e feeds por idioma.
- **SEO:** adicionar dados estruturados coerentes de autor/artigo e imagem social padrão, conferir canonical, previews e páginas de erro. JSON-LD é enriquecimento, não garantia de posicionamento.
- **Leitura técnica:** habilitar sumário em artigos longos, headings semânticos, âncoras copiáveis, blocos com linguagem, tabelas legíveis e diagramas com legendas. Avaliar divisão dos guias extensos.
- **Imagens:** há originais de até 4 MB e imagens acima de 2 MB. O tema já gera variantes; medir o arquivo realmente entregue e o LCP antes de otimizar. Priorizar diagramas reais de arquitetura em trabalhos selecionados.
- **Acessibilidade:** verificar foco visível, teclado, contraste, alt informativo, zoom, mobile, tema claro/escuro e redução de movimento. Alt não vazio não significa alt útil.
- **Integrações:** GA, Disqus, Google Fonts e bibliotecas externas participam da experiência. Avaliar custo de carregamento e utilidade; comentários podem ser dispensáveis num portfólio. Não trocar por outra integração automaticamente.
- **Configuração:** remover configurações de provedores de comentários não usados, preencher manifest e consolidar arquivos SEO. O robots gerado tem 13 bytes; o arquivo manual da raiz não é o que Hugo publica.
- **HTML em Markdown:** `unsafe: true` atende conteúdos com `<details>` existentes. Não desligar sem migrar/testar esses usos.

## Arquitetura editorial proposta para entrevistas

Navegação principal: **Home / Projects / Articles / About / Search**, localizada em português quando houver versão.

A homepage deve apresentar nome e especialidade em poucas linhas, 3–4 trabalhos selecionados, uma seleção curta de artigos e acesso claro a GitHub, LinkedIn e contato. Categorias e arquivo cronológico podem ocupar um papel secundário.

Trabalhos selecionados propostos:

| Candidato | Valor para entrevista | Condição para destaque |
|---|---|---|
| Plataforma bare-metal Kubernetes + Ceph + observabilidade | Arquitetura de infraestrutura, storage, operação e decisões de capacidade | Corrigir série Loki/Mimir/Rook e consolidar topologia e resultados. |
| Previsão de capacidade Ceph | Automação aplicada a uma necessidade operacional real | Corrigir método, validar edge cases e apresentar evidência sem dados internos. |
| IBB Kids | Operação sob restrição de custo, backup, deploy, identidade e trade-offs | Corrigir fundamentos e comprovar comportamento do deployment e recuperação. |
| Terraform Day-2 | Ownership, limites entre equipes, entrega de aplicação e IaC | Distinguir proposta, implantação e resultados; acrescentar evidências quando existirem. |

Estrutura de cada case: problema, contexto e restrições, responsabilidade pessoal, alternativas avaliadas, decisão, implementação, validação, resultados, limitações, aprendizados e próximos passos. Preferir uma métrica verificável a várias alegações amplas. Não transformar SLA contratado em disponibilidade medida nem certificação em prova de experiência operacional.

Organizar os demais conteúdos como tutoriais, análises, notas de estudo e arquivo histórico. Todos podem continuar acessíveis; destaque editorial deve refletir relevância para o cargo e maturidade do material. Certificações ficam como apoio ao perfil, com links públicos de verificação quando disponíveis.

## Fluxo de uma nova postagem

1. Criar branch e gerar bundle com archetype próprio (`hugo new content ...` ou script equivalente). Ter modelos distintos para tutorial e case.
2. Preencher metadados: título, descrição, slug estável, data, draft, idioma, categorias, tags; campos de revisão e versões testadas quando houver revisão/teste real. Marcar `featured` somente após curadoria.
3. Escrever junto com exemplos e diagramas. Código executável deve ter origem única em `examples/` ou repositório companion; snippets parciais devem ser identificados como tais.
4. Rodar preview local com drafts e sem integrações de produção.
5. Rodar verificação local equivalente ao CI: metadados, build, links/assets e testes relevantes do exemplo.
6. Abrir PR com resumo, artefato de preview e checklist editorial curto: precisão, fontes, reprodução, imagens, links, exposição de dados e resultado comprovável.
7. Publicar alterando `draft` para false e fazendo merge após checks. PR que adiciona somente rascunho continua útil para revisão.
8. Validar publicação. Registrar `lastmod` nas revisões substanciais e manter histórico de correções relevantes.

Links externos devem ter verificação periódica com retry e exceções justificadas, evitando bloquear cada PR por rate limit de terceiros. Para publicação agendada, definir explicitamente um build programado; data futura sozinha não dispara um novo deploy de site estático.

## Sequência de execução e critérios de aceite

| Etapa | Entrega | Critério de aceite |
|---|---|---|
| 1. Rotas e correções P0 | Slugs preservados e revisão dos artigos com erros confirmados | Comparação com inventário sem perda de URLs; casos mínimos passam; correções conceituais com fontes. |
| 2. Hugo e tema | Versões atuais compatíveis e dependências rastreáveis | Build limpo; busca, feeds, traduções, imagens e paginação funcionando; regressão visual verificada. |
| 3. Workflow editorial | Archetypes, exemplos verificáveis, comandos locais, CI e preview | Criar um rascunho do zero, revisar em PR e gerar artefato sem publicação acidental. |
| 4. Portfólio e design | Homepage, Projects, About e 3–4 cases revisados | Leitor consegue identificar especialidade, contribuição pessoal e evidência em poucos passos. |
| 5. Revisão do acervo | Cada bundle marcado como revisado, histórico ou pendente, com motivo | Nenhum artigo destacado com erro conhecido; versões e limitações explícitas; EN/PT coerentes. |
| 6. Qualidade e release | SEO, acessibilidade, desempenho, deploy e rollback | Auditoria de navegador concluída; checks automatizados passam; publicação remota e recuperação verificadas. |

Não considerar a modernização concluída apenas porque o site compila. O resultado final precisa demonstrar precisão técnica, utilidade para o leitor e um fluxo de manutenção que o autor consiga repetir.
