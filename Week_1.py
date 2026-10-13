import pandas as pd
from datetime import date
import glob
import os

START_YEAR, START_MONTH = 2024, 1
 
today = date.today()

if today.month == 1:
    END_YEAR, END_MONTH = today.year - 1, 12
else:
    END_YEAR, END_MONTH = today.year, today.month - 1
 
year_months = []
y, m = START_YEAR, START_MONTH
while (y, m) <= (END_YEAR, END_MONTH):
    year_months.append(f"{y}{m:02d}")
    m += 1
    if m > 12:
        m = 1
        y += 1
 
print(f"Pulling months: {year_months[0]} through {year_months[-1]} "
      f"({len(year_months)} months)")


DATA_DIR = "/Users/brianzhao/csv" 
 
 
def load_and_concat(prefix, year_months, data_dir):
    frames = []
    missing = []
    row_counts_by_month = {}
 
    for ym in year_months:
        standard_name = f"{prefix}{ym}.csv"
        filled_name = f"{prefix}{ym}_filled.csv"
        standard_path = os.path.join(data_dir, standard_name)
        filled_path = os.path.join(data_dir, filled_name)
 
        if os.path.exists(standard_path):
            filepath, filename = standard_path, standard_name
        elif os.path.exists(filled_path):
            filepath, filename = filled_path, filled_name
        else:
            filepath, filename = None, standard_name
 
        if filepath:
            df = pd.read_csv(filepath, low_memory=False)
            row_counts_by_month[ym] = len(df)
            frames.append(df)
        else:
            missing.append(filename)
 
    if missing:
        print(f"WARNING: missing {len(missing)} file(s) for {prefix}: {missing}")
 
    combined = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    return combined, row_counts_by_month


sold, sold_counts_by_month = load_and_concat("CRMLSSold", year_months, DATA_DIR)
 
sold_rows_before_concat = sum(sold_counts_by_month.values())
sold_rows_after_concat = len(sold)
 
# SOLD row counts (CONCATENATION)
# Rows before concat: 736770
# Rows after concat: 736770


listing, listing_counts_by_month = load_and_concat("CRMLSListing", year_months, DATA_DIR)
 
listing_rows_before_concat = sum(listing_counts_by_month.values())
listing_rows_after_concat = len(listing)
 
# LISTING row counts (CONCATENATION)
# Rows before concat: 1021977
# Rows after concat: 1021977

OUTPUT_DIR = "/Users/brianzhao/py"
os.makedirs(OUTPUT_DIR, exist_ok=True)

sold.to_csv(os.path.join(OUTPUT_DIR, "combined_sold_all_types.csv"), index=False)

sold_rows_before_filter = len(sold)
sold_residential = sold[sold["PropertyType"] == "Residential"].copy()
sold_rows_after_filter = len(sold_residential)
 
# SOLD row counts (RESIDENTIAL FILTER)
# Rows before Residential filter: 736770
# Rows after Residential filter: 495407
 
listing_rows_before_filter = len(listing)
listing_residential = listing[listing["PropertyType"] == "Residential"].copy()
listing_rows_after_filter = len(listing_residential)
 
# LISTING row counts (RESIDENTIAL FILTER)
# Rows before Residential filter: 1021977
# Rows after Residential filter:  649783

print(f"SOLD    -- before concat: {sold_rows_before_concat}, after concat: {sold_rows_after_concat}, "
      f"before filter: {sold_rows_before_filter}, after Residential filter: {sold_rows_after_filter}")
print(f"LISTING -- before concat: {listing_rows_before_concat}, after concat: {listing_rows_after_concat}, "
      f"before filter: {listing_rows_before_filter}, after Residential filter: {listing_rows_after_filter}")

sold_out_path = os.path.join(OUTPUT_DIR, "combined_sold_residential.csv")
listing_out_path = os.path.join(OUTPUT_DIR, "combined_listing_residential.csv")
 
sold_residential.to_csv(sold_out_path, index=False)
listing_residential.to_csv(listing_out_path, index=False)