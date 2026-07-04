# 兆易创新（603986.SH）技术指标分析实验室 — 规格说明书

> **TASK2 — 技术指标计算与信号回测**
> 版本: 1.0 | 日期: 2026-07-04

---

## 1. 项目概述

### 1.1 项目目标
基于兆易创新（603986.SH）日线价格数据，构建一个 Jupyter Notebook 技术指标实验室，聚焦 **MACD、BB（布林带）、RSI、ATR** 四项核心技术指标的计算与可视化，并通过 MACD 金叉/死叉、RSI 超买/超卖信号进行简单的信号回测评估。

### 1.2 分析对象
- **股票名称**: 兆易创新
- **股票代码**: 603986.SH
- **上市交易所**: 上海证券交易所（A股）

### 1.3 数据区间与样本量
- **时间范围**: 2025-07-01 至 2026-07-01
- **交易日数**: 243 个交易日
- **数据频率**: 日线

### 1.4 与 TASK1 的关系
- TASK1 完成了基本分析报告（统计概览、价格走势、月度收益、成交额分析）
- TASK2 在 TASK1 的数据基础上，深入技术指标层面，聚焦四项核心指标的计算、可视化与信号回测
- 两者共享同一数据源 `data/603986_daily.csv`

---

## 2. 数据源描述

### 2.1 数据文件路径
```
data/603986_daily.csv
```
Notebook 运行目录为 `task02_indicator_lab/`，因此相对路径为 `../data/603986_daily.csv`。

### 2.2 字段定义表

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| trade_date | string | 交易日期 (YYYY-MM-DD) | 2025-07-01 |
| open | float | 开盘价 | 126.00 |
| high | float | 最高价 | 126.55 |
| low | float | 最低价 | 123.51 |
| close | float | 收盘价 | 124.02 |
| pre_close | float | 前收盘价 | 126.53 |
| change | float | 涨跌额 | -2.51 |
| pct_chg | float | 涨跌幅(%) | -1.98 |
| vol | float | 成交量(手) | 142875.87 |
| amount | float | 成交额(元) | 1771946539.74 |

### 2.3 数据预处理
1. 使用 `pd.read_csv()` 读取 CSV 文件
2. 将 `trade_date` 列解析为 `datetime` 类型
3. 按日期升序排列
4. 将 `trade_date` 设为 DataFrame 索引
5. rolling 窗口前期产生的 NaN 由 pandas 自动处理，可视化时自动忽略

### 2.4 数据概览统计
在 Notebook 中通过 `df.describe()` 展示各字段的 count、mean、std、min、25%、50%、75%、max 统计值。

---

## 3. 环境要求

### 3.1 Python 版本
- Python 3.13.12
- 虚拟环境: `.venv/`（项目根目录下）

### 3.2 依赖包列表

| 包名 | 版本 | 用途 |
|------|------|------|
| pandas | 3.0.3 | 数据处理、指标计算 |
| numpy | 2.5.0 | 数值计算 |
| matplotlib | 3.11.0 | 可视化 |
| jupyter | latest | Notebook 运行环境 |

### 3.3 字体要求
- 中文字体: `SimHei`, `Microsoft YaHei`, `DejaVu Sans`（依次回退）
- 配置: `plt.rcParams['axes.unicode_minus'] = False`（解决负号显示问题）

### 3.4 显示规范

| 规范项 | 值 |
|--------|-----|
| DPI | 150 |
| 后端 | `%matplotlib inline`（Jupyter 交互式显示） |
| 网格 | `alpha=0.25, linestyle='--'` |
| 布局 | `plt.tight_layout()` |

**颜色常量（A股规范：红涨绿跌）**:

| 颜色名 | 十六进制 | 用途 |
|--------|---------|------|
| RED | #e74c3c | 涨/正/超买/金叉 |
| GREEN | #27ae60 | 跌/负/超卖/死叉 |
| BLUE | #3498db | 辅助线/BB中轨 |
| ORANGE | #f39c12 | BB上下轨 |
| PURPLE | #9b59b6 | RSI/ATR 主线 |
| DARK | #1a1a2e | 收盘价主线 |

---

## 4. 技术指标规格

### 4.1 MACD（指数平滑异同移动平均线）— 趋势类

**定义**: 利用快速与慢速指数移动平均线之间的聚合与分离状况，判断买卖时机。

**参数**: 快线=12, 慢线=26, 信号线=9

**计算公式**:
- DIF (快线) = EMA(close, 12) - EMA(close, 26)
- DEA (信号线) = EMA(DIF, 9)
- MACD 柱 = 2 × (DIF - DEA)  ← **A股惯例用 2 倍系数**

**pandas 实现**:
```python
ema12 = df['close'].ewm(span=12, adjust=False).mean()
ema26 = df['close'].ewm(span=26, adjust=False).mean()
df['DIF']  = ema12 - ema26
df['DEA']  = df['DIF'].ewm(span=9, adjust=False).mean()
df['MACD'] = 2 * (df['DIF'] - df['DEA'])
```

**计算方式**: pandas `ewm()` 手动组合（非单函数）

**可视化方案**:
- 图表类型: 双子图（折线 + 柱状图）
- 子图布局: 上子图(收盘价 + DIF + DEA 折线) : 下子图(MACD柱状图) = 3:1
- 颜色: 收盘价=DARK, DIF=BLUE, DEA=ORANGE, MACD正柱=RED, MACD负柱=GREEN
- 图表尺寸: figsize=(14, 8), DPI=150

**关键阈值/解读**:
- DIF 上穿 DEA → 金叉（买入信号）
- DIF 下穿 DEA → 死叉（卖出信号）
- DIF > 0 → 多头市场；DIF < 0 → 空头市场
- MACD 柱由负转正 → 多头动能增强

---

### 4.2 BB（布林带, Bollinger Bands）— 趋势/波动类

**定义**: 利用统计学原理，求出股价的标准差及其置信区间，反映价格的波动范围。

**参数**: 周期=20, 标准差倍数=2

**计算公式**:
- MID (中轨) = MA(close, 20)
- UPPER (上轨) = MID + 2 × std(close, 20)
- LOWER (下轨) = MID - 2 × std(close, 20)

**pandas 实现**:
```python
df['BB_MID']   = df['close'].rolling(window=20).mean()
df['BB_UPPER'] = df['BB_MID'] + 2 * df['close'].rolling(window=20).std()
df['BB_LOWER'] = df['BB_MID'] - 2 * df['close'].rolling(window=20).std()
```

**计算方式**: pandas `rolling().mean()` + `rolling().std()`

**可视化方案**:
- 图表类型: 折线图 + 填充区域
- 子图布局: 单图（收盘价 + 上中下三轨 + 上下轨间填充）
- 颜色: 收盘价=DARK, MID=BLUE, UPPER/LOWER=ORANGE(虚线), 填充 alpha=0.1
- 图表尺寸: figsize=(14, 6), DPI=150

**关键阈值/解读**:
- 价格触及上轨 → 可能超买，有回调风险
- 价格触及下轨 → 可能超卖，有反弹机会
- 带宽(UPPER-LOWER)收窄 → 市场趋于平静，预示即将变盘
- 带宽扩张 → 波动加剧，趋势确立

---

### 4.3 RSI（相对强弱指数）— 动量类

**定义**: 衡量一段时间内上涨幅度与下跌幅度的比值，反映市场买卖力量的强弱。

**参数**: 周期=14

**计算公式**（Wilder 平滑法）:
- delta = close - prev_close
- gain = max(delta, 0), loss = max(-delta, 0)
- avg_gain = Wilder 平滑（等价于 ewm alpha=1/14, adjust=False）
- avg_loss = 同上
- RS = avg_gain / avg_loss
- RSI = 100 - 100 / (1 + RS)

**pandas 实现**:
```python
delta = df['close'].diff()
gain = delta.clip(lower=0)
loss = -delta.clip(upper=0)
avg_gain = gain.ewm(alpha=1/14, adjust=False).mean()
avg_loss = loss.ewm(alpha=1/14, adjust=False).mean()
rs = avg_gain / avg_loss
df['RSI'] = 100 - 100 / (1 + rs)
```

**计算方式**: pandas `ewm()` 手动实现 Wilder 平滑

**可视化方案**:
- 图表类型: 折线图 + 参考线 + 区域填充
- 子图布局: 单图（RSI 折线 + 70/50/30 水平参考线）
- 颜色: RSI线=PURPLE, 70线=RED(虚线), 30线=GREEN(虚线), 50线=灰色
- 超买区域(>70)填充红色 alpha=0.1, 超卖区域(<30)填充绿色 alpha=0.1
- 图表尺寸: figsize=(14, 5), DPI=150

**关键阈值/解读**:
- RSI > 70 → 超买区域，可能见顶回落
- RSI < 30 → 超卖区域，可能见底反弹
- RSI = 50 → 多空平衡线
- RSI 从 30 以下上穿 30 → 买入信号
- RSI 从 70 以上下穿 70 → 卖出信号

---

### 4.4 ATR（平均真实波幅）— 波动率类

**定义**: 衡量市场波动程度的指标，反映价格的波动幅度。

**参数**: 周期=14

**计算公式**:
- TR (真实波幅) = max(
    high - low,
    |high - prev_close|,
    |low - prev_close|
  )
- ATR = MA(TR, 14)  （简单移动平均）

**pandas 实现**:
```python
tr1 = df['high'] - df['low']
tr2 = (df['high'] - df['close'].shift(1)).abs()
tr3 = (df['low']  - df['close'].shift(1)).abs()
tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
df['ATR'] = tr.rolling(window=14).mean()
```

**计算方式**: pandas `rolling().mean()` 手动组合 TR

**可视化方案**:
- 图表类型: 双子图（折线 + 折线）
- 子图布局: 上子图(收盘价) : 下子图(ATR折线 + ATR/close百分比) = 2:1
- 颜色: ATR=PURPLE, ATR/close=ORANGE(虚线)
- 图表尺寸: figsize=(14, 8), DPI=150

**关键阈值/解读**:
- ATR 上升 → 波动加剧，趋势可能加速或反转
- ATR 下降 → 市场趋于平静
- ATR/close 比率 → 衡量相对波动率，常用于止损位设定（如止损 = ATR × 2）

---

## 5. 信号回测方法

### 5.1 MACD 金叉/死叉信号定义

| 信号类型 | 定义 |
|---------|------|
| **金叉（买入）** | 当日 DIF > DEA 且 前一日 DIF ≤ DEA（DIF 从下方穿越 DEA 向上） |
| **死叉（卖出）** | 当日 DIF < DEA 且 前一日 DIF ≥ DEA（DIF 从上方穿越 DEA 向下） |

**信号检测代码**:
```python
df['DIF_prev'] = df['DIF'].shift(1)
df['DEA_prev'] = df['DEA'].shift(1)
df['MACD_golden'] = (df['DIF'] > df['DEA']) & (df['DIF_prev'] <= df['DEA_prev'])
df['MACD_death']  = (df['DIF'] < df['DEA']) & (df['DIF_prev'] >= df['DEA_prev'])
```

### 5.2 RSI 超买/超卖信号定义

| 信号类型 | 定义 |
|---------|------|
| **超卖买入** | RSI 从 30 以下上穿 30（RSI[t-1] < 30 且 RSI[t] ≥ 30） |
| **超买卖出** | RSI 从 70 以上下穿 70（RSI[t-1] > 70 且 RSI[t] ≤ 70） |

**信号检测代码**:
```python
df['RSI_prev'] = df['RSI'].shift(1)
df['RSI_oversold']  = (df['RSI_prev'] < 30) & (df['RSI'] >= 30)
df['RSI_overbought'] = (df['RSI_prev'] > 70) & (df['RSI'] <= 70)
```

### 5.3 回测评估方法

对每类信号，计算信号触发后持有 N 日的收益表现：

- **持有期**: N = 5, 10, 20 个交易日
- **收益率**（买入信号）: `(close[t+N] - close[t]) / close[t] × 100%`
- **收益率**（卖出信号）: `(close[t] - close[t+N]) / close[t] × 100%`（做空收益）
- **胜率**: 收益为正的信号数 / 总信号数 × 100%
- **平均收益**: 所有有效信号收益的均值
- **边界处理**: 若信号触发后不足 N 日数据（如最后 20 天的信号），标注为"未到期"，不纳入统计

### 5.4 汇总表格式

| 信号类型 | 信号数量 | 5日胜率 | 5日均收益 | 10日胜率 | 10日均收益 | 20日胜率 | 20日均收益 |
|---------|---------|--------|----------|---------|-----------|---------|-----------|
| MACD金叉 | — | — | — | — | — | — | — |
| MACD死叉 | — | — | — | — | — | — | — |
| RSI超卖买入 | — | — | — | — | — | — | — |
| RSI超买卖出 | — | — | — | — | — | — | — |

**可视化**:
- 在价格图上标注金叉/死叉信号点（RED ▲ 金叉 / GREEN ▼ 死叉）
- 回测汇总表用 pandas DataFrame 直接显示

---

## 6. Notebook 结构规范

### 6.1 单元格分组

Notebook 按逻辑分 7 个 Section，共约 24 个单元格：

| Section | 主题 | 单元格数 |
|---------|------|---------|
| 1 | 项目介绍与数据加载 | 6 |
| 2 | MACD 指标 | 2 |
| 3 | BB（布林带）指标 | 2 |
| 4 | RSI 指标 | 2 |
| 5 | ATR 指标 | 2 |
| 6 | 信号回测 | 7 |
| 7 | 综合分析 | 3 |

### 6.2 各单元格内容

**Section 1: 项目介绍与数据加载**
- Cell 1 [Markdown] — 标题与介绍
- Cell 2 [Code] — 环境配置与导入（pandas/numpy/matplotlib + 颜色常量 + 字体 + `%matplotlib inline`）
- Cell 3 [Markdown] — 数据加载说明
- Cell 4 [Code] — 数据加载（`pd.read_csv` + 日期解析 + 排序 + `set_index`）
- Cell 5 [Code] — 数据概览统计（`df.describe()`）
- Cell 6 [Code] — 数据概览图（收盘价 + 成交量双子图）

**Section 2: MACD**
- Cell 7 [Markdown] — MACD 指标介绍
- Cell 8 [Code] — MACD 计算 + 双子图可视化

**Section 3: BB（布林带）**
- Cell 9 [Markdown] — BB 指标介绍
- Cell 10 [Code] — BB 计算 + 可视化

**Section 4: RSI**
- Cell 11 [Markdown] — RSI 指标介绍
- Cell 12 [Code] — RSI 计算 + 可视化

**Section 5: ATR**
- Cell 13 [Markdown] — ATR 指标介绍
- Cell 14 [Code] — ATR 计算 + 双子图可视化

**Section 6: 信号回测**
- Cell 15 [Markdown] — 信号回测介绍
- Cell 16 [Code] — MACD 金叉/死叉信号检测
- Cell 17 [Code] — MACD 信号回测评估（5/10/20 日收益 + 胜率）
- Cell 18 [Code] — MACD 信号可视化（价格图标注信号点）
- Cell 19 [Code] — RSI 超买/超卖信号检测
- Cell 20 [Code] — RSI 信号回测评估 + 可视化
- Cell 21 [Code] — 回测汇总表

**Section 7: 综合分析**
- Cell 22 [Markdown] — 综合分析结论
- Cell 23 [Code] — 指标综合仪表盘（2×2 多子图）
- Cell 24 [Markdown] — 免责声明

### 6.3 可视化规范

| 规范项 | 值 |
|--------|-----|
| 后端 | `%matplotlib inline` |
| DPI | 150 |
| 字体 | SimHei, Microsoft YaHei |
| 网格 | `ax.grid(True, alpha=0.25, linestyle='--')` |
| 布局 | `plt.tight_layout()` |
| 单指标图 | figsize=(14, 6) |
| 双子图指标 | figsize=(14, 8) |
| 综合仪表盘 | figsize=(16, 12) |

**A股颜色惯例**:
- MACD 柱: 正值=RED(#e74c3c), 负值=GREEN(#27ae60)
- 信号标记: 金叉=RED ▲, 死叉=GREEN ▼

---

## 7. 交付物规范

### 7.1 .ipynb 文件
- 文件名: `indicator_lab.ipynb`
- 路径: `task02_indicator_lab/indicator_lab.ipynb`
- 要求: 所有单元格可正常执行无报错，图表中文显示正常

### 7.2 导出 HTML 文件
- 文件名: `indicator_lab.html`
- 路径: `task02_indicator_lab/indicator_lab.html`
- 导出命令:
  ```bash
  jupyter nbconvert --to html --execute indicator_lab.ipynb --output-dir ./
  ```

### 7.3 质量验收标准
1. Notebook 所有单元格正常执行无报错
2. HTML 导出成功且可独立打开查看
3. 所有图表中文显示正常（无方块乱码）
4. 四项指标计算结果正确（可通过抽样验证）
5. 回测汇总表数据合理（信号数量、胜率、收益在合理范围）
6. 代码结构清晰，注释完整
7. 颜色遵循 A 股规范（红涨绿跌）
