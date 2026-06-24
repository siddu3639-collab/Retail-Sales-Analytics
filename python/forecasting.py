"""
forecasting.py
--------------
Builds a simple but effective sales forecast using:
  - 3-month moving average
  - Linear trend extrapolation (12-month forecast horizon)

Exports forecast_results.csv and prints accuracy metrics.

Run:  python python/forecasting.py
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

CLEANED_PATH  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "cleaned",   "cleaned_retail_sales.csv")
PROCESSED_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "processed")
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(os.path.dirname(CLEANED_PATH), exist_ok=True)

# ── Load & aggregate monthly ───────────────────────────────────────────────────
df = pd.read_csv(CLEANED_PATH, parse_dates=["Order_Date"])
monthly = (
    df.groupby(df["Order_Date"].dt.to_period("M"))
      .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
      .reset_index()
)
monthly["Order_Date"] = monthly["Order_Date"].dt.to_timestamp()
monthly = monthly.sort_values("Order_Date").reset_index(drop=True)

# ── Moving averages ────────────────────────────────────────────────────────────
monthly["MA_3"]  = monthly["Sales"].rolling(window=3).mean().round(2)
monthly["MA_6"]  = monthly["Sales"].rolling(window=6).mean().round(2)
monthly["MA_12"] = monthly["Sales"].rolling(window=12).mean().round(2)

# ── Linear trend forecast ──────────────────────────────────────────────────────
x = np.arange(len(monthly))
y = monthly["Sales"].values

# Fit line through all historical data
coeffs = np.polyfit(x, y, deg=1)  # coeffs[0]=slope, coeffs[1]=intercept
slope, intercept = coeffs
print(f"📈 Trend: Sales {'increasing' if slope > 0 else 'decreasing'} by ₹{abs(slope):,.0f}/month")

# Forecast next 12 months
forecast_periods = 12
last_date  = monthly["Order_Date"].max()
future_x   = np.arange(len(monthly), len(monthly) + forecast_periods)
future_dates = pd.date_range(
    start=last_date + pd.DateOffset(months=1),
    periods=forecast_periods,
    freq="MS"
)
future_sales = (slope * future_x + intercept).clip(min=0)

# Seasonal adjustment: compute average seasonal index from historical data
monthly["Month"] = monthly["Order_Date"].dt.month
seasonal_idx = monthly.groupby("Month")["Sales"].mean()
seasonal_idx = seasonal_idx / seasonal_idx.mean()  # normalize

future_months    = future_dates.month
seasonal_factors = future_months.map(seasonal_idx).values
future_sales_adj = (future_sales * seasonal_factors).round(2)

# Build forecast dataframe
forecast_df = pd.DataFrame({
    "Order_Date":          future_dates,
    "Forecast_Sales":      future_sales.round(2),
    "Forecast_Sales_Adj":  future_sales_adj,   # seasonally adjusted
    "Type":                "Forecast",
})

# Build historical dataframe for easy comparison
historical_df = monthly[["Order_Date", "Sales", "MA_3", "MA_6"]].copy()
historical_df["Type"] = "Actual"
historical_df.rename(columns={"Sales": "Forecast_Sales"}, inplace=True)
historical_df["Forecast_Sales_Adj"] = np.nan

# Combine
full_df = pd.concat([historical_df, forecast_df], ignore_index=True)
full_df.to_csv(f"{PROCESSED_DIR}/forecast_results.csv", index=False)

# ── Accuracy (MAE on last 3 months hold-out) ───────────────────────────────────
hold_out = monthly.tail(3)
hold_x   = np.arange(len(monthly) - 3, len(monthly))
hold_pred = slope * hold_x + intercept
mae = np.mean(np.abs(hold_out["Sales"].values - hold_pred))
mape = np.mean(np.abs((hold_out["Sales"].values - hold_pred) / hold_out["Sales"].values)) * 100

print(f"   Hold-out MAE  : ₹{mae:,.0f}")
print(f"   Hold-out MAPE : {mape:.1f}%")

print("\n📅 12-Month Forecast:")
print(f"{'Month':<15} {'Trend Forecast':>18} {'Seasonal Adj':>16}")
print("-" * 52)
for _, row in forecast_df.iterrows():
    print(f"{row['Order_Date'].strftime('%b %Y'):<15} ₹{row['Forecast_Sales']:>16,.2f} ₹{row['Forecast_Sales_Adj']:>14,.2f}")

print(f"\n💾 Saved → {PROCESSED_DIR}/forecast_results.csv")
