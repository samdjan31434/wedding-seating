import numpy as np
import time
import random
import math
import os
from collections import Counter


rng = np.random.default_rng()

n= 100    # number of guest
m= 10    # number of tables

"""
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
    
    return Preference   """

def age_score(age_diff):
    if age_diff <= 5:
        return 10
    elif age_diff <= 10:
        return 5
    elif age_diff <= 20:
        return 2
    elif age_diff <= 30:
        return 0
    elif age_diff <= 40:
        return -5
    else:
        return -10

# generates guest matrix
def generate_guest(n, m, graph_density):
    # build n by n matrix
    preference = np.zeros((n,n), dtype =int)

    # dictionary that ages of each guest
    ages = {i: rng.integers(18, 90) for i in range(n)}

    # num of couples 20%
    num_couples = int(n*0.2) //2


    # assign pref score of 10 to first 20% of guest
    for i in range(0,num_couples*2,2):
        preference[i][i+1] = 10
        preference[i+1][i] =10
        
    # assume half of couples have a child 
    # assign a child to every other couple 
    child_index = num_couples * 2
    for i in range(0, num_couples * 2, 4):   
        if child_index >= n:
            break
        preference[child_index][i] = 10
        preference[i][child_index] = 10
        preference[child_index][i+1] = 10
        preference[i+1][child_index] = 10
        child_index += 1


    # assigns a random positive score to random guest with no preference
    for i in range(n):
        for j in range(i+1,n):
            if preference[i][j] ==0:
                if rng.random(0,1) < graph_density:
                    score = rng.randint(1,9)
                    preference[i][j] = score
                    preference[j][i] = score
    
    num_conflicts = int(n * 0.05)
    conflicts_assigned = 0
    while conflicts_assigned < num_conflicts:
        i = rng.integers(0, n)
        j = rng.integers(0, n)
        if i != j and preference[i][j] == 0:
            score = rng.integers(-10, -1)
            preference[i][j] = score
            preference[j][i] = score
            conflicts_assigned += 1

    for i in range(n):
        for j in range(i+1, n):
            if preference[i][j] == 0:
                age_diff = abs(ages[i] - ages[j])
                score = age_score(age_diff)
                preference[i][j] = score
                preference[j][i] = score

    return preference
    

def save_file_instances(n, m, filename='instance.npy'):
    P = generate_guest(n, m, 0.3)   # always generates new instance
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


class Compatible_Graph:
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
    return len(self.vertices[vertex])           # count number of guest they are in conflict wit




def build_graph(P, n, condition):
    graph  = Compatible_Graph()

    # inistialise the graph with n vertices
    for i in range(n):
        graph.add_vertex(i)

    # intilialises edges with weight between guest with preference
    for i in range(n):
        for j in range(i+1, n):
            weight = P[i][j]
            if condition(weight):
                graph.add_edge(i, j)
                graph.add_edge(j, i)
                graph.add_weight(i, j, P[i][j])
    
    return graph


def build_graph_negative(P, n):
    return build_graph(P, n, lambda w: w<0)

def build_graph_positive(P, n):
    return build_graph(P, n, lambda w: w>0)



    

# greedy colouring algorihtm - find the first available table that is feasible for that guest and does not cause table capacity to overflow

def negative_greedy(graph, n, m):
    # dictionary key(guest ): value(table guest is assigned)
    assignment = {}
    # finds the table capacity
    capacity = n // m

    # key(table number): value(guest count at each table)
    table_count = {t: 0 for t in range(1, m+1)}    

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

    return assignment


def mixed_greedy(n,m, P):
    # dictionary key(guest ): value(table guest is assigned)
    assignment = {}
    # finds the table capacity
    capacity = n // m

    # create a dictionary
    # key(table number): value(guest count at each table)
    table_count = {}
    for t in range(1, m+1):    
        table_count[t] = 0     
   

    for guest in range(n):
        best_score = -10000000
        best_table = 1 

        for table in range(1,m+1):

            if table_count[table]< capacity:
                score  =0
                for neighbours, table_assigned in assignment.items():
                    if table == table_assigned:
                        score += P[guest][neighbours]

                if score > best_score:
                    best_score =score
                    best_table = table
            
        assignment[guest] = best_table
        table_count[best_table] += 1

    return assignment    


def ordered_positive_greedy(n,m,P):
    # dictionary key(guest ): value(table guest is assigned)
    assignment = {}
    # finds the table capacity
    capacity = n // m

    # create a dictionary
    # key(table number): value(guest count at each table)
    table_count = {}
    for t in range(1, m+1):    
        table_count[t] = 0  
    
    sums = {}
    for i in range(n):
        total =0
        for j in range(n):
            if P[i][j]> 0:
                total+= P[i][j]
        sums[i] = total


    guest_order = sorted(sums, key=sums.get,reverse=True)

    for guest in guest_order:
        best_score = -1000000
        best_table = 1

        for table in range(1, m+1):
            if table_count[table] < capacity:
                score = 0
                for neighbour, table_assigned in assignment.items():
                    if table_assigned == table:
                        score += P[guest][neighbour]

                if score > best_score:
                    best_score = score
                    best_table = table

        assignment[guest] = best_table
        table_count[best_table] += 1

    return assignment


def BFS_greedy(graph,n,m):
     # dictionary key(guest ): value(table guest is assigned)
    assignment = {}
    # finds the table capacity
    capacity = n // m

    # create a dictionary
    # key(table number): value(guest count at each table)
    table_count = {}
    for t in range(1, m+1):    
        table_count[t] = 0  

    visited =set()
    current_table = 1
    start_guest  =0 
    most_neighbours = 0
    for i in range(n):
        count = graph.get_adjacent_count(i)
        if most_neighbours > count:
            most_neighbours = count
            start_guest = i

    queue = [start_guest]

    while len(assignment)<n:
        guest = queue.pop(0)
        if guest in visited:
            continue

        visited.add(guest)

        if table_count[current_table]< capacity:
            assignment[guest] = current_table
            table_count[current_table] +=1
        else:
            current_table+=1 
            if current_table>m:
                current_table =m
            assignment[guest] = current_table
            table_count[current_table] += 1

        for neighbour in graph.vertices[guest]:
            if neighbour not in visited:
                queue.append(neighbour)

        for guest in range(n):
            if guest not in visited:
                queue.append(guest)
                break

    return assignment       



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

        while new_assignment[guest1] == new_assignment[guest2]:
            guest2 = random.randint(0, n-1)
        new_assignment[guest1], new_assignment[guest2] = new_assignment[guest2], new_assignment[guest1]

    return new_assignment



def initial_temp_cal(assignment,num_samples,n,acceptance_rate =0.8): 
    neg_change = []
    current_assignment = assignment.copy()

    for i in range(num_samples):
        guest1 = random.randint(0, n-1)
        guest2 = random.randint(0, n-1)
        while current_assignment[guest1] == current_assignment[guest2]:
            guest2 = random.randint(0, n-1)

        score_before = satisfaction_score(current_assignment,P,n)
        current_assignment[guest1] , current_assignment[guest2] = current_assignment[guest2],current_assignment[guest1]
        score_after  = satisfaction_score(current_assignment,P,n)

        if (score_after -score_before)< 0:
            neg_change.append(abs(score_after-score_before))
        
        current_assignment[guest1],current_assignment[guest2] = current_assignment[guest2],current_assignment[guest1]

    if neg_change:
        average_change = sum(neg_change) / len(neg_change)
    else:
        average_change = 1 

    T = average_change / (-math.log(acceptance_rate))

    return T



# used the pseudocode from https://www.researchgate.net/publication/354721896_A_Heuristic_Approach_in_Solving_the_Optimal_Seating_Chart_Problem
# variable and parameter used in simmulated annealing



def simulated_annealing(initial_assignment,n,m,P, T):

        time_limit = 5
        best_state = initial_assignment.copy()
        stagnation = 0
        v = 1
        start_time = time.time()
        max_stagnation  = 100
        gamma = 0.90
        il_limit = 100 
        x = initial_assignment.copy()
             


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

        return best_state



"""
neg_assignment = negative_greedy(build_graph_negative(P, n),n,m)
neg_initial_score = satisfaction_score(neg_assignment, P, n)
neg_temp = initial_temp_cal(neg_assignment, 200 , n)
neg_sa_state = simulated_annealing(neg_assignment,n,m,P,neg_temp)
neg_sa_score = satisfaction_score(neg_sa_state, P, n)
print(f"Satisfaction score with negative greedy: {neg_sa_score}")


mix_assignment = mixed_greedy(n, m, P)
mix_initial_score = satisfaction_score(mix_assignment, P, n)
mix_temp = initial_temp_cal(mix_assignment,200,n)
mix_sa_state = simulated_annealing(mix_assignment, n, m, P,mix_temp)
mix_sa_score = satisfaction_score(mix_sa_state, P, n)
print(f"Satisfaction score with mix greedy: {mix_sa_score}")


pos_assignment = ordered_positive_greedy(n, m, P)
pos_initial_score = satisfaction_score(pos_assignment, P, n)
ordered_temp  = initial_temp_cal(pos_assignment,200,n)
pos_sa_state = simulated_annealing(pos_assignment, n, m, P, ordered_temp)
pos_sa_score = satisfaction_score(pos_sa_state, P, n)
print(f"Satisfaction score with positive greedy: {pos_sa_score}")


bfs_assignment = BFS_greedy(build_graph_positive(P,n),n,m)
bfs_initial_score = satisfaction_score(bfs_assignment, P, n)
bfs_temp = initial_temp_cal(bfs_assignment, 100 , n)
bfs_sa_state = simulated_annealing(bfs_assignment, n, m, P,bfs_temp)
bfs_sa_score = satisfaction_score(bfs_sa_state, P, n)
print(f"Satisfaction score with bfs: {bfs_sa_score}")
"""


def create_table_guest(state):
    table_guest = {}
    for table in range(1,m+1):
        table_guest[table] = []

    for g in range(n):
        table_guest[state[g]].append(g)
    
    return table_guest

        


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


def local_search(assignment ,n ,m ,P):
    current_scores = each_table_satifaction(create_table_guest(assignment),P)
    sorted_table_scoring = sorted(current_scores,key= current_scores.get)
    worst_table1 = sorted_table_scoring[0]
    worst_table2 = sorted_table_scoring[1]
    improved = True
    while improved:
        improved = False

        table_guests = {}
        for table in range(1, m+1):
            table_guests[table] = []
        for g in range(n):
            table_guests[assignment[g]].append(g)
        current_scores = each_table_satifaction(table_guests,P)
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
 

""""Check that each guest is asssigned to only one table and table capacity is not exceeded"""
def testing_feasibility(assignment,n,m):
    capacity = n//m
    

    # Check if all guest are assigned
    assert len(assignment) == n, "not all guest are assigned tables"

    # Check guest are assigned to a valid table number
    for guest in range(n):
        table = assignment[guest]
        assert table<1 or table >m, " guest are assigned to invalid table number"
           
    
    table_counts = Counter(assignment.values())

    for table,count in table_counts.items():
        assert count > capacity , "table capacity exceeded"

    print("produces feasible solution")
           


"""Check if preferene matrix is symmetric """
def test_symmetry(P,n):
    for i in range(n):
        for j in range(n):
            assert P[i][j] == P[j][i] , "Not symmetric"

    print("Preference matrix is symmetric")

test_symmetry(P,n)    

        
"""check if the SA score is greater than or equal to the greedy score"""
def test_sa_score(greedy_score, sa_score, greedy_name):
    assert sa_score >= greedy_score, f"Simulated annealing produce worst solution for {greedy_name}"
    print("SA score passed for {greedy_name}")        


"""check if the local score is greater than or equal to the SA score"""
def test_local_search(sa_score , ls_score, greedy_name):
    assert ls_score > sa_score, f"Local search produce worst solution for {greedy_name}"
    print(f"Local search test passed for {greedy_name}")
    
def test_satisfaction_score():
    # 4 guests, 2 tables, manual instance
    test_P = np.array([
        [0, 7, -6, 0],
        [7, 0,  0, 3],
        [-6, 0,  0, 10],
        [0,  3,  10, 0]
    ])
    # assign g1,g2 to table 1 and g3,g4 to table 2
    test_assignment = {0: 1, 1: 1, 2: 2, 3: 2}
    score = satisfaction_score(test_assignment, test_P, 4)
    # expected: P[0][1] + P[2][3] =  7 + 10 = 17
    assert score == 17, f"Expected score of 17 but got {score}"
    print("Satisfaction score test passed")

test_satisfaction_score()



def bellows_peterson_instance():
    n = 17
    P = np.zeros((n,n),dtype=int)

    couples = [(1,2),(3,4),(5,6), (7,8), (10,11)]
    for i,j in couples:
        P[i][j] =50
        P[j][i] = 50
    
    P[3][9] = 10
    P[9][3] =10 

    for i in range(9):
        for j in range(i+1, 9):
            if P[i][j] == 0:
                P[i][j] = 1
                P[j][i] = 1

    for i in range(9,17):
        for j in range(i+1,17):
            if P[i][j] == 0:
                P[i][j] = 1
                P[j][i] = 1

    

    return n, P

n,P = bellows_peterson_instance()

# make a file for GAMS
with open('bellows_instance.inc', 'w') as f:
    for i in range(n):
        for j in range(n):
            if P[i][j] != 0:
                f.write(f"P('g{i+1}','g{j+1}') = {P[i][j]} ;\n")


P = np.array([
        [0, 7, -6, 0],
        [7, 0,  0, 3],
        [-6, 0,  0, 10],
        [0,  3,  10, 0]
])
n= 4
m=2    
