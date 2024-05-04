import pandas as pd
from pulp import *

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

# The target pop for each district is 602468. County 53033 (King County) has a pop of 1.8 mil, enough for 3 target populations (it contains Seattle).
# So we should assign 3 districts to this county. 

# 53053 (Pierce County), and 53061 (Snohomish County) also have pops greater than the target pop, so I believe we can auto-assign 
# them their own districts too. This leaves us with 36 counties to fill 5 districts, which gives us 180 decision variables.

# With these counties excluded, we need a new target population for the remaining counties. 
remaining_target_pop = (total_pop - 1813470 - 709366 - 639797) / 5
print(remaining_target_pop)

# The target population for the remaining counties is 572411. We want our 5 remaining districts to have populations that are close to that number,
# so we will need to include that in our constraints.

# List of the counties
counties = df['state_county'].tolist()

# List of districts (1st - 5th are accounted for by King, Pierce, and Snohomish counties)
districts = ['6th', '7th', '8th', '9th', '10th']

# Dictionary with counties and their populations
county_pops = df.set_index('state_county')['Total_Population'].to_dict()

# Create the binary variables for each county/district pair
designate = pulp.LpVariable.dicts("Designate", [(c, d) for c in counties for d in districts], 0, 1, cat='Integer')

# Define the IP problem
prob = LpProblem("problem", LpMinimize)


# Objective function 


# Constraint: each county is assigned only 1 district
for c in counties:
    prob += pulp.lpSum(designate[(c, d)] for d in districts) == 1


# Constraint: each district has roughly equal population
for d in districts:
    prob += pulp.lpSum(designate[(c, d)] * county_pops[c] for c in counties) >= 0.9 * remaining_target_pop
    prob += pulp.lpSum(designate[(c, d)] * county_pops[c] for c in counties) <= 1.1 * remaining_target_pop

