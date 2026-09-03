# Core KPI Definitions — ApexPlanet Sales Dataset
**Task 3: Deep-Dive Analysis & Interactive Dashboarding**

---

## KPI 1: Total Revenue (₹)
**Formula:** `SUM(Total_Sales)`
**Business Rationale:** The single most important top-line health metric. Tracks how much money the business is generating from orders. Used as the headline number in every executive dashboard.
**Current Value:** ₹13.94 Cr across 1,000 orders

---

## KPI 2: Average Order Value (AOV) (₹)
**Formula:** `SUM(Total_Sales) / COUNT(Order_ID)`
**Business Rationale:** Measures how much revenue a typical transaction generates. A rising AOV means customers are buying more units or choosing higher-priced products. Used to benchmark the effectiveness of upsell/cross-sell campaigns.
**Current Value:** ₹1,39,399 per order

---

## KPI 3: Repeat Customer Rate (%)
**Formula:** `(COUNT of Customer_IDs appearing more than once / COUNT(DISTINCT Customer_ID)) × 100`
**Business Rationale:** Measures customer loyalty and retention effectiveness. A higher rate means customers are coming back — which is cheaper than acquiring new ones.
**Current Value:** 5.6% (53 out of 947 unique customers placed more than one order)

---

## KPI 4: Revenue per Customer (₹)
**Formula:** `SUM(Total_Sales) / COUNT(DISTINCT Customer_ID)`
**Business Rationale:** Combines purchase frequency and order size into one number. Unlike AOV (per-transaction), this measures per-customer lifetime value within the dataset period.
**Current Value:** ₹1,47,201 per unique customer

---

## KPI 5: Category Revenue Contribution (%)
**Formula:** `SUM(Total_Sales WHERE Category = X) / SUM(Total_Sales) × 100`
**Business Rationale:** Shows which product categories drive the business. Helps prioritize inventory investment, marketing spend, and supplier negotiations.

| Category    | Revenue    | Share  |
|-------------|------------|--------|
| Electronics | ₹5.09 Cr   | 36.5%  |
| Education   | ₹3.22 Cr   | 23.1%  |
| Furniture   | ₹2.74 Cr   | 19.7%  |
| Fashion     | ₹1.26 Cr   | 9.1%   |
| Grocery     | ₹0.94 Cr   | 6.7%   |

---

*These KPIs are surfaced live in the interactive Plotly Dash dashboard (`dashboard/app.py`),
where they update dynamically as filters (City, Category, Gender) are applied.*
