+++
slug = "automatizando-a-previsão-de-capacidade-do-ceph-com-grafana-mimir"
lastmod = "2026-10-27"
title = "Automatizando a Previsão de Capacidade do Ceph com Grafana Mimir"
description = "Pipeline de dados completo que recupera métricas de armazenamento Ceph do Grafana Mimir, processa previsões usando pandas e seaborn, gera gráficos de previsão acionáveis com correção de outliers e entrega resumos automatizados e visualizações diretamente para o Microsoft Teams."
date =  "2025-09-17"
draft = false
toc = true
categories = ["python", "grafana"]
tags = ["python", "grafana"]
image = "forecast.png"
author = "Fabio M. Lopes"
+++

## Contexto e decisões na época

Nossa equipe precisava com urgência das informações geradas para o processo de aquisição de hardware, então construí o que era essencial e coloquei em funcionamento o mais rápido possível. Como não sou especialista em análises, um colega forneceu a lógica e inicialmente tudo foi desenvolvido em um Jupyter Notebook, sendo depois migrado para um ambiente com agendamento e acesso direto ao Mimir.

As decisões foram orientadas por essa necessidade: integrar coleta, tratamento, projeção e comunicação em um único fluxo; usar uma projeção simples e compreensível para apoiar o planejamento; e entregar os gráficos e resumos no Teams, sem depender de preparação manual a cada execução. Os modelos mais sofisticados e as demais evoluções ficaram para depois da entrega mais urgente.

## Introdução
O planejamento de capacidade para clusters de armazenamento distribuído é um desafio constante, especialmente em ambientes onde o crescimento rápido de dados pode se transformar rapidamente em riscos de capacidade ou em cenários de aquisições urgentes. No SERPRO, desenvolvi uma solução baseada em Python que automatiza a coleta de métricas de uso do Ceph a partir do Grafana Mimir, analisa tendências históricas de utilização, aplica correção de outliers e projeta o consumo previsto até um ano à frente para múltiplos sites e classes de dispositivos. O sistema não apenas visualiza o uso da capacidade com tendências dinâmicas, robustas a outliers, e indicadores de limite, mas também gera blocos concisos de resumo — automaticamente postados em canais do Microsoft Teams em Adaptive Cards estruturados. Ao integrar ciência de dados com comunicação fluida entre equipes, esse fluxo oferece insights acionáveis que ajudam o time a atuar de forma proativa na gestão da previsão de capacidade de armazenamento.

## O que foi feito
O objetivo principal deste projeto é automatizar a previsão de capacidade para clusters de armazenamento Ceph, integrando recuperação, processamento, visualização e relatórios em um único fluxo de trabalho Python. O processo começa consultando o Grafana Mimir via sua API Prometheus para buscar métricas históricas e recentes de bytes brutos e usados, segmentados por classes de dispositivos e sites (neste caso, São Paulo e Brasília). O fluxo utiliza consultas PromQL estruturadas para coletar não só o uso de armazenamento, mas também a classificação dos dispositivos, para uma análise mais detalhada.

Após a coleta, os dados brutos são mesclados em um DataFrame unificado do pandas. A abordagem lida com lacunas e valores ausentes por interpolação diária, garantindo que a série temporal necessária para análise estatística e plotagem permaneça contínua e regularizada. O tratamento de outliers consiste no cálculo dos deltas diários e aplicação de um filtro baseado no desvio padrão móvel. Saltos repentinos e anômalos no uso diário, provavelmente causados por falhas temporárias ou eventos excepcionais, são substituídos pela mediana do delta diário, assegurando que as tendências de longo prazo não sejam distorcidas por artefatos momentâneos.

A previsão é realizada com um método simples e robusto: o sistema projeta o crescimento do uso para frente usando o aumento diário mediano histórico, assumindo crescimento linear para os próximos 365 dias. Isso se alinha às necessidades práticas do planejamento de capacidade, onde tendências rápidas e compreensíveis têm prioridade sobre modelos complexos e excessivamente ajustados.

Para cada dimensão (site e classe de dispositivo), o script gera gráficos de previsão utilizando matplotlib e seaborn, sobrepondo uso atual, projeções e limiares coloridos (75%, 85% e 100% da capacidade disponível) para melhor clareza visual. Juntamente com os gráficos, o fluxo prepara um resumo textual contendo métricas-chave como datas previstas de saturação, taxas de crescimento e tempos estimados para atingir limites críticos.

Por fim, todo o conteúdo é organizado e enviado ao Microsoft Teams via webhook, utilizando Adaptive Cards para dashboards estruturados e legíveis de forma inline. A automação garante que esses insights estejam sempre atualizados e disponíveis para stakeholders, sem necessidade de intervenção manual ou pipelines separados de relatórios.

## Tratamento dos Dados e Abordagem de Previsão
A fase de tratamento dos dados é fundamental para garantir que as previsões de uso sejam confiáveis e robustas. As métricas brutas recuperadas do Grafana Mimir geralmente contêm ruídos, valores ausentes e outliers ocasionais — picos ou quedas irregulares que não representam padrões típicos de uso, mas podem distorcer a análise de tendências se não corrigidos.

Para mitigar isso, o fluxo primeiro alinha as séries temporais reamostrando para frequência diária e preenche quaisquer pontos faltantes via interpolação linear. Isso garante uma linha do tempo contínua, essencial para cálculos estatísticos consistentes e modelagem de regressão.

O tratamento dos outliers foca nos incrementos diários de uso (a diferença entre dias consecutivos). O script calcula esses deltas para métricas de uso e aplica uma verificação estatística utilizando o desvio padrão móvel para identificar saltos anormais. Valores que ultrapassam essa faixa são considerados outliers e substituídos pela mediana dos deltas calculada a partir dos dados não anômalos. Esse método suaviza flutuações erráticas preservando a tendência subjacente de crescimento.

Ao corrigir os outliers no nível do delta, e não diretamente nos valores brutos, o modelo mantém a consistência cumulativa da métrica. Os deltas corrigidos são somados cumulativamente para reconstruir uma série temporal de uso corrigida. Essa abordagem mitiga efetivamente distorções causadas por pontos anômalos sem eliminar os sinais reais de crescimento.

Para a previsão, os incrementos históricos corrigidos são usados para projetar o crescimento futuro de forma linear ao longo de um horizonte definido (365 dias). O delta diário mediano serve como uma estimativa estável e robusta do aumento esperado de uso por dia. Embora existam modelos mais sofisticados, esse método combina simplicidade e praticidade, fornecendo resultados facilmente interpretáveis e úteis para o planejamento de capacidade. Evita o risco de sobreajuste que pode ocorrer com modelos complexos aplicados a dados operacionais reais ruidosos.

No geral, essa combinação de interpolação cuidadosa, correção estatística de outliers e previsão linear baseada em mediana cria uma base sólida para compreender e antecipar as tendências de consumo do Ceph com complexidade computacional mínima e alta transparência.

## O Código

{{< code-file file="forecast.py" lang="python" collapse="false" >}}

## Melhorias Futuras

- **Modelos de Previsão Avançados:** Em vez de uma extrapolação linear com medianas, incorporar métodos de séries temporais como ARIMA, Prophet, ou modelos de machine learning para capturar sazonalidade, tendências e padrões não lineares com maior precisão;

- **Processamento em Tempo Real ou Próximo disso:** Adaptar a coleta e previsão para suportar atualizações frequentes (ex.: horárias), permitindo reações mais rápidas a variações repentinas ou falhas;

- **Detecção de Anomalias e Alertas:** Integrar métodos automáticos para identificar picos inesperados ou degradações, combinados com alertas proativos em Teams ou outros canais para notificar imediatamente as equipes;

- **Parâmetros de Limite Configuráveis:** Permitir ajuste dinâmico dos limiares (75%, 85%, 100%) via arquivos de configuração ou variáveis de ambiente, aumentando a flexibilidade para diferentes ambientes ou políticas;

- **Visualizações Melhoradas:** Incluir intervalos de confiança nas previsões, dashboards interativos com Plotly Dash ou painéis Grafana, e suporte a cenários múltiplos de longo prazo (ex.: otimista, pessimista);

- **Melhorias de Segurança e Autenticação:** Proteger chamadas de API com autenticação adequada (tokens OAuth, certificados) e gerenciar com segurança URLs de webhook e credenciais de proxy;

- **Extensibilidade para Outras Métricas:** Generalizar o pipeline para incorporar indicadores adicionais de saúde e performance do Ceph (latência, IOPS, status de recuperação) para dashboards mais completos de capacidade e saúde do cluster.

{{< callout type="note" title="Sobre esta implementação histórica" >}}

O código acima documenta a implementação publicada em setembro de 2025 e foi preservado sem alterações de lógica. Configurações específicas daquele ambiente, integrações e limitações refletem essa versão histórica. Uma nova implantação exigiria uma revisão própria; as melhorias listadas acima não são apresentadas como já implementadas.

A expressão “desvio padrão móvel” no relato original descrevia a intenção do tratamento; o código publicado calcula o desvio na série coletada, sem uma janela móvel. Da mesma forma, o comentário “regressão linear” no código nomeia uma extrapolação pelos incrementos medianos. Esses esclarecimentos não alteram a implementação original.
{{< /callout >}}
