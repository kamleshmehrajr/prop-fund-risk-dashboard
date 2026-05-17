"""
dashboard.py
Prop Fund Risk Management Dashboard — Plotly Dash
Run: python dashboard.py  →  open http://localhost:8050
"""

import dash
from dash import dcc, html, dash_table, Input, Output, State
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import base64
import io

from risk_engine import (
    load_trades, risk_summary, session_breakdown,
    STARTING_BALANCE, MAX_TRAILING_DRAWDOWN, DAILY_LOSS_LIMIT, PROFIT_TARGET
)

app = dash.Dash(__name__)
app.title = "Prop Fund Risk Dashboard"

# ── Colour palette ────────────────────────────────────────────────────────────
GREEN  = "#2ecc71"
RED    = "#e74c3c"
BLUE   = "#3498db"
ORANGE = "#f39c12"
BG     = "#0f1117"
CARD   = "#1a1f2e"
TEXT   = "#ecf0f1"

def card(children, style=None):
    base = {
        "background": CARD, "borderRadius": "8px",
        "padding": "16px", "marginBottom": "12px",
        "border": "1px solid #2c3e50"
    }
    if style: base.update(style)
    return html.Div(children, style=base)

def metric(label, value, color=TEXT, sub=None):
    return html.Div([
        html.P(label, style={"margin": 0, "fontSize": "12px", "color": "#95a5a6"}),
        html.H3(value, style={"margin": "4px 0", "color": color, "fontSize": "22px"}),
        html.P(sub or "", style={"margin": 0, "fontSize": "11px", "color": "#7f8c8d"})
    ])

# ── Layout ────────────────────────────────────────────────────────────────────
app.layout = html.Div(style={"background": BG, "minHeight": "100vh", "padding": "20px",
                              "fontFamily": "Arial, sans-serif", "color": TEXT}, children=[

    html.H2("📊 Prop Fund Risk Dashboard", style={"color": BLUE, "marginBottom": "4px"}),
    html.P("Mirrors GFT Funding / Pips drawdown rules", style={"color": "#7f8c8d", "marginTop": 0}),

    # Upload
    card([
        html.P("Upload MT4/MT5 trade history (CSV) or use sample data:", style={"margin": "0 0 8px"}),
        dcc.Upload(id="upload", children=html.Button("📁 Upload CSV", style={
            "background": BLUE, "color": "white", "border": "none",
            "padding": "8px 16px", "borderRadius": "6px", "cursor": "pointer"
        })),
        html.Button("Use sample data", id="sample-btn", n_clicks=0, style={
            "marginLeft": "10px", "background": "transparent",
            "color": BLUE, "border": f"1px solid {BLUE}",
            "padding": "8px 16px", "borderRadius": "6px", "cursor": "pointer"
        }),
        html.Div(id="upload-status", style={"marginTop": "8px", "color": GREEN})
    ]),

    html.Div(id="dashboard-content")
])

def build_dashboard(df):
    rs = risk_summary(df)
    sb = session_breakdown(df)

    dd_color  = RED if rs["dd_alert"] else GREEN
    dd_pct    = abs(rs["current_drawdown"]) / MAX_TRAILING_DRAWDOWN * 100

    # Alert banners
    alerts = []
    if rs["dd_breach"]:
        alerts.append(html.Div("🚨 MAX DRAWDOWN BREACHED — Account would be closed",
            style={"background": RED, "padding": "10px", "borderRadius": "6px",
                   "fontWeight": "bold", "marginBottom": "8px"}))
    elif rs["dd_alert"]:
        alerts.append(html.Div("⚠️ Drawdown warning — approaching max limit (80%+)",
            style={"background": ORANGE, "padding": "10px", "borderRadius": "6px",
                   "marginBottom": "8px"}))
    if rs["target_hit"]:
        alerts.append(html.Div("🎯 Profit target reached!",
            style={"background": GREEN, "padding": "10px", "borderRadius": "6px",
                   "color": "#000", "marginBottom": "8px"}))

    # Metrics row
    metrics_row = html.Div(style={"display": "grid", "gridTemplateColumns": "repeat(4,1fr)", "gap": "12px"}, children=[
        card(metric("Total Return",     f"{rs['total_return']:.2%}",
                    GREEN if rs['total_return'] >= 0 else RED)),
        card(metric("Current Drawdown", f"{rs['current_drawdown']:.2%}",
                    dd_color, f"{dd_pct:.0f}% of limit used")),
        card(metric("Win Rate",         f"{rs['win_rate']:.1%}", BLUE)),
        card(metric("Risk:Reward",      f"{rs['rr_ratio']:.2f}", ORANGE)),
    ])

    # Equity curve
    eq = rs["equity_curve"].reset_index()
    eq.columns = ["date", "equity"]
    fig_eq = go.Figure()
    fig_eq.add_trace(go.Scatter(x=eq["date"], y=eq["equity"],
        fill="tozeroy", line=dict(color=GREEN, width=1.5), name="Equity"))
    fig_eq.update_layout(title="Equity Curve", plot_bgcolor=BG, paper_bgcolor=CARD,
        font_color=TEXT, height=280, margin=dict(l=0,r=0,t=40,b=0))

    # Drawdown curve
    dd = rs["drawdown_curve"].reset_index()
    dd.columns = ["date", "drawdown"]
    fig_dd = go.Figure()
    fig_dd.add_trace(go.Scatter(x=dd["date"], y=dd["drawdown"]*100,
        fill="tozeroy", line=dict(color=RED, width=1.5), name="Drawdown %"))
    fig_dd.add_hline(y=-MAX_TRAILING_DRAWDOWN*100, line_dash="dash", line_color=ORANGE,
                     annotation_text="Max DD limit")
    fig_dd.update_layout(title="Trailing Drawdown", plot_bgcolor=BG, paper_bgcolor=CARD,
        font_color=TEXT, height=280, margin=dict(l=0,r=0,t=40,b=0))

    # Session breakdown table
    sb_reset = sb.reset_index()

    # Daily PnL bar
    dpnl = rs["daily_pnl"].reset_index()
    dpnl.columns = ["date", "pnl"]
    dpnl["date"] = dpnl["date"].astype(str)
    fig_daily = go.Figure(go.Bar(
        x=dpnl["date"], y=dpnl["pnl"],
        marker_color=[GREEN if v >= 0 else RED for v in dpnl["pnl"]]
    ))
    fig_daily.update_layout(title="Daily P&L", plot_bgcolor=BG, paper_bgcolor=CARD,
        font_color=TEXT, height=250, margin=dict(l=0,r=0,t=40,b=0))

    return html.Div([
        *alerts,
        metrics_row,
        html.Div(style={"display":"grid","gridTemplateColumns":"1fr 1fr","gap":"12px"}, children=[
            card(dcc.Graph(figure=fig_eq, config={"displayModeBar":False})),
            card(dcc.Graph(figure=fig_dd, config={"displayModeBar":False})),
        ]),
        card(dcc.Graph(figure=fig_daily, config={"displayModeBar":False})),
        card([
            html.H4("Session Breakdown", style={"marginTop":0}),
            dash_table.DataTable(
                data=sb_reset.to_dict("records"),
                columns=[{"name":c,"id":c} for c in sb_reset.columns],
                style_table={"overflowX":"auto"},
                style_cell={"background":CARD,"color":TEXT,"border":"1px solid #2c3e50","textAlign":"center"},
                style_header={"background":"#2c3e50","fontWeight":"bold"}
            )
        ])
    ])

@app.callback(
    Output("dashboard-content", "children"),
    Output("upload-status", "children"),
    Input("upload", "contents"),
    Input("sample-btn", "n_clicks"),
    State("upload", "filename"),
    prevent_initial_call=True
)
def update(contents, n_clicks, filename):
    ctx = dash.callback_context
    trigger = ctx.triggered[0]["prop_id"]

    if "sample-btn" in trigger:
        df = load_trades("sample_trades.csv")
        return build_dashboard(df), "✅ Loaded sample trade data (20 trades)"

    if contents:
        _, content_str = contents.split(",")
        decoded = base64.b64decode(content_str)
        df = pd.read_csv(io.StringIO(decoded.decode("utf-8")), parse_dates=["open_time","close_time"])
        return build_dashboard(df), f"✅ Loaded {filename} ({len(df)} trades)"

    return html.Div(), ""

if __name__ == "__main__":
    app.run(debug=True)
