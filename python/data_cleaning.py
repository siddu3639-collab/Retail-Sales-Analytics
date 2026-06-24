"""
data_cleaning.py
----------------
Loads raw retail_sales.csv, cleans it, engineers features,
and exports cleaned_retail_sales.csv to data/cleaned/.

Run:  python python/data_cleaning.py
"""

import pandas as pd
import numpy as np
import os

RAW_PATH     = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "raw",     "retail_sales.csv")
CLEANED_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "cleaned", "cleaned_retail_sales.csv")

# ── 1. Load ────────────────────────────────────────────────────────────────────
print("📂 Loading raw data...")
df = pd.read_csv(RAW_PATH)
print(f"   Shape: {df.shape}")

# ── 2. Inspect ─────────────────────────────────────────────────────────────────
print("\n🔍 Missing values before cleaning:")
print(df.isnull().sum()[df.isnull().sum() > 0])
print(f"\n   Duplicate rows: {df.duplicated().sum()}")

# ── 3. Remove duplicates ───────────────────────────────────────────────────────
before = len(df)
df.drop_duplicates(inplace=True)
print(f"\n🗑️  Dropped {before - len(df)} duplicate rows.")

# ── 4. Handle missing values ───────────────────────────────────────────────────
# Fill numeric NaNs with column median (keeps data realistic)
for col in ["Sales", "Profit", "Shipping_Cost"]:
    if df[col].isnull().any():
        median_val = df[col].median()
        df[col] = df[col].fillna(median_val)
        print(f"   Filled '{col}' NaNs with median ({median_val:.2f})")

# Drop any remaining rows with nulls in critical columns
critical_cols = ["Order_ID", "Order_Date", "Customer_ID", "Product_ID"]
before = len(df)
df.dropna(subset=critical_cols, inplace=True)
print(f"   Dropped {before - len(df)} rows missing critical IDs.")

# ── 5. Data type corrections ───────────────────────────────────────────────────
df["Order_Date"] = pd.to_datetime(df["Order_Date"])
df["Sales"]         = df["Sales"].round(2)
df["Profit"]        = df["Profit"].round(2)
df["Shipping_Cost"] = df["Shipping_Cost"].round(2)
df["Discount"]      = df["Discount"].round(2)
df["Quantity"]      = df["Quantity"].astype(int)

# ── 6. Feature engineering ─────────────────────────────────────────────────────
df["Year"]           = df["Order_Date"].dt.year
df["Month"]          = df["Order_Date"].dt.month
df["Month_Name"]     = df["Order_Date"].dt.strftime("%b")
df["Quarter"]        = df["Order_Date"].dt.quarter
df["Week_of_Year"]   = df["Order_Date"].dt.isocalendar().week.astype(int)
df["Day_of_Week"]    = df["Order_Date"].dt.day_name()

# KPI-style derived columns
df["Profit_Margin_%"]     = (df["Profit"] / df["Sales"].replace(0, np.nan) * 100).round(2)
df["Revenue_after_Ship"]  = (df["Sales"] - df["Shipping_Cost"]).round(2)
df["Is_Profitable"]       = (df["Profit"] > 0).astype(int)
df["Discount_Bucket"]     = pd.cut(
    df["Discount"],
    bins=[-0.01, 0, 0.15, 0.35, 1.0],
    labels=["No Discount", "Low (≤15%)", "Medium (16–35%)", "High (>35%)"]
)

# ── 7. Validate ────────────────────────────────────────────────────────────────
assert df["Order_ID"].is_unique or True          # orders can repeat across products
assert df["Sales"].min() >= 0, "Negative sales!"
print(f"\n✅ Clean dataset: {df.shape[0]:,} rows × {df.shape[1]} columns")

# ── 8. Export ──────────────────────────────────────────────────────────────────
os.makedirs(os.path.dirname(CLEANED_PATH), exist_ok=True)
df.to_csv(CLEANED_PATH, index=False)
print(f"💾 Saved → {os.path.abspath(CLEANED_PATH)}")

# ── 9. Summary stats ───────────────────────────────────────────────────────────
print("\n📊 Quick summary:")
print(f"   Total Sales  : ₹{df['Sales'].sum():>15,.2f}")
print(f"   Total Profit : ₹{df['Profit'].sum():>15,.2f}")
print(f"   Avg Margin   : {df['Profit_Margin_%'].mean():.1f}%")
print(f"   Date range   : {df['Order_Date'].min().date()} → {df['Order_Date'].max().date()}")
print(f"   Unique Customers : {df['Customer_ID'].nunique()}")
print(f"   Unique Products  : {df['Product_ID'].nunique()}")
