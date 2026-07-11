#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Fetch adj_factor data for qfq calculation via Tushare HTTP API."""
import csv, json, os, sys, time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
API_URL = "https://api.tushare.pro"

STOCKS = {
    "603986": {"ts_code": "603986.SH", "name": "兆易创新"},
    "001280": {"ts_code": "001280.SZ", "name": "中国铀业"},
    "601318": {"ts_code": "601318.SH", "name": "中国平安"},
    "301275": {"ts_code": "301275.SZ", "name": "汉朔科技"},
    "603893": {"ts_code": "603893.SH", "name": "瑞芯微"},
}


def fetch_adj(ts_code, token):
    payload = {
        "api_name": "adj_factor",
        "token": token,
        "params": {"ts_code": ts_code},
        "fields": "ts_code,trade_date,adj_factor",
    }
    try:
        import requests
    except ImportError:
        return []
    resp = requests.post(API_URL, json=payload, timeout=30)
    data = resp.json()
    if data.get("code") != 0:
        print(f"  adj_factor Error [{ts_code}]: {data.get('msg')}", file=sys.stderr)
        return []
    items = data["data"]["items"]
    result = []
    for item in items:
        result.append({"trade_date": item[1], "adj_factor": float(item[2])})
    result.sort(key=lambda r: r["trade_date"])
    return result


def save_adj(code, data):
    fp = os.path.join(DATA_DIR, f"{code}_adj.csv")
    with open(fp, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["trade_date", "adj_factor"])
        w.writeheader()
        w.writerows(data)
    return fp


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", default=os.environ.get("TUSHARE_TOKEN", ""))
    parser.add_argument("--delay", type=float, default=61.0, help="API间隔秒 (adj_factor限频)")
    args = parser.parse_args()

    if not args.token:
        print("ERROR: set TUSHARE_TOKEN", file=sys.stderr)
        sys.exit(1)

    os.makedirs(DATA_DIR, exist_ok=True)

    for code, info in STOCKS.items():
        print(f"  adj_factor: [{info['name']}]", end=" ", flush=True)
        data = fetch_adj(info["ts_code"], args.token)
        if data:
            fp = save_adj(code, data)
            print(f"{len(data)} rows, latest {data[-1]['adj_factor']:.4f}")
        else:
            print("no data")
        time.sleep(args.delay)

    return 0


if __name__ == "__main__":
    sys.exit(main())
