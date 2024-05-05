# msds460-assignment6

001.Data Bases: contains various .csv files containing Washington county census data.

Importing_Data_Web_Adjacency.ipynb: utilizes BeautifulSoup to extract county adjacency data, which was saved in washington_counties_adjacency.csv

Importing_Data_Web_Population_Extractor.ipynb: utilizes BeautifulSoup to extract county census data, which was saved in washington_census_data.csv

integer_programming_constraints_done.ipynb: creates and implements constraints for ensuring districts contain only adjacent counties

integer_programming.py: the primary code file, uses PuLP to create and solve the integer programming problem. This file attempts to incorporate the adjacency constraints from integer_programming_constraints_done.ipynb into it's model. 

Actual Districts.pdf: the 2021 Washington State Congressional District Map, sourced from https://www.redistricting.wa.gov/district-maps-handouts

Redistriced Counties.png: the districts resulting from the integer_programming.py model output