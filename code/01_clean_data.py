"""
01_clean_data.py — ECC3479 Research Project
Author: Anton Kozlovsky (36194239)

PURPOSE:
This script takes the raw Victorian Government rent data (a wide Excel file
with quarters as columns) and reshapes it into a long, tidy panel dataset
ready for analysis. It also calculates rent growth and a lagged rent column.

Once vacancy rate data is obtained from SQM Research, the script merges
that in too.

HOW IT WORKS (step by step):
1. Reads the VIC rent Excel file ("All properties" sheet)
2. Parses the messy header rows to extract quarter labels
3. Keeps only Melbourne suburbs (drops regional VIC and "Group Total" rows)
4. Reshapes from wide format (one column per quarter) to long format
   (one row per suburb per quarter)
5. Calculates quarter-on-quarter rent growth
6. Creates a lagged rent column (previous quarter's median rent)
7. If vacancy data exists, merges it in and creates lagged vacancy rate
8. Saves the final panel to data/clean/suburb_quarter_panel.csv
"""

import pandas as pd
import os

# ── 1. CONFIGURATION ──────────────────────────────────────────────────
# These are the file paths. The rent file should already be in data/raw/.
# The vacancy file is optional — the script works without it.

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
#   Row 1: quarter labels (e.g. "Mar 2000", "Jun 2000", ...) — each
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
# that column is "Count" or "Median". We want only the "Median" columns.
#
# We loop through columns 2 onwards and build a list of (quarter, type) pairs.

quarter_labels = raw.iloc[1, 2:]   # e.g. "Mar 2000", "Mar 2000", "Jun 2000", ...
col_types = raw.iloc[2, 2:]        # e.g. "Count", "Median", "Count", "Median", ...

# Find which column indices hold "Median" values
median_cols = []        # column index in the original DataFrame
median_quarters = []    # the quarter label for that column

for i, (quarter, col_type) in enumerate(zip(quarter_labels, col_types)):
    if col_type == "Median":
        col_idx = i + 2  # +2 because we skipped columns 0 and 1
        median_cols.append(col_idx)
        median_quarters.append(quarter)

print(f"  Found {len(median_cols)} quarters of median rent data")
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
# We'll build a list of small DataFrames (one per quarter) and stack them.

rows = []
for col_idx, quarter_label in zip(median_cols, median_quarters):
    # For each quarter, grab the suburb info + that quarter's median rent
    temp = data[["region", "suburb"]].copy()
    temp["quarter_label"] = quarter_label
    temp["median_rent"] = data[col_idx]
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

# ── 9. CLEAN UP THE MEDIAN RENT VALUES ──────────────────────────────
# Some cells have "-" meaning too few observations. We replace these
# with NaN (Not a Number) which means "missing" in pandas.
# Then we convert to float so we can do math on the column.

panel["median_rent"] = pd.to_numeric(panel["median_rent"], errors="coerce")

# ── 10. SORT AND CALCULATE RENT GROWTH ──────────────────────────────
# Sort by suburb then date, so each suburb's data runs chronologically.
panel = panel.sort_values(["suburb", "date"]).reset_index(drop=True)

# pct_change() calculates: (this_quarter - last_quarter) / last_quarter
# We multiply by 100 to get a percentage (e.g. 2.5 means 2.5% growth).
# groupby("suburb") ensures we only compare within the same suburb.
panel["rent_growth"] = (
    panel.groupby("suburb")["median_rent"].pct_change() * 100
)

# Also create a lagged rent column (last quarter's rent).
panel["lag_median_rent"] = panel.groupby("suburb")["median_rent"].shift(1)

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

keep_cols = ["region", "suburb", "quarter", "median_rent", "rent_growth", "lag_median_rent"]

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
