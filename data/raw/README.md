# Raw Data Sources

## Included in this repository

### Victorian Rent Data
**File:** `Moving annual median rent by suburb and town - September quarter 2025.xlsx`
**Source:** Victorian Government, Department of Families, Fairness and Housing (DFFH)
**URL:** https://discover.data.vic.gov.au/dataset/rental-report-quarterly-moving-annual-rents-by-suburb
**License:** Creative Commons Attribution 4.0 International
**Description:** Moving annual median rent by suburb and town for Victoria,
broken down by dwelling type (1-bed flat, 2-bed house, etc.) and an
"All properties" aggregate. Quarterly data from March 2000 to September 2025.
Based on bonds lodged with the Residential Tenancies Bond Authority.

## Not included - proprietary data

### Vacancy Rate Data
**File name (if obtained):** `vacancy_rates.csv`
**Source:** SQM Research - Residential Vacancy Rates
**URL:** https://sqmresearch.com.au/graph_vacancy.php
**Why not included:** SQM Research requires a paid subscription for
suburb-level data downloads. Academic access was requested but not
received in time for this submission.

**How to obtain (if access is available):**
1. Go to https://sqmresearch.com.au/graph_vacancy.php
2. Enter a Melbourne suburb's postcode
3. Click "Buy the data behind this chart" to download the CSV
4. Repeat for each suburb, or contact SQM about bulk academic access
5. Save as `data/raw/vacancy_rates.csv` and re-run the cleaning script

**Expected columns (at minimum):**
| Column | Description |
|--------|-------------|
| `suburb` | Suburb name (e.g. "Armadale", "St Kilda") |
| `date` | Date in YYYY-MM-DD format (e.g. "2022-03-01") |
| `vacancy_rate` | Rental vacancy rate as a percentage (e.g. 2.5) |

The cleaning script (`code/01_clean_data.py`) will automatically detect
and merge this file if it is present.
