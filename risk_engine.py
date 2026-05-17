"""
risk_engine.py
Core risk calculations mirroring prop firm account rules.
"""

import pandas as pd
import numpy as np

# ── Prop firm rule defaults ───────────────────────────────────────────────────
MAX_TRAILING_DRAWDOWN = 0.10   # 10% trailing drawdown limit
DAILY_LOSS_LIMIT      = 0.05   # 5% daily loss limit
PROFIT_TARGET         = 0.10   # 10% profit target
STARTING_BALANCE      = 10000  # default account size


def load_trades(filepath: str) -> pd.DataFrame:
    """Load MT4/MT5 CSV trade history."""
    df = pd.read_csv(filepath, parse_dates=["open_time", "close_time"])
    df = df.sort_values("close_time").reset_index(drop=True)
    return df


def compute_equity_curve(df: pd.DataFrame, balance: float = STARTING_BALANCE) -> pd.Series:
    """Cumulative equity curve from trade history."""
    df = df.copy()
    df["cumulative_profit"] = df["profit"].cumsum()
    df["equity"] = balance + df["cumulative_profit"]
    return df.set_index("close_time")["equity"]


def compute_trailing_drawdown(equity: pd.Series) -> pd.Series:
    """Trailing drawdown from peak equity."""
    peak = equity.cummax()
    return (equity - peak) / peak


def compute_daily_pnl(df: pd.DataFrame) -> pd.Series:
    """Daily P&L grouped by close date."""
    df = df.copy()
    df["date"] = pd.to_datetime(df["close_time"]).dt.date
    return df.groupby("date")["profit"].sum()


def risk_summary(df: pd.DataFrame, balance: float = STARTING_BALANCE) -> dict:
    """Full risk summary for dashboard display."""
    equity    = compute_equity_curve(df, balance)
    drawdown  = compute_trailing_drawdown(equity)
    daily_pnl = compute_daily_pnl(df)

    current_equity     = equity.iloc[-1]
    total_return       = (current_equity - balance) / balance
    max_drawdown       = drawdown.min()
    current_drawdown   = drawdown.iloc[-1]
    worst_daily_loss   = daily_pnl.min() / balance
    best_daily_gain    = daily_pnl.max() / balance
    win_rate           = (df["profit"] > 0).mean()
    avg_win            = df[df["profit"] > 0]["profit"].mean()
    avg_loss           = df[df["profit"] < 0]["profit"].mean()
    rr_ratio           = abs(avg_win / avg_loss) if avg_loss != 0 else np.nan

    # Rule breach flags
    dd_alert      = current_drawdown < -(MAX_TRAILING_DRAWDOWN * 0.8)
    dd_breach     = current_drawdown < -MAX_TRAILING_DRAWDOWN
    daily_breach  = worst_daily_loss < -DAILY_LOSS_LIMIT
    target_hit    = total_return >= PROFIT_TARGET

    return {
        "current_equity"   : round(current_equity, 2),
        "total_return"     : round(total_return, 4),
        "max_drawdown"     : round(max_drawdown, 4),
        "current_drawdown" : round(current_drawdown, 4),
        "worst_daily_loss" : round(worst_daily_loss, 4),
        "best_daily_gain"  : round(best_daily_gain, 4),
        "win_rate"         : round(win_rate, 3),
        "rr_ratio"         : round(rr_ratio, 2),
        "dd_alert"         : dd_alert,
        "dd_breach"        : dd_breach,
        "daily_breach"     : daily_breach,
        "target_hit"       : target_hit,
        "equity_curve"     : equity,
        "drawdown_curve"   : drawdown,
        "daily_pnl"        : daily_pnl,
    }


def session_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """Classify trades by trading session."""
    df = df.copy()
    df["hour"] = pd.to_datetime(df["open_time"]).dt.hour

    def get_session(h):
        if 0 <= h < 8:   return "Asian"
        if 8 <= h < 13:  return "London"
        if 13 <= h < 21: return "New York"
        return "Off-hours"

    df["session"] = df["hour"].apply(get_session)
    return df.groupby("session")["profit"].agg(
        total_pnl="sum",
        trades="count",
        win_rate=lambda x: (x > 0).mean(),
        avg_pnl="mean"
    ).round(2)
