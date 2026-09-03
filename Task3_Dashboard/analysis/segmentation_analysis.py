"""
ApexPlanet Software Pvt Ltd — Data Analytics Internship
Task 3: Deep-Dive Analysis — Customer Segmentation (RFM)
---------------------------------------------------------
Performs full RFM segmentation on the sales dataset and saves
all outputs to visuals/ and reports/.

Run from the project root:
    python analysis/segmentation_analysis.py
"""

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

# ── Paths ──────────────────────────────────────────────────────────────────
ROOT      = Path(__file__).parent.parent
RAW_DATA  = ROOT / "data" / "raw" / "ApexPlanet_DataAnalytics_Dataset.xlsx"
PROC_DATA = ROOT / "data" / "processed"
VISUALS   = ROOT / "visuals"
REPORTS   = ROOT / "reports"

for p in [PROC_DATA, VISUALS, REPORTS]:
    p.mkdir(parents=True, exist_ok=True)

SNAPSHOT_DATE = pd.Timestamp("2026-01-02")   # one day after last order

SEGMENT_COLORS = {
    "Champions":           "#2ecc71",
    "Loyal Customers":     "#27ae60",
    "Potential Loyalists": "#1abc9c",
    "At Risk":             "#e74c3c",
    "Lost":                "#c0392b",
    "New Customers":       "#3498db",
    "Promising":           "#9b59b6",
}

# ── 1. Load & prep ──────────────────────────────────────────────────────────
def load_data():
    df = pd.read_excel(RAW_DATA, sheet_name="Sales_Dataset")
    df["Order_Date"] = pd.to_datetime(df["Order_Date"], errors="coerce")
    df["Age"] = df["Age"].fillna(df["Age"].median())
    print(f"Loaded {len(df):,} rows")
    return df

# ── 2. RFM calculation ──────────────────────────────────────────────────────
def compute_rfm(df):
    rfm = df.groupby("Customer_ID").agg(
        Recency   = ("Order_Date",  lambda x: (SNAPSHOT_DATE - x.max()).days),
        Frequency = ("Order_ID",    "count"),
        Monetary  = ("Total_Sales", "sum"),
    ).reset_index()

    rfm["R_Score"] = pd.qcut(rfm["Recency"],  5, labels=[5,4,3,2,1]).astype(int)
    rfm["F_Score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 5, labels=[1,2,3,4,5]).astype(int)
    rfm["M_Score"] = pd.qcut(rfm["Monetary"], 5, labels=[1,2,3,4,5]).astype(int)
    rfm["RFM_Score"] = rfm["R_Score"] * 100 + rfm["F_Score"] * 10 + rfm["M_Score"]

    print(f"RFM computed for {len(rfm):,} customers")
    return rfm

# ── 3. Segment assignment ────────────────────────────────────────────────────
def assign_segment(row):
    r, f, m = row["R_Score"], row["F_Score"], row["M_Score"]
    if r >= 4 and f >= 4 and m >= 4:   return "Champions"
    elif r >= 3 and f >= 3:             return "Loyal Customers"
    elif r >= 3 and f <= 2:             return "Potential Loyalists"
    elif r <= 2 and f >= 3:             return "At Risk"
    elif r == 1 and f == 1:             return "Lost"
    elif r >= 4 and f == 1:             return "New Customers"
    else:                               return "Promising"

# ── 4. Visualisations ────────────────────────────────────────────────────────
sns.set_theme(style="darkgrid")
plt.rcParams.update({"figure.dpi": 150})

def plot_kpi_summary(rfm, df):
    total_rev   = df["Total_Sales"].sum()
    aov         = df["Total_Sales"].mean()
    repeat_rate = (rfm["Frequency"] > 1).sum() / len(rfm) * 100
    rev_per_cust= total_rev / len(rfm)

    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    kpis = [
        ("Total Revenue",        f"₹{total_rev/1e7:.2f} Cr", "#2ecc71"),
        ("Avg Order Value",      f"₹{aov/1e3:.1f}K",          "#3498db"),
        ("Repeat Customer Rate", f"{repeat_rate:.1f}%",        "#e67e22"),
        ("Revenue / Customer",   f"₹{rev_per_cust/1e5:.2f}L", "#9b59b6"),
    ]
    for ax, (title, value, color) in zip(axes, kpis):
        ax.set_facecolor(color)
        ax.text(0.5, 0.6, value, ha="center", va="center",
                fontsize=22, fontweight="bold", color="white", transform=ax.transAxes)
        ax.text(0.5, 0.25, title, ha="center", va="center",
                fontsize=11, color="white", transform=ax.transAxes, wrap=True)
        ax.set_xticks([]); ax.set_yticks([])
        for spine in ax.spines.values(): spine.set_visible(False)
    fig.suptitle("Core KPI Dashboard Snapshot", fontsize=15, fontweight="bold", y=1.02)
    plt.tight_layout()
    fig.savefig(VISUALS / "00_kpi_snapshot.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved: 00_kpi_snapshot.png")

def plot_segment_distribution(rfm):
    counts = rfm["Segment"].value_counts()
    colors = [SEGMENT_COLORS.get(s, "#95a5a6") for s in counts.index]
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(counts.index, counts.values, color=colors)
    ax.bar_label(bars, padding=4, fontsize=11, fontweight="bold")
    ax.set_xlabel("Number of Customers", fontsize=12)
    ax.set_title("Customer Segments — RFM Segmentation", fontsize=14, fontweight="bold", pad=15)
    ax.invert_yaxis()
    plt.tight_layout()
    fig.savefig(VISUALS / "01_segment_distribution.png", dpi=150)
    plt.close()
    print("Saved: 01_segment_distribution.png")

def plot_revenue_by_segment(rfm):
    rev = rfm.groupby("Segment")["Monetary"].sum().sort_values(ascending=False)
    colors = [SEGMENT_COLORS.get(s, "#95a5a6") for s in rev.index]
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(rev.index, rev.values / 1e7, color=colors, edgecolor="white", linewidth=0.5)
    ax.bar_label(bars, fmt="₹%.2f Cr", padding=4, fontsize=10, fontweight="bold")
    ax.set_ylabel("Revenue (₹ Crore)", fontsize=12)
    ax.set_title("Revenue Contribution by Customer Segment", fontsize=14, fontweight="bold", pad=15)
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    fig.savefig(VISUALS / "02_revenue_by_segment.png", dpi=150)
    plt.close()
    print("Saved: 02_revenue_by_segment.png")

def plot_rfm_scatter(rfm):
    fig, ax = plt.subplots(figsize=(10, 7))
    for seg, grp in rfm.groupby("Segment"):
        ax.scatter(grp["Frequency"], grp["Monetary"] / 1e5,
                   label=seg, alpha=0.7, s=60,
                   color=SEGMENT_COLORS.get(seg, "#95a5a6"))
    ax.set_xlabel("Purchase Frequency", fontsize=12)
    ax.set_ylabel("Monetary Value (₹ Lakh)", fontsize=12)
    ax.set_title("Frequency vs Monetary Value by Segment", fontsize=14, fontweight="bold", pad=15)
    ax.legend(loc="upper left", fontsize=9, framealpha=0.8)
    plt.tight_layout()
    fig.savefig(VISUALS / "03_rfm_scatter.png", dpi=150)
    plt.close()
    print("Saved: 03_rfm_scatter.png")

def plot_recency_boxplot(rfm):
    segments_order = list(rfm.groupby("Segment")["Recency"].median().sort_values().index)
    colors = [SEGMENT_COLORS.get(s, "#95a5a6") for s in segments_order]
    fig, ax = plt.subplots(figsize=(12, 6))
    data = [rfm[rfm["Segment"] == s]["Recency"].values for s in segments_order]
    bp = ax.boxplot(data, patch_artist=True, tick_labels=segments_order)
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    ax.set_ylabel("Days Since Last Purchase (Recency)", fontsize=12)
    ax.set_title("Recency Distribution by Customer Segment", fontsize=14, fontweight="bold", pad=15)
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    fig.savefig(VISUALS / "04_recency_boxplot.png", dpi=150)
    plt.close()
    print("Saved: 04_recency_boxplot.png")

def plot_segment_heatmap(rfm):
    pivot = rfm.groupby("Segment")[["R_Score", "F_Score", "M_Score"]].mean().round(2)
    pivot = pivot.sort_values("M_Score", ascending=False)
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.heatmap(pivot, annot=True, fmt=".2f", cmap="YlGn", linewidths=0.5,
                cbar_kws={"label": "Average Score (1–5)"}, ax=ax)
    ax.set_title("Average RFM Scores by Segment", fontsize=14, fontweight="bold", pad=15)
    plt.tight_layout()
    fig.savefig(VISUALS / "05_rfm_heatmap.png", dpi=150)
    plt.close()
    print("Saved: 05_rfm_heatmap.png")

def plot_monthly_revenue_trend(df):
    df2 = df.copy()
    df2["Month"] = df2["Order_Date"].dt.to_period("M")
    monthly = df2.groupby("Month")["Total_Sales"].sum().reset_index()
    monthly["Month_str"] = monthly["Month"].astype(str)
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.fill_between(monthly["Month_str"], monthly["Total_Sales"] / 1e5, alpha=0.3, color="#3498db")
    ax.plot(monthly["Month_str"], monthly["Total_Sales"] / 1e5, marker="o", color="#2980b9", linewidth=2)
    ax.set_ylabel("Revenue (₹ Lakh)", fontsize=12)
    ax.set_title("Monthly Revenue Trend (Jan 2025 – Jan 2026)", fontsize=14, fontweight="bold", pad=15)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    fig.savefig(VISUALS / "06_monthly_trend.png", dpi=150)
    plt.close()
    print("Saved: 06_monthly_trend.png")

# ── 5. Save processed data & report ──────────────────────────────────────────
def save_outputs(rfm, df):
    def safe_mode(x):
        m = x.mode()
        return m.iat[0] if len(m) > 0 else None

    out = rfm.merge(
        df.groupby("Customer_ID").agg(
            City        = ("City",     safe_mode),
            Gender      = ("Gender",   safe_mode),
            Top_Category= ("Category", safe_mode),
        ).reset_index(),
        on="Customer_ID", how="left"
    )
    out.to_csv(PROC_DATA / "rfm_segments.csv", index=False)
    print("Saved: data/processed/rfm_segments.csv")

    seg_summary = rfm.groupby("Segment").agg(
        Customers     = ("Customer_ID", "count"),
        Avg_Recency   = ("Recency",     "mean"),
        Avg_Frequency = ("Frequency",   "mean"),
        Avg_Monetary  = ("Monetary",    "mean"),
        Total_Revenue = ("Monetary",    "sum"),
    ).round(2).sort_values("Total_Revenue", ascending=False)

    report = f"""# Deep-Dive Report: Customer Segmentation (RFM Analysis)
**ApexPlanet Software Pvt Ltd — Data Analytics Internship, Task 3**

## What is RFM?
RFM stands for Recency, Frequency, Monetary — three dimensions that describe how
valuable a customer is to the business:
- **Recency:** How recently did they buy? (lower days = better)
- **Frequency:** How many times have they bought?
- **Monetary:** How much have they spent in total?

Each customer gets a score of 1–5 on each dimension, then is assigned a segment label.

## Dataset
- 1,000 orders | 947 unique customers | ₹13.94 Cr total revenue
- Date range: Jan 2025 – Jan 2026
- Snapshot date (for recency): 2 Jan 2026

## Segment Summary

{seg_summary.to_string()}

## Key Findings

### 1. Champions are few but hugely valuable
Champions (R≥4, F≥4, M≥4) contribute a disproportionate share of total revenue — a classic
Pareto distribution.
**Action:** VIP treatment — early access, exclusive discounts, loyalty programme.

### 2. "At Risk" segment needs immediate attention
At Risk customers used to buy frequently but haven't recently.
**Action:** Win-back campaign — personalised email with time-limited offer (10% off their
most purchased category).

### 3. Repeat Customer Rate is only 5.6%
Only 53 of 947 unique customers placed more than one order.
**Action:** Post-purchase email sequence (Day 3: review request, Day 14: product
recommendation, Day 30: discount voucher).

### 4. New Customers need converting to Loyalists
New Customers (R≥4, F=1) are engaged but haven't returned.
**Action:** Second-purchase incentive within 7–14 days of first order.

### 5. Lost customers are a write-off risk
Lost customers (R=1, F=1) haven't bought in a long time and bought only once.
**Action:** Final re-engagement campaign. If no response, remove from active lists.

## Business Impact Summary
| Segment | Recommended Action | Priority |
|---|---|---|
| Champions | VIP programme, early access | 🟢 High |
| Loyal Customers | Reward & referral programme | 🟢 High |
| At Risk | Win-back campaign | 🔴 Urgent |
| New Customers | Second-purchase incentive | 🟡 Medium |
| Promising | Nurture email sequence | 🟡 Medium |
| Potential Loyalists | Category cross-sell | 🟡 Medium |
| Lost | Final re-engagement, then suppress | ⚪ Low |

## Dashboard
Run `python dashboard/app.py` and open http://127.0.0.1:8050 to explore the live
interactive dashboard with filters for City, Category, and Gender.
"""
    (REPORTS / "deep_dive_report.md").write_text(report, encoding="utf-8")
    print("Saved: reports/deep_dive_report.md")

# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("TASK 3 — Customer Segmentation Analysis (RFM)")
    print("=" * 60)

    df  = load_data()
    rfm = compute_rfm(df)
    rfm["Segment"] = rfm.apply(assign_segment, axis=1)

    print("\nSegment distribution:")
    print(rfm["Segment"].value_counts().to_string())

    print("\nGenerating visualisations...")
    plot_kpi_summary(rfm, df)
    plot_segment_distribution(rfm)
    plot_revenue_by_segment(rfm)
    plot_rfm_scatter(rfm)
    plot_recency_boxplot(rfm)
    plot_segment_heatmap(rfm)
    plot_monthly_revenue_trend(df)

    save_outputs(rfm, df)

    print("\n✅ Done! Run `python dashboard/app.py` to launch the interactive dashboard.")

if __name__ == "__main__":
    main()
