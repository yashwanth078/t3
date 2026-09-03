# Deep-Dive Report: Customer Segmentation (RFM Analysis)
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

                     Customers  Avg_Recency  Avg_Frequency  Avg_Monetary  Total_Revenue
Segment                                                                                
At Risk                    218       291.06           1.03     155032.80    33797150.20
Potential Loyalists        218       106.23           1.00     151033.61    32925327.44
Loyal Customers            272       116.29           1.06     114165.61    31053046.67
Champions                   78        61.23           1.40     284395.94    22182883.06
Promising                  116       274.84           1.00     127952.04    14842437.11
Lost                        45       320.13           1.00     102191.00     4598595.17

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
