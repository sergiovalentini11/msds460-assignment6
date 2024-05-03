import pandas as pd

# Read in the census data
df = pd.read_csv("001. Data Bases/washington_census_data.csv")

# Sorting df in order of population
df = df.sort_values(by='Total_Population', ascending=False)
print(df.head())

# We need to determine the target population that our 10 districts need to aim for. 
# We can determine this by taking the total population of Washington and dividing by 10.
total_pop = df['Total_Population'].sum()
print(total_pop)

target_pop = total_pop / 10
print(target_pop)



