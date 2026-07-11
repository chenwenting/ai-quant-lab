#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Calculate qfq (forward-adjusted) prices from raw daily + adj_factor."""
import csv, os, sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

STOCKS = ["603986", "001280", "601318", "301275", "603893"]
FIELDS = ["trade_date", "ts_code", "open", "high", "low", "close", "pre_close", "change", "pct_chg", "vol", "amount"]


def calc_one(code):
    daily_path = os.path.join(DATA_DIR, f"{code}_daily.csv")
    adj_path = os.path.join(DATA_DIR, f"{code}_adj.csv")

    if not os.path.exists(daily_path):
        print(f"  SKIP {code}: no daily.csv", file=sys.stderr)
        return False

    # Read adj_factor map
    adj_map = {}
    if os.path.exists(adj_path):
        with open(adj_path, "r", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                adj_map[row["trade_date"]] = float(row["adj_factor"])
        latest_factor = max(adj_map.values()) if adj_map else 1.0
    else:
        latest_factor = 1.0

    # Read daily
    rows = []
    with open(daily_path, "r", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            rows.append(row)

    # Calculate qfq
    qfq_rows = []
    for row in rows:
        td = row["trade_date"]
        adj = adj_map.get(td, latest_factor)
        ratio = adj / latest_factor

        qfq = {}
        qfq["trade_date"] = td
        qfq["ts_code"] = row["ts_code"]
        qfq["vol"] = row["vol"]
        qfq["amount"] = row["amount"]

        o = float(row["open"]) * ratio
        h = float(row["high"]) * ratio
        l = float(row["low"]) * ratio
        c = float(row["close"]) * ratio
        pc = float(row["pre_close"]) * ratio

        qfq["open"] = f"{o:.2f}"
        qfq["high"] = f"{h:.2f}"
        qfq["low"] = f"{l:.2f}"
        qfq["close"] = f"{c:.2f}"
        qfq["pre_close"] = f"{pc:.2f}"
        qfq["change"] = f"{c - pc:.2f}"
        qfq["pct_chg"] = f"{(c/pc - 1) * 100:.4f}" if pc > 0 else "0"

        qfq_rows.append(qfq)

    # Save
    qfq_path = os.path.join(DATA_DIR, f"{code}_qfq.csv")
    with open(qfq_path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(qfq_rows)

    print(f"  {code}: {len(qfq_rows)} qfq rows -> {qfq_path}")
    return True


def main():
    for code in STOCKS:
        calc_one(code)
    return 0


if __name__ == "__main__":
    sys.exit(main())
