# Data Codebook - `suburb_quarter_panel.csv`

This file describes the variables in the cleaned dataset produced by
`code/01_clean_data.py`.

## Unit of Observation

Each row is one **Melbourne suburb in one quarter** (e.g. Armadale in 2022Q1).

## Variables

| Variable | Type | Description |
|----------|------|-------------|
| `region` | string | Melbourne sub-region (e.g. "Inner Melbourne", "Southern Melbourne") |
| `suburb` | string | Suburb or suburb group name (e.g. "Armadale", "CBD-St Kilda Rd") |
| `quarter` | string | Year-quarter label (e.g. "2018Q1", "2025Q3") |
| `median_rent` | float | Moving annual median weekly rent in AUD, all property types combined |
| `rent_growth` | float | Quarter-on-quarter percentage change in median rent (%). Null for the first quarter of each suburb. |
| `lag_median_rent` | float | Previous quarter's median rent for the same suburb (AUD). Null for the first quarter of each suburb. |
| `bond_count` | int | Moving annual count of new bond lodgements in the suburb (= number of new tenancies started over the prior 4 quarters). Used as a proxy for rental market activity / turnover. |
| `lag_bond_count` | float | Previous quarter's bond count. Null for first quarter of each suburb. |
| `log_bond_count` | float | Natural log of (bond_count + 1). Used as the regressor of interest in the FE model: a 1% increase in turnover is associated with a beta percentage-point change in rent growth. |
| `lag_log_bond_count` | float | Previous quarter's log_bond_count. Null for the first quarter of each suburb. |


**Note on vacancy data:** The original research design called for suburb-level
rental vacancy rate data from SQM Research (`vacancy_rate`, `lag_vacancy_rate`).
This data is paid and could not be obtained, so we use `log_bond_count` as a
proxy for rental market activity instead - it is a free, suburb-level,
quarterly measure derived from the same DFFH bond-lodgement dataset that
provides the rent figures. The cleaning script will still merge SQM data if
a `vacancy_rates.csv` is added to `data/raw/`.

## Coverage

- **Geography:** 110 Melbourne metro suburbs across 9 regions
- **Time period:** 2018Q1 to 2025Q3 (31 quarters)
- **Total rows:** 3,410 suburb-quarter observations

## Notes

- Median rent and bond count are both "moving annual" figures: each value
  reflects the prior 4 quarters of bond lodgements with the Victorian RTBA.
  This smooths quarter-to-quarter noise but means changes are gradual.
- `rent_growth` = (rent_t - rent_{t-1}) / rent_{t-1} * 100
- `log_bond_count` = ln(bond_count + 1); the +1 handles any zero counts.
- Suburbs with "-" in the raw data (too few bonds) are treated as missing.
- The data source groups some adjacent suburbs together (e.g. "Albert Park-Middle Park-West St Kilda").
