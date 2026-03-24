"""
01_clean_data.py — ECC3479 Research Project
Author: Anton Kozlovsky (36194239)

This script takes the two raw CSV files (vacancy rates and median rents),
cleans them, merges them into a single suburb-quarter panel, and saves
the result to data/clean/.

HOW IT WORKS (step by step):
1. Reads the raw vacancy rate CSV and the raw rent CSV from data/raw/
2. Standardises suburb names so they match across both datasets
3. Converts monthly data into quarterly averages
4. Merges the two datasets on suburb + quarter
5. Calculates rent growth (% change from previous quarter)
6. Creates a lagged vacancy rate column (previous quarter's vacancy)
7. Saves the final panel to data/clean/suburb_quarter_panel.csv
"""

import pandas as pd

# ── 1. CONFIGURATION ──────────────────────────────────────────────────
# Update these filenames to match exactly what you downloaded.
# The files should be placed inside data/raw/ before running this script.

VACANCY_FILE = "data/raw/vacancy_rates.csv"
RENT_FILE = "data/raw/median_rents.csv"
OUTPUT_FILE = "data/clean/suburb_quarter_panel.csv"

# ── 2. LOAD RAW DATA ─────────────────────────────────────────────────
# pd.read_csv() reads a CSV file into a DataFrame (like a spreadsheet).
# You may need to adjust column names below to match your actual CSVs.

print("Loading raw data...")

vacancy_raw = pd.read_csv(VACANCY_FILE)
rent_raw = pd.read_csv(RENT_FILE)

print(f"  Vacancy data: {vacancy_raw.shape[0]} rows, {vacancy_raw.shape[1]} columns")
print(f"  Rent data:    {rent_raw.shape[0]} rows, {rent_raw.shape[1]} columns")

# ── 3. STANDARDISE SUBURB NAMES ──────────────────────────────────────
# Different data sources may spell suburbs differently (e.g. "St Kilda"
# vs "ST KILDA" vs "St. Kilda"). We convert everything to lowercase and
# strip extra whitespace so that merging works correctly.

vacancy_raw["suburb"] = vacancy_raw["suburb"].str.strip().str.lower()
rent_raw["suburb"] = rent_raw["suburb"].str.strip().str.lower()

# ── 4. PARSE DATES AND CREATE QUARTER COLUMN ─────────────────────────
# We convert the date column to a proper datetime format, then extract
# the year and quarter. This lets us group monthly data into quarters.
#
# pd.to_datetime() turns text like "2022-03-01" into a date object.
# .dt.to_period("Q") converts that date into a quarter like "2022Q1".

vacancy_raw["date"] = pd.to_datetime(vacancy_raw["date"])
vacancy_raw["quarter"] = vacancy_raw["date"].dt.to_period("Q")

rent_raw["date"] = pd.to_datetime(rent_raw["date"])
rent_raw["quarter"] = rent_raw["date"].dt.to_period("Q")

# ── 5. AGGREGATE TO SUBURB-QUARTER LEVEL ─────────────────────────────
# If your raw data is monthly, we average to get one value per quarter.
# .groupby() splits the data by suburb + quarter, then .mean() averages
# the numeric columns within each group.
# .reset_index() turns the grouped result back into a normal table.

vacancy_quarterly = (
    vacancy_raw
    .groupby(["suburb", "city", "quarter"], as_index=False)["vacancy_rate"]
    .mean()
)

rent_quarterly = (
    rent_raw
    .groupby(["suburb", "city", "quarter"], as_index=False)["median_rent"]
    .mean()
)

print(f"  Vacancy quarterly: {vacancy_quarterly.shape[0]} suburb-quarter rows")
print(f"  Rent quarterly:    {rent_quarterly.shape[0]} suburb-quarter rows")

# ── 6. MERGE VACANCY AND RENT DATA ──────────────────────────────────
# pd.merge() joins two tables together like a VLOOKUP in Excel.
# We match rows where suburb, city, AND quarter are the same.
# how="inner" means we only keep rows that appear in BOTH datasets.

panel = pd.merge(
    vacancy_quarterly,
    rent_quarterly,
    on=["suburb", "city", "quarter"],
    how="inner",
)

print(f"  Merged panel: {panel.shape[0]} suburb-quarter observations")

# ── 7. SORT BY SUBURB AND TIME ───────────────────────────────────────
# Sorting ensures each suburb's data runs in chronological order,
# which is needed for calculating changes over time in the next step.

panel = panel.sort_values(["suburb", "quarter"]).reset_index(drop=True)

# ── 8. CALCULATE RENT GROWTH ────────────────────────────────────────
# pct_change() calculates the percentage change from the previous row.
# We multiply by 100 so the result is in percentage points (e.g. 2.5%).
# groupby("suburb") makes sure we only compare within the same suburb
# (we don't want to compare the last quarter of one suburb with the
# first quarter of the next suburb).

panel["rent_growth"] = (
    panel.groupby("suburb")["median_rent"].pct_change() * 100
)

# ── 9. CREATE LAGGED VACANCY RATE ───────────────────────────────────
# shift(1) moves each value down by one row within each suburb group.
# This gives us "last quarter's vacancy rate" on each row.
# This is our key explanatory variable: does LAST quarter's vacancy
# predict THIS quarter's rent change?

panel["lag_vacancy_rate"] = panel.groupby("suburb")["vacancy_rate"].shift(1)

# ── 10. CONVERT QUARTER BACK TO STRING FOR CSV ──────────────────────
# Period objects don't save nicely to CSV, so we convert to strings
# like "2022Q1" before saving.

panel["quarter"] = panel["quarter"].astype(str)

# ── 11. SAVE CLEANED PANEL ──────────────────────────────────────────
panel.to_csv(OUTPUT_FILE, index=False)

print(f"\nDone! Cleaned panel saved to {OUTPUT_FILE}")
print(f"Final dataset: {panel.shape[0]} rows, {panel.shape[1]} columns")
print(f"Columns: {list(panel.columns)}")
