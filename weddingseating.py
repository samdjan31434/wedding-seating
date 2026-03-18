import numpy as np
import time
import random
import math
import os
import pandas as pd

# used to repeat the random number 20 times
#random.seed(1)


# create guest and assign random score to some of them 
def generate_guest(n,m):
    Preference = np.zeros((n,n),dtype =int)

    # assume about 25 % are couple that must sit together
    for i in range(0, n//4, 2):
        Preference[i][i+1] = 10
        Preference[i+1][i] = 10
    
    for guest in range(n):
        i = np.random.randint(0,n)
        j = np.random.randint(0,n)
        if i!=j and Preference[i][j] ==0:
            random_score = np.random.randint(-10,10)
            Preference[i][j] = random_score
            Preference[j][i] = random_score
    
    return Preference

n= 80    # number of guest
m= 10    # number of tables


def save_file_instances(n, m, filename='instance.npy'):
    P = generate_guest(n, m)   # always generates new instance
    np.save(filename, P)
    return P

"""
# create a file so that i can compare on same guest list 
def save_file_instances(n, m, filename='instance.npy'):
    # create a new file if it does exit
    if not os.path.exists(filename):
        P = generate_guest(n, m)
        np.save(filename, P)
        print(f"New instance generated and saved to {filename}")
    else:
        print(f"Loading existing instance from {filename}")
    
    return np.load(filename)  """


P = save_file_instances(n, m)

    
# save the file as .inc to use in GAMS
with open('Generated_instance.inc', 'w') as f:
    for i in range(n):
        for j in range(n):
            if P[i][j] != 0:
                f.write(f"P('g{i+1}','g{j+1}') = {P[i][j]} ;\n")




class Conflict_Graph:
  def __init__(self):
    self.vertices = {}    # store each guest and the list of conflciting vertices
    self.edges = {}       # stores weight for conflict between edges

  def add_vertex(self, vertex):
    self.vertices[vertex] = []     # add guest to an empty list since no conflict yet

  def add_edge(self, source, target):
    self.vertices[source].append(target)   # add edges bewteen guest with conflicts

  def add_weight(self , source, target , weight):
     self.edges[(source,target)] = weight 
     self.edges[(target, source)] = weight      # add the preference score as weight between conflicting guests

  def get_adjacent_count(self, vertex):
    return len(self.vertices[vertex])           # count number of guest they are in conflict with
  


graph  = Conflict_Graph()

# inistialise the graph with n vertices
for i in range(n):
   graph.add_vertex(i)


# intilialises edges with weight between guest with preference
for i in range(n):
   for j in range(i+1,n):
      if P[i][j]<0:
         graph.add_edge(i,j)
         graph.add_edge(j, i)
         graph.add_weight(i,j,P[i][j])



# dictionary key(guest ): value(table guest is assigned)
assignment = {}

# finds the table capacity
capacity = n // m

# create a dictionary
# key(table number): value(guest count at each table)
table_count = {}
for t in range(1, m+1):
    table_count[t] = 0

# greedy colouring graph algorithm used to find an initial solution
for guest in range(n):
    # find tables used by conflicting neighbours
    used_tables = set()
    for neighbour in graph.vertices[guest]:
        if neighbour in assignment:
            used_tables.add(assignment[neighbour])
    
    # used to find the lowest table number that has no conflicting guest and is not full
    # neutral guest are assinged to the lowest avaialbe table number since used table return an emtpy set
    table = 1
    while table <= m:
        if table not in used_tables and table_count[table] < capacity:
            break
        table += 1
        # this occur when there a seating choice would result in conflict therefore pick table with the least capacity 
        if table > m:
            table = min(table_count, key=table_count.get)
            break

    # assing guest to a table
    assignment[guest] = table
    table_count[table] += 1


# calculate the total satisfaction score 
def satisfaction_score(assignment,P ,n):
   total_score = 0
   for i in range(n):
     for j in range(i+1, n):
         if assignment[i] == assignment[j]:
             total_score += P[i][j]
   return total_score  


# swap operator, changes assigment of guest at different tables
def generate_neighbour_state(assignment ,n,v):
    new_assignment  = assignment.copy()

    # v is the number of swap operation to do 
    for i in range(v):
        guest1 = random.randint(0,n-1)
        guest2 = random.randint(0,n-1)

        if assignment[guest1] != assignment[guest2]:
                new_assignment[guest1], new_assignment[guest2] = new_assignment[guest2], new_assignment[guest1]

    return new_assignment







# used the pseudocode from https://www.researchgate.net/publication/354721896_A_Heuristic_Approach_in_Solving_the_Optimal_Seating_Chart_Problem
# variable and parameter used in simmulated annealing
time_limit = 2
best_state = assignment.copy()
stagnation = 0
v = 1
start_time = time.time()
max_stagnation  = 100
T = 125
gamma = 0.95
il_limit = 100 
x = assignment.copy()
             


# Simmulated annealing that continue while temperture is not zero or the time limit is not reached
while T>0 and (time.time()- start_time)< time_limit:
    for il in range(il_limit):
        y = x.copy()
        y = generate_neighbour_state(y,n,v)
        f_x = satisfaction_score(x,P,n)
        f_y = satisfaction_score(y,P,n)

        if f_y > f_x:
            x = y
            stagnation =0
            v =1
            if f_y > satisfaction_score(best_state, P , n):
                best_state = y.copy()
        else:
            r = random.random()
            try:
                prob_y = 1 / (1 + math.exp(-(f_y - f_x) / T))
            except OverflowError:
                prob_y = 0
            if prob_y > r :
                x = y.copy()
                stagnation = 0
                v = 1
            else:
                stagnation = stagnation + 1
            if stagnation == max_stagnation:
                stagnation =0
                v += 1
                if v>m:
                    v = 1
    T = T * gamma           

               
sa_score = satisfaction_score(best_state, P, n)
print(f"Satisfaction score: {sa_score}")


# greedy colouring algorihtm - find the first available table that is feasible for that guest and does not cause table capacity to overflow

table_guest = {}
for table in range(1,m+1):
    table_guest[table] = []

for g in range(n):
    table_guest[best_state[g]].append(g)    


def each_table_satifaction(table_guest, P ):
    current_scores = {}
    for table,guest  in table_guest.items():
        total = 0
        for i in range(len(guest)):
            for j in range(i+1,len(guest)):
                guest1 = guest[i]
                guest2 = guest[j]
                total+= P[guest1][guest2]
        current_scores[table] = total

    return current_scores            

current_scores = each_table_satifaction(table_guest,P)
sorted_table_scoring = sorted(current_scores,key= current_scores.get)
worst_table1 = sorted_table_scoring[0]
worst_table2 = sorted_table_scoring[1]


def local_search(assignment ,n ,m ,P):

    improved = True
    while improved:
        improved = False

        table_guests = {}
        for table in range(1, m+1):
            table_guests[table] = []
        for g in range(n):
            table_guests[assignment[g]].append(g)
        current_scores = each_table_satifaction(table_guest,P)
        sorted_table_scoring = sorted(current_scores,key= current_scores.get)
        worst_table1 = sorted_table_scoring[0]
        worst_table2 = sorted_table_scoring[1]
        for guest1 in table_guests[worst_table1]:
            for guest2 in table_guests[worst_table2]:
                before_score = satisfaction_score(assignment,P,n)
                assignment[guest1], assignment[guest2] = assignment[guest2], assignment[guest1]
                after_score = satisfaction_score(assignment, P, n)
                if after_score> before_score:
                    improved = True
                    break
                else:
                    assignment[guest1], assignment[guest2] = assignment[guest2], assignment[guest1]
    return assignment             
 

"""
def local_search(assignment ,n ,m ,P):
        current_scores = each_table_satifaction(table_guest,P)
        sorted_table_scoring = sorted(current_scores,key= current_scores.get)
        worst_table1 = sorted_table_scoring[0]
        worst_table2 = sorted_table_scoring[1]
        for guest1 in table_guest[worst_table1]:
            for guest2 in table_guest[worst_table2]:
                before_score = satisfaction_score(assignment,P,n)
                assignment[guest1], assignment[guest2] = assignment[guest2], assignment[guest1]
                after_score = satisfaction_score(assignment, P, n)
                if after_score> before_score:
                    break
                else:
                    assignment[guest1], assignment[guest2] = assignment[guest2], assignment[guest1]
        return assignment 
"""        



new_best_state = local_search(best_state,n,m, P)
print(f"Score after local search: {satisfaction_score(new_best_state, P, n)}")
