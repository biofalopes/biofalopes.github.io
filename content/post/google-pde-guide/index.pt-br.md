+++
title = "Google Cloud Professional Data Engineer: guia prático de estudo e referência de serviços"
description = "Uma referência complementar para o exame Professional Data Engineer, com seleção de serviços, BigQuery, pipelines, streaming, segurança, operações e cenários de prática."
date = "2025-02-04"
lastmod = "2026-10-30"
draft = false
toc = true
categories = ["gcp", "data"]
tags = ["gcp", "data-engineering", "certification", "study-guide"]
author = "Fabio M. Lopes"
+++

A [certificação Google Cloud Professional Data Engineer (PDE)](https://cloud.google.com/learn/certification/data-engineer) abrange diversos assuntos: armazenamento de dados, processamento em lote e streaming, orquestração, segurança, governança, aprendizado de máquina e operação de sistemas de dados ao longo do tempo.

Quando reuni minhas primeiras anotações de preparação para o PDE, queria um único lugar para comparar serviços, revisar conceitos e retomar cenários que poderiam aparecer no exame. As anotações acabaram ficando longas demais para o artigo sobre minha experiência pessoal de preparação.

Este guia complementar mantém aquele objetivo e facilita a consulta. Ele está organizado em torno das decisões que um engenheiro de dados pode precisar tomar, em vez de uma longa sequência de descrições de produtos. Combina assuntos das minhas anotações originais de 2025 com atualizações de terminologia e documentação revisadas em outubro de 2026. **É um material de estudo independente, não um guia oficial nem uma garantia de cobertura do exame.**

Para conhecer meu processo pessoal de preparação e os recursos de aprendizado que utilizei, veja o artigo complementar: [Preparação para o exame Google Cloud Professional Data Engineer: minha abordagem e recursos de estudo]({{< relref "/post/google-pde-prep" >}}).

> **Como usar este guia:** Comece pelo [guia oficial do exame](https://cloud.google.com/learn/certification/data-engineer). Depois, utilize as seções abaixo para identificar assuntos que ainda não consegue explicar com suas próprias palavras. Faça um laboratório ou um pequeno experimento e, por fim, pratique explicar *por que* um serviço pode se encaixar melhor em determinado cenário do que outro.

## 1. Comece pelos objetivos do exame

A página oficial da certificação é a referência para o formato atual do exame, os idiomas, os critérios de elegibilidade e os links para os guias do exame padrão e de renovação. Os objetivos e os serviços mudam, então eu não trataria nenhuma lista estática como exaustiva.

Eu organizaria meus estudos em torno destas áreas principais:

- Projeto de arquiteturas de processamento de dados, incluindo lote e streaming.
- Ingestão, armazenamento e processamento de dados com serviços adequados.
- Manutenção de pipelines confiáveis e orquestração de cargas de trabalho dependentes.
- Segurança, governança, qualidade dos dados e gerenciamento de acesso.
- Monitoramento, diagnóstico de problemas, desempenho e otimização de custos.
- Compreensão do papel do aprendizado de máquina nos fluxos de engenharia de dados.

Como exercício, pegue qualquer questão de arquitetura e identifique o volume da carga de trabalho, os requisitos de latência, as expectativas de consistência, as restrições operacionais, os requisitos de segurança e as prioridades de custo **antes** de escolher um produto.

## 2. Um mapa rápido para selecionar serviços

| Requisito | Serviços a avaliar | Pergunta principal |
| --- | --- | --- |
| SQL analítico sobre grandes conjuntos de dados | BigQuery | A carga principal é analítica ou transacional? |
| Acesso por chave em grande escala e com baixa latência | Bigtable | Os padrões de acesso são conhecidos e o projeto das chaves de linha é adequado? |
| Transações relacionais distribuídas globalmente | Spanner | Os requisitos de consistência forte e escala horizontal justificam a complexidade e o custo? |
| Banco de dados relacional gerenciado | Cloud SQL | Um mecanismo relacional convencional atende à carga de trabalho? |
| Armazenamento de objetos e entradas de data lakes | Cloud Storage | Qual classe de armazenamento, ciclo de vida e formato de arquivo atendem ao padrão de acesso? |
| Ingestão e distribuição de eventos para vários consumidores | Pub/Sub | Como os consumidores lidarão com duplicatas, ordenação e contrapressão? |
| Transformações gerenciadas em lote ou streaming | Dataflow / Apache Beam | Processamento pelo tempo do evento, janelas e escalabilidade automática são relevantes? |
| Cargas gerenciadas de Spark ou Hadoop | Dataproc | Há código Spark/Hadoop existente ou compatibilidade com o ecossistema a preservar? |
| Fluxos agendados com dependências | Cloud Composer / Apache Airflow | As dependências, novas tentativas e a visibilidade operacional justificam a orquestração? |
| Treinamento e inferência de modelos | Vertex AI | O requisito é preparar atributos, treinar, avaliar ou disponibilizar predições? |
| ML baseado em SQL sobre dados do warehouse | BigQuery ML | O fluxo do modelo pode permanecer próximo aos dados no BigQuery? |
| Metadados, descoberta e governança | BigQuery universal catalog | Como os ativos de dados serão descobertos, classificados e governados? |

Esses são pontos de partida, não equivalências diretas. Por exemplo, o Pub/Sub pode substituir alguns padrões de mensageria associados a Kafka ou RabbitMQ, mas os produtos não oferecem semânticas de execução e operação idênticas.

## 3. Armazenamento de dados e sistemas analíticos

### BigQuery: cargas analíticas

O BigQuery é central em muitos cenários do PDE. Eu dedicaria tempo a entender **como os dados são modelados, carregados, consultados, protegidos e cobrados**, em vez de memorizar exemplos isolados de SQL.

**Modelagem.** Conheça as vantagens e limitações dos esquemas estrela e floco de neve, da desnormalização e dos campos aninhados e repetidos, além de como essas escolhas influenciam os padrões de consulta analítica. Um esquema estrela pode simplificar consultas dimensionais comuns; uma normalização maior pode reduzir duplicações, mas exigir mais joins.

**Particionamento e clustering.** O particionamento pode reduzir os dados lidos quando as consultas filtram por uma chave de partição compatível. O clustering pode ajudar a organizar os dados para filtros e agregações. Nenhum desses recursos é uma otimização universal: examine os predicados reais das consultas e a distribuição dos dados antes de escolher as chaves.

**Execução e ajuste de consultas.** Estude os detalhes de execução pelo plano de consulta e pelo grafo de execução do BigQuery, junto com bytes processados, comportamento de shuffle, joins e eliminação de partições. Minhas anotações originais faziam referência a `EXPLAIN` genérico e leituras baseadas em índices; esse não é um modelo mental útil para o mecanismo de execução do BigQuery. A [documentação de planos de consulta do BigQuery](https://cloud.google.com/bigquery/docs/query-plan-explanation) é uma referência melhor.

**Resultados derivados.** Views, views materializadas e consultas agendadas atendem a necessidades diferentes. Views materializadas podem acelerar agregações repetidas compatíveis, mas é preciso considerar o comportamento de atualização, os critérios de elegibilidade e os custos de manutenção.

**Preços.** Compare a cobrança de consultas sob demanda com a cobrança de computação baseada em capacidade, utilizando as edições, reservas e slots do BigQuery. A antiga distinção entre preço fixo e cobrança sob demanda das minhas primeiras anotações está desatualizada. Armazenamento, streaming e outras cobranças também precisam entrar na conta. [Preços atuais](https://cloud.google.com/bigquery/pricing).

**Ingestão de dados.** Conheça as cargas em lote a partir do Cloud Storage, as transferências gerenciadas pelo BigQuery Data Transfer Service e a ingestão pela Storage Write API. Considere latência, semânticas de pelo menos uma vez e exatamente uma vez quando aplicáveis, custo e complexidade operacional.

**Segurança.** Entenda os padrões de acesso por projeto, dataset, tabela, linha e coluna; views autorizadas; policy tags; mascaramento de dados; IAM; e chaves de criptografia gerenciadas pelo cliente (CMEK). Uma view que expõe campos selecionados é útil, mas apenas criá-la não equivale a aplicar todos os requisitos de segurança por linha e coluna.

**Outros recursos.** Entenda o BigQuery ML para fluxos de modelos centrados em SQL e o BigQuery Omni para determinados padrões de análise entre nuvens. Vale conhecê-los conceitualmente, mas sempre verifique os limites atuais e as regiões compatíveis.

**Cenário para refletir:** Um dashboard agrega vendas por data e categoria de produto repetidamente. Quais são os benefícios relativos do particionamento, do clustering, de uma view materializada e de uma reserva de capacidade? Que evidências você reuniria antes de escolher?

### Cloud Storage: objetos e formatos de arquivos analíticos

O Cloud Storage costuma ser a área de entrada dos arquivos antes de uma etapa de processamento ou análise.

Conheça as classes Standard, Nearline, Coldline e Archive, junto com seus períodos mínimos de armazenamento, custos de recuperação e políticas de ciclo de vida. A baixa frequência de acesso, por si só, não determina a melhor classe; os padrões de recuperação e a retenção importam.

Revise versionamento de objetos, controles de retenção, gerenciamento do ciclo de vida, URLs assinadas, IAM, Storage Transfer Service e a família de comandos `gcloud storage`. Materiais antigos ainda podem utilizar `gsutil`; reconheça a ferramenta, mas aprenda também as opções atuais.

**Formatos de arquivo importam:** CSV e JSON são formatos comuns de intercâmbio; Avro é orientado a linhas e oferece suporte a esquemas; Parquet e ORC são formatos colunares que podem ser eficientes em leituras analíticas. Minhas anotações originais agrupavam incorretamente o Avro com formatos colunares. O suporte à compressão e à evolução de esquemas varia conforme o formato e a integração.

**Cenário:** Você ingere grandes arquivos diários de eventos e consulta apenas algumas colunas. Transformaria os arquivos em Parquet antes da análise? Como isso se relacionaria com sua estratégia posterior de carga no BigQuery?

### Cloud SQL: mecanismos relacionais gerenciados

Revise as opções de implantação de MySQL, PostgreSQL e SQL Server; backups; recuperação para um ponto no tempo; alta disponibilidade; réplicas de leitura; gerenciamento de conexões; acesso relacionado ao IAM; redes; e o Cloud SQL Auth Proxy.

Alta disponibilidade e replicação de leitura atendem a propósitos diferentes. Uma réplica de leitura não equivale automaticamente a uma configuração de failover de alta disponibilidade. Para uma aplicação sensível à latência, o pool de conexões e os limites do banco podem ser tão importantes quanto o tamanho da instância.

**Cenário:** Uma aplicação transacional precisa de failover automático e recuperação após exclusões acidentais. Explique por que failover, backups e recuperação para um ponto no tempo tratam modos de falha diferentes.

### Spanner: consistência relacional em escala

Estude o projeto de chaves primárias, os conceitos de interleaving ou localidade de tabelas, índices secundários, transações, replicação e as implicações da distribuição dos dados para custo e desempenho. Chaves que crescem de forma monotônica podem criar hotspots, dependendo do esquema e da carga de trabalho.

Não presuma que o Spanner é preferível sempre que um banco relacional precisa escalar. Seu valor depende da distribuição geográfica, dos requisitos de consistência, dos padrões de escrita e da tolerância da organização à complexidade operacional e financeira.

### Bigtable: acesso de baixa latência com colunas largas

Conheça o projeto de chaves de linha, padrões de acesso, hotspots, famílias de colunas e replicação, além das diferenças entre uma carga de chave-valor ou colunas largas e um warehouse de SQL analítico.

Uma comparação útil: o **Bigtable** pode atender a consultas por chave com alta vazão; o **BigQuery**, a grandes leituras analíticas; e o **Spanner**, a transações relacionais em escala distribuída. Eles resolvem problemas que se sobrepõem, mas são substancialmente diferentes.

### Firestore no modo Datastore

Revise tipos de entidade, chaves, índices, transações, comportamento de consistência, namespaces e limitações de consulta. As anotações originais descreviam o Datastore de forma geral como tendo “consistência eventual”, o que é amplo demais para uma referência de exame. Consulte as garantias do modo de banco e da operação específicos na [documentação atual do Firestore](https://cloud.google.com/firestore/docs).

## 4. Processamento de dados: lote, streaming e orquestração

### Dataflow e Apache Beam

O Dataflow executa pipelines do Apache Beam em um ambiente gerenciado. Entenda como `PCollection`, `PTransform` e as definições de pipeline se relacionam com o grafo de processamento.

Os conceitos mais desafiadores costumam envolver **tempo do evento, tempo de processamento, watermarks, janelas, gatilhos, dados atrasados e estado**.

| Conceito | Perguntas a fazer |
| --- | --- |
| Janela fixa | É aceitável agrupar por intervalos sem sobreposição? |
| Janela deslizante | Uma visão móvel justifica cálculos sobrepostos? |
| Janela de sessão | A atividade é separada por intervalos, como períodos de inatividade do usuário? |
| Watermark | Como o sistema estima até que ponto os eventos já chegaram, considerando o tempo do evento? |
| Gatilho | Quando os resultados parciais ou finais devem ser emitidos? |
| Atraso permitido | O que acontece quando os dados chegam depois da watermark? |
| Deduplicação | As fontes e as novas tentativas podem gerar eventos duplicados? |

Pipelines em lote e streaming têm características diferentes de recursos, latência e operação. Revise escalabilidade automática, falhas de workers, shuffle, processamento com estado e templates. A recuperação automática de workers não significa que o código da aplicação esteja livre de efeitos colaterais ou do risco de processamento duplicado.

**Cenário:** Você precisa detectar um carrinho abandonado depois que um usuário fica inativo. Uma janela de sessão pode ajudar a representar a inatividade, mas também é necessário definir quais eventos indicam a conclusão da compra e como eventos atrasados afetam a decisão.

### Dataproc, Spark e Hadoop

O Dataproc é especialmente relevante quando uma organização já utiliza Spark, Hadoop, Hive ou componentes relacionados desse ecossistema.

Conheça DataFrames, Spark SQL, RDDs e os fundamentos de grafos de execução e particionamento. Para Hadoop, entenda HDFS e MapReduce conceitualmente. O modelo do Spark pode ser vantajoso para computação iterativa, mas o desempenho depende da carga de trabalho e da configuração.

Entre os assuntos operacionais das minhas anotações que vale revisar estão dimensionamento de clusters, políticas de escalabilidade automática, descomissionamento de workers, envio de jobs (`gcloud dataproc jobs submit spark`), ações de inicialização, versões de imagem, component gateway e integrações com Cloud Storage, BigQuery e Cloud Logging.

Tenha cuidado com afirmações simplistas sobre escalabilidade automática: o comportamento do Dataproc depende da configuração, dos componentes compatíveis e das métricas relevantes do YARN; um exemplo genérico de limite de CPU não descreve de forma confiável seu mecanismo de políticas de escalabilidade.

**Cenário:** Sua empresa já possui jobs e bibliotecas Spark. O que seria ganho ou perdido ao migrá-los para Dataflow em vez de executá-los no Dataproc?

### Pub/Sub: mensageria e processamento assíncrono

Revise tópicos, assinaturas, publicadores, pull versus push, filtros, retenção, tópicos de mensagens não processadas (dead-letter), políticas de novas tentativas, prazos de confirmação e observabilidade dos assinantes.

**A entrega padrão é de pelo menos uma vez, sem garantia geral de ordenação.** Chaves de ordenação podem ordenar mensagens com a mesma chave sob as restrições documentadas. A entrega exatamente uma vez é um recurso configurável de assinaturas pull, com escopo regional e sujeito à semântica documentada. Ela não garante automaticamente que operações de negócio arbitrárias nos sistemas seguintes ocorram exatamente uma vez. Veja o [comportamento das assinaturas](https://cloud.google.com/pubsub/docs/subscription-overview) e a [entrega exatamente uma vez](https://cloud.google.com/pubsub/docs/exactly-once-delivery).

Construa consumidores capazes de lidar com entregas duplicadas, eventos atrasados, contrapressão e processamento de mensagens dead-letter. Saiba quando a idempotência deve ser garantida pela lógica da aplicação.

**Cenário:** Um evento de pagamento inicia o atendimento de um pedido. Como o consumidor pode evitar atender ao mesmo pedido duas vezes quando as mensagens são entregues novamente? Como você monitoraria o acúmulo de mensagens não confirmadas e a idade da mensagem mais antiga?

### Cloud Composer e Apache Airflow

O Composer fornece um ambiente Airflow gerenciado para orquestrar cargas de trabalho dependentes. Estude DAGs, tarefas, operadores, agendamento, novas tentativas, conexões, variáveis, XCom, idempotência, backfills, catchup e logs operacionais.

Eu me concentraria na distinção entre um orquestrador e um mecanismo de processamento. O Airflow pode coordenar jobs de BigQuery e Dataflow sem executar toda a computação nos próprios workers.

Os nomes de operadores e os providers evoluem, então evite memorizar classes antigas como `BigQueryOperator` sem consultar o pacote atual do provider. Prefira entender o que o operador faz e como autenticação, novas tentativas e dependências de dados são modeladas.

**Cenário:** Um pipeline diário carrega arquivos do Cloud Storage, transforma os dados no BigQuery, valida os resultados e publica um relatório. O que acontece se a transformação falhar depois que a carga já tiver sido concluída? Como novas execuções evitarão saídas duplicadas?

### Computação orientada a eventos

O Cloud Functions, atualmente discutido com frequência dentro da família de produtos Cloud Run functions, pode executar código acionado por eventos e HTTP sem gerenciamento direto de servidores. Estude fontes de eventos, contas de serviço, configurações de memória e tempo limite, concorrência quando disponível, cold starts, novas tentativas e observabilidade.

Entenda a diferença entre utilizar uma função para processar um evento leve e utilizar Dataflow ou Dataproc para processamento contínuo em grande escala. Nomes de serviços, recursos específicos de cada geração e limites precisam ser conferidos na documentação atual.

## 5. Aprendizado de máquina pela perspectiva do engenheiro de dados

O PDE não é, principalmente, um exame de pesquisa em ML. A preocupação prática costuma ser se os dados são confiáveis, estão devidamente transformados, seguem os controles de governança e estão prontos para treinamento ou inferência.

### Vertex AI

Conheça os papéis dos datasets gerenciados, treinamento personalizado, abordagens AutoML, pipelines, registro de modelos, endpoints, predição em lote, predição online, monitoramento e gerenciamento de atributos (features).

Vale entender conceitos como treinamento versus disponibilização do modelo para inferência, métricas de avaliação (precisão, revocação e AUC quando apropriado), ajuste de hiperparâmetros, treinamento distribuído e mudanças na distribuição dos dados (data drift). Os recursos de modelos e atributos evoluem com frequência, então confirme os nomes atuais dos produtos antes de se apoiar em diagramas antigos.

### BigQuery ML

Entenda quando faz sentido construir modelos com SQL perto dos dados do warehouse. Pratique reconhecer os fluxos compatíveis e suas implicações para movimentação de dados, avaliação de modelos e operação em produção.

### TensorFlow, PyTorch, GPUs e TPUs

Conheça essas opções de ecossistema e computação, em vez de tentar memorizar todas as APIs de treinamento. Saiba explicar por que o tamanho de um modelo ou dataset, os requisitos do framework, os aceleradores e a estratégia de treinamento distribuído podem influenciar o projeto de uma carga no Vertex AI.

**Cenário:** A maioria dos atributos já está no BigQuery e o objetivo é um modelo de regressão simples. O BigQuery ML simplificaria o fluxo? O que justificaria escolher treinamento personalizado no Vertex AI?

## 6. Segurança, privacidade e governança de dados

### IAM e hierarquia de recursos

Revise organizações, pastas, projetos, políticas, herança, tipos de identidades (principals), grupos, contas de serviço, papéis predefinidos, papéis personalizados e privilégio mínimo.

Lembre-se de que permissões amplas concedidas nos níveis superiores da hierarquia podem afetar os recursos abaixo. As políticas IAM geralmente combinam as permissões aplicáveis; uma concessão em um nível inferior não substitui simplesmente outra em um nível superior. Políticas de negação e outros controles introduzem regras adicionais.

Chaves de contas de serviço trazem riscos de credenciais de longa duração. Quando adequado, prefira identidades de carga de trabalho com escopo apropriado e autenticação sem chaves, em vez de tratar a rotação periódica de chaves como uma solução completa.

### Classificação, descoberta e governança de dados

Minhas anotações originais incluíam o **Data Catalog**, que foi marcado como obsoleto em 2025, com encerramento previsto para 30 de janeiro de 2026. Estude a direção do [BigQuery universal catalog](https://cloud.google.com/dataplex/docs/catalog-overview), reconhecendo os nomes antigos ao consultar materiais históricos de prática.

Entenda descoberta, metadados, linhagem, classificação, policy tags, qualidade dos dados e auditabilidade no nível arquitetural.

### Dados sensíveis e Cloud KMS

Revise os conceitos de Sensitive Data Protection, anteriormente Cloud DLP, como inspeção, infoTypes, mascaramento, ocultação, desidentificação e tokenização. Entenda quando utilizar templates e como dados sensíveis podem aparecer no Cloud Storage, no BigQuery e em fluxos de dados.

No Cloud KMS, estude key rings, versões de chaves, rotação, papéis IAM, CMEK, criptografia de envelope e as implicações operacionais da indisponibilidade de chaves. As políticas de rotação dependem dos requisitos de conformidade e de como as chaves são utilizadas; elas não substituem os controles de autorização.

**Cenário:** Vários clientes compartilham uma plataforma de dados, mas não devem acessar os dados uns dos outros. Avalie separação de datasets, políticas por linha, identidades de serviço e logs de auditoria. Quais controles impõem isolamento e quais apenas ajudam a detectar violações?

## 7. Operações, confiabilidade e custo

### Monitoramento e diagnóstico de problemas

Diferencie métricas, logs, traces e logs de auditoria. Revise dashboards e alertas do Cloud Monitoring, consultas e registros estruturados do Cloud Logging, métricas baseadas em logs e sinks de logs para Cloud Storage, BigQuery ou Pub/Sub.

Para pipelines de dados, sinais úteis podem incluir vazão, taxas de erro, latência de processamento, acúmulo de mensagens dos consumidores, jobs com falha, eventos duplicados, dados atrasados e atualização dos dados de ponta a ponta. Um pipeline pode estar tecnicamente em execução enquanto os dados entregues estão desatualizados ou incorretos.

### Padrões de confiabilidade que vale reconhecer

- Processamento idempotente e backfills repetíveis.
- Novas tentativas controladas com backoff e comportamento claro diante de falhas definitivas.
- Tratamento de mensagens dead-letter e fluxos de reprocessamento.
- Checkpoints, recuperação e comportamento de reprodução de eventos.
- Validação de dados nas etapas de ingestão e transformação.
- Cotas de serviços, restrições de capacidade e limites da escalabilidade automática.
- Separação entre falhas do sistema de origem e falhas dos consumidores seguintes.

### Custo e desempenho

Entenda como leituras de consultas, slots, classes de armazenamento, transferência de dados, ingestão por streaming, capacidade de workers e localização regional podem afetar os custos. Para cada otimização, examine a carga de trabalho antes de presumir que a mudança será benéfica.

## 8. Exercícios de raciocínio no estilo do exame

Estes são **exercícios de estudo originais**, não questões oficiais nem reproduzidas de memória do exame. Em vez de tratar as respostas como associações fixas a nomes de produtos, registre suas premissas e explique sua escolha.

**1. As consultas analíticas estão ficando caras.** Uma grande tabela do BigQuery particionada por data é lida repetidamente para relatórios semanais. Que evidências você examinaria antes de ajustar a chave de partição, os campos de clustering, o projeto das consultas ou a configuração das reservas?

**2. Os eventos chegam fora de ordem.** Um pipeline Dataflow agrega a atividade dos usuários. Como tempo do evento, watermarks, janelas e gatilhos interagem? O que acontece com os eventos atrasados?

**3. Mensagens duplicadas causam efeitos colaterais.** Um assinante do Pub/Sub envia notificações e pode receber mensagens mais de uma vez. Onde a idempotência deve ser garantida e o que muda ao ativar a entrega exatamente uma vez?

**4. Um banco precisa de continuidade de negócios.** Uma aplicação no Cloud SQL exige failover automático e recuperação após uma atualização destrutiva acidental. Por que alta disponibilidade e recuperação para um ponto no tempo são relevantes?

**5. Uma migração de Spark tem restrições operacionais.** Uma equipe precisa migrar jobs existentes de Hadoop/Spark para o Google Cloud. O que determina se Dataproc ou um pipeline redesenhado em Beam/Dataflow é a abordagem inicial mais razoável?

**6. Os dados dos clientes precisam de isolamento.** Uma plataforma analítica compartilhada atende a vários clientes. Como datasets, IAM, segurança por linha e logs de auditoria tratam aspectos diferentes do problema?

**7. Um pipeline informa sucesso, mas os dados estão desatualizados.** Que métricas e verificações de validação você acrescentaria além da saúde dos workers e do status de conclusão dos jobs?

**8. Um modelo precisa de treinamento diário.** Que papéis Cloud Composer, BigQuery, Vertex AI e Cloud Storage poderiam desempenhar? Qual componente é responsável pela orquestração, preparação, treinamento e pelos artefatos?

**9. É necessária consistência relacional global.** Quais características da carga de trabalho justificam avaliar Spanner em vez de Cloud SQL ou Bigtable?

**10. Um arquivo é acessado raramente.** Como você escolheria uma classe do Cloud Storage considerando cobranças de recuperação, períodos mínimos e requisitos de recuperação operacional?

## 9. Questões de prática, laboratórios e referências

**Comece pelo material oficial:**

- [Certificação Google Cloud Professional Data Engineer e guia do exame](https://cloud.google.com/learn/certification/data-engineer)
- [Trilha de aprendizado de Data Engineer do Google Cloud](https://www.cloudskillsboost.google/paths/16/)
- [Questões de exemplo do Google Cloud](https://cloud.google.com/learn/certification/data-engineer)
- [Documentação do BigQuery](https://cloud.google.com/bigquery/docs)
- [Documentação do Dataflow](https://cloud.google.com/dataflow/docs)
- [Documentação do Dataproc](https://cloud.google.com/dataproc/docs)
- [Documentação do Pub/Sub](https://cloud.google.com/pubsub/docs)

**Recursos complementares de prática:**

- [Questões gratuitas de PDE do DailyDebian](https://dailydebian.com/blogs/practice-questions/google-professional-data-engineer-practice-questions). Adicionado na revisão de outubro de 2026. O site anuncia 87 questões gratuitas com explicações, além de coleções maiores opcionais.

- [Questões de PDE do ExamPrepper](https://www.examprepper.co/exam/10/1). Esse estava entre os recursos da comunidade nas minhas anotações originais; verifique a atualidade das questões e das explicações.

- [Simulados de PDE na Udemy](https://www.udemy.com/). A oferta, os nomes e a qualidade dos cursos mudam, então prefira uma listagem atual a um cupom expirado ou uma alegação antiga sobre a versão do exame.

Bancos de questões de terceiros podem revelar lacunas de conhecimento, mas também podem conter respostas desatualizadas ou simplificadas demais. Eu os utilizaria para praticar o raciocínio e depois verificaria os detalhes controversos na documentação oficial.

## 10. Uma lista final de revisão

Antes de me considerar pronto, eu gostaria de conseguir explicar com segurança, sem consultar anotações:

- Quando escolher BigQuery, Cloud SQL, Spanner, Bigtable e Cloud Storage.
- Por que particionamento, clustering e projeto de consultas influenciam o custo e o desempenho do BigQuery.
- Como o processamento pelo tempo do evento no Dataflow lida com janelas, gatilhos, watermarks e dados atrasados.
- Como entrega, ordenação, novas tentativas e idempotência se relacionam no Pub/Sub.
- Quando o Dataproc é adequado para cargas existentes de Spark ou Hadoop.
- Como orquestrar pipelines confiáveis utilizando o Cloud Composer.
- Como engenheiros de dados utilizam BigQuery ML e Vertex AI sem confundir treinamento com disponibilização para inferência.
- Como IAM, controles por linha e coluna, metadados, classificação e gerenciamento de chaves protegem os dados.
- Como investigar um pipeline que está disponível, mas produz resultados incorretos ou desatualizados.
- Como a seleção de serviços muda conforme latência, escala, custo, governança e maturidade operacional.

Esta é a referência que eu queria ao reunir minhas primeiras anotações: abrangente o suficiente para orientar um plano completo de preparação, mas organizada para facilitar a revisão de assuntos específicos. Ela não substitui laboratórios práticos, objetivos oficiais ou experiência com sistemas de dados em produção. A preparação mais útil, na minha opinião, é conseguir explicar uma decisão e suas limitações, em vez de apenas lembrar o nome de um produto isolado.
