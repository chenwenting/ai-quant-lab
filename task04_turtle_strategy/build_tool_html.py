#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Build turtle-strategy interactive HTML tool with embedded data"""
import json, os

BASE = os.path.dirname(os.path.abspath(__file__))
EMBEDDED = os.path.join(os.path.dirname(BASE), 'data', 'embedded.json')
OUTPUT = os.path.join(os.path.dirname(BASE), 'strategies', 'turtle-strategy', 'index.html')

with open(EMBEDDED, 'r', encoding='utf-8') as f:
    embed_json = f.read()

html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>海龟交易系统 — AI Quant Lab</title>
<script src="https://cdn.plot.ly/plotly-2.35.0.min.js"></script>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:-apple-system,"Microsoft YaHei",sans-serif; background:#f5f6f8; display:flex; min-height:100vh; }}
:root {{ --s1:#4fc3f7; --s2:#ab47bc; --up:#ef5350; --down:#26a69a; }}

.nav {{ position:fixed; top:0; left:0; right:0; height:44px; background:linear-gradient(135deg,#1a1a2e,#0f3460); color:#fff; display:flex; align-items:center; padding:0 16px; z-index:100; gap:16px; font-size:13px; }}
.nav a {{ color:#4361ee; text-decoration:none; font-weight:600; }}
.nav .info {{ flex:1; text-align:center; }}
.nav .info .t {{ font-size:14px; font-weight:600; }}
.nav .info .s {{ font-size:11px; opacity:0.7; }}

#sidebar {{ width:320px; min-width:320px; background:#fff; border-right:1px solid #e0e0e0; overflow-y:auto; padding:54px 16px 16px; display:flex; flex-direction:column; gap:10px; }}
#main {{ flex:1; padding:54px 16px 16px; overflow-y:auto; }}

.section {{ border:1px solid #e8eaed; border-radius:8px; padding:12px; background:#fafafa; }}
.section h4 {{ font-size:13px; margin-bottom:8px; color:#333; }}
.section label {{ font-size:12px; color:#666; display:flex; justify-content:space-between; margin-bottom:3px; }}
.section label span {{ font-weight:600; color:#333; }}
.section input[type=range] {{ width:100%; accent-color:#4361ee; }}
.section select {{ width:100%; padding:6px; border:1px solid #ddd; border-radius:6px; font-size:13px; }}

.stock-info {{ font-size:12px; color:#666; margin-top:4px; }}

.metrics {{ display:grid; grid-template-columns:repeat(4,1fr); gap:8px; margin-bottom:12px; }}
.metrics .row-label {{ grid-column:1/-1; font-size:12px; font-weight:600; padding:4px 8px; border-radius:4px; text-align:center; }}
.metrics .row-label.s1 {{ background:#e3f2fd; color:#1565c0; }}
.metrics .row-label.s2 {{ background:#f3e5f5; color:#7b1fa2; }}
.metric-card {{ background:#fff; border:1px solid #e8eaed; border-radius:8px; padding:10px 8px; text-align:center; }}
.metric-card .label {{ font-size:11px; color:#999; margin-bottom:3px; }}
.metric-card .value {{ font-size:16px; font-weight:700; }}
.metric-card.s1 .value {{ color:#1565c0; }}
.metric-card.s2 .value {{ color:#7b1fa2; }}

.chart {{ background:#fff; border:1px solid #e8eaed; border-radius:8px; margin-bottom:10px; overflow:hidden; }}

.presets {{ display:flex; gap:6px; }}
.presets button {{ flex:1; padding:6px; border:1px solid #4361ee; background:#fff; color:#4361ee; border-radius:6px; cursor:pointer; font-size:12px; font-weight:600; }}
.presets button:hover {{ background:#4361ee; color:#fff; }}

.trade-log {{ background:#fff; border:1px solid #e8eaed; border-radius:8px; padding:12px; margin-top:10px; }}
.trade-log h4 {{ font-size:13px; margin-bottom:8px; }}
.trade-log table {{ width:100%; border-collapse:collapse; font-size:11px; }}
.trade-log th, .trade-log td {{ border-bottom:1px solid #eee; padding:5px 6px; text-align:right; }}
.trade-log th {{ background:#f5f6f8; font-weight:600; text-align:center; font-size:11px; }}
.trade-log td:nth-child(1), .trade-log td:nth-child(2) {{ text-align:center; }}
.trade-log .entry {{ color:var(--up); }}
.trade-log .exit {{ color:var(--down); }}
.trade-log .stop {{ color:#f44336; }}
.trade-log .add {{ color:#ff9800; }}

.toggle-row {{ display:flex; gap:6px; margin-bottom:8px; }}
.toggle-row button {{ padding:4px 12px; border:1px solid #ddd; border-radius:6px; background:#fff; cursor:pointer; font-size:12px; }}
.toggle-row button.active {{ background:#4361ee; color:#fff; border-color:#4361ee; }}

@media (max-width:900px) {{ body {{ flex-direction:column; }} #sidebar {{ width:100%; min-width:auto; max-height:50vh; }} }}
</style>
</head>
<body>

<div class="nav">
  <a href="../../index.html"> AI Quant Lab</a>
  <div class="info">
    <div class="t" id="navTitle">海龟交易系统 Turtle Trading System</div>
    <div class="s" id="navSub"></div>
  </div>
</div>

<div id="sidebar">
  <div class="section">
    <h4> 股票选择</h4>
    <select id="stockSelect"></select>
    <div class="stock-info" id="stockInfo"></div>
  </div>

  <div class="section">
    <h4> 系统参数</h4>
    <label><span>S1 入场周期</span> <span id="s1eVal">20</span></label>
    <input type="range" id="s1Entry" min="10" max="60" value="20" step="1">
    <label><span>S1 离场周期</span> <span id="s1xVal">10</span></label>
    <input type="range" id="s1Exit" min="5" max="30" value="10" step="1">
    <label><span>S2 入场周期</span> <span id="s2eVal">55</span></label>
    <input type="range" id="s2Entry" min="20" max="120" value="55" step="1">
    <label><span>S2 离场周期</span> <span id="s2xVal">20</span></label>
    <input type="range" id="s2Exit" min="10" max="60" value="20" step="1">
    <label><span>ATR 周期</span> <span id="atrpVal">20</span></label>
    <input type="range" id="atrPeriod" min="10" max="50" value="20" step="1">
  </div>

  <div class="section">
    <h4> 风险参数</h4>
    <label><span>止损 ATR 倍数</span> <span id="stopmVal">2.0</span></label>
    <input type="range" id="stopMult" min="10" max="40" value="20" step="1">
    <label><span>加仓间隔 (ATR)</span> <span id="addiVal">0.5</span></label>
    <input type="range" id="addInterval" min="2" max="20" value="5" step="1">
    <label><span>最大加仓单位</span> <span id="maxuVal">4</span></label>
    <input type="range" id="maxUnits" min="1" max="8" value="4" step="1">
    <label><span>单笔风险比例</span> <span id="riskVal">2.0%</span></label>
    <input type="range" id="riskPct" min="5" max="50" value="20" step="1">
  </div>

  <div class="section">
    <h4> 成本参数</h4>
    <label><span>初始资金 (万)</span> <span id="capVal">100</span></label>
    <input type="range" id="capital" min="10" max="500" value="100" step="5">
    <label>手续费率</label>
    <select id="feeRate">
      <option value="0.0001">万一 (0.01%)</option>
      <option value="0.0003" selected>万三 (0.03%)</option>
      <option value="0.0005">万五 (0.05%)</option>
    </select>
    <label>滑点</label>
    <select id="slippage">
      <option value="0">无滑点</option>
      <option value="0.0005">0.05%</option>
      <option value="0.001" selected>0.1%</option>
      <option value="0.002">0.2%</option>
    </select>
  </div>

  <div class="section">
    <h4> 预设方案</h4>
    <div class="presets">
      <button onclick="applyPreset('classic')"> 经典海龟</button>
      <button onclick="applyPreset('aggressive')"> 激进短线</button>
      <button onclick="applyPreset('conservative')"> 保守长线</button>
    </div>
  </div>
</div>

<div id="main">
  <div id="metricsPanel"></div>
  <div class="chart" id="chartKline" style="min-height:420px"></div>
  <div class="chart" id="chartEquity" style="min-height:280px"></div>
  <div class="chart" id="chartDrawdown" style="min-height:240px"></div>
  <div class="trade-log" id="tradeLogSection">
    <h4> 交易记录</h4>
    <div class="toggle-row">
      <button id="btnS1" class="active" onclick="switchTradeLog('S1')">System 1</button>
      <button id="btnS2" onclick="switchTradeLog('S2')">System 2</button>
    </div>
    <div id="tradeLogTable"></div>
  </div>
</div>

<script type="application/json" id="stockData">
{embed_json}
</script>

<script>
// ====== DATA ======
const STOCK_DATA = JSON.parse(document.getElementById('stockData').textContent);
const STOCK_NAMES = {{}};
for (const [k,v] of Object.entries(STOCK_DATA)) STOCK_NAMES[k] = v.name;

let currentCode = '603986';
let debounceTimer = null;
let resultCache = null;
let tradeLogFilter = 'S1';

// ====== DONCHIAN CHANNEL ======
function calcDonchian(high, low, entryN, exitN) {{
  const n = high.length;
  const upper = new Array(n).fill(null);
  const lower = new Array(n).fill(null);
  for (let i = entryN + 1; i < n; i++) {{
    let mx = -Infinity; for (let j = i-entryN; j < i; j++) if (high[j] > mx) mx = high[j];
    upper[i] = mx;
  }}
  for (let i = exitN + 1; i < n; i++) {{
    let mn = Infinity; for (let j = i-exitN; j < i; j++) if (low[j] < mn) mn = low[j];
    lower[i] = mn;
  }}
  return {{ upper, lower }};
}}

// ====== ATR ======
function calcATR(high, low, close, period = 20) {{
  const n = high.length;
  const tr = new Array(n).fill(0); tr[0] = high[0] - low[0];
  for (let i = 1; i < n; i++)
    tr[i] = Math.max(high[i]-low[i], Math.abs(high[i]-close[i-1]), Math.abs(low[i]-close[i-1]));
  const atr = new Array(n).fill(null);
  let sum = 0; for (let i = 0; i < period; i++) sum += tr[i];
  atr[period-1] = sum / period;
  for (let i = period; i < n; i++) atr[i] = (atr[i-1]*(period-1)+tr[i])/period;
  return atr;
}}

// ====== BACKTEST ENGINE ======
function runBacktest(data, params) {{
  const {{ o, h, l, c }} = data;
  const {{ entryN, exitN, atrPeriod, stopMult, addInterval, maxUnits, riskPct, fee, slip, capital }} = params;
  const n = c.length;
  const dc = calcDonchian(h, l, entryN, exitN);
  const atr = calcATR(h, l, c, atrPeriod);
  let cash = capital, shares = 0, units = [];
  let stopPrice = null, pendingEntry = null, pendingExit = null, inTrade = false;
  const equity = new Array(n);
  const trades = [];
  const signals = new Array(n).fill(0);

  for (let i = 0; i < n; i++) {{
    const price = c[i], todayAtr = atr[i];

    if (pendingEntry !== null && !inTrade) {{
      const ep = o[i] * (1 + slip);
      const us = pendingEntry;
      const cost = us * ep * (1 + fee);
      if (cost <= cash) {{
        shares = us; cash -= cost; inTrade = true;
        stopPrice = ep - stopMult * todayAtr;
        units.push({{price:ep,shares:us,atr:todayAtr,cost}});
        trades.push({{date:data.dates[i],type:'ENTRY',price:Math.round(ep*100)/100,shares:us,amount:Math.round(cost),fee:Math.round(us*ep*fee),units:units.length,stop:stopPrice?Math.round(stopPrice*100)/100:null,pnl:null}});
        signals[i] = 1;
      }}
      pendingEntry = null;
    }}

    if (pendingExit !== null && inTrade) {{
      const xp = o[i] * (1 - slip);
      const xa = shares * xp * (1 - fee);
      const tc = units.reduce((s,u)=>s+u.cost,0);
      trades.push({{date:data.dates[i],type:'EXIT',price:Math.round(xp*100)/100,shares,amount:Math.round(xa),fee:Math.round(shares*xp*fee),units:units.length,stop:null,pnl:Math.round(xa-tc)}});
      cash += xa; shares = 0; units = []; stopPrice = null; inTrade = false;
      signals[i] = 3;
      pendingExit = null;
    }}

    if (inTrade && stopPrice !== null && l[i] <= stopPrice) {{
      const xp = stopPrice * (1 - slip);
      const xa = shares * xp * (1 - fee);
      const tc = units.reduce((s,u)=>s+u.cost,0);
      trades.push({{date:data.dates[i],type:'STOP_LOSS',price:Math.round(xp*100)/100,shares,amount:Math.round(xa),fee:Math.round(shares*xp*fee),units:units.length,stop:null,pnl:Math.round(xa-tc)}});
      cash += xa; shares = 0; units = []; stopPrice = null; inTrade = false;
      pendingEntry = null; pendingExit = null;
      signals[i] = 2;
    }}

    if (inTrade && dc.lower[i] !== null && price < dc.lower[i]) pendingExit = true;

    if (inTrade && units.length < maxUnits && !pendingExit) {{
      if (todayAtr !== null) {{
        const lp = units[units.length-1].price;
        const ea = units[0].atr;
        if (price >= lp + addInterval * ea) {{
          const ceq = cash + shares * price;
          let us = Math.max(100, Math.floor(ceq * riskPct / todayAtr / 100) * 100);
          const ap = price * (1 + slip);
          const ac = us * ap * (1 + fee);
          if (ac <= cash) {{
            cash -= ac; shares += us;
            stopPrice = ap - stopMult * todayAtr;
            units.push({{price:ap,shares:us,atr:todayAtr,cost:ac}});
            trades.push({{date:data.dates[i],type:'ADD',price:Math.round(ap*100)/100,shares:us,amount:Math.round(ac),fee:Math.round(us*ap*fee),units:units.length,stop:stopPrice?Math.round(stopPrice*100)/100:null,pnl:null}});
            signals[i] = 4;
          }}
        }}
      }}
    }}

    if (!inTrade && dc.upper[i] !== null && price > dc.upper[i] && todayAtr !== null && todayAtr > 0) {{
      const ceq = cash + shares * price;
      let us = Math.max(100, Math.floor(ceq * riskPct / todayAtr / 100) * 100);
      pendingEntry = us;
    }}

    equity[i] = Math.max(0, cash + shares * price);
  }}

  return {{ equity, trades, signals, dc, atr, dates:data.dates }};
}}

// ====== METRICS ======
function calcMetrics(equity, trades, capital, rf = 0.025) {{
  if (equity.length < 2) return {{cumReturn:0, annualReturn:0, mdd:0, sharpe:0, winRate:0, profitFactor:0, tradeCount:0}};
  const finalEq = equity[equity.length-1];
  const cumReturn = finalEq > 0 ? (finalEq - capital) / capital : -1;
  const annualReturn = cumReturn > -1 ? Math.pow(1+cumReturn, 252/equity.length) - 1 : -1;
  let peak = equity[0], mdd = 0;
  for (const v of equity) {{ if (v>peak) peak=v; const dd = (peak-v)/peak; if (dd>mdd) mdd=dd; }}
  const dr = []; for (let i=1;i<equity.length;i++) dr.push((equity[i]-equity[i-1])/Math.max(equity[i-1],1));
  const avgR = dr.reduce((a,b)=>a+b,0)/dr.length;
  const stdR = Math.sqrt(dr.reduce((s,r)=>s+(r-avgR)**2,0)/(dr.length-1));
  const sharpe = stdR > 0 ? (avgR*252-rf)/(stdR*Math.sqrt(252)) : 0;
  const closed = trades.filter(t=>t.type==='EXIT'||t.type==='STOP_LOSS');
  const wins = closed.filter(t=>t.pnl>0);
  const winRate = closed.length>0 ? wins.length/closed.length : 0;
  const totalP = wins.reduce((s,t)=>s+t.pnl,0);
  const totalL = Math.abs(closed.filter(t=>t.pnl<=0).reduce((s,t)=>s+t.pnl,0));
  const pf = totalL>0 ? totalP/totalL : (totalP>0?Infinity:0);
  return {{cumReturn, annualReturn, mdd, sharpe, winRate, profitFactor:pf, tradeCount:closed.length}};
}}

// ====== GET PARAMS ======
function getParams() {{
  const toNum = id => parseFloat(document.getElementById(id).value);
  return {{
    s1Entry: toNum('s1Entry'), s1Exit: toNum('s1Exit'),
    s2Entry: toNum('s2Entry'), s2Exit: toNum('s2Exit'),
    atrPeriod: toNum('atrPeriod'),
    stopMult: toNum('stopMult')/10, addInterval: toNum('addInterval')/10,
    maxUnits: toNum('maxUnits'), riskPct: toNum('riskPct')/1000,
    capital: toNum('capital')*10000,
    fee: parseFloat(document.getElementById('feeRate').value),
    slip: parseFloat(document.getElementById('slippage').value),
  }};
}}

// ====== RUN ALL ======
function runAll() {{
  const p = getParams();
  const data = STOCK_DATA[currentCode];
  const capital = p.capital;

  // Update labels
  document.getElementById('s1eVal').textContent = p.s1Entry;
  document.getElementById('s1xVal').textContent = p.s1Exit;
  document.getElementById('s2eVal').textContent = p.s2Entry;
  document.getElementById('s2xVal').textContent = p.s2Exit;
  document.getElementById('atrpVal').textContent = p.atrPeriod;
  document.getElementById('stopmVal').textContent = (p.stopMult).toFixed(1);
  document.getElementById('addiVal').textContent = (p.addInterval).toFixed(1);
  document.getElementById('maxuVal').textContent = p.maxUnits;
  document.getElementById('riskVal').textContent = (p.riskPct*100).toFixed(1)+'%';
  document.getElementById('capVal').textContent = Math.round(p.capital/10000);

  // Run S1
  const s1 = runBacktest(data, {{entryN:p.s1Entry, exitN:p.s1Exit, atrPeriod:p.atrPeriod, stopMult:p.stopMult, addInterval:p.addInterval, maxUnits:p.maxUnits, riskPct:p.riskPct, fee:p.fee, slip:p.slip, capital}});
  // Run S2
  const s2 = runBacktest(data, {{entryN:p.s2Entry, exitN:p.s2Exit, atrPeriod:p.atrPeriod, stopMult:p.stopMult, addInterval:p.addInterval, maxUnits:p.maxUnits, riskPct:p.riskPct, fee:p.fee, slip:p.slip, capital}});
  // BH
  const bhEq = data.c.map(px => capital * px / data.c[0]);

  const m1 = calcMetrics(s1.equity, s1.trades, capital);
  const m2 = calcMetrics(s2.equity, s2.trades, capital);
  const mBH = calcMetrics(bhEq, [], capital);

  resultCache = {{s1, s2, bhEq, m1, m2, mBH, data, p, capital}};

  renderMetrics(m1, m2);
  renderKlineChart();
  renderEquityChart();
  renderDrawdownChart();
  renderTradeLog();
  updateNav();
}}

// ====== RENDER METRICS ======
function renderMetrics(m1, m2) {{
  const pc = v => (v*100).toFixed(2)+'%';
  const html = `
    <div class="row-label s1"> System 1 (${{getParams().s1Entry}}/${{getParams().s1Exit}})</div>
    <div class="metric-card s1"><div class="label">累计回报</div><div class="value">${{pc(m1.cumReturn)}}</div></div>
    <div class="metric-card s1"><div class="label">年化收益</div><div class="value">${{pc(m1.annualReturn)}}</div></div>
    <div class="metric-card s1"><div class="label">MDD</div><div class="value">${{pc(m1.mdd)}}</div></div>
    <div class="metric-card s1"><div class="label">夏普比率</div><div class="value">${{m1.sharpe.toFixed(3)}}</div></div>
    <div class="row-label s2"> System 2 (${{getParams().s2Entry}}/${{getParams().s2Exit}})</div>
    <div class="metric-card s2"><div class="label">累计回报</div><div class="value">${{pc(m2.cumReturn)}}</div></div>
    <div class="metric-card s2"><div class="label">年化收益</div><div class="value">${{pc(m2.annualReturn)}}</div></div>
    <div class="metric-card s2"><div class="label">MDD</div><div class="value">${{pc(m2.mdd)}}</div></div>
    <div class="metric-card s2"><div class="label">夏普比率</div><div class="value">${{m2.sharpe.toFixed(3)}}</div></div>
  `;
  document.getElementById('metricsPanel').innerHTML = '<div class="metrics">'+html+'</div>';
}}

// ====== PLOTLY CHARTS ======
const PLOT_BG = '#131722'; const GRID = '#2a2e39'; const FONT_C = '#d1d4dc';

function renderKlineChart() {{
  if (!resultCache) return;
  const {{s1, s2, data, p}} = resultCache;
  const dates = data.dates.map(d => d.slice(0,4)+'-'+d.slice(4,6)+'-'+d.slice(6));

  const traces = [];
  // Candlestick - show only last 120 days for readability
  const start = Math.max(0, data.c.length - 180);
  const sl = i => data.dates.slice(start).map(d => d.slice(0,4)+'-'+d.slice(4,6)+'-'+d.slice(6))[i-start];

  traces.push({{
    type: 'candlestick', name: 'OHLC', x: dates, xaxis:'x',
    open: data.o, high: data.h, low: data.l, close: data.c,
    increasing: {{line:{{color:'#ef5350'}}, fillcolor:'#ef5350'}},
    decreasing: {{line:{{color:'#26a69a'}}, fillcolor:'#26a69a'}},
    showlegend: true
  }});

  // S1 channels
  const s1u = s1.dc.upper.map(v => v!==null?Math.round(v*100)/100:null);
  const s1l = s1.dc.lower.map(v => v!==null?Math.round(v*100)/100:null);
  traces.push({{type:'scatter',x:dates,y:s1u,mode:'lines',name:'S1上轨('+p.s1Entry+')',line:{{color:'#ef5350',dash:'dash',width:1}},showlegend:true}});
  traces.push({{type:'scatter',x:dates,y:s1l,mode:'lines',name:'S1下轨('+p.s1Exit+')',line:{{color:'#26a69a',dash:'dash',width:1}},showlegend:true}});

  // S2 channels
  const s2u = s2.dc.upper.map(v => v!==null?Math.round(v*100)/100:null);
  const s2l = s2.dc.lower.map(v => v!==null?Math.round(v*100)/100:null);
  traces.push({{type:'scatter',x:dates,y:s2u,mode:'lines',name:'S2上轨('+p.s2Entry+')',line:{{color:'#ff9800',dash:'dot',width:1}},showlegend:true}});
  traces.push({{type:'scatter',x:dates,y:s2l,mode:'lines',name:'S2下轨('+p.s2Exit+')',line:{{color:'#66bb6a',dash:'dot',width:1}},showlegend:true}});

  // S1 signals
  const sigData = (sig, marker, name, color) => {{
    const idx = sig.map((s,i)=>s===marker?i:-1).filter(i=>i>=0);
    return {{type:'scatter',x:idx.map(i=>dates[i]),y:idx.map(i=>data.c[i]),
      mode:'markers',name,marker:{{symbol:marker===1?'triangle-up':marker===2?'x':marker===3?'triangle-down':'diamond',size:10,color,line:{{color:'white',width:1}}}},showlegend:true}};
  }};
  traces.push(sigData(s1.signals, 1, 'S1 入场▲', '#ef5350'));
  traces.push(sigData(s1.signals, 4, 'S1 加仓◆', '#ff9800'));
  traces.push(sigData(s1.signals, 2, 'S1 止损✕', '#f44336'));
  traces.push(sigData(s1.signals, 3, 'S1 离场▼', '#26a69a'));

  const layout = {{
    title: {{text:STOCK_NAMES[currentCode]+' ('+currentCode+') — K线 + 唐奇安通道 + 交易信号',font:{{size:14,color:FONT_C}}}},
    plot_bgcolor:PLOT_BG, paper_bgcolor:PLOT_BG, font:{{color:FONT_C,size:11}},
    xaxis:{{gridcolor:GRID,rangeslider:{{visible:false}},type:'category',nticks:20}},
    yaxis:{{gridcolor:GRID,title:'价格 (¥)'}}, margin:{{l:60,r:20,t:50,b:40}},
    hovermode:'x unified', legend:{{x:0.01,y:0.99,bgcolor:'rgba(19,23,34,0.9)',bordercolor:GRID,font:{{size:10}}}},
    height:420
  }};
  Plotly.react('chartKline', traces, layout, {{responsive:true}});
}}

function renderEquityChart() {{
  if (!resultCache) return;
  const {{s1, s2, bhEq, data, p, capital}} = resultCache;
  const dates = data.dates.map(d => d.slice(0,4)+'-'+d.slice(4,6)+'-'+d.slice(6));
  const traces = [
    {{type:'scatter',x:dates,y:s1.equity,mode:'lines',name:'S1 ('+p.s1Entry+'/'+p.s1Exit+')',line:{{color:'#4fc3f7',width:2}}}},
    {{type:'scatter',x:dates,y:s2.equity,mode:'lines',name:'S2 ('+p.s2Entry+'/'+p.s2Exit+')',line:{{color:'#ab47bc',width:2}}}},
    {{type:'scatter',x:dates,y:bhEq,mode:'lines',name:'买入持有',line:{{color:'#9e9e9e',width:1.5,dash:'dash'}}}},
  ];
  const layout = {{
    title: {{text:'净值曲线对比',font:{{size:13,color:FONT_C}}}},
    plot_bgcolor:PLOT_BG, paper_bgcolor:PLOT_BG, font:{{color:FONT_C,size:11}},
    xaxis:{{gridcolor:GRID}}, yaxis:{{gridcolor:GRID,title:'净值 (¥)'}},
    shapes:[{{type:'line',x0:dates[0],x1:dates[dates.length-1],y0:capital,y1:capital,line:{{color:GRID,dash:'dot',width:1}}}}],
    margin:{{l:60,r:20,t:40,b:40}}, legend:{{x:0.01,y:0.99,bgcolor:'rgba(19,23,34,0.9)',bordercolor:GRID,font:{{size:10}}}},
    height:280
  }};
  Plotly.react('chartEquity', traces, layout, {{responsive:true}});
}}

function renderDrawdownChart() {{
  if (!resultCache) return;
  const {{s1, s2, data}} = resultCache;
  const dates = data.dates.map(d => d.slice(0,4)+'-'+d.slice(4,6)+'-'+d.slice(6));
  const dd = eq => {{ let peak=eq[0]; const dds=[]; for(const v of eq){{if(v>peak)peak=v;dds.push((peak-v)/peak*100);}} return dds; }};
  const dd1 = dd(s1.equity); const dd2 = dd(s2.equity);
  const traces = [
    {{type:'scatter',x:dates,y:dd1,mode:'lines',name:'S1 回撤',fill:'tozeroy',fillcolor:'rgba(79,195,247,0.2)',line:{{color:'#4fc3f7',width:1.5}}}},
    {{type:'scatter',x:dates,y:dd2,mode:'lines',name:'S2 回撤',fill:'tozeroy',fillcolor:'rgba(171,71,188,0.2)',line:{{color:'#ab47bc',width:1.5}}}},
  ];
  const layout = {{
    title: {{text:'回撤曲线 (S1最大: '+dd1.reduce((a,b)=>Math.max(a,b),0).toFixed(1)+'% / S2最大: '+dd2.reduce((a,b)=>Math.max(a,b),0).toFixed(1)+'%)',font:{{size:13,color:FONT_C}}}},
    plot_bgcolor:PLOT_BG, paper_bgcolor:PLOT_BG, font:{{color:FONT_C,size:11}},
    xaxis:{{gridcolor:GRID}}, yaxis:{{gridcolor:GRID,title:'回撤 %',autorange:'reversed'}},
    margin:{{l:60,r:20,t:40,b:40}}, legend:{{x:0.01,y:0.01,bgcolor:'rgba(19,23,34,0.9)',bordercolor:GRID,font:{{size:10}}}},
    height:240
  }};
  Plotly.react('chartDrawdown', traces, layout, {{responsive:true}});
}}

function renderTradeLog() {{
  if (!resultCache) return;
  const trades = tradeLogFilter === 'S1' ? resultCache.s1.trades : resultCache.s2.trades;
  if (!trades.length) {{ document.getElementById('tradeLogTable').innerHTML = '<p style="color:#999;font-size:13px">无交易记录</p>'; return; }}
  const cls = t => t==='ENTRY'?'entry':t==='EXIT'?'exit':t==='STOP_LOSS'?'stop':'add';
  const sym = t => t==='ENTRY'?'▲':t==='EXIT'?'▼':t==='STOP_LOSS'?'✕':'◆';
  const rows = trades.map(t => `
    <tr>
      <td>${{t.date}}</td>
      <td class="${{cls(t.type)}}">${{sym(t.type)}} ${{t.type==='STOP_LOSS'?'止损':t.type==='EXIT'?'离场':t.type==='ADD'?'加仓':'入场'}}</td>
      <td>${{typeof t.price==='number'?t.price.toFixed(2):t.price}}</td>
      <td>${{t.shares.toLocaleString()}}</td>
      <td>${{(t.amount/10000).toFixed(1)}}万</td>
      <td>${{t.pnl!==null?(t.pnl>=0?'+':'')+(t.pnl/10000).toFixed(1)+'万':'—'}}</td>
      <td>${{t.units}}</td>
      <td>${{t.stop?t.stop.toFixed(2):'—'}}</td>
    </tr>
  `).join('');
  document.getElementById('tradeLogTable').innerHTML = `
    <div style="max-height:300px;overflow-y:auto">
      <table>
        <thead><tr><th>日期</th><th>类型</th><th>价格</th><th>股数</th><th>金额</th><th>盈亏</th><th>单位</th><th>止损价</th></tr></thead>
        <tbody>${{rows}}</tbody>
      </table>
    </div>`;
}}

function switchTradeLog(sys) {{
  tradeLogFilter = sys;
  document.getElementById('btnS1').classList.toggle('active', sys==='S1');
  document.getElementById('btnS2').classList.toggle('active', sys==='S2');
  renderTradeLog();
}}

function updateNav() {{
  if (!resultCache) return;
  const {{data, p}} = resultCache;
  document.getElementById('navSub').textContent =
    STOCK_NAMES[currentCode]+' '+currentCode+' · '+data.dates.length+'天 · 前复权日线';
}}

// ====== EVENT HANDLERS ======
function onParamChange() {{
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(runAll, 300);
}}

function onStockSelect() {{
  currentCode = document.getElementById('stockSelect').value;
  const data = STOCK_DATA[currentCode];
  document.getElementById('stockInfo').textContent =
    STOCK_NAMES[currentCode]+' '+currentCode+' · '+data.dates.length+' 交易日 · 前复权日线';
  runAll();
}}

function applyPreset(type) {{
  const presets = {{
    classic: {{s1Entry:20,s1Exit:10,s2Entry:55,s2Exit:20,atrPeriod:20,stopMult:20,addInterval:5,maxUnits:4,riskPct:20}},
    aggressive: {{s1Entry:10,s1Exit:5,s2Entry:30,s2Exit:15,atrPeriod:15,stopMult:15,addInterval:3,maxUnits:6,riskPct:30}},
    conservative: {{s1Entry:40,s1Exit:20,s2Entry:80,s2Exit:40,atrPeriod:30,stopMult:30,addInterval:10,maxUnits:2,riskPct:10}},
  }};
  const p = presets[type];
  for (const [k,v] of Object.entries(p)) document.getElementById(k).value = v;
  onParamChange();
}}

// ====== INIT ======
document.addEventListener('DOMContentLoaded', () => {{
  // Populate stock selector
  const sel = document.getElementById('stockSelect');
  for (const [code, info] of Object.entries(STOCK_DATA)) {{
    const opt = document.createElement('option');
    opt.value = code; opt.textContent = info.name + ' (' + code + ')';
    sel.appendChild(opt);
  }}
  sel.value = currentCode;
  sel.addEventListener('change', onStockSelect);

  // Bind parameter sliders
  const sliders = ['s1Entry','s1Exit','s2Entry','s2Exit','atrPeriod','stopMult','addInterval','maxUnits','riskPct','capital'];
  sliders.forEach(id => document.getElementById(id).addEventListener('input', onParamChange));
  document.getElementById('feeRate').addEventListener('change', onParamChange);
  document.getElementById('slippage').addEventListener('change', onParamChange);

  // Initial run
  onStockSelect();
}});
</script>
</body>
</html>'''

with open(OUTPUT, 'w', encoding='utf-8') as f:
    f.write(html)
print(f'Generated: {OUTPUT}')
print(f'Size: {len(html)} bytes ({len(html)//1024} KB)')
