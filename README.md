# 🛡️ Prop Fund Risk Management Dashboard

> A real-time risk monitoring dashboard that mirrors the **exact drawdown rules** used by prop trading firms like GFT Funding and Pips — built from 1.5 years of live funded account trading.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Dash](https://img.shields.io/badge/Plotly-Dash-lightblue?logo=plotly)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🧠 What Problem Does This Solve?

Prop firm traders get their accounts **closed** for breaching drawdown rules — often without realising how close they are to the limit. This dashboard gives a real-time view of your risk position relative to firm limits, with automated alerts before you breach.

Built because I personally needed this tool during live funded trading.

---

## ⚡ Features

| Feature | Description |
|---------|-------------|
| 📉 Trailing drawdown monitor | Live % of max drawdown limit used |
| 🚨 Kill-switch alert | Fires at 80% of max drawdown threshold |
| 📅 Daily loss limit tracker | Flags breach of daily 5% loss rule |
| 🎯 Profit target progress | Bar showing % of target achieved |
| 🕐 Session breakdown | P&L by London / New York / Asian session |
| 📂 MT4/MT5 CSV import | Upload your real trade history |
| 📊 Equity & drawdown curves | Visual P&L and risk over time |

---

## 🏦 Prop Firm Rules Simulated

| Rule                  | Typical Limit     | Dashboard Action         |
|-----------------------|-------------------|--------------------------|
| Max trailing drawdown | 10% of balance    | ⚠️ Alert at 80% (8%)    |
| Daily loss limit      | 5% of balance     | 🚨 Kill-switch flag      |
| Profit target         | 10% of balance    | 🎯 Progress bar          |

> These are standard rules for most funded firms (GFT Funding, Pips, FTMO, MyForexFunds style).

---

## ⚙️ Tech Stack

| Layer     | Library          |
|-----------|------------------|
| Dashboard | Plotly Dash      |
| Data      | pandas, NumPy    |
| Charts    | Plotly           |
| Input     | MT4/MT5 CSV      |

---

## 🚀 Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/kamleshmehra/prop-fund-risk-dashboard
cd prop-fund-risk-dashboard

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the dashboard
python dashboard.py
```

Open your browser at `http://localhost:8050`

Click **"Use sample data"** to see it working immediately with 20 sample trades.

---

## 📂 Using Your Own MT4/MT5 Trade History

1. In MT4/MT5: **Account History → Save as Report → CSV**
2. Open the dashboard at `http://localhost:8050`
3. Click **"Upload CSV"** and select your file
4. Dashboard auto-loads and calculates all risk metrics

**Expected CSV columns:**
```
open_time, close_time, symbol, type, lots, open_price, close_price, profit
```

---

## 📁 Project Structure

```
prop-fund-risk-dashboard/
├── dashboard.py         → main Dash app (run this)
├── risk_engine.py       → drawdown, daily PnL, session logic
├── sample_trades.csv    → 20 sample trades to test with
├── requirements.txt
└── README.md
```

---

## 📊 Risk Metrics Explained

- **Trailing Drawdown** — calculated from peak equity, not starting balance. This is how most prop firms measure it.
- **Daily Loss** — sum of all closed trades on that calendar day vs starting balance
- **Session P&L** — trades grouped by open time into London (8–13 UTC), New York (13–21 UTC), Asian (0–8 UTC)
- **Win Rate** — % of trades closed in profit (excluding breakeven)
- **Risk:Reward** — average winner size ÷ average loser size

---

## 👤 Author

**Kamlesh Mehra** — Prop fund trader (GFT Funding, Pips) · BCA, Amity University Delhi

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?logo=linkedin)](https://www.linkedin.com/in/kamlesh-mehra-743391268)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-black?logo=github)](https://github.com/kamleshmehra)

---

## 📄 License

MIT — free to use, modify, and share.
