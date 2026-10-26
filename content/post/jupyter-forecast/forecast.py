"""Daily Ceph capacity baseline. Standard library; matplotlib is optional."""

import argparse
import csv
import json
import math
import os
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from statistics import median
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, build_opener, HTTPSHandler, HTTPRedirectHandler
import ssl

TIB = 1024 ** 4


def project(samples, horizon=365, threshold=0.75):
    """Samples: ordered (date, used_bytes, capacity_bytes), one per UTC day."""
    if not isinstance(horizon, int) or isinstance(horizon, bool) or not 1 <= horizon <= 3650:
        raise ValueError("horizon must be an integer between 1 and 3650")
    if not math.isfinite(threshold) or not 0 < threshold <= 1:
        raise ValueError("threshold must be in (0, 1]")
    if len(samples) < 2:
        raise ValueError("At least two daily observations are required")
    for i, (day, used, capacity) in enumerate(samples):
        if not all(math.isfinite(v) for v in (used, capacity)):
            raise ValueError("Non-finite metric")
        if used < 0 or capacity <= 0 or used > capacity:
            raise ValueError("Invalid used/capacity pair")
        if i and day - samples[i - 1][0] != timedelta(days=1):
            raise ValueError("Missing, duplicate or unordered daily observations")
    capacity = samples[-1][2]
    if any(not math.isclose(row[2], capacity, rel_tol=1e-6) for row in samples):
        raise ValueError("Capacity changed: select a stable window and review the event")

    # Do not rewrite history or replace real changes with zero.
    deltas = [samples[i][1] - samples[i - 1][1] for i in range(1, len(samples))]
    daily_growth = median(deltas)
    last_day, last_used, _ = samples[-1]
    limit = capacity * threshold
    points = [
        (last_day + timedelta(days=step), max(0.0, last_used + step * daily_growth))
        for step in range(1, horizon + 1)
    ]
    if last_used >= limit:
        status, days_to_limit = "already_reached", 0
    elif daily_growth <= 0:
        status, days_to_limit = "not_reached_nonpositive_growth", None
    elif points[-1][1] < limit:
        status, days_to_limit = "beyond_horizon", None
    else:
        status = "within_horizon"
        days_to_limit = math.ceil((limit - last_used) / daily_growth)
    return {
        "as_of": last_day.isoformat(),
        "used_bytes": last_used,
        "capacity_bytes": capacity,
        "threshold_fraction": threshold,
        "daily_growth_bytes": daily_growth,
        "horizon_days": horizon,
        "status": status,
        "days_to_limit": days_to_limit,
        "limit_date": (last_day + timedelta(days=days_to_limit)).isoformat()
        if days_to_limit is not None else None,
        "forecast": [{"date": d.isoformat(), "used_bytes": u} for d, u in points],
    }


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Do not forward credentials to a redirected destination.
        return None


def request_bytes(url, payload=None, headers=None):
    if urlsplit(url).scheme != "https":
        raise ValueError("Configure an HTTPS endpoint")
    context = ssl.create_default_context(cafile=os.environ.get("METRICS_CA_FILE"))
    opener = build_opener(HTTPSHandler(context=context), NoRedirect())
    request_headers = dict(headers or {})
    data = None
    if payload is not None:
        data = json.dumps(payload, allow_nan=False).encode("utf-8")
        request_headers["Content-Type"] = "application/json"
    request = Request(url, data=data, headers=request_headers)
    with opener.open(request, timeout=30) as response:
        return response.read()


def read_matrix(payload):
    if payload.get("status") != "success" or payload.get("warnings"):
        raise ValueError("Mimir returned an error or a warning; inspect the query before forecasting")
    data = payload.get("data", {})
    if data.get("resultType") != "matrix" or not data.get("result"):
        raise ValueError("Mimir returned no usable range series")
    result = {}
    for series in data["result"]:
        labels = series["metric"]
        key = (labels["site"], labels["device_class"])
        if key in result:
            raise ValueError("Query must return one series per site/device_class")
        values = {}
        for timestamp, value in series["values"]:
            day = datetime.fromtimestamp(float(timestamp), timezone.utc).date()
            if day in values:
                raise ValueError("Duplicate daily sample")
            values[day] = float(value)
        result[key] = values
    return result


def collect(history_days):
    if history_days < 2:
        raise ValueError("history_days must be at least 2")
    endpoint = os.environ["MIMIR_QUERY_URL"]  # Full /prometheus/api/v1/query_range URL.
    headers = {"X-Scope-OrgID": os.environ["MIMIR_TENANT_ID"]}
    token = os.environ.get("MIMIR_BEARER_TOKEN")
    if token:
        headers["Authorization"] = "Bearer " + token
    end = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
    start = end - timedelta(days=history_days - 1)
    matrices = {}
    for name, metric in (("used", "ceph_osd_stat_bytes_used"), ("capacity", "ceph_osd_stat_bytes")):
        query = (
            f"sum by (site, device_class) ({metric} + on(site, ceph_daemon) "
            "group_left(device_class) (0 * ceph_osd_metadata))"
        )
        params = urlencode({"query": query, "start": start.isoformat(), "end": end.isoformat(), "step": "1d"})
        matrices[name] = read_matrix(json.loads(request_bytes(endpoint + "?" + params, headers=headers)))
    if matrices["used"].keys() != matrices["capacity"].keys():
        raise ValueError("Usage and capacity dimensions differ")
    expected_days = {start.date() + timedelta(days=i) for i in range(history_days)}
    groups = {}
    for key, usage in matrices["used"].items():
        capacity = matrices["capacity"][key]
        if set(usage) != expected_days or set(capacity) != expected_days:
            raise ValueError("Missing or stale observations; repair the collection window")
        groups[key] = [(day, usage[day], capacity[day]) for day in sorted(expected_days)]
    return groups


def read_csv(path):
    groups = {}
    with open(path, encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            key = (row["site"], row["device_class"])
            groups.setdefault(key, []).append((date.fromisoformat(row["date"]), float(row["used_bytes"]), float(row["capacity_bytes"])))
    if not groups:
        raise ValueError("CSV contains no observations")
    return {key: sorted(rows) for key, rows in groups.items()}


def save_plot(samples, result, path, label):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot([s[0] for s in samples], [s[1] / TIB for s in samples], label="Observed")
    ax.plot([samples[-1][0]] + [date.fromisoformat(p["date"]) for p in result["forecast"]],
            [samples[-1][1] / TIB] + [p["used_bytes"] / TIB for p in result["forecast"]],
            "--", label="Median-delta baseline")
    ax.axhline(result["capacity_bytes"] * result["threshold_fraction"] / TIB,
               color="darkorange", label=f"Threshold {result['threshold_fraction']:.0%}")
    ax.axhline(result["capacity_bytes"] / TIB, color="firebrick", label="Raw capacity")
    ax.set(title=label, ylabel="Raw used TiB", xlabel="Date (UTC)")
    ax.legend()
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def teams_payload(reports):
    body = [{"type": "TextBlock", "text": "Ceph capacity baseline", "weight": "Bolder"}]
    for row in reports:
        text = (f"{row['site']} / {row['device_class']} | as of {row['as_of']} | "
                f"{row['daily_growth_bytes'] / TIB:.3f} TiB/day | "
                f"{row['status']} | threshold date: {row['limit_date'] or 'not projected'}")
        body.append({"type": "TextBlock", "text": text, "wrap": True})
    return {"type": "message", "attachments": [{"contentType": "application/vnd.microsoft.card.adaptive",
            "contentUrl": None, "content": {"type": "AdaptiveCard", "version": "1.2", "body": body}}]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, help="Offline daily observations")
    parser.add_argument("--history-days", type=int, default=30)
    parser.add_argument("--horizon", type=int, default=365)
    parser.add_argument("--threshold", type=float, default=0.75)
    parser.add_argument("--output", type=Path, default=Path("forecast-output"))
    parser.add_argument("--plot", action="store_true", help="Requires matplotlib")
    parser.add_argument("--send-teams", action="store_true", help="Explicitly send to TEAMS_WEBHOOK_URL")
    args = parser.parse_args()
    groups = read_csv(args.csv) if args.csv else collect(args.history_days)
    # Validate every dimension before writing or sending any report.
    reports = [{"site": key[0], "device_class": key[1], **project(rows, args.horizon, args.threshold)}
               for key, rows in sorted(groups.items())]
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "forecast.json").write_text(json.dumps(reports, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    with (args.output / "forecast.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["site", "device_class", "date", "used_bytes"])
        for row in reports:
            writer.writerows((row["site"], row["device_class"], point["date"], point["used_bytes"]) for point in row["forecast"])
    if args.plot:
        for index, row in enumerate(reports):
            save_plot(groups[(row["site"], row["device_class"])], row, args.output / f"forecast-{index}.png", f"{row['site']} / {row['device_class']}")
    payload = teams_payload(reports)
    (args.output / "teams-payload.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    if args.send_teams:
        request_bytes(os.environ["TEAMS_WEBHOOK_URL"], payload=payload)
    print(f"Wrote {len(reports)} forecast(s) to {args.output}")


if __name__ == "__main__":
    main()
