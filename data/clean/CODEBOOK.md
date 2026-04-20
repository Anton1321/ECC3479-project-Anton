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


**Note:** The research design also calls for suburb-level vacancy rate
data from SQM Research (`vacancy_rate`, `lag_vacancy_rate`). This data
could not be obtained due to access restrictions. The cleaning script
will add these columns automatically if the data becomes available.
See `data/raw/README.md` for details.

## Coverage

- **Geography:** 110 Melbourne metro suburbs across 9 regions
- **Time period:** 2018Q1 to 2025Q3 (31 quarters)
- **Total rows:** 3,410 suburb-quarter observations

## Notes

- Median rent is a "moving annual" figure based on bonds lodged with the Victorian RTBA
- `rent_growth` = (rent_t - rent_{t-1}) / rent_{t-1} * 100
- Suburbs with "-" in the raw data (too few bonds) are treated as missing
- The data source groups some adjacent suburbs together (e.g. "Albert Park-Middle Park-West St Kilda")
