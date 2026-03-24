# Data Codebook — `suburb_quarter_panel.csv`

This file describes the variables in the cleaned analysis-ready dataset
produced by `code/01_clean_data.py`.

## Unit of Observation

Each row is one **suburb in one quarter** (e.g. Bondi in 2022Q1).

## Variables

| Variable | Type | Description |
|----------|------|-------------|
| `suburb` | string | Suburb name, lowercase (e.g. "bondi", "st kilda") |
| `city` | string | City — "sydney" or "melbourne" |
| `quarter` | string | Year-quarter label (e.g. "2022Q1") |
| `vacancy_rate` | float | Average rental vacancy rate for the quarter (%) |
| `median_rent` | float | Average median weekly asking rent for the quarter (AUD) |
| `rent_growth` | float | Quarter-on-quarter percentage change in median rent (%). Null for the first quarter of each suburb. |
| `lag_vacancy_rate` | float | Previous quarter's vacancy rate for the same suburb (%). Null for the first quarter of each suburb. This is the key explanatory variable. |

## Notes

- Vacancy rate and rent are averaged from monthly values within each quarter
- `rent_growth` is calculated as: (rent_t - rent_{t-1}) / rent_{t-1} * 100
- `lag_vacancy_rate` uses a one-quarter lag to test whether vacancy in quarter t-1 predicts rent growth in quarter t
- The first observation for each suburb will have null values for `rent_growth` and `lag_vacancy_rate` (no prior quarter to compare against)
