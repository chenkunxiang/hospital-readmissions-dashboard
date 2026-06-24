"""
Hospital Readmissions Dashboard
Data: CMS Hospital Readmissions Reduction Program (HRRP)

Run: python app.py  →  open http://localhost:8050
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, callback
from pathlib import Path

# ── Data loading ──────────────────────────────────────────────────────────────

DATA_PATH = Path("data/readmissions.csv")

def load_data():
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            "data/readmissions.csv not found.\n"
            "Run:  python download_data.py"
        )
    df = pd.read_csv(DATA_PATH)

    # Shorten long condition names for display
    condition_map = {
        "READM-30-HF-HRRP": "Heart Failure",
        "READM-30-AMI-HRRP": "Heart Attack (AMI)",
        "READM-30-PN-HRRP": "Pneumonia",
        "READM-30-COPD-HRRP": "COPD",
        "READM-30-HIP-KNEE-HRRP": "Hip/Knee Replacement",
        "READM-30-CABG-HRRP": "Coronary Bypass (CABG)",
    }
    # Also handle full text versions CMS sometimes returns
    full_text_map = {
        "HEART FAILURE": "Heart Failure",
        "ACUTE MYOCARDIAL INFARCTION": "Heart Attack (AMI)",
        "PNEUMONIA": "Pneumonia",
        "CHRONIC OBSTRUCTIVE PULMONARY DISEASE (COPD)": "COPD",
        "HIP/KNEE ARTHROPLASTY": "Hip/Knee Replacement",
        "CORONARY ARTERY BYPASS GRAFT (CABG)": "Coronary Bypass (CABG)",
    }
    df["condition"] = (
        df["measure_name"]
        .map(condition_map)
        .fillna(df["measure_name"].str.upper().map(full_text_map))
        .fillna(df["measure_name"])
    )

    return df

df = load_data()
conditions = sorted(df["condition"].dropna().unique())
states = sorted(df["state"].dropna().unique())

# ── App layout ────────────────────────────────────────────────────────────────

app = Dash(__name__, title="Hospital Readmissions Dashboard")

CARD = {
    "background": "#1e2130",
    "borderRadius": "8px",
    "padding": "16px",
    "marginBottom": "16px",
}
PAGE_BG = "#12141f"
TEXT = "#e0e4f0"
ACCENT = "#636efa"

app.layout = html.Div(
    style={"backgroundColor": PAGE_BG, "minHeight": "100vh", "fontFamily": "Inter, sans-serif", "color": TEXT},
    children=[

        # Header
        html.Div(
            style={"backgroundColor": "#161829", "padding": "24px 40px", "borderBottom": "1px solid #2a2d40"},
            children=[
                html.H1("Hospital Readmissions Dashboard", style={"margin": 0, "fontSize": "22px", "fontWeight": 700}),
                html.P(
                    "CMS Hospital Readmissions Reduction Program (HRRP) — 30-day readmission rates",
                    style={"margin": "4px 0 0", "color": "#8b90a8", "fontSize": "13px"},
                ),
            ],
        ),

        # Controls
        html.Div(
            style={"padding": "24px 40px 0"},
            children=[
                html.Div(
                    style={"display": "flex", "gap": "24px", "flexWrap": "wrap"},
                    children=[
                        html.Div([
                            html.Label("Condition", style={"fontSize": "12px", "color": "#8b90a8", "marginBottom": "6px", "display": "block"}),
                            dcc.Dropdown(
                                id="condition-filter",
                                options=[{"label": c, "value": c} for c in conditions],
                                value=conditions[0] if conditions else None,
                                clearable=False,
                                style={"width": "260px", "fontSize": "13px"},
                            ),
                        ]),
                        html.Div([
                            html.Label("State (optional)", style={"fontSize": "12px", "color": "#8b90a8", "marginBottom": "6px", "display": "block"}),
                            dcc.Dropdown(
                                id="state-filter",
                                options=[{"label": s, "value": s} for s in states],
                                value=None,
                                placeholder="All states",
                                style={"width": "200px", "fontSize": "13px"},
                            ),
                        ]),
                    ],
                ),
            ],
        ),

        # KPI row
        html.Div(id="kpi-row", style={"padding": "20px 40px 0", "display": "flex", "gap": "16px"}),

        # Charts
        html.Div(
            style={"padding": "0 40px 40px", "display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "16px", "marginTop": "16px"},
            children=[
                html.Div(dcc.Graph(id="map-chart"), style=CARD),
                html.Div(dcc.Graph(id="bar-chart"), style=CARD),
                html.Div(dcc.Graph(id="scatter-chart"), style=CARD),
                html.Div(dcc.Graph(id="distribution-chart"), style=CARD),
            ],
        ),
    ],
)

# ── Callbacks ─────────────────────────────────────────────────────────────────

def filter_df(condition, state):
    filtered = df[df["condition"] == condition].copy()
    if state:
        filtered = filtered[filtered["state"] == state]
    return filtered


@callback(Output("kpi-row", "children"), Input("condition-filter", "value"), Input("state-filter", "value"))
def update_kpis(condition, state):
    filtered = filter_df(condition, state)
    if filtered.empty:
        return []

    avg_predicted = filtered["predicted_readmission_rate"].mean()
    avg_expected = filtered["expected_readmission_rate"].mean()
    avg_err = filtered["excess_readmission_ratio"].mean()
    n_hospitals = filtered["facility_name"].nunique()
    high_risk = (filtered["excess_readmission_ratio"] > 1.0).sum()

    kpis = [
        ("Hospitals", f"{n_hospitals:,}", None),
        ("Avg Predicted Rate", f"{avg_predicted:.1f}%", None),
        ("Avg Expected Rate", f"{avg_expected:.1f}%", None),
        ("Avg Excess Ratio", f"{avg_err:.3f}", "#ef4444" if avg_err > 1 else "#22c55e"),
        ("High-Risk Hospitals", f"{high_risk:,}", "#ef4444" if high_risk > 0 else TEXT),
    ]

    def kpi_card(label, value, color):
        return html.Div(
            style={**CARD, "flex": "1", "minWidth": "140px", "marginBottom": 0},
            children=[
                html.P(label, style={"margin": 0, "fontSize": "11px", "color": "#8b90a8", "textTransform": "uppercase", "letterSpacing": "0.05em"}),
                html.P(value, style={"margin": "6px 0 0", "fontSize": "26px", "fontWeight": 700, "color": color or TEXT}),
            ],
        )

    return [kpi_card(*k) for k in kpis]


@callback(Output("map-chart", "figure"), Input("condition-filter", "value"), Input("state-filter", "value"))
def update_map(condition, state):
    state_df = df[df["condition"] == condition].groupby("state", as_index=False).agg(
        avg_ratio=("excess_readmission_ratio", "mean"),
        hospitals=("facility_name", "nunique"),
    )

    fig = px.choropleth(
        state_df,
        locations="state",
        locationmode="USA-states",
        color="avg_ratio",
        scope="usa",
        color_continuous_scale=["#22c55e", "#facc15", "#ef4444"],
        color_continuous_midpoint=1.0,
        hover_data={"hospitals": True, "avg_ratio": ":.3f"},
        labels={"avg_ratio": "Excess Ratio", "state": "State"},
        title=f"Excess Readmission Ratio by State — {condition}",
    )
    fig.update_layout(
        paper_bgcolor="#1e2130", plot_bgcolor="#1e2130", font_color=TEXT,
        margin={"t": 40, "b": 0, "l": 0, "r": 0}, height=300,
        coloraxis_colorbar={"title": "Ratio", "tickfont": {"color": TEXT}},
        geo={"bgcolor": "#1e2130", "lakecolor": "#12141f", "landcolor": "#2a2d40", "showlakes": True},
    )
    if state:
        fig.add_annotation(text=f"Filtered to: {state}", showarrow=False, x=0.5, y=-0.05, xref="paper", yref="paper", font={"color": "#8b90a8", "size": 11})
    return fig


@callback(Output("bar-chart", "figure"), Input("condition-filter", "value"), Input("state-filter", "value"))
def update_bar(condition, state):
    filtered = filter_df(condition, state)
    if filtered.empty:
        return go.Figure()

    top = (
        filtered.nlargest(20, "excess_readmission_ratio")
        [["facility_name", "state", "excess_readmission_ratio", "predicted_readmission_rate"]]
        .sort_values("excess_readmission_ratio")
    )
    top["label"] = top["facility_name"].str[:35] + " (" + top["state"] + ")"

    fig = px.bar(
        top, x="excess_readmission_ratio", y="label", orientation="h",
        color="excess_readmission_ratio",
        color_continuous_scale=["#facc15", "#ef4444"],
        labels={"excess_readmission_ratio": "Excess Ratio", "label": ""},
        title="Top 20 Highest Excess Readmission Ratio Hospitals",
    )
    fig.add_vline(x=1.0, line_dash="dash", line_color="#8b90a8", annotation_text="Ratio = 1.0 (expected)")
    fig.update_layout(
        paper_bgcolor="#1e2130", plot_bgcolor="#1e2130", font_color=TEXT,
        margin={"t": 40, "b": 20, "l": 10, "r": 10}, height=350,
        showlegend=False, coloraxis_showscale=False,
        yaxis={"tickfont": {"size": 10}},
    )
    return fig


@callback(Output("scatter-chart", "figure"), Input("condition-filter", "value"), Input("state-filter", "value"))
def update_scatter(condition, state):
    filtered = filter_df(condition, state).dropna(subset=["predicted_readmission_rate", "expected_readmission_rate", "number_of_discharges"])
    if filtered.empty:
        return go.Figure()

    fig = px.scatter(
        filtered,
        x="expected_readmission_rate",
        y="predicted_readmission_rate",
        size=np.clip(filtered["number_of_discharges"].fillna(100), 10, 2000),
        color="excess_readmission_ratio",
        color_continuous_scale=["#22c55e", "#facc15", "#ef4444"],
        color_continuous_midpoint=1.0,
        hover_name="facility_name",
        hover_data={"state": True, "excess_readmission_ratio": ":.3f", "number_of_discharges": True},
        labels={
            "expected_readmission_rate": "Expected Rate (%)",
            "predicted_readmission_rate": "Predicted Rate (%)",
            "excess_readmission_ratio": "Excess Ratio",
        },
        title="Predicted vs Expected Readmission Rate (bubble = discharges)",
        opacity=0.7,
    )
    # y=x line
    mn = filtered[["predicted_readmission_rate", "expected_readmission_rate"]].min().min()
    mx = filtered[["predicted_readmission_rate", "expected_readmission_rate"]].max().max()
    fig.add_shape(type="line", x0=mn, y0=mn, x1=mx, y1=mx, line={"dash": "dash", "color": "#8b90a8"})
    fig.update_layout(
        paper_bgcolor="#1e2130", plot_bgcolor="#1e2130", font_color=TEXT,
        margin={"t": 40, "b": 20, "l": 10, "r": 10}, height=350,
        coloraxis_colorbar={"title": "Excess Ratio", "tickfont": {"color": TEXT}},
    )
    return fig


@callback(Output("distribution-chart", "figure"), Input("condition-filter", "value"), Input("state-filter", "value"))
def update_distribution(condition, state):
    filtered = filter_df(condition, state).dropna(subset=["excess_readmission_ratio"])
    if filtered.empty:
        return go.Figure()

    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=filtered["excess_readmission_ratio"],
        nbinsx=40,
        marker_color=ACCENT,
        opacity=0.85,
        name="Hospitals",
    ))
    fig.add_vline(x=1.0, line_dash="dash", line_color="#ef4444",
                  annotation_text="Ratio = 1.0", annotation_font_color="#ef4444")
    fig.add_vline(x=filtered["excess_readmission_ratio"].mean(), line_dash="dot", line_color="#facc15",
                  annotation_text=f"Mean = {filtered['excess_readmission_ratio'].mean():.3f}",
                  annotation_font_color="#facc15")
    fig.update_layout(
        title="Distribution of Excess Readmission Ratios",
        xaxis_title="Excess Readmission Ratio",
        yaxis_title="Number of Hospitals",
        paper_bgcolor="#1e2130", plot_bgcolor="#1e2130", font_color=TEXT,
        margin={"t": 40, "b": 20, "l": 10, "r": 10}, height=350,
        bargap=0.05,
    )
    return fig


if __name__ == "__main__":
    app.run(debug=True, port=8050)
