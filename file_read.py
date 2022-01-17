#import statements
import pandas as pd
import numpy as np
from gurobipy import *


#read in data
animal_data = pd.read_excel("zoo_data.xlsx", sheet_name = 0)
species_data = pd.read_excel("zoo_data.xlsx", sheet_name = 1, index_col = 0, header = 1)
inf_data = pd.read_excel("zoo_data.xlsx", sheet_name = 2)



#modify species data
del animal_data['Notes']
new_animal_data = []
animal_data["c_or_a"] =  [-99999,]*len(animal_data)

for animal in animal_data.values.tolist():
	temp_animal_row = animal
	#print(animal)
	species = animal[1]
	age = animal[2]
	
	comparison_age = float(species_data.loc[species,"Adulthood Age"])
	if comparison_age < age:
		a_or_c = 1 #adult
	elif comparison_age >= age:
		a_or_c = 0 #child

	temp_animal_row = [species, age, a_or_c]
	new_animal_data.append(temp_animal_row)

dict = {}
for line in new_animal_data:
	if line[0] not in dict:
		dict[line[0]] = {"c": 0, "a": 0, "t": 0}
		if line[2] == 0:
			dict[line[0]]["c"] += 1
		elif line[2] == 1:
			dict[line[0]]["a"] += 1

	else:
		if line[2] == 0:
			dict[line[0]]["c"] += 1
		elif line[2] == 1:
			dict[line[0]]["a"] += 1
	dict[line[0]]["t"] += 1

header = ["animal_and_age", "reccomended_food", "count_species_age", "welfare_1", "cost_1", "welfare_2", "cost_2", "welfare_3", "cost_3"]
fin_animal_data = []
animal_name_age_dat_forGurobi = []
sum_anim = 0

for animal in new_animal_data:
	if animal[2] == 1:
		animal_and_age = animal[0]+"_adult"
		age = "adult"
		num_animal = dict[animal[0]]["a"]
		reccomended_food = species_data.loc[animal[0],"Adult Recommended food"]
	elif animal[2] == 0:
		animal_and_age = animal[0]+"_child"
		age = "child"
		num_animal = dict[animal[0]]["c"]
		reccomended_food = species_data.loc[animal[0],"Child Recommended Food"]
	
	if animal_and_age not in animal_name_age_dat_forGurobi:
		animal_name_age_dat_forGurobi.append(animal_and_age)
		welfare_1 = species_data.loc[animal[0],"Welfare value"]
		cost_1 = species_data.loc[animal[0],"Cost/10 lb"]
		welfare_2 = species_data.loc[animal[0],"Welfare value.1"]
		cost_2 = species_data.loc[animal[0],"Cost/10 lb.1"]
		welfare_3 = species_data.loc[animal[0],"Welfare value.2"]
		cost_3 = species_data.loc[animal[0],"Cost/10 lb.2"]

		temp_row = [animal_and_age, reccomended_food, num_animal, welfare_1, cost_1, welfare_2, cost_2, welfare_3, cost_3]
		fin_animal_data.append(temp_row)
	sum_anim += 1

animals = animal_name_age_dat_forGurobi
animal_data_df = pd.DataFrame(fin_animal_data, columns = header, index = animals)

header_no_age = ["animal", "total_of_species", "welfare_1", "cost_1", "welfare_2", "cost_2", "welfare_3", "cost_3"]
animal_data_no_age = []
animal_name_age_dat_forGurobi_no_age = []

for animal in new_animal_data:	
	temp_row = []
	if animal[0] not in animal_name_age_dat_forGurobi_no_age:
		total_of_species = dict[animal[0]]["t"]
		animal_name_age_dat_forGurobi_no_age.append(animal[0])
		welfare_1 = species_data.loc[animal[0],"Welfare value"]
		cost_1 = species_data.loc[animal[0],"Cost/10 lb"]
		welfare_2 = species_data.loc[animal[0],"Welfare value.1"]
		cost_2 = species_data.loc[animal[0],"Cost/10 lb.1"]
		welfare_3 = species_data.loc[animal[0],"Welfare value.2"]
		cost_3 = species_data.loc[animal[0],"Cost/10 lb.2"]

		temp_row = [animal[0], total_of_species, welfare_1, cost_1, welfare_2, cost_2, welfare_3, cost_3]
		animal_data_no_age.append(temp_row)

animals_no_age = animal_name_age_dat_forGurobi_no_age
animal_data_df_no_age = pd.DataFrame(animal_data_no_age, columns = header_no_age, index = animals_no_age)

facilities_data = inf_data.values.tolist()
facilities = inf_data["Facility Name"].tolist()
facilities_data = pd.DataFrame(facilities_data, index = facilities, columns = ["facility", "invstment_per_10k"])

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#Gurobi
food_type = ["food_1","food_2","food_3"]
food_costs = ["cost_1", "cost_2", "cost_3"]

m = Model("Max Average Welfare")

#vars
x_i_n = m.addVars(animals, food_type, name = 'x_i_n')
y_k = m.addVars(facilities, name = "y_k")

#Objective
m.setObjective((1/sum_anim)*
	quicksum(
		animal_data_df.loc[i,"count_species_age"]*(
		(animal_data_df.loc[i,"welfare_1"]*(x_i_n[i,"food_1"]/animal_data_df.loc[i,"reccomended_food"])) + 
		(animal_data_df.loc[i,"welfare_2"]*(x_i_n[i,"food_2"]/animal_data_df.loc[i,"reccomended_food"])) + 
		(animal_data_df.loc[i,"welfare_3"]*(x_i_n[i,"food_3"]/animal_data_df.loc[i,"reccomended_food"]))) for i in animals),
		sense = GRB.MAXIMIZE)

#constraints
m.addConstrs(x_i_n[i,"food_1"] + x_i_n[i,"food_2"] + x_i_n[i,"food_3"] == animal_data_df.loc[i,"reccomended_food"] for i in animals)

m.addConstr(200000 + (30/10000)*quicksum(facilities_data.loc[k, "invstment_per_10k"]*y_k[k] for k in facilities) >= 1.05*(100000 + 
	quicksum(90*(1/10)*animal_data_df.loc[i,"count_species_age"]*animal_data_df.loc[i,c]*x_i_n[i,j] for i in animals for j in food_type for c in food_costs) + 
	quicksum(y_k[k] for k in facilities)))

m.addConstrs(x_i_n[i,j] >= 0 for i in animals for j in food_type)
m.addConstrs(y_k[k] >= 0 for k in facilities)
m.addConstrs(y_k[k] <= 20000 for k in facilities)

#Optimize
m.optimize()

for i in animals:
    for j in food_type:
    	print("animal:", i, "amount of food type", j, "purchased =", x_i_n[i,j].x, "lbs")
for k in facilities:
	print("amount invested into "+k+": "+"$"+str(y_k[k].x))
