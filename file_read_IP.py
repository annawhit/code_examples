##THIS IS THE IP VERSION

#import statements
import pandas as pd
import numpy as np
from gurobipy import *


#read in data
animal_data = pd.read_excel("zoo_data_IP.xlsx", sheet_name = 0)
species_data = pd.read_excel("zoo_data_IP.xlsx", sheet_name = 1, index_col = 0, header = 1)
inf_data = pd.read_excel("zoo_data_IP.xlsx", sheet_name = 2)



#modify species data
del animal_data['Notes']
new_animal_data = []
animal_data["c_or_a"] =  [-99999,]*len(animal_data)

for animal in animal_data.values.tolist():
	temp_animal_row = animal
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

#NEW IP STUFF
animals_on_reserve = list(animal_data_df_no_age.index)
all_species = list(species_data.index)
big_cats = ["Siberian Tiger", "Clouded Leopard", "Cheetah", "West African Lion"]

species_not_on_reserve = []
for i in all_species:
	if i not in animals_on_reserve:
		species_not_on_reserve.append(i)

header_not_on_reserve = ["animal", "total_of_species", "Adult Recommended food", "welfare_1", "cost_1", "welfare_2", "cost_2", "welfare_3", "cost_3"]
not_on_reserve_species_data = []
for animal in species_not_on_reserve:
	rec_food = species_data.loc[animal, "Adult Recommended food"]
	welfare_1 = species_data.loc[animal,"Welfare value"]
	cost_1 = species_data.loc[animal,"Cost/10 lb"]
	welfare_2 = species_data.loc[animal,"Welfare value.1"]
	cost_2 = species_data.loc[animal,"Cost/10 lb.1"]
	welfare_3 = species_data.loc[animal,"Welfare value.2"]
	cost_3 = species_data.loc[animal,"Cost/10 lb.2"]
	not_on_reserve_species_data.append([animal, 0, rec_food, welfare_1, cost_1, welfare_2, cost_2, welfare_3, cost_3])
not_on_reserve_species_data = pd.DataFrame(not_on_reserve_species_data, columns = header_not_on_reserve, index = species_not_on_reserve)

bcn = []
for i in big_cats:
	bcn.append(i+" num chosen")

nsn = []
for i in species_not_on_reserve:
	nsn.append(i+" num chosen")

esn = []
for i in animals_on_reserve:
	esn.append(i+" num chosen")
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#Gurobi
food_type = ["food_1","food_2","food_3"]
food_costs = ["cost_1", "cost_2", "cost_3"]

m = Model("Max Average Welfare")

#vars
x_i_n = m.addVars(animals, food_type, name = 'x_i_n')
y_k = m.addVars(facilities, name = "y_k")

b_c = m.addVars(big_cats, name = 'b_c', vtype = GRB.BINARY) #big cat types
b_c_n = m.addVars(bcn, name = 'b_c_n', vtype = GRB.INTEGER) #big cats bum chosen

n_s = m.addVars(species_not_on_reserve, name = 'n_s', vtype = GRB.BINARY) # not on reserve type
ns_x_i_n = m.addVars(species_not_on_reserve, food_type, name = 'ns_x_i_n') # not on reserve
n_s_n = m.addVars(nsn, name = 'b_c_n', vtype = GRB.INTEGER) # not on reserve num chosen

e_s = m.addVars(animals_on_reserve, name = "e_s", vtype = GRB.BINARY)
e_s_n = m.addVars(esn, name = 'e_s_n', vtype = GRB.INTEGER)

#Objective
m.setObjective(
	#quicksum(b_c_n[j] for j in bcn) + quicksum(n_s_n[i] for i in nsn) + quicksum(e_s_n[i] for i in esn),
	quicksum(
		((animal_data_df.loc[i,"welfare_1"]*(x_i_n[i,"food_1"]/animal_data_df.loc[i,"reccomended_food"])) + 
		(animal_data_df.loc[i,"welfare_2"]*(x_i_n[i,"food_2"]/animal_data_df.loc[i,"reccomended_food"])) + 
		(animal_data_df.loc[i,"welfare_3"]*(x_i_n[i,"food_3"]/animal_data_df.loc[i,"reccomended_food"]))) for i in animals)+
	quicksum(
		(not_on_reserve_species_data.loc[i,"welfare_1"]*(ns_x_i_n[i,"food_1"]/not_on_reserve_species_data.loc[i,"Adult Recommended food"])) + 
		(not_on_reserve_species_data.loc[i,"welfare_2"]*(ns_x_i_n[i,"food_2"]/not_on_reserve_species_data.loc[i,"Adult Recommended food"])) + 
		(not_on_reserve_species_data.loc[i,"welfare_3"]*(ns_x_i_n[i,"food_3"]/not_on_reserve_species_data.loc[i,"Adult Recommended food"])) for i in species_not_on_reserve),
		sense = GRB.MAXIMIZE)

#IP FIRST

#big cats
m.addConstr(quicksum(b_c[i] for i in  big_cats) <= 1)
for i in big_cats:
	for j in bcn:
		if j.split(" num")[0] == i:
			m.addConstr(b_c_n[j] <= 5*b_c[i])
#m.addConstrs()

#retrofitted enclosue
m.addConstr(quicksum(n_s[i] for i in species_not_on_reserve) <= 1)

m.addConstrs(ns_x_i_n[i,"food_1"] + ns_x_i_n[i,"food_2"] + ns_x_i_n[i,"food_3"] == not_on_reserve_species_data.loc[i,"Adult Recommended food"]*n_s_n[i+" num chosen"] for i in species_not_on_reserve)
for i in species_not_on_reserve:
	for j in nsn:
		if j.split(" num")[0] == i:
			m.addConstr(n_s_n[j] <= 5*n_s[i])

#renovated enclosure
m.addConstr(quicksum(e_s[i] for i in animals_on_reserve) <= 2)
for i in animals_on_reserve:
	for j in esn:
		if j.split(" num")[0] == i:
			m.addConstr(e_s_n[j] <= 2*e_s[i])

for i in animals_on_reserve:
	for j in big_cats:
		if i == j:
			m.addConstr(b_c[j] + e_s[i] <= 1)
			m.addConstr(b_c_n[j+" num chosen"] <= 5*(1-e_s[i]))
			m.addConstr(e_s_n[i+" num chosen"] <= 2*(1-b_c[j]))
			#This enforces that if a bc is chosen to moce to a new enclosure, it's enclosure can not be renovated
print(animal_data_df)
#LP constraints
m.addConstrs((x_i_n[i,"food_1"] + x_i_n[i,"food_2"] + x_i_n[i,"food_3"] == animal_data_df.loc[i,"reccomended_food"]
	*( 
		(b_c_n[i.split("_")[0]+" num chosen"] if (i.split("_")[0] in big_cats and i.split("_")[1] == "adult") else 0) + 
		(e_s_n[i.split("_")[0]+" num chosen"] if (i.split("_")[0] in animals_on_reserve and i.split("_")[1] == "adult") else 0) +
		animal_data_df.loc[i,"count_species_age"] 
	)) for i in animals)

m.addConstr(200000 + (30/10000)*quicksum(facilities_data.loc[k, "invstment_per_10k"]*y_k[k] for k in facilities) >= 1.05*(100000 + 
	quicksum(90*(1/10)*animal_data_df.loc[i,c]*x_i_n[i,j] for i in animals for j in food_type for c in food_costs) + 
	quicksum(90*(1/10)*not_on_reserve_species_data.loc[i,c]*ns_x_i_n[i,j] for i in species_not_on_reserve for j in food_type for c in food_costs) + 
	#NOT YET SURE IF YOU NEED TO ACCOUNT FOR NEW ANIMALS IN THE REVENUE CALCULATION
	#IF SO, PUT IT HERE
	#quicksum(not_on_reserve_species_data.loc[i,c]*ns_x_i_n[i,j] for i in species_not_on_reserve for j in food_type for c in food_costs) + 
	quicksum(y_k[k] for k in facilities)))

m.addConstrs(x_i_n[i,j] >= 0 for i in animals for j in food_type)
m.addConstrs(y_k[k] >= 0 for k in facilities)
m.addConstrs(y_k[k] <= 20000 for k in facilities)

#Optimize
m.optimize()



# Print the result
status_code = {1: 'LOADED', 2: 'OPTIMAL', 3: 'INFEASIBLE', 4: 'INF_OR_UNBD', 5: 
'UNBOUNDED'}
status = m.status
print("The optimization status is {}".format(status_code[status]))
print("                                                                                      ")
if status == 2:
# Retrieve variables value
    print("Optimal objective value:\n{}".format(m.objVal))

print("                                                                                      ")
print("                                                                                      ")
print("Values of Variables:")

for k in facilities:
	print("Amount invested into "+k+": "+"$"+str(y_k[k].x))
print("                                                                                      ")

for i in animals:
	for j in food_type:
		if x_i_n[i,j].x > 0:
			print( x_i_n[i,j].x, "lbs of food type", j, "will be purchased for the", i.split("_")[1], i.split("_")[0]+"(s)")
print("                                                                                      ")

for i in big_cats:
	if b_c[i].x > 0:
		print("The big cat", i, "was chosen")
for i in bcn:
	if b_c_n[i].x > 0:
		print(int(b_c_n[i].x), "new ",i.split(" num")[0]+"s will join the reserve" )
print("                                                                                      ")

for i in species_not_on_reserve:
	if n_s[i].x > 0:
		print("The new species", i, "was chosen to move in to the retrofitted enclosure")
for i in nsn:
	if n_s_n[i].x > 0:
		print(int(n_s_n[i].x), "new ",i.split(" num")[0]+"s will join the reserve" )
print("                                                                                      ")

for i in animals_on_reserve:
	if e_s[i].x > 0:
		print("The existing species", i, "was chosen have its' enclosure renovated")
for i in esn:
	if e_s_n[i].x > 0:
		print(int(e_s_n[i].x), "new ",i.split(" num")[0]+"s will join the reserve" )