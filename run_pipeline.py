"""
run_pipeline.py
---------------
Master script: runs the full data pipeline end-to-end.

Usage:
    python run_pipeline.py              # uses generated sample data
    python run_pipeline.py --real       # expects data/raw/retail_sales.csv to exist

Steps:
    1. (Optional) Generate 10K sample data
    2. Clean & validate data
    3. Feature engineering & KPI aggregations
    4. Sales forecasting
    5. Load into SQLite database
    6. Print project summary
"""

import subprocess
import sys
import os
import time

BASE_DIR = os.path.dirname(__file__)
PY       = sys.executable

STEPS = [
    ("🔧 Generating sample data...",   "python/generate_sample_data.py"),
    ("🧹 Cleaning data...",            "python/data_cleaning.py"),
    ("📊 Running preprocessing...",    "python/preprocessing.py"),
    ("📈 Running forecasting...",      "python/forecasting.py"),
    ("🗄️  Loading into database...",   "python/load_to_db.py"),
]

use_real_data = "--real" in sys.argv

print("=" * 60)
print("  RETAIL SALES ANALYTICS PIPELINE")
print("=" * 60)

if use_real_data:
    raw_path = os.path.join(BASE_DIR, "data", "raw", "retail_sales.csv")
    if not os.path.exists(raw_path):
        print(f"❌  --real flag set but {raw_path} not found.")
        print("    Place your CSV at data/raw/retail_sales.csv and retry.")
        sys.exit(1)
    STEPS = STEPS[1:]  # skip data generation
    print("📂 Using real data from data/raw/retail_sales.csv\n")
else:
    print("🤖 Using generated sample data (10,000 rows)\n")

for label, script in STEPS:
    print(label)
    start = time.time()
    result = subprocess.run(
        [PY, os.path.join(BASE_DIR, script)],
        capture_output=False,
        text=True,
    )
    elapsed = time.time() - start
    if result.returncode != 0:
        print(f"❌  Step failed: {script}")
        sys.exit(1)
    print(f"   ✅ Done ({elapsed:.1f}s)\n")

print("=" * 60)
print("  PIPELINE COMPLETE!")
print("=" * 60)
print("""
Next steps:
  1. Open Power BI Desktop
  2. Get Data → CSV → data/cleaned/cleaned_retail_sales.csv
     OR Get Data → SQLite → data/retail_sales.db
  3. Import DAX measures from reports/powerbi_dax_measures.txt
  4. Build your dashboard pages!

Processed files (for Power BI tables):
  data/processed/monthly_sales_trend.csv
  data/processed/regional_performance.csv
  data/processed/category_performance.csv
  data/processed/top10_customers.csv
  data/processed/top10_products.csv
  data/processed/forecast_results.csv
  data/processed/discount_impact.csv
  data/processed/payment_mode.csv
""")
