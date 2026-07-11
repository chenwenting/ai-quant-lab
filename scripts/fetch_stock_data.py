#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Updated: fetch stock daily data via Tushare HTTP API.
Supports --token for CI, 5 stocks by default.
"""
import csv, json, os, sys, time
from datetime import datetime, timedelta

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

DEFAULT_START = "20250704"
FIELDS = "ts_code,trade_date,open,high,low,close,pre_close,change,pct_chg,vol,amount"


def fetch_daily(ts_code, start, end, token):
    payload = {
        "api_name": "daily",
        "token": token,
        "params": {"ts_code": ts_code, "start_date": start, "end_date": end},
        "fields": FIELDS,
    }
    try:
        import requests
    except ImportError:
        print("ERROR: pip install requests", file=sys.stderr)
        return []

    for attempt in range(3):
        try:
            resp = requests.post(API_URL, json=payload, timeout=30)
            data = resp.json()
            break
        except Exception as e:
            if attempt < 2:
                print(f"  retry {attempt+1}: {e}", file=sys.stderr)
                time.sleep(5)
            else:
                raise

    if data.get("code") != 0:
        msg = data.get("msg", "unknown")
        print(f"  API Error [{ts_code}]: {msg}", file=sys.stderr)
        return []

    items = data["data"]["items"]
    field_list = FIELDS.split(",")
    result = []
    for item in items:
        row = dict(zip(field_list, item))
        result.append(row)

    result.sort(key=lambda r: r["trade_date"])
    return result


def merge_csv(code, new_data):
    """Merge new data into existing CSV, deduplicate by trade_date."""
    fp = os.path.join(DATA_DIR, f"{code}_daily.csv")
    existing = {}
    extra_order = []
    if os.path.exists(fp):
        with open(fp, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing[row["trade_date"]] = row
                extra_order.append(row["trade_date"])

    added = 0
    for row in new_data:
        if row["trade_date"] not in existing:
            existing[row["trade_date"]] = row
            extra_order.append(row["trade_date"])
            added += 1

    extra_order = sorted(set(extra_order))
    field_list = FIELDS.split(",")
    with open(fp, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=field_list, extrasaction="ignore")
        w.writeheader()
        for d in extra_order:
            w.writerow(existing[d])
    return fp, added, extra_order[0], extra_order[-1]


def main():
    import argparse
    parser = argparse.ArgumentParser(description="A股日线数据取数")
    parser.add_argument("--token", default=os.environ.get("TUSHARE_TOKEN", ""), help="Tushare token")
    parser.add_argument("--code", default="", help="股票代码逗号分隔")
    parser.add_argument("--start", default=DEFAULT_START, help="开始日期")
    parser.add_argument("--end", default=datetime.now().strftime("%Y%m%d"), help="结束日期")
    parser.add_argument("--delay", type=float, default=0.3, help="API间隔")
    args = parser.parse_args()

    if not args.token:
        print("ERROR: set TUSHARE_TOKEN or --token", file=sys.stderr)
        sys.exit(1)

    if args.code:
        codes = [c.strip() for c in args.code.split(",")]
        targets = {c: STOCKS[c] for c in codes if c in STOCKS}
    else:
        targets = STOCKS

    os.makedirs(DATA_DIR, exist_ok=True)

    print(f"Fetching {len(targets)} stocks: {args.start} ~ {args.end}")
    total_added = 0
    for code, info in targets.items():
        print(f"  [{info['name']}]", end=" ", flush=True)
        data = fetch_daily(info["ts_code"], args.start, args.end, args.token)
        if not data:
            print("no data")
            continue
        fp, added, d0, d1 = merge_csv(code, data)
        total_added += added
        print(f"+{added} rows, {d0}~{d1}")
        time.sleep(args.delay)

    print(f"Done: {total_added} new rows total")
    return 0 if total_added > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
