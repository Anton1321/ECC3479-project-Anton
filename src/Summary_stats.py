import pandas as pd

# 1. Read the cleaned data
df = pd.read_csv('data/clean/cleaned_sample_data.csv')

# 2. Calculate mean and standard deviation for key variables, grouped by state
summary_stats = df.groupby('state')[['unemployment_rate', 'participation_rate']].agg(['mean', 'std'])

# 3. Print the results clearly
print("Summary Statistics by State:")
print(summary_stats)