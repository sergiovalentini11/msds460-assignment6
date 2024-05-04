import pandas as pd
from pulp import *
import numpy as np

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
num_remaining_districts = 5
remaining_target_pop = (total_pop - 1813470 - 709366 - 639797) / num_remaining_districts
print(remaining_target_pop)

# The target population for the remaining counties is 572411. We want our 5 remaining districts to have populations that are close to that number,
# so we will need to include that in our constraints.

# List of the counties
counties = df['state_county'].tolist()
print(counties)

# Excluding the top 3 most populated counties
remaining_counties = counties[3:]
num_remaining_counties = len(remaining_counties)

# List of districts (1st - 5th are accounted for by King, Pierce, and Snohomish counties)
# districts = ['6th', '7th', '8th', '9th', '10th']


# Array with county populations, excluding the 3 largest counties
county_pops = np.array(df['Total_Population'])
removed_counties = [0,1,2]
county_pops = np.delete(county_pops, removed_counties)
print(county_pops)



# Define the IP problem
prob = LpProblem("Redistricting-Problem", LpMinimize)

var_names = [str(i)+str(j) for j in range(1, num_remaining_districts+1) \
                                for i in range(1, num_remaining_counties+1)]

var_names.sort()
print(var_names)

# The Decision Variable is 1 if the county is assigned to the district.
DV_variable_y = LpVariable.matrix("Y", var_names, cat="Binary")
assignment = np.array(DV_variable_y).reshape(36,5)

# The Decision Variable is the population allocated to the district.
DV_variable_x = LpVariable.matrix("X", var_names, cat="Integer",
                                  lowBound=0)
allocation = np.array(DV_variable_x).reshape(36,5)    

# Objective function minimizes the counties split among multiple districts
objective_function = lpSum(assignment) 
prob += objective_function


# Constraints

# Allocate 100% of the population from each county.
for i in range(num_remaining_counties):
    prob += lpSum(allocation[i][j] for j in range(num_remaining_districts)) == county_pops[i] , "Allocate All " + str(i)

# This constraint makes assignment required for allocation.
# sum(county_populations) is the "big M"
# At least 20% of population must be allocated for any assignment.
for i in range(num_remaining_counties): 
    for j in range(num_remaining_districts):
        prob += allocation[i][j] <= sum(county_pops)*assignment[i][j] \
                 , "Allocation assignment " + str(i) + str(j)
        if assignment[i][j] == 1:
            prob += allocation[i][j] >= assignment[i][j]*0.20*county_pops[i] \
                     , "Allocation min " + str(i) + str(j)
            

# Solve the model.
prob.solve() 

print('The model status is: ',LpStatus[prob.status])
print('The objective value is: ', value(objective_function))

for variable in prob.variables():
    print(f"{variable.name} = {variable.varValue}")