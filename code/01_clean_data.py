"""
01_clean_data.py - ECC3479 Research Project
Author: Anton Kozlovsky (36194239)

PURPOSE:
This script takes the raw Victorian Government rent data (a wide Excel file
with quarters as columns) and reshapes it into a long, tidy panel dataset
ready for analysis. The DFFH file contains TWO numbers per quarter per
suburb: the median rent AND the count of new bond lodgements (= number of
new tenancies started that quarter). We extract both.

The bond-lodgement count is used as a proxy for rental market turnover
(how many new tenancies are starting). It is the closest free, suburb-level,
quarterly measure of rental market activity available - true vacancy rate
data (e.g. from SQM Research) is paid and could not be obtained.

If vacancy rate data from SQM Research is later added (as a CSV in
data/raw/vacancy_rates.csv), the script merges it in automatically.

HOW IT WORKS (step by step):
1. Reads the VIC rent Excel file ("All properties" sheet)
2. Parses the messy header rows to extract quarter labels
3. Keeps only Melbourne suburbs (drops regional VIC and "Group Total" rows)
4. Reshapes from wide format (one column per quarter) to long format
   (one row per suburb per quarter), keeping BOTH median rent and bond count
5. Calculates quarter-on-quarter rent growth
6. Creates lagged columns (previous quarter's rent and bond count)
7. Computes log(bond_count) for use as an explanatory variable
8. If vacancy data exists, merges it in and creates lagged vacancy rate
9. Saves the final panel to data/clean/suburb_quarter_panel.csv
"""

import pandas as pd
import numpy as np
import os

# ── 1. CONFIGURATION ──────────────────────────────────────────────────
# These are the file paths. The rent file should already be in data/raw/.
# The vacancy file is optional - the script works without it.

RENT_FILE = "data/raw/Moving annual median rent by suburb and town - September quarter 2025.xlsx"
VACANCY_FILE = "data/raw/vacancy_rates.csv"  # Add this file when you have it
OUTPUT_FILE = "data/clean/suburb_quarter_panel.csv"

# We only want Melbourne metro suburbs, not regional VIC.
# These are the region names in the Excel file that count as "Melbourne".
MELBOURNE_REGIONS = [
    "Inner Melbourne",
    "Inner Eastern Melbourne",
    "Southern Melbourne",
    "Outer Western Melbourne",
    "North Western Melbourne",
    "North Eastern Melbourne",
    "Outer Eastern Melbourne",
    "South Eastern Melbourne",
    "Mornington Peninsula",
]

# We only want data from 2018 onwards (to match our research period).
START_YEAR = 2018

# ── 2. LOAD THE RAW RENT DATA ────────────────────────────────────────
# The Excel file has a messy layout:
#   Row 0: title row
#   Row 1: quarter labels (e.g. "Mar 2000", "Jun 2000", ...) - each
#          quarter appears TWICE (once for Count, once for Median)
#   Row 2: "Count" or "Median" labels
#   Row 3 onwards: actual data
#   Column 0: region name (only filled for the first suburb in each region)
#   Column 1: suburb name
#   Column 2 onwards: the data values
#
# We read with header=None so pandas doesn't misinterpret the messy headers.

print("Loading VIC rent data...")
raw = pd.read_excel(RENT_FILE, sheet_name="All properties", header=None)
print(f"  Raw file: {raw.shape[0]} rows x {raw.shape[1]} columns")

# ── 3. PARSE THE QUARTER LABELS ─────────────────────────────────────
# Row 1 has the quarter names (e.g. "Mar 2000") and row 2 says whether
# that column is "Count" or "Median". We want BOTH:
#   - "Median" = median weekly rent in that suburb-quarter
#   - "Count"  = number of new bond lodgements (= new tenancies) that quarter
#
# We loop through columns 2 onwards and build TWO lists:
# one for the median columns and one for the count columns.

quarter_labels = raw.iloc[1, 2:]   # e.g. "Mar 2000", "Mar 2000", "Jun 2000", ...
col_types = raw.iloc[2, 2:]        # e.g. "Count", "Median", "Count", "Median", ...

median_cols = []        # column indices that hold "Median" (rent) values
median_quarters = []    # the quarter label for each median column
count_cols = []         # column indices that hold "Count" (bond lodgement) values
count_quarters = []     # the quarter label for each count column

for i, (quarter, col_type) in enumerate(zip(quarter_labels, col_types)):
    col_idx = i + 2  # +2 because we skipped columns 0 and 1
    if col_type == "Median":
        median_cols.append(col_idx)
        median_quarters.append(quarter)
    elif col_type == "Count":
        count_cols.append(col_idx)
        count_quarters.append(quarter)

print(f"  Found {len(median_cols)} quarters of median rent data")
print(f"  Found {len(count_cols)} quarters of bond-lodgement count data")
print(f"  Date range: {median_quarters[0]} to {median_quarters[-1]}")

# ── 4. EXTRACT SUBURB DATA ──────────────────────────────────────────
# Column 0 has the region name, but only on the FIRST row of each region.
# We use "forward fill" to copy the region name down to all suburbs
# in that region.

data = raw.iloc[3:].copy()  # skip the 3 header rows
data.columns = range(len(data.columns))  # reset column names to numbers

# Forward-fill the region column (column 0)
# This means: if a cell is empty, copy the value from the cell above it.
data[0] = data[0].ffill()

# Rename columns 0 and 1 for clarity
data = data.rename(columns={0: "region", 1: "suburb"})

# ── 5. FILTER TO MELBOURNE SUBURBS ONLY ─────────────────────────────
# We only keep rows where the region is in our Melbourne list.
# We also drop "Group Total" rows (these are subtotals, not real suburbs).

data = data[data["region"].isin(MELBOURNE_REGIONS)]
data = data[data["suburb"] != "Group Total"]

print(f"  Melbourne suburbs: {data.shape[0]}")

# ── 6. RESHAPE FROM WIDE TO LONG FORMAT ─────────────────────────────
# Right now each quarter is a separate column (wide format).
# We want one row per suburb per quarter (long format).
# Think of it like unpivoting a pivot table in Excel.
#
# We need BOTH the median rent AND the bond-lodgement count for each
# suburb-quarter. Median and Count columns alternate in the spreadsheet,
# and we already collected their column indices in step 3.
#
# We'll build a list of small DataFrames (one per quarter) that includes
# both the median rent and the bond count, then stack them.

# Pair up median and count columns by quarter (they should align since
# quarters appear in the same order for both lists)
assert median_quarters == count_quarters, (
    "Median and Count columns are not aligned by quarter - check the file format"
)

rows = []
for med_col, cnt_col, quarter_label in zip(median_cols, count_cols, median_quarters):
    # For each quarter, grab the suburb info + that quarter's rent + count
    temp = data[["region", "suburb"]].copy()
    temp["quarter_label"] = quarter_label
    temp["median_rent"] = data[med_col]
    temp["bond_count"] = data[cnt_col]
    rows.append(temp)

# pd.concat stacks all the small DataFrames on top of each other
panel = pd.concat(rows, ignore_index=True)

# ── 7. PARSE QUARTER DATES ──────────────────────────────────────────
# Convert "Mar 2000" into a proper date so we can filter and sort by time.
# pd.to_datetime turns text into a date object.
# .dt.to_period("Q") converts to a quarter period like "2000Q1".

panel["date"] = pd.to_datetime(panel["quarter_label"], format="%b %Y")
panel["quarter"] = panel["date"].dt.to_period("Q").astype(str)
panel["year"] = panel["date"].dt.year

# ── 8. FILTER TO 2018 ONWARDS ───────────────────────────────────────
panel = panel[panel["year"] >= START_YEAR]

# ── 9. CLEAN UP THE NUMERIC VALUES ──────────────────────────────────
# Some cells have "-" meaning too few observations. We replace these
# with NaN (Not a Number) which means "missing" in pandas.
# Then we convert to float so we can do math on the columns.

panel["median_rent"] = pd.to_numeric(panel["median_rent"], errors="coerce")
panel["bond_count"] = pd.to_numeric(panel["bond_count"], errors="coerce")

# ── 10. SORT AND CALCULATE DERIVED VARIABLES ────────────────────────
# Sort by suburb then date, so each suburb's data runs chronologically.
panel = panel.sort_values(["suburb", "date"]).reset_index(drop=True)

# Quarter-on-quarter rent growth (%): (this_q - last_q) / last_q * 100.
# groupby("suburb") ensures we only compare within the same suburb.
panel["rent_growth"] = (
    panel.groupby("suburb")["median_rent"].pct_change() * 100
)

# Lagged rent column (last quarter's rent).
panel["lag_median_rent"] = panel.groupby("suburb")["median_rent"].shift(1)

# Lagged bond count (last quarter's number of new bond lodgements).
panel["lag_bond_count"] = panel.groupby("suburb")["bond_count"].shift(1)

# log(bond_count) - useful for regression because:
#   1. Bond counts are right-skewed (many small suburbs, few large ones)
#   2. With FE, the coefficient on log(bond_count) becomes a semi-elasticity:
#      a 1% increase in bond lodgements is associated with a beta-percentage
#      point change in rent growth.
# We add 1 before taking the log to handle suburb-quarters with zero bonds.
panel["log_bond_count"] = np.log(panel["bond_count"] + 1)
panel["lag_log_bond_count"] = panel.groupby("suburb")["log_bond_count"].shift(1)

# ── 11. MERGE VACANCY DATA (if available) ───────────────────────────
# If you've downloaded vacancy data from SQM Research and saved it as
# a CSV, this section merges it into the panel.

if os.path.exists(VACANCY_FILE):
    print(f"\nLoading vacancy data from {VACANCY_FILE}...")
    vacancy = pd.read_csv(VACANCY_FILE)

    # Standardise suburb names to lowercase for matching
    vacancy["suburb"] = vacancy["suburb"].str.strip().str.lower()
    panel["suburb_lower"] = panel["suburb"].str.strip().str.lower()

    # Parse vacancy dates and create quarter column
    vacancy["date"] = pd.to_datetime(vacancy["date"])
    vacancy["quarter"] = vacancy["date"].dt.to_period("Q").astype(str)

    # Average monthly vacancy to quarterly
    vacancy_quarterly = (
        vacancy
        .groupby(["suburb", "quarter"], as_index=False)["vacancy_rate"]
        .mean()
    )

    # Merge on suburb (lowercase) and quarter
    panel = panel.merge(
        vacancy_quarterly,
        left_on=["suburb_lower", "quarter"],
        right_on=["suburb", "quarter"],
        how="left",
        suffixes=("", "_vac"),
    )

    # Clean up duplicate columns from merge
    if "suburb_vac" in panel.columns:
        panel = panel.drop(columns=["suburb_vac"])
    if "suburb_lower" in panel.columns:
        panel = panel.drop(columns=["suburb_lower"])

    # Create lagged vacancy rate
    panel = panel.sort_values(["suburb", "date"]).reset_index(drop=True)
    panel["lag_vacancy_rate"] = (
        panel.groupby("suburb")["vacancy_rate"].shift(1)
    )

    print(f"  Vacancy data merged. Non-null vacancy values: {panel['vacancy_rate'].notna().sum()}")
else:
    print(f"\n  Note: No vacancy file found at {VACANCY_FILE}")
    print("  The output will contain rent data only.")
    print("  Add vacancy data later by saving it to that path and re-running.")

# ── 12. SELECT FINAL COLUMNS AND SAVE ───────────────────────────────
# Pick only the columns we need, in a clear order.

keep_cols = [
    "region", "suburb", "quarter",
    "median_rent", "rent_growth", "lag_median_rent",
    "bond_count", "lag_bond_count", "log_bond_count", "lag_log_bond_count",
]

# Add vacancy columns if they exist
if "vacancy_rate" in panel.columns:
    keep_cols += ["vacancy_rate", "lag_vacancy_rate"]

panel = panel[keep_cols]

# Drop the date helper column and save
panel.to_csv(OUTPUT_FILE, index=False)

print(f"\nDone! Saved to {OUTPUT_FILE}")
print(f"  {panel.shape[0]} rows x {panel.shape[1]} columns")
print(f"  {panel['suburb'].nunique()} suburbs")
print(f"  {panel['quarter'].nunique()} quarters")
print(f"  Columns: {list(panel.columns)}")
