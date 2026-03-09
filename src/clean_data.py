import pandas as pd

# ---------------------------------------------------------
# Data Cleaning Script for ECC3479 Project
# This script reads the raw ABS labour force data, converts 
# the quarter format, calculates the employment rate, and 
# sorts the data for easier analysis.
# ---------------------------------------------------------

print("Starting data cleaning process...")

# 1. Load the raw data
df = pd.read_csv('data/raw/sample_data.csv')

# 2. Create 'quarter_num' converting Q1-Q4 to 1-4
# This removes the 'Q' and turns the remaining number into an integer
df['quarter_num'] = df['quarter'].str.replace('Q', '').astype(int)

# 3. Create 'emp_rate' (100 - unemployment_rate)
df['emp_rate'] = 100 - df['unemployment_rate']

# 4. Sort rows by state, then year, then quarter_num
df = df.sort_values(by=['state', 'year', 'quarter_num'])

# 5. Save the cleaned output to the clean folder (without overwriting raw data)
df.to_csv('data/clean/cleaned_sample_data.csv', index=False)

print("Success! Cleaned data saved to data/clean/cleaned_sample_data.csv")