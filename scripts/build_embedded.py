#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Build embedded.json from qfq CSV files."""
import csv, json, os, sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

STOCKS = {
    "603986": "兆易创新", "001280": "中国铀业", "601318": "中国平安",
    "301275": "汉朔科技", "603893": "瑞芯微",
}


def main():
    all_data = {}
    for code, name in STOCKS.items():
        fp = os.path.join(DATA_DIR, f"{code}_qfq.csv")
        if not os.path.exists(fp):
            print(f"  SKIP {code}: no qfq.csv", file=sys.stderr)
            continue
        with open(fp, "r", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        all_data[code] = {
            "name": name,
            "dates": [r["trade_date"] for r in rows],
            "o": [float(r["open"]) for r in rows],
            "h": [float(r["high"]) for r in rows],
            "l": [float(r["low"]) for r in rows],
            "c": [float(r["close"]) for r in rows],
            "v": [float(r["vol"]) for r in rows],
        }

    out_path = os.path.join(DATA_DIR, "embedded.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False)

    total = sum(len(v["dates"]) for v in all_data.values())
    print(f"embedded.json: {len(json.dumps(all_data))} bytes, {total} rows, {len(all_data)} stocks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
