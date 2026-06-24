"""
generate_sample_data.py
-----------------------
Generates a realistic retail_sales.csv with 10,000 rows
and saves it to data/raw/retail_sales.csv
Run this first if you don't have a real dataset.
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

random.seed(42)
np.random.seed(42)

# ── Constants ──────────────────────────────────────────────────────────────────
N = 10_000
START_DATE = datetime(2021, 1, 1)
END_DATE   = datetime(2023, 12, 31)

SEGMENTS  = ["Consumer", "Corporate", "Home Office"]
REGIONS   = ["East", "West", "South", "North"]
STATES    = {
    "East":  ["New York", "Pennsylvania", "New Jersey", "Massachusetts", "Connecticut"],
    "West":  ["California", "Washington", "Oregon", "Nevada", "Arizona"],
    "South": ["Texas", "Florida", "Georgia", "North Carolina", "Virginia"],
    "North": ["Illinois", "Michigan", "Ohio", "Minnesota", "Wisconsin"],
}
CATEGORIES = {
    "Furniture":        ["Chairs", "Tables", "Bookcases", "Furnishings"],
    "Technology":       ["Phones", "Accessories", "Machines", "Copiers"],
    "Office Supplies":  ["Labels", "Paper", "Binders", "Art", "Envelopes", "Fasteners", "Storage"],
}
PAYMENT_MODES = ["Card", "Cash", "UPI", "Net Banking"]

# ── Helpers ────────────────────────────────────────────────────────────────────
def random_date(start, end):
    return start + timedelta(days=random.randint(0, (end - start).days))

def make_customer_pool(n=500):
    first = ["James","Mary","Robert","Patricia","John","Jennifer","Michael","Linda",
             "David","Barbara","William","Susan","Richard","Jessica","Joseph","Sarah"]
    last  = ["Smith","Johnson","Williams","Brown","Jones","Miller","Davis","Wilson",
             "Moore","Taylor","Anderson","Thomas","Jackson","White","Harris","Martin"]
    customers = []
    for i in range(n):
        seg    = random.choice(SEGMENTS)
        region = random.choice(REGIONS)
        state  = random.choice(STATES[region])
        customers.append({
            "Customer_ID":   f"CUST-{i+1:04d}",
            "Customer_Name": f"{random.choice(first)} {random.choice(last)}",
            "Segment":       seg,
            "Region":        region,
            "State":         state,
        })
    return customers

def make_product_pool(n=200):
    adjectives = ["Premium","Basic","Pro","Ultra","Classic","Smart","Eco","Elite"]
    nouns = {
        "Furniture":       ["Chair","Desk","Shelf","Cabinet","Lamp","Sofa","Stool"],
        "Technology":      ["Laptop","Phone","Tablet","Monitor","Printer","Camera","Speaker"],
        "Office Supplies": ["Pen Set","Notebook","Stapler","Folder","Tape","Scissors","Marker"],
    }
    products = []
    for i in range(n):
        cat     = random.choice(list(CATEGORIES.keys()))
        sub_cat = random.choice(CATEGORIES[cat])
        noun    = random.choice(nouns[cat])
        products.append({
            "Product_ID":    f"PROD-{i+1:04d}",
            "Category":      cat,
            "Sub_Category":  sub_cat,
            "Product_Name":  f"{random.choice(adjectives)} {noun} {random.randint(100,999)}",
        })
    return products

# ── Generate ───────────────────────────────────────────────────────────────────
customers = make_customer_pool(500)
products  = make_product_pool(200)

rows = []
for i in range(N):
    cust = random.choice(customers)
    prod = random.choice(products)
    date = random_date(START_DATE, END_DATE)

    # Base price varies by category
    base_price = {
        "Furniture":       random.uniform(100, 2000),
        "Technology":      random.uniform(50,  3000),
        "Office Supplies": random.uniform(5,   200),
    }[prod["Category"]]

    qty      = random.randint(1, 10)
    discount = round(random.choice([0, 0, 0, 0.1, 0.2, 0.3, 0.4, 0.5]), 2)
    sales    = round(base_price * qty * (1 - discount), 2)

    # Profit margin is hurt by high discounts
    profit_pct = random.uniform(0.05, 0.35) - (discount * 0.8)
    profit     = round(sales * profit_pct, 2)

    shipping   = round(random.uniform(3, 50) * qty, 2)

    rows.append({
        "Order_ID":      f"ORD-{i+1:06d}",
        "Order_Date":    date.strftime("%Y-%m-%d"),
        "Customer_ID":   cust["Customer_ID"],
        "Customer_Name": cust["Customer_Name"],
        "Segment":       cust["Segment"],
        "Region":        cust["Region"],
        "State":         cust["State"],
        "Product_ID":    prod["Product_ID"],
        "Category":      prod["Category"],
        "Sub_Category":  prod["Sub_Category"],
        "Product_Name":  prod["Product_Name"],
        "Sales":         sales,
        "Quantity":      qty,
        "Discount":      discount,
        "Profit":        profit,
        "Shipping_Cost": shipping,
        "Payment_Mode":  random.choice(PAYMENT_MODES),
    })

df = pd.DataFrame(rows)

# Inject a few missing / duplicate rows to make cleaning realistic
missing_idx = random.sample(range(N), 80)
for idx in missing_idx:
    col = random.choice(["Sales", "Profit", "Shipping_Cost"])
    df.at[idx, col] = np.nan

dup_idx = random.sample(range(N), 30)
df = pd.concat([df, df.iloc[dup_idx]], ignore_index=True)

script_dir = os.path.dirname(os.path.abspath(__file__))
out_path = os.path.join(script_dir, "..", "data", "raw", "retail_sales.csv")
os.makedirs(os.path.dirname(out_path), exist_ok=True)
df.to_csv(out_path, index=False)
print(f"✅  Generated {len(df):,} rows → {os.path.abspath(out_path)}")
