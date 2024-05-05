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


# Trying to incorporate the adjacency constraints
#
#
#
# read the adjacency file
adjacency = pd.read_csv('001. Data Bases/washington_counties_adjacency.csv')

# drop the rows where parent_state_county is equal to child_state_county
adjacency = adjacency[adjacency['parent_state_county'] != adjacency['child_state_county']]

# n_counties equals the unique parent_state_county
#n_counties = adjacency['parent_state_county'].nunique()

# n_districts = 10


# assing to an integer from 1 to 39 each county
adjacency['parent_state_county'] = adjacency['parent_state_county'].astype('category')
adjacency['parent_state_county'] = adjacency['parent_state_county'].cat.codes + 1

# save in a new temp_df the unique values of parent_state_county and parent_county_desc
temp_df = adjacency[['parent_state_county', 'parent_county_desc']].drop_duplicates()

# rename the columns
temp_df.columns = ['child_state_county_code', 'child_state_county_desc']

# left join the adjacency with the temp_df
# using parent_county_desc as the key
adjacency = adjacency.merge(temp_df, on='child_state_county_desc', how='left')

# force str to have 1 leading zero if the number is less than 10
variable_names = [str(i).zfill(2)+'_'+str(j).zfill(2) for j in range(1, num_remaining_districts+1) \
    for i in range(1, num_remaining_counties+1)]

variable_names.sort()

Adj_DV_variable_y = LpVariable.matrix("Y", variable_names, cat="Binary")

assignment = np.array(Adj_DV_variable_y).reshape(36,5)

adjacency[adjacency['parent_state_county'] == 1]['child_state_county_code']
#
#
#
#



# Define the IP problem
prob = LpProblem("Redistricting-Problem", LpMinimize)

# Define the Decision Variables, and add a leading 0 to the county number if it is less than 10
var_names = [str(i).zfill(2)+'_'+str(j) for j in range(1, num_remaining_districts+1) \
                                for i in range(1, num_remaining_counties+1)]


var_names.sort()
print(var_names)

# The Decision Variable is 1 if the county is assigned to the district.
# The output variables will look like Y_102 = 1.0, which means that County 1 is assigned to district 2.
# County 1 is the first county in county_pops, which is the most populous remaining county, County 2 is the second, etc.

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
            


# ATTEMPTING TO INCORPORATE adjacent district constraints
#
#
for i in range(num_remaining_counties):
    for j in range(num_remaining_districts):
        # use apply to read the adjacency dataframe
        # column parent_state_county is equal to i
        # assignment[i,j] should be greater the members in the column child_state_county_code
        #prob += assignment[i,j] <= adjacency[adjacency['parent_state_county'] == i+1]['child_state_county_code'].apply(lambda x: assignment[x-1,j-1]).sum()
        child_state_county_codes = adjacency[adjacency['parent_state_county'] == i+1]['child_state_county_code']
        valid_child_state_county_codes = [x for x in child_state_county_codes if x-1 < len(assignment) and j-1 < len(assignment[0])]
        prob += assignment[i,j] <= sum(assignment[x-1,j-1] for x in valid_child_state_county_codes)



# Set the upper and lower bounds of each district
pop_upper_bound = remaining_target_pop + (remaining_target_pop * .1)
pop_lower_bound = remaining_target_pop - (remaining_target_pop * .1)


# District size constraints
for j in range(num_remaining_districts):
    prob += lpSum(allocation[i][j] for i in range(num_remaining_counties)) <= pop_upper_bound , "District Size Maximum " + str(j)
    prob += lpSum(allocation[i][j] for i in range(num_remaining_counties)) >= pop_lower_bound , "District Size Minimum " + str(j)


# Solve the model
prob.solve() 

# Print the results
print('The model status is: ',LpStatus[prob.status])
print('The objective value is: ', value(objective_function))

# This prints out all the county assignments. 
# I.e. Y_102 = 1.0 means that County 10 is assigned to district 2
# or Y_14 = 1.0 means that County 1 is assigned to district 4

list_of_dist_assignments = []

for var in prob.variables():
    if var.varValue == 1:
        list_of_dist_assignments.append(var.name)
        print(f"{var.name} = {var.varValue}")

# read in the washington_census_data_with_names_long_lat.csv
answers_df = pd.read_csv('001. Data Bases/washington_census_data_with_names_long_lat.csv')

# sort the answers_df by the Total_Population
answers_df = answers_df.sort_values(by='Total_Population', ascending=False)

# remove the top 3 most populous counties
answers_df = answers_df.iloc[3:]

# add a column to the answers_df called 'District'
answers_df['District'] = list_of_dist_assignments

answers_df['District'] = answers_df['District'].str[5:]

# sum the Total_Population for each district
district_populations = answers_df.groupby('District').sum()

# drop the columns that are not needed
district_populations = district_populations.drop(columns=['Total_Population_White_Alone', 'Latitude', 'Longitude', 'Name', 'state_county'])

print(answers_df)
print(district_populations)
