+++  
title = "Automatizando a Previsão de Capacidade do Ceph com Grafana Mimir"  
description = "Pipeline de dados completo que recupera métricas de armazenamento Ceph do Grafana Mimir, processa previsões usando pandas e seaborn, gera gráficos de previsão acionáveis com correção de outliers e entrega resumos automatizados e visualizações diretamente para o Microsoft Teams."  
date =  "2025-09-17"  
draft = false  
toc = false  
categories = ["python", "grafana"]  
tags = ["python", "grafana"]  
image = "forecast.png"  
author = "Fabio M. Lopes"  
+++  

# Introdução  
O planejamento de capacidade para clusters de armazenamento distribuído é um desafio constante, especialmente em ambientes onde o crescimento rápido de dados pode se transformar rapidamente em riscos de capacidade ou em cenários de aquisições urgentes. No SERPRO, desenvolvi uma solução baseada em Python que automatiza a coleta de métricas de uso do Ceph a partir do Grafana Mimir, analisa tendências históricas de utilização, aplica correção de outliers e projeta o consumo previsto até um ano à frente para múltiplos sites e classes de dispositivos. O sistema não apenas visualiza o uso da capacidade com tendências dinâmicas, robustas a outliers, e indicadores de limite, mas também gera blocos concisos de resumo — automaticamente postados em canais do Microsoft Teams em Adaptive Cards estruturados. Ao integrar ciência de dados com comunicação fluida entre equipes, esse fluxo oferece insights acionáveis que ajudam o time a atuar de forma proativa na gestão da previsão de capacidade de armazenamento.

# O que foi feito  
O objetivo principal deste projeto é automatizar a previsão de capacidade para clusters de armazenamento Ceph, integrando recuperação, processamento, visualização e relatórios em um único fluxo de trabalho Python. O processo começa consultando o Grafana Mimir via sua API Prometheus para buscar métricas históricas e recentes de bytes brutos e usados, segmentados por classes de dispositivos e sites (neste caso, São Paulo e Brasília). O fluxo utiliza consultas PromQL estruturadas para coletar não só o uso de armazenamento, mas também a classificação dos dispositivos, para uma análise mais detalhada.

Após a coleta, os dados brutos são mesclados em um DataFrame unificado do pandas. A abordagem lida com lacunas e valores ausentes por interpolação diária, garantindo que a série temporal necessária para análise estatística e plotagem permaneça contínua e regularizada. O tratamento de outliers consiste no cálculo dos deltas diários e aplicação de um filtro baseado no desvio padrão móvel. Saltos repentinos e anômalos no uso diário, provavelmente causados por falhas temporárias ou eventos excepcionais, são substituídos pela mediana do delta diário, assegurando que as tendências de longo prazo não sejam distorcidas por artefatos momentâneos.

A previsão é realizada com um método simples e robusto: o sistema projeta o crescimento do uso para frente usando o aumento diário mediano histórico, assumindo crescimento linear para os próximos 365 dias. Isso se alinha às necessidades práticas do planejamento de capacidade, onde tendências rápidas e compreensíveis têm prioridade sobre modelos complexos e excessivamente ajustados.

Para cada dimensão (site e classe de dispositivo), o script gera gráficos de previsão utilizando matplotlib e seaborn, sobrepondo uso atual, projeções e limiares coloridos (75%, 85% e 100% da capacidade disponível) para melhor clareza visual. Juntamente com os gráficos, o fluxo prepara um resumo textual contendo métricas-chave como datas previstas de saturação, taxas de crescimento e tempos estimados para atingir limites críticos.

Por fim, todo o conteúdo é organizado e enviado ao Microsoft Teams via webhook, utilizando Adaptive Cards para dashboards estruturados e legíveis de forma inline. A automação garante que esses insights estejam sempre atualizados e disponíveis para stakeholders, sem necessidade de intervenção manual ou pipelines separados de relatórios.

# Tratamento dos Dados e Abordagem de Previsão  
A fase de tratamento dos dados é fundamental para garantir que as previsões de uso sejam confiáveis e robustas. As métricas brutas recuperadas do Grafana Mimir geralmente contêm ruídos, valores ausentes e outliers ocasionais — picos ou quedas irregulares que não representam padrões típicos de uso, mas podem distorcer a análise de tendências se não corrigidos.

Para mitigar isso, o fluxo primeiro alinha as séries temporais reamostrando para frequência diária e preenche quaisquer pontos faltantes via interpolação linear. Isso garante uma linha do tempo contínua, essencial para cálculos estatísticos consistentes e modelagem de regressão.

O tratamento dos outliers foca nos incrementos diários de uso (a diferença entre dias consecutivos). O script calcula esses deltas para métricas de uso e aplica uma verificação estatística utilizando o desvio padrão móvel para identificar saltos anormais. Valores que ultrapassam essa faixa são considerados outliers e substituídos pela mediana dos deltas calculada a partir dos dados não anômalos. Esse método suaviza flutuações erráticas preservando a tendência subjacente de crescimento.

Ao corrigir os outliers no nível do delta, e não diretamente nos valores brutos, o modelo mantém a consistência cumulativa da métrica. Os deltas corrigidos são somados cumulativamente para reconstruir uma série temporal de uso corrigida. Essa abordagem mitiga efetivamente distorções causadas por pontos anômalos sem eliminar os sinais reais de crescimento.

Para a previsão, os incrementos históricos corrigidos são usados para projetar o crescimento futuro de forma linear ao longo de um horizonte definido (365 dias). O delta diário mediano serve como uma estimativa estável e robusta do aumento esperado de uso por dia. Embora existam modelos mais sofisticados, esse método combina simplicidade e praticidade, fornecendo resultados facilmente interpretáveis e úteis para o planejamento de capacidade. Evita o risco de sobreajuste que pode ocorrer com modelos complexos aplicados a dados operacionais reais ruidosos.

No geral, essa combinação de interpolação cuidadosa, correção estatística de outliers e previsão linear baseada em mediana cria uma base sólida para compreender e antecipar as tendências de consumo do Ceph com complexidade computacional mínima e alta transparência.

# O Código  

```python
import os
import io
import json
import base64
import logging
import urllib3
import requests
import pandas
from datetime import datetime, timedelta, timezone
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker

output_dir = '/srv/scripts'
TiB = 1099511627776 # Is this really necessary?

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=os.path.join(output_dir,'capacidade-forecast.log'),
    filemode='w'
)
logger = logging.getLogger(__name__)
logger.info(f"-----Inicio-----")

## 1. Query Configuration
logger.info("1. Configuração da Query")
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://mimir-endpoint/prometheus/api/v1/query_range"
headers = {
    'X-Scope-OrgID': 'anonymous'
}

queries = {
    "Capacidade SPO": "sum by (device_class) (ceph_osd_stat_bytes{site='spo'} + on(site,ceph_daemon) group_left(device_class) (0*ceph_osd_metadata{site='spo'}))",
    "Capacidade BSA": "sum by (device_class) (ceph_osd_stat_bytes{site='bsa'} + on(site,ceph_daemon) group_left(device_class) (0*ceph_osd_metadata{site='bsa'}))",
    "Uso SPO": "sum by (device_class) ((ceph_osd_stat_bytes_used{site='spo'}) + on(site,ceph_daemon) group_left(device_class) (0*ceph_osd_metadata{site='spo'}))",
    "Uso BSA": "sum by (device_class) ((ceph_osd_stat_bytes_used{site='bsa'}) + on(site,ceph_daemon) group_left(device_class) (0*ceph_osd_metadata{site='bsa'}))"
}

current_utc = datetime.now(timezone.utc)
end_date = (current_utc).replace(hour=0, minute=0, second=0, microsecond=0)
start_date = datetime(2024, 9, 27, 0, 0, 0)  # No data prior to this date

params_template = {
    "start": start_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
    "end": end_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
    "step": "1d"
}

## 2. Query Execution
logger.info("2. Execução da Query")
dataframe = pandas.DataFrame()

for query_name, query in queries.items():
    params = params_template.copy()
    params["query"] = query
    response = requests.get(url, params=params, headers=headers, verify=False)
    try:
        response.raise_for_status()
        mimir_data = response.json()['data']['result']
        if not mimir_data:
            logger.error(f"No data returned for query: {query_name}")
            continue
        for result in mimir_data:
            if 'device_class' not in result['metric']:
                continue
            device_class = result['metric']['device_class']
            temp_df = pandas.DataFrame(result['values'], columns=['timestamp', f'{query_name} {device_class}'])
            temp_df['timestamp'] = pandas.to_datetime(temp_df['timestamp'], unit='s')
            if dataframe.empty:
                dataframe = temp_df
            else:
                dataframe = pandas.merge(dataframe, temp_df, on='timestamp', how='outer')
    except requests.exceptions.HTTPError as err:
        logger.error(f"HTTP error for query '{query_name}': {err}\nResponse body: {response.text}")
    except KeyError:
        logger.error(f"Unexpected response format for query '{query_name}': {response.json()}")

# Save as CSV
#output_file = 'device_data.csv'
#dataframe.to_csv(output_file, index=False)

## 3. Treat the Data
logger.info("3. Tratamento dos Dados")
# Define the index
dataframe = dataframe.rename(columns={'timestamp': 'Time'})
dataframe.set_index('Time', inplace=True)

# Convert values to numeric
numeric_columns = dataframe.columns.drop('Time') if 'Time' in dataframe.columns else dataframe.columns
for col in numeric_columns:
    dataframe[col] = pandas.to_numeric(dataframe[col], errors='coerce')

# Interpolate missing values
dataframe = dataframe.resample('D').interpolate(method='linear')
dataframe.reset_index(inplace=True)

## Treat the Outliers
cols_uso = [col for col in dataframe.columns if col.startswith('Uso')]
std_dev = {}
medianas = {}

# Calculate Delta and Standard Deviation
for col in cols_uso:
    _, site, device_class = col.split(' ')
    delta_col = f'Delta {site} {device_class}'
    delta_corrigido_col = f'Delta Corrigido {site} {device_class}'
    uso_corrigido_col = f'Uso Corrigido {site} {device_class}'
    
    # Calculate Delta
    dataframe[delta_col] = dataframe[col].diff()
    
    # Calculate Standard Deviation
    std_dev = dataframe[delta_col].iloc[1:].std()
    logger.debug(f"Desvio Padrão {site} {device_class}: {std_dev/TiB:.2f} TiB")
    
    # Apply the outlier correction
    dataframe[delta_corrigido_col] = dataframe[delta_col].where(
        (abs(dataframe[delta_col]) <= std_dev) | (dataframe.index == dataframe.index[0]), 0
    )
    
    # Calculate the delta median without the outliers
    medianas[col] = dataframe[delta_corrigido_col].iloc[1:].median()
    
    # Fill zero/empty values with the median
    dataframe[delta_corrigido_col] = dataframe[delta_corrigido_col].where(
        (dataframe[delta_corrigido_col] != 0) | (dataframe.index == dataframe.index[0]), 
        medianas[col]
    )

# Calculate Corrected raw usage
cols_delta = [col for col in dataframe.columns if col.startswith('Delta Corrigido')]
for col in cols_delta:
    _, _, site, device_class = col.split()
    uso_col = f"Uso {site} {device_class}"
    corrigido_col = f"Uso Corrigido {site} {device_class}"
    
    # Initialize the 'Corrected Usage' column with the first value from the 'Usage' column
    dataframe[corrigido_col] = dataframe[uso_col].iloc[0]
    
    # Calculate the cumulative sum of the corrected delta, starting from the second row
    dataframe.loc[1:, corrigido_col] += dataframe.loc[1:, col].cumsum()

# Drop unecessary columns
cols_drop = [col for col in dataframe.columns if col.startswith('Delta')]
dataframe = dataframe.drop(columns=cols_drop)

# Save to .csv
# output_file = 'device_data.csv'
# dataframe.to_csv(os.path.join(output_dir, output_file), index=False)


## 4. Calculation of the Linear Regression
logger.info("4. Cálculo da Regressão Linear")
# Gerar o Horizonte da Previsão
ultima_coleta = dataframe['Time'].max()
data_inicial = ultima_coleta.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
forecast_horizonte = 365
forecast_datas = pandas.date_range(start=data_inicial, periods=forecast_horizonte)
forecast_df = pandas.DataFrame({'Time': forecast_datas})

# Generate Forecasts
for col in cols_uso:
    _, site, device_class = col.split(' ')
    forecast = [dataframe[col].iloc[-1]]
    for _ in range(1, forecast_horizonte):
        forecast.append(forecast[-1] + medianas[col])   
    column_name = f"{site}_{device_class}"
    forecast_df[column_name] = forecast

forecast_df.tail()

## 5. Generate the Summary
logger.info(f"5. Geração do Resumo")
results = {}
summary_text = ""
current_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

for col in cols_uso:
    _, site, device_class = col.split(' ')
    forecast_col = f"{site}_{device_class}"
    
    # Obtain the Capacity and calculate the Rate
    capacidade = dataframe[f'Capacidade {site} {device_class}'].iloc[-1] * 0.75 / TiB
    uso_atual = dataframe[col].iloc[-1] / TiB
    uso_final = forecast_df[forecast_col].iloc[-1] / TiB
    taxa = (uso_final - uso_atual) / forecast_horizonte 
    
    # Check the Threshold
    threshold_mask = (forecast_df[forecast_col] / TiB) >= capacidade
    if threshold_mask.any():
        threshold_date = forecast_df.loc[threshold_mask, 'Time'].min().strftime('%d-%m-%Y')
    else:
        threshold_date = "Limite não atingido no período"
    
    # Calculate remaining Days
    days_remaining = abs((capacidade - uso_atual) / taxa)
    years, months, days = int(days_remaining // 365), int((days_remaining % 365) // 30.42), round((days_remaining % 365) % 30.42)
    doomsday = (dataframe['Time'].iloc[-1] + timedelta(days=days_remaining)).strftime('%d-%m-%Y')
    doomsday_f = (f"{years} anos, {months} meses e {days} dias")
    
    # Generate the Summary
    summary_text += f"""
Resumo {site} {device_class}:
Capacidade (75%): {capacidade:.2f} TiB
Uso em 31/12/2025: {uso_final:.2f} TiB
Taxa de crescimento diária: {taxa:.2f} TiB/dia
Quando atinge 75%: {doomsday}
Tempo até atingir 75%: {doomsday_f}
"""

## 6. Generate the Graphs
logger.info("6. Geração dos Gráficos")
# Obter Sites e Classes
sites = set()
device_classes = set()

for col in dataframe.columns:
    if col.startswith('Uso'):
        parts = col.split()
        sites.add(parts[1])
        device_classes.add(parts[2])

# Generate the Plots
plots = {}
for site in sites:
    for device_class in device_classes:
        try:
            # Verify the columns
            uso_col = f'Uso {site} {device_class}'
            uso_corrigido_col = f'Uso Corrigido {site} {device_class}'
            capacidade_col = f'Capacidade {site} {device_class}'
            forecast_col = f'{site}_{device_class}'
            
            if not all(col in dataframe.columns for col in [uso_col, uso_corrigido_col, capacidade_col]):
                continue

            if forecast_col not in forecast_df.columns:
                continue

            plt.figure(figsize=(12, 6))

            # Plot Lines
            sns.lineplot(x=dataframe['Time'], y=dataframe[uso_col]/TiB,
                         label='Uso Bruto', linewidth=1.5, color='purple')
            sns.lineplot(x=forecast_df['Time'], y=forecast_df[forecast_col]/TiB,
                         label='Previsão', linestyle='--', linewidth=2, color='navy')

            # Plot Thresholds
            capacity_tib = dataframe[capacidade_col].iloc[-1]/TiB
            limits = [
                (capacity_tib * 0.75, '75%', 'gold'),
                (capacity_tib * 0.85, '85%', 'darkorange'),
                (capacity_tib, '100%', 'crimson')
            ]   
            for value, label, color in limits:
                plt.axhline(y=value, color=color, linestyle='-.',
                            linewidth=1.5, alpha=0.8, label=label)

            # Format
            plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            plt.xticks(rotation=45, ha='right')
            plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{x:,.1f} TiB'))
            plt.gca().yaxis.set_major_locator(ticker.MaxNLocator(10))
            plt.title(f'Previsão Ceph {site} - Classe {device_class.upper()}', fontsize=16, pad=20)
            plt.xlabel('Data', fontsize=12, labelpad=10)
            plt.ylabel(f'Uso {device_class.upper()} (TiB)', fontsize=12, labelpad=10)
            plt.grid(True, linestyle='--', alpha=0.6)

            # Configure Subtitles
            handles, labels = plt.gca().get_legend_handles_labels()
            order = [0, 1, 2, 3, 4]
            plt.legend([handles[idx] for idx in order], [labels[idx] for idx in order], 
                       loc='upper left', frameon=True, shadow=True, fontsize=12)
            plt.tight_layout()
            
            # Save Graphs
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            buffer.seek(0)
            plots[f'{site}_{device_class}'] = base64.b64encode(buffer.getvalue()).decode('utf-8')
            buffer.close()
            plt.close()
            
        except Exception as e:
            print(f"Error generating plot for {site} {device_class}: {str(e)}")
            plt.close()

## 7. Send to Teams
logger.info(f"7. Envio para o Teams")
# Create the message
def create_teams_message(summary_data, plots):
    cards = []
    sections = parse_summary_text(summary_data)
    
    for site in ['SPO', 'BSA']:
        card = {
            "type": "message",
            "attachments": [{
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.2",
                    "body": [
                        {
                            "type": "TextBlock",
                            "text": "São Paulo" if site == "SPO" else "Brasília",
                            "weight": "Bolder",
                            "size": "Large",
                            "color": "Accent"
                        },
                        *create_device_sections(sections.get(site, {}))
                    ]
                }
            }]
        }
        
        # Add site-specific plots
        site_plots = {k: v for k, v in plots.items() if k.lower().startswith(site.lower())}
        for plot_name, plot_data in site_plots.items():
            image_block = {
                "type": "Image",
                "url": f"data:image/png;base64,{plot_data}",
                "size": "auto"
            }
            card['attachments'][0]['content']['body'].append(image_block)
        
        cards.append(card)
    
    return [json.dumps(card) for card in cards]

# Convert the Summary Text
def parse_summary_text(text):
    sections = {}
    current_section = None
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue
        if line.startswith('Resumo'):
            parts = line.replace('Resumo ', '').replace(':', '').split()
            site = parts[0]
            device_class = parts[1]
            if site not in sections:
                sections[site] = {}
            current_section = sections[site].setdefault(device_class, {})            
        elif line and current_section is not None:
            key_value = line.split(':')
            if len(key_value) == 2:
                key = key_value[0].strip()
                value = key_value[1].strip()
                current_section[key] = value            
    return sections

# Create the Sections
def create_device_sections(devices):
    sections = []
    for device_class, data in devices.items():
        section = {
            "type": "Container",
            "style": "emphasis",
            "items": [
                {
                    "type": "TextBlock",
                    "text": f"Classe {device_class.upper()}",
                    "weight": "Bolder",
                    "size": "Small"
                },
                {
                    "type": "FactSet",
                    "facts": [
                        {"title": "Capacidade (75%):", "value": data.get('Capacidade (75%)', 'N/A')},
                        {"title": "Uso em 31/12/2025:", "value": data.get('Uso em 31/12/2025', 'N/A')},
                        {"title": "Taxa de crescimento:", "value": data.get('Taxa de crescimento diária', 'N/A')},
                        {"title": "Quando atinge 75%:", "value": data.get('Quando atinge 75%', 'N/A')},
                        {"title": "Tempo até atingir 75%:", "value": data.get('Tempo até atingir 75%', 'N/A')}
                    ]
                }
            ]
        }
        sections.append(section)
    return sections
 
# Send to Teams
def send_to_teams(payloads):
    # Chat Capacidade
    WEBHOOK_URL = "https://corp.webhook.office.com/webhookb2/id"

    PROXIES = {'https': 'http://proxy:3128'}
    headers = {'Content-Type': 'application/json'}
    statuses = []
    for payload in payloads:
        response = requests.post(
            WEBHOOK_URL,
            data=payload,
            headers=headers,
            proxies=PROXIES,
            verify=False
        )
        statuses.append(response.status_code)
    
    return statuses

# Create and send the message
messages = create_teams_message(summary_text, plots)
status = send_to_teams(messages)
logger.info(f"-----Fim-----")
```

# Melhorias Futuras  
Nossa equipe precisava com urgência das informações geradas para o processo de aquisição de hardware, então construí o que era essencial e coloquei em funcionamento o mais rápido possível. Como não sou especialista em análises, um colega forneceu a lógica e inicialmente tudo foi desenvolvido em um Jupyter Notebook, sendo depois migrado para um ambiente com agendamento e acesso direto ao Mimir. Após resolver as questões mais urgentes, pudemos refletir sobre melhorias para a ferramenta:

- **Modelos de Previsão Avançados:** Em vez de uma extrapolação linear com medianas, incorporar métodos de séries temporais como ARIMA, Prophet, ou modelos de machine learning para capturar sazonalidade, tendências e padrões não lineares com maior precisão;

- **Processamento em Tempo Real ou Próximo disso:** Adaptar a coleta e previsão para suportar atualizações frequentes (ex.: horárias), permitindo reações mais rápidas a variações repentinas ou falhas;

- **Detecção de Anomalias e Alertas:** Integrar métodos automáticos para identificar picos inesperados ou degradações, combinados com alertas proativos em Teams ou outros canais para notificar imediatamente as equipes;

- **Parâmetros de Limite Configuráveis:** Permitir ajuste dinâmico dos limiares (75%, 85%, 100%) via arquivos de configuração ou variáveis de ambiente, aumentando a flexibilidade para diferentes ambientes ou políticas;

- **Visualizações Melhoradas:** Incluir intervalos de confiança nas previsões, dashboards interativos com Plotly Dash ou painéis Grafana, e suporte a cenários múltiplos de longo prazo (ex.: otimista, pessimista);

- **Melhorias de Segurança e Autenticação:** Proteger chamadas de API com autenticação adequada (tokens OAuth, certificados) e gerenciar com segurança URLs de webhook e credenciais de proxy;

- **Extensibilidade para Outras Métricas:** Generalizar o pipeline para incorporar indicadores adicionais de saúde e performance do Ceph (latência, IOPS, status de recuperação) para dashboards mais completos de capacidade e saúde do cluster.