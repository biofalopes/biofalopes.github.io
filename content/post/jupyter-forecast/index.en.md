+++
title = "Automating Ceph Storage Forecasting with Grafana Mimir"
description = "End-to-end data pipeline that retrieves Ceph storage metrics from Grafana Mimir, processes forecasts using pandas and seaborn, generates actionable forecast charts with outlier correction, and delivers automated usage summaries and visualizations straight to Microsoft Teams."
date =  "2025-09-17"
draft = true
toc = false
categories = ["python", "grafana" ]
tags = ["python", "grafana" ]
image = "forecast.png"
author = "Fabio M. Lopes"
+++

# Intro
Capacity planning for distributed storage clusters is a constant challenge, especially in environments where rapid data growth can quickly turn into capacity risks or urgent procurement scenarios. At SERPRO, I developed a Python-based solution that automates the collection of Ceph usage metrics from Grafana Mimir, analyzes historical utilization trends, applies outlier correction, and projects forecasted consumption up to a year ahead for multiple sites and device classes. The system not only visualizes capacity usage with dynamic, outlier-robust trends and threshold indicators but also generates concise summary blocks—automatically posted into Microsoft Teams channels in structured Adaptive Cards. By integrating data science with seamless team communication, this workflow provides actionable insights that help our team act proactively on storage forecasting challenges.

# What was done
The core objective of this project is to automate capacity forecasting for Ceph storage clusters by integrating data retrieval, processing, visualization, and reporting into a single Python workflow. The process starts by querying Grafana Mimir via its Prometheus API to fetch historical and recent metrics for raw and used bytes across device classes and sites (in this case, São Paulo and Brasília). The workflow uses structured PromQL queries to collect not only storage usage but also device classification for more granular analysis.

Once the raw metric data is gathered, it is merged into a unified pandas DataFrame. The method handles gaps and missing values through daily interpolation, ensuring the time series needed for statistical analysis and plotting remain continuous and regularized. Outlier treatment comprises delta computation and the application of a rolling standard deviation filter. Sudden, anomalous jumps in daily usage (likely due to transient glitches or exceptional events) are replaced by the median daily delta, ensuring that longer-term trends are not skewed by momentary artifacts.

Forecasting is handled through a simple, robust approach: the system projects usage growth forward using the historical median daily increase, assuming linear growth for the next 365 days. This matches the practical needs for capacity planning where quick, understandable trends trump overfitting or overcomplex modeling.

For each dimension (site and device class), the script generates forecast graphs with matplotlib and seaborn, overlaying current usage, projections, and colored thresholds (75%, 85%, and 100% of available capacity) for visual clarity. Alongside plots, the workflow prepares a text summary containing key metrics such as projected fill dates, growth rates, and estimated time to reach critical thresholds.

Finally, everything is packaged and sent to Microsoft Teams via webhook, using Adaptive Cards for structured, readable inline dashboards. The automation ensures that these insights are always up to date and readily available to stakeholders, without manual intervention or separate reporting pipelines.

# Data Treatment and Forecasting Approach
The data treatment phase is crucial for ensuring that the usage forecasts are reliable and robust. The raw metrics retrieved from Grafana Mimir often contain noise, missing values, and occasional outliers—irregular spikes or drops that do not represent typical usage patterns but can distort trend analysis if left uncorrected.

To address this, the workflow first aligns the time series data by resampling it to a daily frequency and fills any missing data points via linear interpolation. This guarantees a continuous timeline, which is essential for consistent statistical calculations and regression modeling.

Outlier handling focuses on the daily usage increments (the difference between consecutive days). The script calculates these deltas for usage metrics and computes their rolling standard deviation to statistically identify abnormal jumps. Values exceeding this threshold are considered outliers and replaced with the median delta value calculated from the non-outlier data. This method smooths erratic fluctuations while preserving the underlying growth trend.

By repairing outliers at the delta level rather than raw usage values directly, the model maintains the cumulative consistency of the metric. The corrected deltas are then cumulatively summed to reconstruct a corrected usage time series. This approach effectively mitigates distortion from anomalous data points without discarding real growth signals.

For forecasting, the corrected historical increments are used to project future growth linearly over a defined horizon (365 days). The median daily delta serves as a stable, robust estimate of expected usage increase per day. While more sophisticated models exist, this method balances simplicity and practicality, yielding easily interpretable results and forecasts useful for capacity planning. It avoids overfitting that can occur with complex models on noisy real-world operational data.

Overall, this combination of careful interpolation, statistically informed outlier correction, and straightforward median-based linear forecasting creates a solid foundation for understanding and anticipating Ceph storage consumption trends with minimal computational complexity and high transparency.

# The code

Disclaimer: Some variables will be in portuguese.

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

# Future Improvements
Our team urgently needed the information provided by this for the hardware aquisition process, so I build what was essential and put it to work as fast as possible. Since I'm no expert on analytics, my colleague provided the logic and I first built exerything as a Jupyter Notebook, and later moved it to a place where it could be scheduled and had direct access to Mimir. After the more urgent issues were addressed, we could stop to think about improvements to the tool:

- **Advanced Forecasting Models:** Instead of a linear extrapolation using median deltas, incorporate time series forecasting methods such as ARIMA, Prophet, or machine learning regression models to capture seasonality, trends, and potential non-linear growth patterns more accurately;

- **Real-Time or Near Real-Time Processing:** Adapt the data collection and forecasting pipeline to support streaming or more frequent updates (e.g., hourly), enabling quicker reaction times to sudden usage changes or outages;

- **Anomaly Detection and Alerting:** Integrate automatic anomaly detection techniques beyond simple standard deviation filtering to identify unexpected spikes or degradations. Pair these with proactive alerts in Teams or other channels to notify teams immediately;

- **Capacity Thresholds as Configurable Parameters:** Allow dynamic adjustment of threshold levels (75%, 85%, 100%) via configuration files or environment variables instead of hardcoded values, improving flexibility for different environments or changing policies;

- **Improved Visualization:** Enhance graphs by including confidence intervals on forecasts, interactive dashboards using tools such as Plotly Dash or Grafana panels, and support for multiple longer-term scenarios (e.g., optimistic, pessimistic);

- **Authentication & Security Enhancements:** Secure API calls with proper authentication (OAuth tokens, certificates) and securely manage webhook URLs and proxy credentials;

- **Extensibility for Other Metrics:** Generalize the pipeline to incorporate additional Ceph health and performance indicators (e.g., latency, IOPS, recovery status) for a more comprehensive capacity and cluster health dashboard.