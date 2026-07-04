#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
可复用的股票日线数据取数脚本
通过 tushare API (HTTP POST) 批量获取 A股日线数据，保存为规范 CSV

用法:
    python fetch_stock_data.py                          # 获取所有预配置股票
    python fetch_stock_data.py --code 603986            # 仅获取单只
    python fetch_stock_data.py --code 603986,001280     # 获取指定多只
    python fetch_stock_data.py --start 20240101 --end 20241231  # 自定义周期

环境变量:
    TUSHARE_TOKEN   tushare pro token (优先于 MCP 配置)
"""

import csv, json, os, sys, time
from datetime import datetime, timedelta

# ===== 配置 =====
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
TOKEN = os.environ.get("TUSHARE_TOKEN", "")
API_URL = "https://api.tushare.pro"

# 预配置股票列表（代码 → ts_code → 名称）
STOCKS = {
    "603986": {"ts_code": "603986.SH", "name": "兆易创新"},
    "001280": {"ts_code": "001280.SZ", "name": "中国铀业"},
    "301275": {"ts_code": "301275.SZ", "name": "汉朔科技"},
}

# 默认取数周期（近一年）
DEFAULT_START = "20250704"
DEFAULT_END   = "20260704"
FIELDS = "ts_code,trade_date,open,high,low,close,pre_close,change,pct_chg,vol,amount"


def fetch_daily(ts_code, start, end):
    """通过 HTTP POST 调用 tushare API"""
    payload = {
        "api_name": "daily",
        "token": TOKEN,
        "params": {"ts_code": ts_code, "start_date": start, "end_date": end},
        "fields": FIELDS,
    }
    try:
        import requests
    except ImportError:
        print("ERROR: 请安装 requests 库: pip install requests")
        sys.exit(1)

    resp = requests.post(API_URL, json=payload, timeout=30)
    data = resp.json()

    if data.get("code") != 0:
        print(f"  API Error [{ts_code}]: {data.get('msg', 'unknown')}")
        return []

    items = data["data"]["items"]
    field_list = FIELDS.split(",")
    result = []
    for item in items:
        row = {}
        for i, f in enumerate(field_list):
            row[f] = item[i]
        result.append(row)

    result.sort(key=lambda r: r["trade_date"])
    return result


def save_csv(code, data):
    """保存单只股票数据为 CSV"""
    field_list = FIELDS.split(",")
    fp = os.path.join(DATA_DIR, f"{code}_daily.csv")
    with open(fp, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=field_list, extrasaction="ignore")
        w.writeheader()
        w.writerows(data)
    return fp


def generate_manifest(datasets):
    """生成 / 更新 manifest.json"""
    mp = os.path.join(DATA_DIR, "manifest.json")
    existing = {}
    if os.path.exists(mp):
        with open(mp, encoding="utf-8-sig") as f:
            existing = json.load(f)

    manifest = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data_source": "tushare pro (HTTP API)",
        "fetch_period": {"start": DEFAULT_START, "end": DEFAULT_END},
        "datasets": {**existing.get("datasets", {}), **datasets},
    }
    manifest["total_rows"] = sum(d["rows"] for d in manifest["datasets"].values())

    with open(mp, "w", encoding="utf-8-sig") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    return mp


def main():
    import argparse

    parser = argparse.ArgumentParser(description="A股日线数据取数工具 (tushare)")
    parser.add_argument("--code", default="", help="股票代码，逗号分隔 (默认取所有预配置股票)")
    parser.add_argument("--start", default=DEFAULT_START, help="开始日期 YYYYMMDD")
    parser.add_argument("--end", default=DEFAULT_END, help="结束日期 YYYYMMDD")
    parser.add_argument("--delay", type=float, default=0.3, help="API调用间隔(秒)")
    args = parser.parse_args()

    if not TOKEN:
        print("ERROR: 未设置 TUSHARE_TOKEN 环境变量")
        print("  set TUSHARE_TOKEN=your_token    (Windows CMD)")
        print("  $env:TUSHARE_TOKEN='your_token'  (PowerShell)")
        sys.exit(1)

    # 确定要获取的股票
    if args.code:
        codes = [c.strip() for c in args.code.split(",")]
        targets = {c: STOCKS[c] for c in codes if c in STOCKS}
        if not targets:
            print(f"Unknown codes: {args.code}")
            print(f"Known: {list(STOCKS.keys())}")
            sys.exit(1)
    else:
        targets = STOCKS

    # 确保 data 目录存在
    os.makedirs(DATA_DIR, exist_ok=True)

    # 取数
    print(f"获取 {len(targets)} 只股票日线数据")
    print(f"周期: {args.start} ~ {args.end}\n")

    datasets = {}
    total_rows = 0
    for code, info in targets.items():
        ts_code = info["ts_code"]
        name = info["name"]
        print(f"  [{name} {ts_code}]", end=" ", flush=True)
        data = fetch_daily(ts_code, args.start, args.end)

        if not data:
            print("→ 无数据（可能尚未上市或停牌）")
            continue

        fp = save_csv(code, data)
        closes = [float(r["close"]) for r in data]
        rows = len(data)
        total_rows += rows

        entry = {
            "file": f"data/{code}_daily.csv",
            "ts_code": ts_code,
            "rows": rows,
            "date_range": f"{data[0]['trade_date']} ~ {data[-1]['trade_date']}",
            "close_range": f"{min(closes):.2f} ~ {max(closes):.2f}",
        }
        datasets[code] = entry
        print(f"✓ {rows}行, {entry['date_range']}, ¥{entry['close_range']}")

        # API 限速
        if args.delay > 0:
            time.sleep(args.delay)

    # 生成 manifest
    if datasets:
        mp = generate_manifest(datasets)
        print(f"\n总计 {total_rows} 行 → {mp}")
    else:
        print("\n无数据保存")


if __name__ == "__main__":
    main()
