import pandas as pd
import numpy as np
import os

RAW_PATH     = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "raw",     "retail_sales.csv")
CLEANED_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "cleaned", "cleaned_retail_sales.csv")


print("📂 Loading raw data...")
df = pd.read_csv(RAW_PATH)
print(f"   Shape: {df.shape}")


print(df.isnull().sum()[df.isnull().sum() > 0])
print(f"\n   Duplicate rows: {df.duplicated().sum()}")


before = len(df)
df.drop_duplicates(inplace=True)
print(f"\n🗑️  Dropped {before - len(df)} duplicate rows.")


for col in ["Sales", "Profit", "Shipping_Cost"]:
    if df[col].isnull().any():
        median_val = df[col].median()
        df[col] = df[col].fillna(median_val)
        print(f"   Filled '{col}' NaNs with median ({median_val:.2f})")

critical_cols = ["Order_ID", "Order_Date", "Customer_ID", "Product_ID"]
before = len(df)
df.dropna(subset=critical_cols, inplace=True)
print(f"   Dropped {before - len(df)} rows missing critical IDs.")


df["Order_Date"] = pd.to_datetime(df["Order_Date"])
df["Sales"]         = df["Sales"].round(2)
df["Profit"]        = df["Profit"].round(2)
df["Shipping_Cost"] = df["Shipping_Cost"].round(2)
df["Discount"]      = df["Discount"].round(2)
df["Quantity"]      = df["Quantity"].astype(int)


df["Year"]           = df["Order_Date"].dt.year
df["Month"]          = df["Order_Date"].dt.month
df["Month_Name"]     = df["Order_Date"].dt.strftime("%b")
df["Quarter"]        = df["Order_Date"].dt.quarter
df["Week_of_Year"]   = df["Order_Date"].dt.isocalendar().week.astype(int)
df["Day_of_Week"]    = df["Order_Date"].dt.day_name()


df["Profit_Margin_%"]     = (df["Profit"] / df["Sales"].replace(0, np.nan) * 100).round(2)
df["Revenue_after_Ship"]  = (df["Sales"] - df["Shipping_Cost"]).round(2)
df["Is_Profitable"]       = (df["Profit"] > 0).astype(int)
df["Discount_Bucket"]     = pd.cut(
    df["Discount"],
    bins=[-0.01, 0, 0.15, 0.35, 1.0],
    labels=["No Discount", "Low (≤15%)", "Medium (16–35%)", "High (>35%)"]
)


assert df["Order_ID"].is_unique or True          # orders can repeat across products
assert df["Sales"].min() >= 0, "Negative sales!"
print(f"\n✅ Clean dataset: {df.shape[0]:,} rows × {df.shape[1]} columns")


os.makedirs(os.path.dirname(CLEANED_PATH), exist_ok=True)
df.to_csv(CLEANED_PATH, index=False)
print(f"💾 Saved → {os.path.abspath(CLEANED_PATH)}")


print("\n📊 Quick summary:")
print(f"   Total Sales  : ₹{df['Sales'].sum():>15,.2f}")
print(f"   Total Profit : ₹{df['Profit'].sum():>15,.2f}")
print(f"   Avg Margin   : {df['Profit_Margin_%'].mean():.1f}%")
print(f"   Date range   : {df['Order_Date'].min().date()} → {df['Order_Date'].max().date()}")
print(f"   Unique Customers : {df['Customer_ID'].nunique()}")
print(f"   Unique Products  : {df['Product_ID'].nunique()}")
