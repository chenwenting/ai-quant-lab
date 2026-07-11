#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Daily update orchestration script.
Step 1: Fetch daily data (raw)
Step 2: Fetch adj_factor
Step 3: Calculate qfq prices
Step 4: Build embedded.json
Step 5: Rebuild turtle-strategy HTML
Step 6: Update manifest.json
"""
import os, sys, subprocess, json, csv
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYTHON = sys.executable
SCRIPTS = os.path.join(BASE_DIR, "scripts")
DATA_DIR = os.path.join(BASE_DIR, "data")

STOCKS = {
    "603986": {"ts_code": "603986.SH", "name": "兆易创新"},
    "001280": {"ts_code": "001280.SZ", "name": "中国铀业"},
    "601318": {"ts_code": "601318.SH", "name": "中国平安"},
    "301275": {"ts_code": "301275.SZ", "name": "汉朔科技"},
    "603893": {"ts_code": "603893.SH", "name": "瑞芯微"},
}

def run(name, *args):
    cmd = [PYTHON, os.path.join(SCRIPTS, name)] + list(args)
    print(f"\n>>> {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=BASE_DIR)
    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print(result.stderr.strip(), file=sys.stderr)
    return result.returncode

def update_manifest():
    mp = os.path.join(DATA_DIR, "manifest.json")
    datasets = {}
    total = 0
    for code, info in STOCKS.items():
        fp = os.path.join(DATA_DIR, f"{code}_daily.csv")
        if not os.path.exists(fp):
            continue
        with open(fp, "r", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        if not rows:
            continue
        closes = [float(r["close"]) for r in rows]
        datasets[code] = {
            "file": f"data/{code}_daily.csv",
            "name": info["name"],
            "ts_code": info["ts_code"],
            "rows": len(rows),
            "date_range": f"{rows[0]['trade_date']} ~ {rows[-1]['trade_date']}",
            "close_range": f"{min(closes):.2f} ~ {max(closes):.2f}",
        }
        total += len(rows)

    manifest = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data_source": "tushare pro (HTTP API)",
        "fetch_period": {
            "start": "2025-07-04",
            "end": datetime.now().strftime("%Y-%m-%d"),
        },
        "datasets": datasets,
        "total_rows": total,
    }
    with open(mp, "w", encoding="utf-8-sig") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"manifest.json: {total} rows, {len(datasets)} stocks")
    return 0

def main():
    token = os.environ.get("TUSHARE_TOKEN", "")
    if not token:
        print("ERROR: TUSHARE_TOKEN not set", file=sys.stderr)
        return 1

    steps = [
        ("Step 1: Fetch daily", "fetch_stock_data.py", "--token", token),
        ("Step 2: Fetch adj_factor", "fetch_adj_factor.py", "--token", token),
        ("Step 3: Calc qfq", "calc_qfq.py"),
        ("Step 4: Build embedded", "build_embedded.py"),
        ("Step 5: Rebuild HTML", "task04_turtle_strategy/build_tool_html.py"),
    ]

    for label, script, *args in steps:
        print(f"\n{'='*50}")
        print(f"  {label}")
        print(f"{'='*50}")
        rc = run(script, *args)
        if rc != 0:
            print(f"WARNING: {label} exited with {rc}", file=sys.stderr)

    print(f"\n{'='*50}")
    print("Step 6: Update manifest")
    update_manifest()

    print(f"\n{'='*50}")
    print("Daily update complete!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
