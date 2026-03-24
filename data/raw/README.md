# Raw Data — Acquisition Instructions

The raw data files are **not included** in this repository because they come
from proprietary/paywalled sources. Follow the steps below to obtain them.

## 1. Vacancy Rate Data

**Source:** SQM Research — Residential Vacancy Rates
**URL:** https://sqmresearch.com.au/graph_vacancy.php

**Steps:**
1. Go to the SQM Research vacancy rates page
2. Select each suburb in Sydney and Melbourne that you want to include
3. Set the date range to cover 2018–2025
4. Download or copy the monthly vacancy rate data
5. Save as `vacancy_rates.csv` in this folder (`data/raw/`)

**Expected columns (at minimum):**
| Column | Description |
|--------|-------------|
| `suburb` | Suburb name (e.g. "Bondi", "St Kilda") |
| `city` | City — either "sydney" or "melbourne" |
| `date` | Date in YYYY-MM-DD format (e.g. "2022-03-01") |
| `vacancy_rate` | Rental vacancy rate as a percentage (e.g. 2.5) |

## 2. Median Asking Rent Data

**Source:** SQM Research — Weekly Rents, or Domain rental reports
**URL:** https://sqmresearch.com.au/weekly-rents.php

**Steps:**
1. Go to the SQM Research weekly rents page (or Domain)
2. Select the same suburbs as above
3. Set the date range to 2018–2025
4. Download median weekly asking rent data
5. Save as `median_rents.csv` in this folder (`data/raw/`)

**Expected columns (at minimum):**
| Column | Description |
|--------|-------------|
| `suburb` | Suburb name (must match vacancy data) |
| `city` | City — either "sydney" or "melbourne" |
| `date` | Date in YYYY-MM-DD format |
| `median_rent` | Median weekly asking rent in AUD (e.g. 550) |

## Why is the raw data not included?

SQM Research is a paid subscription service. The data cannot be freely
redistributed. If you have access to an SQM Research subscription (e.g.
through Monash University library), you can download the data directly.
