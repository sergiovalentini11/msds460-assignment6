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

# Target pop = 602469. The largest county is 53033 (aka King County) with 1.8 mil - Seatlle is located here.
# This is roughly 3 target pops. This means this county alone will take up 3 districts. 

# Additionally, county 53053 (Pierce county) has a pop of 709366, and county 53061 (Snohomish county) has a pop of 639797,
# which are both enough for a district of their own. 

# This means 5 districts and 3 counties are accounted for in 'fairness'. 

