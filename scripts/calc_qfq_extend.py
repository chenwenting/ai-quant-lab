"""
Extend qfq data by computing adj_factor ratio from existing qfq data,
then applying the same ratio to new raw daily data.
This is accurate as long as no new corporate actions occurred.
"""
import csv, os, sys, json
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

BASE = r"C:\Tina\Tina Projects\量化"
DATA = os.path.join(BASE, "data")
QFQ_DIR = os.path.join(BASE, "task04_turtle_strategy", "data")

STOCKS = {
    "603986": {"ts_code": "603986.SH", "name": "兆易创新"},
    "001280": {"ts_code": "001280.SZ", "name": "中国铀业"},
    "601318": {"ts_code": "601318.SH", "name": "中国平安"},
    "301275": {"ts_code": "301275.SZ", "name": "汉朔科技"},
    "603893": {"ts_code": "603893.SH", "name": "瑞芯微"},
}

FIELDS = ["trade_date","ts_code","open","high","low","close","pre_close","change","pct_chg","vol","amount"]

all_qfq = {}

for code, info in STOCKS.items():
    # Read existing qfq data
    qfq_path = os.path.join(QFQ_DIR, f"{code}_qfq.csv")
    raw_path = os.path.join(DATA, f"{code}_daily.csv")
    
    if not os.path.exists(qfq_path):
        print(f"SKIP {code}: no existing qfq file")
        continue
    
    qfq_rows = {}
    with open(qfq_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            qfq_rows[row['trade_date']] = row
    
    # Read raw data
    raw_rows = {}
    with open(raw_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw_rows[row['trade_date']] = row
    
    # Find last date in qfq to compute ratio
    qfq_dates = sorted(qfq_rows.keys())
    latest_qfq_date = qfq_dates[-1]
    latest_qfq = qfq_rows[latest_qfq_date]
    
    # Get corresponding raw data
    if latest_qfq_date not in raw_rows:
        print(f"WARN {code}: latest qfq date {latest_qfq_date} not in raw data")
        # Try an earlier date
        for d in reversed(qfq_dates[:-1]):
            if d in raw_rows:
                latest_qfq_date = d
                latest_qfq = qfq_rows[d]
                break
    
    raw_latest = raw_rows[latest_qfq_date]
    
    # Compute the adj_factor_ratio: qfq_price = raw_price * ratio
    # ratio = qfq_price / raw_price
    ratios = {}
    for field in ['open', 'high', 'low', 'close', 'pre_close']:
        raw_val = float(raw_latest[field])
        qfq_val = float(latest_qfq[field])
        if raw_val > 0:
            ratios[field] = qfq_val / raw_val
    
    # Average ratio
    avg_ratio = sum(ratios.values()) / len(ratios)
    print(f"{code} {info['name']}: ratio={avg_ratio:.6f} (from {latest_qfq_date})")
    
    # Generate full qfq for all raw data
    qfq_data = []
    for date_str in sorted(raw_rows.keys()):
        raw = raw_rows[date_str]
        if date_str in qfq_rows:
            qfq_data.append(qfq_rows[date_str])
        else:
            # Calculate qfq using the ratio
            qfq_row = {}
            qfq_row['trade_date'] = raw['trade_date']
            qfq_row['ts_code'] = raw['ts_code']
            qfq_row['vol'] = raw['vol']
            qfq_row['amount'] = raw['amount']
            
            o = float(raw['open']) * avg_ratio
            h = float(raw['high']) * avg_ratio
            l = float(raw['low']) * avg_ratio
            c = float(raw['close']) * avg_ratio
            pc = float(raw['pre_close']) * avg_ratio
            
            qfq_row['open'] = f"{o:.2f}"
            qfq_row['high'] = f"{h:.2f}"
            qfq_row['low'] = f"{l:.2f}"
            qfq_row['close'] = f"{c:.2f}"
            qfq_row['pre_close'] = f"{pc:.2f}"
            qfq_row['change'] = f"{c - pc:.2f}"
            if pc > 0:
                qfq_row['pct_chg'] = f"{(c/pc - 1) * 100:.4f}"
            else:
                qfq_row['pct_chg'] = "0"
            
            qfq_data.append(qfq_row)
    
    # Save qfq CSV
    with open(qfq_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(qfq_data)
    
    print(f"  -> {qfq_path}: {len(qfq_data)} rows")
    
    # Store for embedded.json
    all_qfq[code] = {
        "name": info["name"],
        "dates": [r['trade_date'] for r in qfq_data],
        "o": [float(r['open']) for r in qfq_data],
        "h": [float(r['high']) for r in qfq_data],
        "l": [float(r['low']) for r in qfq_data],
        "c": [float(r['close']) for r in qfq_data],
        "v": [float(r['vol']) for r in qfq_data],
    }

# Generate embedded.json for turtle strategy
embed_path = os.path.join(DATA, "embedded.json")
with open(embed_path, 'w', encoding='utf-8') as f:
    json.dump(all_qfq, f, ensure_ascii=False)
print(f"\nembedded.json: {embed_path} ({len(json.dumps(all_qfq))} bytes)")

# Also copy embedded.json to task04 location for backward compat
task04_embed = os.path.join(QFQ_DIR, "embedded.json")
with open(task04_embed, 'w', encoding='utf-8') as f:
    json.dump(all_qfq, f, ensure_ascii=False)
print(f"backup: {task04_embed}")
