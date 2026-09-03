"""
ApexPlanet Software Pvt Ltd — Data Analytics Internship
Task 3: Interactive Dashboard — Plotly Dash
--------------------------------------------
Run from the project root:
    python dashboard/app.py

Then open your browser at: http://127.0.0.1:8050
"""

from pathlib import Path
import pandas as pd
import numpy as np
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go

ROOT = Path(__file__).parent.parent

# ── Load data ──────────────────────────────────────────────────────────────────
def load_data():
    df = pd.read_excel(
        ROOT / "data" / "raw" / "ApexPlanet_DataAnalytics_Dataset.xlsx",
        sheet_name="Sales_Dataset"
    )
    df["Order_Date"] = pd.to_datetime(df["Order_Date"], errors="coerce")
    df["Age"] = df["Age"].fillna(df["Age"].median())
    df["Month"] = df["Order_Date"].dt.to_period("M").astype(str)
    return df

def compute_rfm(df):
    snapshot = pd.Timestamp("2026-01-02")
    rfm = df.groupby("Customer_ID").agg(
        Recency   = ("Order_Date",  lambda x: (snapshot - x.max()).days),
        Frequency = ("Order_ID",    "count"),
        Monetary  = ("Total_Sales", "sum"),
    ).reset_index()
    rfm["R"] = pd.qcut(rfm["Recency"],  5, labels=[5,4,3,2,1]).astype(int)
    rfm["F"] = pd.qcut(rfm["Frequency"].rank(method="first"), 5, labels=[1,2,3,4,5]).astype(int)
    rfm["M"] = pd.qcut(rfm["Monetary"], 5, labels=[1,2,3,4,5]).astype(int)

    def segment(row):
        r, f, m = row["R"], row["F"], row["M"]
        if r >= 4 and f >= 4 and m >= 4: return "Champions"
        elif r >= 3 and f >= 3:           return "Loyal Customers"
        elif r >= 3 and f <= 2:           return "Potential Loyalists"
        elif r <= 2 and f >= 3:           return "At Risk"
        elif r == 1 and f == 1:           return "Lost"
        elif r >= 4 and f == 1:           return "New Customers"
        else:                             return "Promising"

    rfm["Segment"] = rfm.apply(segment, axis=1)
    return rfm

df_raw = load_data()
rfm    = compute_rfm(df_raw)

SEGMENT_COLORS = {
    "Champions":           "#2ecc71",
    "Loyal Customers":     "#27ae60",
    "Potential Loyalists": "#1abc9c",
    "At Risk":             "#e74c3c",
    "Lost":                "#c0392b",
    "New Customers":       "#3498db",
    "Promising":           "#9b59b6",
}

# ── Styles ────────────────────────────────────────────────────────────────────
CARD = {
    "background": "#1e2130", "borderRadius": "10px",
    "padding": "20px", "textAlign": "center", "flex": "1",
    "margin": "0 8px", "boxShadow": "0 4px 12px rgba(0,0,0,0.3)"
}
KPI_NUM = {"fontSize": "28px", "fontWeight": "bold", "color": "#00d4aa", "margin": "8px 0"}
KPI_LBL = {"fontSize": "13px", "color": "#a0aec0"}
CHART_LAYOUT = dict(
    paper_bgcolor="#1e2130", plot_bgcolor="#1e2130",
    font=dict(color="#e2e8f0", size=11),
    margin=dict(l=40, r=20, t=40, b=40),
)

# ── App ───────────────────────────────────────────────────────────────────────
app = Dash(__name__, title="ApexPlanet Sales Dashboard")

app.layout = html.Div(
    style={"fontFamily": "Segoe UI, sans-serif", "background": "#0f1117",
           "minHeight": "100vh", "padding": "24px"},
    children=[

        # Header
        html.Div([
            html.H1("📊 ApexPlanet Sales Intelligence Dashboard",
                    style={"color": "#ffffff", "margin": 0, "fontSize": "26px"}),
            html.P("Task 3 — Deep-Dive Analysis & Interactive Dashboarding | ApexPlanet Internship",
                   style={"color": "#a0aec0", "margin": "4px 0 0 0", "fontSize": "13px"}),
        ], style={"marginBottom": "24px"}),

        # Filters
        html.Div([
            html.Div([
                html.Label("📍 City", style={"color": "#a0aec0", "fontSize": "13px"}),
                dcc.Dropdown(
                    id="filter-city",
                    options=[{"label": "All Cities", "value": "ALL"}] +
                            [{"label": c, "value": c} for c in sorted(df_raw["City"].dropna().unique())],
                    value="ALL", clearable=False,
                    style={"background": "#1e2130", "color": "#000"}
                ),
            ], style={"flex": "1", "marginRight": "12px"}),
            html.Div([
                html.Label("🏷️ Category", style={"color": "#a0aec0", "fontSize": "13px"}),
                dcc.Dropdown(
                    id="filter-category",
                    options=[{"label": "All Categories", "value": "ALL"}] +
                            [{"label": c, "value": c} for c in sorted(df_raw["Category"].unique())],
                    value="ALL", clearable=False,
                    style={"background": "#1e2130", "color": "#000"}
                ),
            ], style={"flex": "1", "marginRight": "12px"}),
            html.Div([
                html.Label("👤 Gender", style={"color": "#a0aec0", "fontSize": "13px"}),
                dcc.Dropdown(
                    id="filter-gender",
                    options=[{"label": "All Genders", "value": "ALL"},
                             {"label": "Male",        "value": "Male"},
                             {"label": "Female",      "value": "Female"}],
                    value="ALL", clearable=False,
                    style={"background": "#1e2130", "color": "#000"}
                ),
            ], style={"flex": "1"}),
        ], style={"display": "flex", "marginBottom": "24px",
                  "background": "#1e2130", "padding": "16px", "borderRadius": "10px"}),

        # KPI Cards
        html.Div(id="kpi-cards", style={"display": "flex", "marginBottom": "24px"}),

        # Row 1: Monthly trend + Category pie
        html.Div([
            html.Div([dcc.Graph(id="chart-monthly",  config={"displayModeBar": False})],
                     style={"flex": "2", "background": "#1e2130", "borderRadius": "10px",
                            "padding": "16px", "marginRight": "12px"}),
            html.Div([dcc.Graph(id="chart-category", config={"displayModeBar": False})],
                     style={"flex": "1", "background": "#1e2130", "borderRadius": "10px",
                            "padding": "16px"}),
        ], style={"display": "flex", "marginBottom": "20px"}),

        # Row 2: City + Gender
        html.Div([
            html.Div([dcc.Graph(id="chart-city",   config={"displayModeBar": False})],
                     style={"flex": "1", "background": "#1e2130", "borderRadius": "10px",
                            "padding": "16px", "marginRight": "12px"}),
            html.Div([dcc.Graph(id="chart-gender", config={"displayModeBar": False})],
                     style={"flex": "1", "background": "#1e2130", "borderRadius": "10px",
                            "padding": "16px"}),
        ], style={"display": "flex", "marginBottom": "20px"}),

        # Row 3: RFM Segments + Scatter
        html.Div([
            html.Div([dcc.Graph(id="chart-segments",    config={"displayModeBar": False})],
                     style={"flex": "1", "background": "#1e2130", "borderRadius": "10px",
                            "padding": "16px", "marginRight": "12px"}),
            html.Div([dcc.Graph(id="chart-rfm-scatter", config={"displayModeBar": False})],
                     style={"flex": "1", "background": "#1e2130", "borderRadius": "10px",
                            "padding": "16px"}),
        ], style={"display": "flex", "marginBottom": "20px"}),

        # Row 4: Age + Product
        html.Div([
            html.Div([dcc.Graph(id="chart-age",     config={"displayModeBar": False})],
                     style={"flex": "1", "background": "#1e2130", "borderRadius": "10px",
                            "padding": "16px", "marginRight": "12px"}),
            html.Div([dcc.Graph(id="chart-product", config={"displayModeBar": False})],
                     style={"flex": "1", "background": "#1e2130", "borderRadius": "10px",
                            "padding": "16px"}),
        ], style={"display": "flex"}),

        html.P("ApexPlanet Software Pvt Ltd · Data Analytics Internship · Task 3",
               style={"textAlign": "center", "color": "#4a5568",
                      "marginTop": "32px", "fontSize": "12px"}),
    ]
)

# ── Callbacks ─────────────────────────────────────────────────────────────────
def filter_df(city, category, gender):
    d = df_raw.copy()
    if city     != "ALL": d = d[d["City"]     == city]
    if category != "ALL": d = d[d["Category"] == category]
    if gender   != "ALL": d = d[d["Gender"]   == gender]
    return d

@app.callback(
    Output("kpi-cards",        "children"),
    Output("chart-monthly",    "figure"),
    Output("chart-category",   "figure"),
    Output("chart-city",       "figure"),
    Output("chart-gender",     "figure"),
    Output("chart-segments",   "figure"),
    Output("chart-rfm-scatter","figure"),
    Output("chart-age",        "figure"),
    Output("chart-product",    "figure"),
    Input("filter-city",     "value"),
    Input("filter-category", "value"),
    Input("filter-gender",   "value"),
)
def update_all(city, category, gender):
    d = filter_df(city, category, gender)

    if d.empty:
        empty = go.Figure()
        empty.update_layout(**CHART_LAYOUT, title="No data for selected filters")
        return [html.Div("No data", style=CARD)], *([empty] * 7)

    total_rev   = d["Total_Sales"].sum()
    aov         = d["Total_Sales"].mean()
    n_customers = d["Customer_ID"].nunique()
    repeat_rate = (d.groupby("Customer_ID")["Order_ID"].count() > 1).mean() * 100

    cards = [
        html.Div([html.P("Total Revenue",        style=KPI_LBL),
                  html.P(f"₹{total_rev/1e7:.2f} Cr", style=KPI_NUM)], style=CARD),
        html.Div([html.P("Avg Order Value",       style=KPI_LBL),
                  html.P(f"₹{aov/1e3:.1f}K",     style=KPI_NUM)], style=CARD),
        html.Div([html.P("Unique Customers",      style=KPI_LBL),
                  html.P(f"{n_customers:,}",      style=KPI_NUM)], style=CARD),
        html.Div([html.P("Repeat Customer Rate",  style=KPI_LBL),
                  html.P(f"{repeat_rate:.1f}%",   style=KPI_NUM)], style=CARD),
        html.Div([html.P("Total Orders",          style=KPI_LBL),
                  html.P(f"{len(d):,}",           style=KPI_NUM)], style=CARD),
    ]

    # Monthly trend
    monthly = d.groupby("Month")["Total_Sales"].sum().reset_index().sort_values("Month")
    fig_monthly = px.area(monthly, x="Month", y="Total_Sales",
                          title="📈 Monthly Revenue Trend",
                          labels={"Total_Sales": "Revenue (₹)", "Month": ""},
                          color_discrete_sequence=["#00d4aa"])
    fig_monthly.update_layout(**CHART_LAYOUT)
    fig_monthly.update_traces(fillcolor="rgba(0,212,170,0.2)", line_color="#00d4aa")

    # Category donut
    cat_rev = d.groupby("Category")["Total_Sales"].sum().reset_index()
    fig_cat = px.pie(cat_rev, values="Total_Sales", names="Category",
                     title="🏷️ Revenue by Category", hole=0.45,
                     color_discrete_sequence=px.colors.qualitative.Set2)
    fig_cat.update_layout(**CHART_LAYOUT)
    fig_cat.update_traces(textposition="outside", textinfo="percent+label")

    # City bar
    city_rev = d.groupby("City")["Total_Sales"].sum().reset_index().sort_values("Total_Sales")
    fig_city = px.bar(city_rev, x="Total_Sales", y="City", orientation="h",
                      title="📍 Revenue by City",
                      labels={"Total_Sales": "Revenue (₹)", "City": ""},
                      color="Total_Sales", color_continuous_scale="Teal")
    fig_city.update_layout(**CHART_LAYOUT, coloraxis_showscale=False)

    # Gender donut
    gen = d.groupby("Gender")["Total_Sales"].sum().reset_index()
    fig_gender = px.pie(gen, values="Total_Sales", names="Gender",
                        title="👤 Revenue by Gender", hole=0.45,
                        color_discrete_map={"Male": "#3498db", "Female": "#e91e8c"})
    fig_gender.update_layout(**CHART_LAYOUT)

    # RFM Segment distribution
    seg_counts = rfm["Segment"].value_counts().reset_index()
    seg_counts.columns = ["Segment", "Customers"]
    fig_segments = px.bar(seg_counts, x="Customers", y="Segment", orientation="h",
                          title="👥 Customer Segments (RFM)",
                          color="Segment", color_discrete_map=SEGMENT_COLORS)
    fig_segments.update_layout(**CHART_LAYOUT, showlegend=False)

    # RFM scatter
    rfm_sample = rfm.sample(min(len(rfm), 300), random_state=42)
    fig_rfm = px.scatter(rfm_sample, x="Frequency", y="Monetary",
                         color="Segment", size="Monetary",
                         title="🔍 Frequency vs Monetary (RFM)",
                         labels={"Monetary": "Total Spend (₹)", "Frequency": "No. of Orders"},
                         color_discrete_map=SEGMENT_COLORS, size_max=20)
    fig_rfm.update_layout(**CHART_LAYOUT)

    # Age histogram
    fig_age = px.histogram(d, x="Age", nbins=20, title="🎂 Customer Age Distribution",
                           labels={"Age": "Age (years)", "count": "No. of Orders"},
                           color_discrete_sequence=["#9b59b6"])
    fig_age.update_layout(**CHART_LAYOUT)

    # Product revenue
    prod_rev = d.groupby("Product")["Total_Sales"].sum().reset_index().sort_values("Total_Sales", ascending=False)
    fig_prod = px.bar(prod_rev, x="Product", y="Total_Sales",
                      title="📦 Revenue by Product",
                      labels={"Total_Sales": "Revenue (₹)", "Product": ""},
                      color="Total_Sales", color_continuous_scale="Blues")
    fig_prod.update_layout(**CHART_LAYOUT, coloraxis_showscale=False)

    return cards, fig_monthly, fig_cat, fig_city, fig_gender, fig_segments, fig_rfm, fig_age, fig_prod

if __name__ == "__main__":
    print("\n" + "=" * 55)
    print("  ApexPlanet Sales Intelligence Dashboard")
    print("  Task 3: Deep-Dive Analysis & Dashboarding")
    print("=" * 55)
    print("\n  Opening at: http://127.0.0.1:8050")
    print("  Press Ctrl+C to stop.\n")
    app.run(debug=False, host="127.0.0.1", port=8050)
