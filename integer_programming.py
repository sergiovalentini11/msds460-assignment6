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

# The target pop for each district is 602468. County 53033 (King County) has a pop of 1.8 mil, enough for 3 target populations.
# So we should assign 3 districts to this county. 

# 53053 (Pierce County), and 53061 (Snohomish County) also have pops greater than the target pop, so I believe we can auto-assign 
# them their own districts too. This leaves us with 36 counties to fill 5 districts, which gives us 180 decision variables.

# With these counties excluded, we need a new target population for the remaining counties. 
remaining_target_pop = (total_pop - 1813470 - 709366 - 639797) / 5
print(remaining_target_pop)

# The target population for the remaining counties is 572411. We want our 5 remaining districts to have populations that are close to that number,
# so we will need to include that in our constraints.

