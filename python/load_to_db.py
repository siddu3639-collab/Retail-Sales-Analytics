"""
load_to_db.py
-------------
Loads cleaned CSV data into a SQLite database (works out of the box,
no server needed). Switch to MySQL/PostgreSQL by changing the
connection string — the rest of the code is identical.

SQLite   : python python/load_to_db.py
MySQL    : set DB_URL below, then run
PostgreSQL: same

Run AFTER: data_cleaning.py
"""

import pandas as pd
import sqlite3
import os

CLEANED_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "cleaned", "cleaned_retail_sales.csv")
DB_PATH      = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "retail_sales.db")

# ── For MySQL / PostgreSQL (uncomment and install sqlalchemy + driver) ─────────
# from sqlalchemy import create_engine
# engine = create_engine("mysql+pymysql://user:password@localhost/retail_db")
# engine = create_engine("postgresql+psycopg2://user:password@localhost/retail_db")
# conn = engine.connect()

# ── SQLite (default — no setup needed) ────────────────────────────────────────
conn = sqlite3.connect(DB_PATH)
print(f"📂 Connected to SQLite → {os.path.abspath(DB_PATH)}")

# ── Load cleaned CSV ───────────────────────────────────────────────────────────
df = pd.read_csv(CLEANED_PATH, parse_dates=["Order_Date"])
print(f"✅ Loaded {len(df):,} rows from cleaned CSV")

# ── Build normalized tables ───────────────────────────────────────────────────
customers_df = df[["Customer_ID", "Customer_Name", "Segment", "Region", "State"]].drop_duplicates()
products_df  = df[["Product_ID", "Category", "Sub_Category", "Product_Name"]].drop_duplicates()
orders_df    = df[[
    "Order_ID", "Order_Date", "Customer_ID", "Product_ID",
    "Sales", "Quantity", "Discount", "Profit", "Shipping_Cost", "Payment_Mode"
]].copy()
orders_df["Order_Date"] = orders_df["Order_Date"].dt.strftime("%Y-%m-%d")

# ── Write to DB ────────────────────────────────────────────────────────────────
customers_df.to_sql("Customers", conn, if_exists="replace", index=False)
products_df.to_sql("Products",  conn, if_exists="replace", index=False)
orders_df.to_sql("Orders",      conn, if_exists="replace", index=False)

print(f"   Customers : {len(customers_df):,} rows loaded")
print(f"   Products  : {len(products_df):,} rows loaded")
print(f"   Orders    : {len(orders_df):,} rows loaded")

# ── Quick verification ─────────────────────────────────────────────────────────
cur = conn.cursor()

cur.execute("SELECT ROUND(SUM(Sales),2) FROM Orders")
print(f"\n📊 Verification — Total Sales in DB: ₹{cur.fetchone()[0]:,}")

cur.execute("""
    SELECT c.Region, ROUND(SUM(o.Sales),2) AS Sales
    FROM Orders o JOIN Customers c ON o.Customer_ID = c.Customer_ID
    GROUP BY c.Region ORDER BY Sales DESC
""")
print("\n🗺️  Sales by Region:")
for row in cur.fetchall():
    print(f"   {row[0]:<10} ₹{row[1]:>12,.2f}")

conn.close()
print(f"\n✅ Database ready → {os.path.abspath(DB_PATH)}")
print("   Open with DB Browser for SQLite or connect Power BI via ODBC.")
