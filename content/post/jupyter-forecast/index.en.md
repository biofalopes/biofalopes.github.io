+++
slug = "automating-ceph-storage-forecasting-with-grafana-mimir"
lastmod = "2026-10-26"
title = "Automating Ceph Storage Forecasting with Grafana Mimir"
description = "A Ceph capacity-planning workflow with a tested median-growth baseline, explicit data-quality checks, and optional Mimir and Teams integration."
date =  "2025-09-17"
draft = false
toc = true
categories = ["python", "grafana" ]
tags = ["python", "grafana" ]
image = "forecast.png"
author = "Fabio M. Lopes"
+++

## Operational context

At SERPRO, I built a Python workflow to collect Ceph capacity metrics from Grafana Mimir and make capacity planning easier for the team. The original work started in a Jupyter Notebook, with forecasting logic discussed with a colleague, and later became a scheduled report with charts and summaries delivered to Microsoft Teams.

**Technical revision — October 2026:** the earlier implementation compared daily changes to an uncentered standard deviation, which could erase constant positive growth. It also described a rolling calculation that the code did not perform. This revision replaces that filter with an explicit median-delta baseline, preserves observed history, and covers zero growth, declining usage, missing data and thresholds already exceeded. This is a revised example, not evidence that the operational deployment was upgraded or that forecast accuracy improved.

## What the baseline does

For each site and device class, the input is one observation per UTC day: raw used bytes and raw capacity bytes. The median of consecutive daily usage changes estimates growth. Starting at the **last actual observation**, day 1 adds one daily increment and day N adds N increments. This is linear extrapolation using a median slope, not fitted linear regression.

The implementation preserves the original measurements. It does not label a sudden change as erroneous or silently replace it with zero. A median reduces the influence of isolated extreme deltas, but cannot determine whether a jump is a collection fault, rebalance, deletion or a real workload change. Review those events and the selected time window before interpreting the result.

The default live window is 30 complete daily observations. Empty data, non-finite values, missing days, unmatched usage/capacity dimensions, and capacity changes within the window stop report generation. There is no interpolation or extrapolation of missing observations. After expansion, select a stable post-change window rather than silently combining two capacity regimes.

The threshold result distinguishes four cases:

| Status | Meaning |
|---|---|
| `already_reached` | Observed usage is already at or above the threshold; remaining days is zero. |
| `not_reached_nonpositive_growth` | Below the threshold, with zero or negative estimated growth; no future crossing is projected. |
| `within_horizon` | The daily projection crosses within the configured horizon. |
| `beyond_horizon` | Positive growth, but no crossing within the horizon; no distant date is fabricated. |

Negative-growth projections are floored at zero. Projections are not capped at capacity, so exceeding 100% indicates that the assumed trajectory is infeasible without action. The example threshold of 75% is a planning choice, not a universal Ceph full ratio. Raw bytes also differ from usable application capacity because replication, erasure coding and failure-domain headroom matter.

## Run the example locally

Download {{< resource-link file="forecast.py" >}} and {{< resource-link file="sample.csv" >}} into the same directory. The sample contains **synthetic data** growing by 10 TiB/day; it contains no operational metrics. Python 3.10+ is sufficient for the core workflow.

```bash
python forecast.py --csv sample.csv --horizon 90 --output forecast-output
```

The command writes JSON, forecast CSV and an Adaptive Card payload. It does not send a message. For PNG charts, install matplotlib in a virtual environment and add `--plot`:

```bash
python -m venv .venv
# Activate .venv using the command for your operating system.
python -m pip install matplotlib
python forecast.py --csv sample.csv --horizon 90 --plot
```

The original cover image illustrates the earlier report, not validation of the revised model.

## Collect from Mimir

Set `MIMIR_QUERY_URL` to the full HTTPS query-range endpoint, `MIMIR_TENANT_ID` to the tenant permitted by your authentication proxy, and optionally `MIMIR_BEARER_TOKEN` to its access token. `METRICS_CA_FILE` can point to your trusted internal CA bundle. Otherwise, the system trust store is used. Certificate verification stays enabled; HTTP requests have a timeout and do not follow redirects.

The example PromQL assumes `site` and `ceph_daemon` identify an OSD uniquely and that `ceph_osd_metadata` supplies `device_class`. Adapt the labels and aggregation if your scrape setup includes multiple clusters per site. Tenant identification is not authentication; enforce authorization at the gateway. The [Prometheus HTTP API](https://prometheus.io/docs/prometheus/latest/querying/api/) documents range-query responses.

```bash
python forecast.py --history-days 30 --horizon 365 --threshold 0.75
```

Live collection ends at the previous day's UTC midnight sample. It requires complete, matching series and stops on query warnings or collection errors. The scheduler should alert on a failed run and the report's `as_of` date should remain visible.

## Deliver a summary to Teams

The original report used an Office webhook. For a new integration, configure a Teams Workflow that receives an HTTP request and posts an Adaptive Card, and match its authentication and payload contract to your tenant. Microsoft documents the [webhook and Workflow options](https://learn.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook).

The example writes `teams-payload.json` for inspection. It supports a webhook URL authorized by possession of that URL; an endpoint requiring OAuth needs a suitable authentication adapter. Only send after configuring the receiver and protecting its URL as a secret:

```bash
python forecast.py --csv sample.csv --send-teams
```

Set `TEAMS_WEBHOOK_URL` through a secret store or protected environment variable. The example sends text summaries; PNG files remain local. Publishing charts requires an approved image-hosting/authentication design, not embedding internal data into a public URL. Mimir and Teams calls were not exercised against production services during this revision.

## Shared implementation

Both language versions render the same source file, so the code can be tested and changed in one place.

{{< code-file file="forecast.py" lang="python" >}}

## Validation and limits

Regression tests cover constant growth, a single spike, zero/negative growth, zero-day threshold crossings, the forecast boundary, gaps, invalid metrics and changed capacity. A synthetic chronological holdout checks the calculation without using future observations in the training window. These tests verify behavior, not accuracy on production data.

Before using the projection for procurement, backtest on historical windows, compare against a no-growth baseline, measure errors at the relevant lead times and review structural changes. There is no confidence interval or demonstrated annual forecast accuracy here. Keep uncertainty and procurement lead time visible alongside the projected date.
