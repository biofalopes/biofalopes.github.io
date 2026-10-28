+++
slug = "automating-ceph-storage-forecasting-with-grafana-mimir"
lastmod = "2026-10-27"
title = "Automating Ceph Storage Forecasting with Grafana Mimir"
description = "End-to-end data pipeline that retrieves Ceph storage metrics from Grafana Mimir, processes forecasts using pandas and seaborn, generates actionable forecast charts with outlier correction, and delivers automated usage summaries and visualizations straight to Microsoft Teams."
date =  "2025-09-17"
draft = false
toc = true
categories = ["python", "grafana" ]
tags = ["python", "grafana" ]
image = "forecast.png"
author = "Fabio M. Lopes"
+++

## Context and decisions at the time

Our team urgently needed this information for the hardware acquisition process, so I built what was essential and put it to work as fast as possible. Since I'm no expert on analytics, my colleague provided the logic and I first built everything as a Jupyter Notebook, and later moved it to a place where it could be scheduled and had direct access to Mimir.

That need shaped the decisions: integrate collection, processing, forecasting and communication into one workflow; use a simple, understandable projection to support planning; and deliver charts and summaries through Teams without preparing each report manually. More sophisticated models and other improvements could follow after the urgent delivery.

## Intro
Capacity planning for distributed storage clusters is a constant challenge, especially in environments where rapid data growth can quickly turn into capacity risks or urgent procurement scenarios. At SERPRO, I developed a Python-based solution that automates the collection of Ceph usage metrics from Grafana Mimir, analyzes historical utilization trends, applies outlier correction, and projects forecasted consumption up to a year ahead for multiple sites and device classes. The system not only visualizes capacity usage with dynamic, outlier-robust trends and threshold indicators but also generates concise summary blocks—automatically posted into Microsoft Teams channels in structured Adaptive Cards. By integrating data science with seamless team communication, this workflow provides actionable insights that help our team act proactively on storage forecasting challenges.

## What was done
The core objective of this project is to automate capacity forecasting for Ceph storage clusters by integrating data retrieval, processing, visualization, and reporting into a single Python workflow. The process starts by querying Grafana Mimir via its Prometheus API to fetch historical and recent metrics for raw and used bytes across device classes and sites (in this case, São Paulo and Brasília). The workflow uses structured PromQL queries to collect not only storage usage but also device classification for more granular analysis.

Once the raw metric data is gathered, it is merged into a unified pandas DataFrame. The method handles gaps and missing values through daily interpolation, ensuring the time series needed for statistical analysis and plotting remain continuous and regularized. Outlier treatment comprises delta computation and the application of a rolling standard deviation filter. Sudden, anomalous jumps in daily usage (likely due to transient glitches or exceptional events) are replaced by the median daily delta, ensuring that longer-term trends are not skewed by momentary artifacts.

Forecasting is handled through a simple, robust approach: the system projects usage growth forward using the historical median daily increase, assuming linear growth for the next 365 days. This matches the practical needs for capacity planning where quick, understandable trends trump overfitting or overcomplex modeling.

For each dimension (site and device class), the script generates forecast graphs with matplotlib and seaborn, overlaying current usage, projections, and colored thresholds (75%, 85%, and 100% of available capacity) for visual clarity. Alongside plots, the workflow prepares a text summary containing key metrics such as projected fill dates, growth rates, and estimated time to reach critical thresholds.

Finally, everything is packaged and sent to Microsoft Teams via webhook, using Adaptive Cards for structured, readable inline dashboards. The automation ensures that these insights are always up to date and readily available to stakeholders, without manual intervention or separate reporting pipelines.

## Data Treatment and Forecasting Approach
The data treatment phase is crucial for ensuring that the usage forecasts are reliable and robust. The raw metrics retrieved from Grafana Mimir often contain noise, missing values, and occasional outliers—irregular spikes or drops that do not represent typical usage patterns but can distort trend analysis if left uncorrected.

To address this, the workflow first aligns the time series data by resampling it to a daily frequency and fills any missing data points via linear interpolation. This guarantees a continuous timeline, which is essential for consistent statistical calculations and regression modeling.

Outlier handling focuses on the daily usage increments (the difference between consecutive days). The script calculates these deltas for usage metrics and computes their rolling standard deviation to statistically identify abnormal jumps. Values exceeding this threshold are considered outliers and replaced with the median delta value calculated from the non-outlier data. This method smooths erratic fluctuations while preserving the underlying growth trend.

By repairing outliers at the delta level rather than raw usage values directly, the model maintains the cumulative consistency of the metric. The corrected deltas are then cumulatively summed to reconstruct a corrected usage time series. This approach effectively mitigates distortion from anomalous data points without discarding real growth signals.

For forecasting, the corrected historical increments are used to project future growth linearly over a defined horizon (365 days). The median daily delta serves as a stable, robust estimate of expected usage increase per day. While more sophisticated models exist, this method balances simplicity and practicality, yielding easily interpretable results and forecasts useful for capacity planning. It avoids overfitting that can occur with complex models on noisy real-world operational data.

Overall, this combination of careful interpolation, statistically informed outlier correction, and straightforward median-based linear forecasting creates a solid foundation for understanding and anticipating Ceph storage consumption trends with minimal computational complexity and high transparency.

## The code

Disclaimer: Some variables will be in portuguese.

{{< code-file file="forecast.py" lang="python" collapse="false" >}}

## Future Improvements

- **Advanced Forecasting Models:** Instead of a linear extrapolation using median deltas, incorporate time series forecasting methods such as ARIMA, Prophet, or machine learning regression models to capture seasonality, trends, and potential non-linear growth patterns more accurately;

- **Real-Time or Near Real-Time Processing:** Adapt the data collection and forecasting pipeline to support streaming or more frequent updates (e.g., hourly), enabling quicker reaction times to sudden usage changes or outages;

- **Anomaly Detection and Alerting:** Integrate automatic anomaly detection techniques beyond simple standard deviation filtering to identify unexpected spikes or degradations. Pair these with proactive alerts in Teams or other channels to notify teams immediately;

- **Capacity Thresholds as Configurable Parameters:** Allow dynamic adjustment of threshold levels (75%, 85%, 100%) via configuration files or environment variables instead of hardcoded values, improving flexibility for different environments or changing policies;

- **Improved Visualization:** Enhance graphs by including confidence intervals on forecasts, interactive dashboards using tools such as Plotly Dash or Grafana panels, and support for multiple longer-term scenarios (e.g., optimistic, pessimistic);

- **Authentication & Security Enhancements:** Secure API calls with proper authentication (OAuth tokens, certificates) and securely manage webhook URLs and proxy credentials;

- **Extensibility for Other Metrics:** Generalize the pipeline to incorporate additional Ceph health and performance indicators (e.g., latency, IOPS, recovery status) for a more comprehensive capacity and cluster health dashboard.

{{< callout type="note" title="About this historical implementation" >}}

The code above documents the implementation published in September 2025 and preserves its original logic. Environment-specific settings, integrations and limitations reflect that historical version. A new deployment would need its own review; the improvements listed above are not presented as already implemented.

The original narrative's “rolling standard deviation” described the intended treatment; the published code calculates standard deviation over the collected series, without a rolling window. Similarly, the code comment “linear regression” names an extrapolation using median increments. These clarifications do not change the original implementation.
{{< /callout >}}
