"""
preprocessing.py
----------------
Reads cleaned data, runs EDA, prints business KPIs,
and exports aggregated CSVs ready for Power BI or SQL load.

Run:  python python/preprocessing.py
"""

import pandas as pd
import numpy as np
import os

CLEANED_PATH   = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "cleaned",   "cleaned_retail_sales.csv")
PROCESSED_DIR  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "processed")
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(os.path.dirname(CLEANED_PATH), exist_ok=True)

# ── Load ───────────────────────────────────────────────────────────────────────
df = pd.read_csv(CLEANED_PATH, parse_dates=["Order_Date"])
print(f"✅ Loaded {len(df):,} rows\n")

# ══════════════════════════════════════════════════════════════════════════════
# A. EXECUTIVE KPIs
# ══════════════════════════════════════════════════════════════════════════════
total_sales   = df["Sales"].sum()
total_profit  = df["Profit"].sum()
total_orders  = df["Order_ID"].nunique()
avg_order_val = df.groupby("Order_ID")["Sales"].sum().mean()
profit_margin = (total_profit / total_sales * 100)

print("=" * 50)
print("  EXECUTIVE KPI SUMMARY")
print("=" * 50)
print(f"  Total Sales        : ₹{total_sales:>13,.2f}")
print(f"  Total Profit       : ₹{total_profit:>13,.2f}")
print(f"  Profit Margin      :  {profit_margin:>12.1f}%")
print(f"  Total Orders       :  {total_orders:>13,}")
print(f"  Avg Order Value    : ₹{avg_order_val:>13,.2f}")
print("=" * 50)

# ══════════════════════════════════════════════════════════════════════════════
# B. MONTHLY SALES TREND
# ══════════════════════════════════════════════════════════════════════════════
monthly = (
    df.groupby(["Year", "Month"])
      .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"), Orders=("Order_ID", "count"))
      .reset_index()
      .sort_values(["Year", "Month"])
)
monthly["MoM_Sales_Growth_%"] = monthly["Sales"].pct_change().mul(100).round(2)
monthly.to_csv(f"{PROCESSED_DIR}/monthly_sales_trend.csv", index=False)
print("\n📅 Monthly sales trend → monthly_sales_trend.csv")

# ══════════════════════════════════════════════════════════════════════════════
# C. REGIONAL PERFORMANCE
# ══════════════════════════════════════════════════════════════════════════════
regional = (
    df.groupby("Region")
      .agg(Sales=("Sales","sum"), Profit=("Profit","sum"), Orders=("Order_ID","count"))
      .reset_index()
)
regional["Profit_Margin_%"] = (regional["Profit"] / regional["Sales"] * 100).round(2)
regional.to_csv(f"{PROCESSED_DIR}/regional_performance.csv", index=False)
print("🗺️  Regional performance → regional_performance.csv")
print(regional.to_string(index=False))

# ══════════════════════════════════════════════════════════════════════════════
# D. CATEGORY PERFORMANCE
# ══════════════════════════════════════════════════════════════════════════════
category = (
    df.groupby(["Category", "Sub_Category"])
      .agg(Sales=("Sales","sum"), Profit=("Profit","sum"), Qty=("Quantity","sum"))
      .reset_index()
      .sort_values("Sales", ascending=False)
)
category["Profit_Margin_%"] = (category["Profit"] / category["Sales"] * 100).round(2)
category.to_csv(f"{PROCESSED_DIR}/category_performance.csv", index=False)
print("\n📦 Category performance → category_performance.csv")

# ══════════════════════════════════════════════════════════════════════════════
# E. TOP 10 CUSTOMERS
# ══════════════════════════════════════════════════════════════════════════════
customers = (
    df.groupby(["Customer_ID", "Customer_Name", "Segment"])
      .agg(Total_Sales=("Sales","sum"),
           Total_Profit=("Profit","sum"),
           Order_Count=("Order_ID","count"))
      .reset_index()
      .sort_values("Total_Sales", ascending=False)
)
# Repeat customer flag (bought more than once)
customers["Is_Repeat"] = (customers["Order_Count"] > 1).astype(int)
repeat_rate = customers["Is_Repeat"].mean() * 100
print(f"\n👥 Repeat Customer Rate: {repeat_rate:.1f}%")

customers.head(10).to_csv(f"{PROCESSED_DIR}/top10_customers.csv", index=False)
print("   Top 10 customers → top10_customers.csv")

# ══════════════════════════════════════════════════════════════════════════════
# F. TOP 10 PRODUCTS
# ══════════════════════════════════════════════════════════════════════════════
products = (
    df.groupby(["Product_ID", "Product_Name", "Category"])
      .agg(Total_Sales=("Sales","sum"), Total_Profit=("Profit","sum"), Units_Sold=("Quantity","sum"))
      .reset_index()
      .sort_values("Total_Sales", ascending=False)
)
products.head(10).to_csv(f"{PROCESSED_DIR}/top10_products.csv", index=False)
print("🏆 Top 10 products → top10_products.csv")

# ══════════════════════════════════════════════════════════════════════════════
# G. DISCOUNT IMPACT ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
discount_impact = (
    df.groupby("Discount_Bucket")
      .agg(Avg_Sales=("Sales","mean"),
           Avg_Profit=("Profit","mean"),
           Avg_Margin=("Profit_Margin_%","mean"),
           Count=("Order_ID","count"))
      .reset_index()
      .round(2)
)
discount_impact.to_csv(f"{PROCESSED_DIR}/discount_impact.csv", index=False)
print("💸 Discount impact → discount_impact.csv")
print(discount_impact.to_string(index=False))

# ══════════════════════════════════════════════════════════════════════════════
# H. PAYMENT MODE BREAKDOWN
# ══════════════════════════════════════════════════════════════════════════════
payment = (
    df.groupby("Payment_Mode")
      .agg(Orders=("Order_ID","count"), Sales=("Sales","sum"))
      .reset_index()
      .sort_values("Orders", ascending=False)
)
payment.to_csv(f"{PROCESSED_DIR}/payment_mode.csv", index=False)
print("\n💳 Payment breakdown → payment_mode.csv")

print("\n✅ All processed files saved to data/processed/")
