# 量化数据取数规格书 (Data Fetch Specification)

**版本**: v1.0 | **日期**: 2026-07-04

---

## 1. 数据源

### 主数据源：tushare pro

| 项目 | 说明 |
|------|------|
| 接口 | `daily` — A股日线行情 |
| 文档 | https://tushare.pro/document/2?doc_id=95 |
| 积分要求 | 120 积分（基础用户即可） |
| 调用方式 | HTTP POST（token 鉴权）或 MCP 协议 |
| 单次上限 | 约 6000 条 |

### 备选数据源

| 数据源 | 特点 | 何时使用 |
|--------|------|---------|
| akshare | 免费开源，无需 token | tushare 不可用时 |
| baostock | 免费，需注册登录 | 备选方案 |
| westock-data MCP | WorkBuddy 内置 | 快速查询（非批量取数） |

---

## 2. CSV 文件标准

### 2.1 命名规范

```
{code}_daily.csv
```
例如：`603986_daily.csv`、`001280_daily.csv`

### 2.2 字段定义

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `trade_date` | string(8) | 交易日期 YYYYMMDD | `20260703` |
| `ts_code` | string | TS 代码 | `603986.SH` |
| `open` | float | 开盘价 | `672.54` |
| `high` | float | 最高价 | `717.66` |
| `low` | float | 最低价 | `642.35` |
| `close` | float | 收盘价 | `677.77` |
| `pre_close` | float | 前收盘价 | `694.81` |
| `change` | float | 涨跌额 | `-17.04` |
| `pct_chg` | float | 涨跌幅(%) | `-2.4525` |
| `vol` | float | 成交量(手) | `623522.15` |
| `amount` | float | 成交额(千元) | `42673730.27` |

### 2.3 格式要求

- **编码**: UTF-8 with BOM (`utf-8-sig`)
- **分隔符**: 逗号 `,`
- **排序**: 按 `trade_date` **升序**（旧日期在前）
- **表头**: 第一行为字段名
- **数值精度**: float 保持原始精度，无需强制保留小数位

---

## 3. 取数流程 SOP

### Step 1: 确定目标

- 确认股票代码（6位数字）
- 确认 ts_code（代码+市场后缀 .SH/.SZ/.BJ）
- 确认取数周期（起止日期 YYYYMMDD）

### Step 2: 获取数据

```python
# Python + requests 方式
import requests
TOKEN = "<your_token>"
r = requests.post("https://api.tushare.pro", json={
    "api_name": "daily",
    "token": TOKEN,
    "params": {"ts_code": "603986.SH", "start_date": "20250704", "end_date": "20260704"},
    "fields": "ts_code,trade_date,open,high,low,close,pre_close,change,pct_chg,vol,amount"
})
data = r.json()["data"]["items"]
```

### Step 3: 数据清洗

1. 按 `trade_date` 升序排列
2. 去重（同一 `trade_date` 保留一条）
3. 检查缺失值（tushare 数据一般无缺失）
4. 注意：**新上市股票**数据起始日为上市日，不是请求的 start_date

### Step 4: 保存

- 保存到 `data/{code}_daily.csv`
- 编码：UTF-8 with BOM
- 更新 `data/manifest.json`

### Step 5: 验证

- 行数 ≥ 交易日数 × 0.95（允许少量缺日）
- 收盘价 > 0
- 最高价 ≥ 最低价
- 涨跌幅 ≈ (close - pre_close) / pre_close × 100

---

## 4. 元数据规范 (manifest.json)

```json
{
  "generated_at": "2026-07-04 09:51:00",
  "data_source": "tushare pro (MCP API)",
  "fetch_period": {"start": "2025-07-04", "end": "2026-07-04"},
  "total_rows": 624,
  "datasets": {
    "603986": {
      "file": "data/603986_daily.csv",
      "ts_code": "603986.SH",
      "rows": 242,
      "date_range": "20250704 ~ 20260703",
      "close_range": "114.24 ~ 840.00"
    }
  }
}
```

---

## 5. 如何新增股票

1. 确定股票代码 → 确定 ts_code（6位数字 + 市场后缀）
2. 在 `scripts/fetch_stock_data.py` 的 `STOCKS` 列表中添加
3. 运行脚本
4. 验证 `data/{code}_daily.csv` 和 `manifest.json`

### 常见市场后缀

| 市场 | 后缀 | 示例 |
|------|------|------|
| 上交所主板 | .SH | 600000.SH |
| 深交所主板 | .SZ | 001280.SZ |
| 深交所创业板 | .SZ | 301275.SZ |
| 科创板 | .SH | 688981.SH |
| 北交所 | .BJ | 833819.BJ |

---

## 6. 注意事项

- **token 安全**: 不要在 Git 中提交 token。使用环境变量或 MCP 配置文件。
- **频率限制**: tushare 免费用户有调用频率限制（约 200次/分钟），批量取数时加 `time.sleep(0.5)`
- **新上市股票**: 上市日之前无数据，属正常现象
- **复权**: `daily` 接口返回的是**未复权**数据，如需复权使用 `adj_factor` 接口
- **编码一致性**: 所有文件统一使用 UTF-8-BOM，避免 Excel 打开乱码
