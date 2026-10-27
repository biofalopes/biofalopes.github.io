+++  
slug = "automatizando-a-previsão-de-capacidade-do-ceph-com-grafana-mimir"
lastmod = "2026-10-26"
title = "Automatizando a Previsão de Capacidade do Ceph com Grafana Mimir"  
description = "Planejamento de capacidade Ceph com projeção pela mediana dos incrementos, validação dos dados e integração opcional com Mimir e Teams."
date =  "2025-09-17"  
draft = false  
toc = true  
categories = ["python", "grafana"]  
tags = ["python", "grafana"]  
image = "forecast.png"  
author = "Fabio M. Lopes"  
+++

## Contexto operacional

No SERPRO, desenvolvi um fluxo em Python para coletar métricas de capacidade do Ceph no Grafana Mimir e apoiar o planejamento da equipe. O trabalho começou em um Jupyter Notebook, com a lógica de previsão discutida com um colega, e evoluiu para relatórios agendados com gráficos e resumos enviados ao Microsoft Teams.

**Revisão técnica — outubro de 2026:** a implementação anterior comparava variações diárias a um desvio padrão sem centralização, podendo apagar crescimento positivo constante. O texto também descrevia um cálculo móvel que o código não realizava. Esta revisão substitui esse filtro por uma projeção explícita pela mediana dos incrementos, preserva o histórico observado e trata crescimento zero ou negativo, dados ausentes e limites já atingidos. O exemplo foi revisado; isso não demonstra atualização da implantação operacional nem melhora de precisão.

## Como funciona a projeção

Para cada site e classe de dispositivo, a entrada contém uma observação por dia UTC: bytes brutos usados e capacidade bruta em bytes. A mediana das diferenças entre dias consecutivos estima o crescimento. Partindo da **última observação real**, o primeiro dia adiciona um incremento e o dia N adiciona N incrementos. Trata-se de extrapolação linear com inclinação mediana, não de regressão linear ajustada.

As medições originais são preservadas. O código não classifica saltos como erros nem os substitui silenciosamente por zero. A mediana reduz a influência de deltas extremos isolados, mas não determina se uma mudança representa falha de coleta, rebalanceamento, exclusão ou alteração real de carga. É preciso avaliar esses eventos e a janela escolhida.

A coleta usa, por padrão, 30 observações diárias completas. Dados vazios, valores não finitos, dias ausentes, dimensões incompatíveis e mudanças de capacidade na janela interrompem o relatório. Não há interpolação nem preenchimento de observações ausentes. Depois de uma expansão, selecione uma janela estável posterior ao evento.

O resultado diferencia quatro situações:

| Status | Significado |
|---|---|
| `already_reached` | Uso observado já atingiu o limite; restam zero dias. |
| `not_reached_nonpositive_growth` | Uso abaixo do limite, com crescimento estimado zero ou negativo; não há cruzamento futuro projetado. |
| `within_horizon` | A projeção diária cruza o limite dentro do horizonte configurado. |
| `beyond_horizon` | Há crescimento positivo, mas o limite não é atingido no horizonte; nenhuma data distante é inventada. |

Projeções decrescentes têm piso em zero. O uso projetado não é limitado à capacidade: ultrapassar 100% indica uma trajetória inviável sem intervenção. O limiar de 75% é uma escolha de planejamento, não um full ratio universal do Ceph. Capacidade bruta também não equivale à capacidade útil da aplicação: replicação, erasure coding e reserva para falhas precisam ser considerados.

## Executar localmente

Baixe {{< resource-link file="forecast.py" >}} e {{< resource-link file="sample.csv" >}} no mesmo diretório. A amostra contém **dados sintéticos** com crescimento de 10 TiB/dia, sem métricas operacionais. Python 3.10+ é suficiente para o fluxo principal.

```bash
python forecast.py --csv sample.csv --horizon 90 --output forecast-output
```

O comando gera JSON, CSV da projeção e um payload de Adaptive Card. Nenhuma mensagem é enviada. Para gerar PNGs, instale matplotlib em um ambiente virtual e use `--plot`:

```bash
python -m venv .venv
# Ative .venv com o comando adequado ao seu sistema operacional.
python -m pip install matplotlib
python forecast.py --csv sample.csv --horizon 90 --plot
```

A imagem de capa mostra o relatório anterior; ela não valida o modelo revisado.

## Coletar do Mimir

Configure `MIMIR_QUERY_URL` com o endpoint HTTPS completo de query range, `MIMIR_TENANT_ID` com o tenant permitido pelo proxy autenticador e, se necessário, `MIMIR_BEARER_TOKEN` com o token de acesso. `METRICS_CA_FILE` pode apontar para o bundle de CAs internas confiáveis; caso contrário, o código usa as CAs do sistema. A validação TLS permanece ativa, as requisições têm timeout e não seguem redirecionamentos.

A PromQL pressupõe que `site` e `ceph_daemon` identificam um OSD de forma única e que `ceph_osd_metadata` fornece `device_class`. Adapte labels e agregações se houver vários clusters por site. Identificação de tenant não é autenticação: a autorização deve ser aplicada no gateway. A [API HTTP do Prometheus](https://prometheus.io/docs/prometheus/latest/querying/api/) descreve o formato das respostas.

```bash
python forecast.py --history-days 30 --horizon 365 --threshold 0.75
```

A janela termina na amostra da meia-noite UTC do dia anterior. A coleta exige séries completas e correspondentes; avisos de consulta e erros interrompem a execução. O agendador deve alertar sobre falhas, e o campo `as_of` deve permanecer visível no relatório.

## Enviar um resumo ao Teams

O relatório original utilizava um webhook do Office. Para uma integração nova, configure um Workflow do Teams que receba uma chamada HTTP e publique um Adaptive Card, adequando autenticação e payload ao tenant. Consulte as [opções de webhook e Workflow da Microsoft](https://learn.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook).

O exemplo grava `teams-payload.json` para inspeção. Ele aceita um webhook autorizado pela posse da URL; endpoints que exigem OAuth precisam de um adaptador de autenticação apropriado. Depois de configurar o receptor e proteger a URL como segredo, o envio é explícito:

```bash
python forecast.py --csv sample.csv --send-teams
```

Forneça `TEAMS_WEBHOOK_URL` por um gerenciador de segredos ou variável de ambiente protegida. O exemplo envia resumos textuais; PNGs ficam locais. Publicar gráficos exige uma solução aprovada de hospedagem e autenticação de imagens. As integrações não foram executadas contra serviços de produção durante esta revisão.

## Implementação compartilhada

As duas versões do artigo renderizam o mesmo arquivo de código, permitindo testes e manutenção em um único lugar.

{{< code-file file="forecast.py" lang="python" >}}

## Validação e limites

Os testes cobrem crescimento constante, pico isolado, crescimento zero ou negativo, limite já atingido, borda do horizonte, lacunas, métricas inválidas e mudança de capacidade. Uma separação cronológica em dados sintéticos verifica o cálculo sem usar observações futuras no treinamento. Esses testes verificam comportamento, não precisão em produção.

Antes de apoiar compras, faça backtesting em janelas históricas, compare com uma previsão sem crescimento, meça erros nos prazos relevantes e revise mudanças estruturais. O exemplo não apresenta intervalo de confiança nem precisão anual comprovada. Exponha as incertezas e o prazo de aquisição junto com a data projetada.
