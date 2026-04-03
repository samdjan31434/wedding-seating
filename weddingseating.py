import numpy as np
import time
import random
import math
import os
from collections import Counter


rng = np.random.default_rng()

n = 10    # number of guest
m = 2   # number of tables


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

def assign_random_positive_preferences(preference, n, graph_density):
    max_pairs = (n * (n-1)) // 2
    
    existing_pairs = 0
    for i in range(n):
        for j in range(i+1, n):
            if preference[i][j] != 0:
                existing_pairs += 1
    
    random_positive_pairs = int(max_pairs * graph_density) - existing_pairs
    count = 0

    for i in range(n):
        for j in range(i+1, n):
            if preference[i][j] == 0:
                if count < random_positive_pairs:
                    score = np.random.randint(1, 9)
                    preference[i][j] = score
                    preference[j][i] = score
                    count += 1

    return preference


def create_couple_pairs(num_couples, adults,preference):
    couple_pairs = []
    for i in range(0, num_couples * 2, 2):
        if i + 1 >= len(adults):
            break
        g1 = adults[i]
        g2 = adults[i+1]
        preference[g1][g2] = 10
        preference[g2][g1] = 10
        couple_pairs.append((g1, g2))

    return couple_pairs, preference



# generates guest matrix
def generate_guest(n, graph_density, difficulty):
    # build n by n matrix
    preference = np.zeros((n,n), dtype =int)

    # dictionary for ages of each guest from 18 to 90
    # normally distributed at 34
    ages = {
    i: int(min(100, max(4, rng.normal(34, 10))))
    for i in range(n)}

    young_children  = []    # age 0 to 7 sit with parents
    teen = []   # age 8 to 17 sit at their own table
    adults = []  # singles and couples

    for i in range(n):
        if ages[i] <= 7:
            young_children.append(i)
        elif ages[i] <= 17:
            teen.append(i)
        else:
            adults.append(i)

   
    if difficulty == "easy":
        # create a sparse matrix, assume no children and dont care for ages
        num_couples = int(len(adults)*0.2) // 2
        conflict_rate  =  0.01
    elif difficulty == "medium":
        # assume children sit at own table, care for ages
        num_couples = int(len(adults)*0.3) // 2
        conflict_rate = 0.02
    elif difficulty == "realistic":
        # children sit with parent wedding 
        num_couples = int(len(adults)*0.55) // 2
        conflict_rate = 0.05
    elif difficulty =="hard":
        num_couples = int(len(adults)* 0.55) // 2
        conflict_rate = 0.1

        


    if difficulty == "easy":
        
        # assign conflict
        num_conflicts = int(n * conflict_rate)
        conflicts_assigned = 0
        while conflicts_assigned < num_conflicts:
            i = rng.integers(0, n)
            j = rng.integers(0, n)
            if i != j and preference[i][j] == 0:
                score = rng.integers(-10, -1)
                preference[i][j] = score
                preference[j][i] = score
                conflicts_assigned += 1

        preference = assign_random_positive_preferences(preference, n, graph_density)

        return preference

        
    if difficulty == "medium": 

        couple_pairs , preference = create_couple_pairs(num_couples, adults, preference)
        
        # try to make teenager not sit with adults
        for teenager in teen:
            for adult in adults:
                if preference[teenager][adult] == 0:
                    preference[teenager][adult] = -5
                    preference[adult][teenager] = -5
        
        # discourage single adult to sit with couples
        couple_guests = set()
        for g1, g2 in couple_pairs:
            couple_guests.add(g1)
            couple_guests.add(g2)

        single_adults = []
        for a in adults:
            if a not in couple_guests:   
                single_adults.append(a)

        for g1, g2 in couple_pairs:
            for single in single_adults:
                if preference[g1][single] == 0:
                    preference[g1][single] = -3
                    preference[single][g1] = -3
                if preference[g2][single] == 0:
                    preference[g2][single] = -3
                    preference[single][g2] = -3
        
        # assign conflicts
        num_conflicts = int(n * conflict_rate)
        conflicts_assigned = 0
        while conflicts_assigned < num_conflicts:
            i = rng.integers(0, n)
            j = rng.integers(0, n)
            if i != j and preference[i][j] == 0:
                score = rng.integers(-10, -1)
                preference[i][j] = score
                preference[j][i] = score
                conflicts_assigned += 1

        preference = assign_random_positive_preferences(preference, n, graph_density)
        
        # age similarity for the remaining neutral pairs of guest
        for i in range(n):
            for j in range(i+1, n):
                if preference[i][j] == 0:
                    age_diff = abs(ages[i] - ages[j])
                    score = age_score(age_diff)
                    preference[i][j] = score
                    preference[j][i] = score
 
        return preference



    # hard and realistics
    child_index = 0
    half_couples = len(couple_pairs) // 2
    for parent1, parent2 in couple_pairs[:half_couples]:
        if child_index >= len(young_children):
            break
        child = young_children[child_index]
        preference[child][parent1] = 10
        preference[parent1][child] = 10
        preference[child][parent2] = 10
        preference[parent2][child] = 10
        child_index += 1


    # try to make teenager sit at own table and not sit with adults
    for teenager in teen:
        for adult in adults:
            if preference[teenager][adult] == 0:
                preference[teenager][adult] = -5
                preference[adult][teenager] = -5

    couple_guests = set()
    for g1, g2 in couple_pairs:
        couple_guests.add(g1)
        couple_guests.add(g2)

    single_adults = []
    for a in adults:
        if a not in couple_guests:   
            single_adults.append(a)

    for g1, g2 in couple_pairs:
        for single in single_adults:
            if preference[g1][single] == 0:
                preference[g1][single] = -3
                preference[single][g1] = -3
            if preference[g2][single] == 0:
                preference[g2][single] = -3
                preference[single][g2] = -3

    
    # assings conflict
    num_conflicts = int(n * conflict_rate)
    conflicts_assigned = 0
    while conflicts_assigned < num_conflicts:
        i = rng.integers(0, n)
        j = rng.integers(0, n)
        if i != j and preference[i][j] == 0:
            score = rng.integers(-10, -1)
            preference[i][j] = score
            preference[j][i] = score
            conflicts_assigned += 1

    preference = assign_random_positive_preferences(preference, n, graph_density)

    # age scoring for remaining neutral pairs
    for i in range(n):
        for j in range(i+1, n):
            if preference[i][j] == 0:
                age_diff = abs(ages[i] - ages[j])
                score = age_score(age_diff)
                preference[i][j] = score
                preference[j][i] = score

    return preference
    
def save_file_instances(n, filename='instance.npy'):
    P = generate_guest(n, 0.1, "easy")   # generates new instance
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


P = save_file_instances(n)

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
def initialize(m):
    # create a dictionary
    # key(table number): value(guest count at each table)
    return {t: 0 for t in range(1,m+1)}


def negative_greedy(graph, n, m):
    # dictionary key(guest ): value(table guest is assigned)
    assignment = {}
    # finds the table capacity
    capacity = n // m

    table_count = initialize(m)

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

    table_count = initialize(m)    
   

    for guest in range(n):
        best_score = -10000000
        best_table = 1 

        for table in range(1,m+1):

            if table_count[table] < capacity:
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
   
    table_count = initialize(m)
    
    sums = {}
    for i in range(n):
        total = 0 
        for j in range(n):
            if P[i][j]> 0:
                total += P[i][j]
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

    table_count = initialize(m)

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

    while len(assignment) < n:
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


def DSATUR(graph,n,m):
    assignment = {}
    capacity = n // m
    
    table_count = initialize(m)


    # saturation degree - number of different table assigned to neighbouring guest
    saturation = {}
    for guest in range(n):
        saturation[guest] = 0

    # break ties by storing the number of conflict for each guest
    conflict_count  = {}
    for guest in range(n):
        conflict_count[guest] = graph.get_adjacent_count(guest)

    unnassigned  = set(range(n))

    while unnassigned:

        # find the guest with the highest saturation and break ties by looking at conflict count
        best_guest = None
        largest_satur = -1
        highest_conflict = -1
        for guest in unnassigned:
            if (saturation[guest]> largest_satur) or (saturation[guest] == largest_satur and conflict_count[guest] > highest_conflict):
                best_guest = guest
                highest_conflict = conflict_count[guest]
                largest_satur = saturation[guest]

        # used to find lowest table number which has not conflicting guest and is not full
        used_tables = set()
        for neighbour in graph.vertices[best_guest]:
            if neighbour in assignment:
                used_tables.add(assignment[neighbour])

        table = 1
        while table <= m:
            if table not in used_tables and table_count[table] < capacity:
                break
            table += 1
            if table > m:
                table = min(table_count,key= table_count.get)
                break

        # assing guest to table        
        assignment[best_guest] = table
        table_count[table] += 1
        unnassigned.remove(best_guest)

        for neighbour in graph.vertics[best_guest]:
            if neighbour in unnassigned:
                neighbour_tables = set()
                for neigh_table in graph.vertices[neighbour]:
                    if neigh_table in assignment:
                        neighbour_tables.add(assignment[neigh_table])
                saturation[neighbour] = len(neighbour_tables)


        return assignment 


def DSATUR_positive_greedy(graph,n,m,P):
    assignment = {}
    capacity = n // m
    
    table_count = initialize(m)


    # saturation degree - number of different table assigned to neighbouring guest
    saturation = {}
    for guest in range(n):
        saturation[guest] = 0

    # break ties by storing the number of conflict for each guest
    conflict_count  = {}
    for guest in range(n):
        conflict_count[guest] = graph.get_adjacent_count(guest)

    unassigned  = set(range(n))

    while unassigned:

        # find the guest with the highest saturation and break ties by looking at conflict count
        best_guest = None
        largest_satur = -1
        highest_conflict = -1
        for guest in unassigned:
            if (saturation[guest]> largest_satur) or (saturation[guest] == largest_satur and conflict_count[guest] > highest_conflict):
                best_guest = guest
                highest_conflict = conflict_count[guest]
                largest_satur = saturation[guest]

        for table in range(1, m+1):
            if table_count[table] < capacity:
                score = 0
                for neighbour in graph.vertices[best_guest]:
                    if neighbour in assignment:
                        if assignment[neighbour] == table:
                            score += P[best_guest][neighbour]
                if score > best_score:
                    best_score = score
                    best_table = table

        # assign guest to best table
        assignment[best_guest] = best_table
        table_count[best_table] += 1
        unassigned.remove(best_guest)
        
        
        # update saturation of unassigned positive neighbours
        for neighbour in graph.vertices[best_guest]:
            if neighbour in unassigned:
                neighbour_tables = set()
                for nn in graph.vertices[neighbour]:
                    if nn in assignment:
                        neighbour_tables.add(assignment[nn])
                saturation[neighbour] = len(neighbour_tables)

    return assignment


# calculate the total satisfaction score 
def satisfaction_score(assignment, P, n):
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
    time_limit = 10
    best_state = initial_assignment.copy()
    stagnation = 0
    v = 1
    il_limit = 100 
    x = initial_assignment.copy()
    start_time = time.time()
    max_stagnation  = 100
    gamma = 0.90
        
    # Simmulated annealing that continue while temperture is not zero or the time limit is not reached
    while T>0 and (time.time()- start_time)< time_limit:
        for il in range(il_limit):
            y = x.copy()
            y = generate_neighbour_state(y, n, v)
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


# calculate the satisfaction score for each table
def satifaction_per_table(table_guest, P ):
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
    improved = True
    while improved:
        improved = False

        table_guests = {table: [] for table in range(1, m+1)}
        for g in range(n):
            table_guests[assignment[g]].append(g)

        current_scores = satifaction_per_table(table_guests,P)
        sorted_table_scoring = sorted(current_scores, key=current_scores.get)
        worst_table1, worst_table2 = sorted_table_scoring[:2]

        before_score = satisfaction_score(assignment, P, n)

        for guest1 in table_guests[worst_table1]:
            for guest2 in table_guests[worst_table2]:
                
                assignment[guest1], assignment[guest2] = assignment[guest2], assignment[guest1]
                after_score = satisfaction_score(assignment, P, n)

                if after_score> before_score:
                    improved = True
                    break
                else:
                    assignment[guest1], assignment[guest2] = assignment[guest2], assignment[guest1]
            if improved:
                break

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
def test_symmetry(P):
    assert np.array_equal(P, P.T), " not symmetric"
    print("Preference matrix is symmetric")

test_symmetry(P)    

        
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


"""

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
"""



neg_assignment = negative_greedy(build_graph_negative(P, n), n, m)
neg_initial_score = satisfaction_score(neg_assignment, P, n)
neg_temp = initial_temp_cal(neg_assignment, 200, n)
neg_sa_state = simulated_annealing(neg_assignment, n, m, P, neg_temp)
neg_sa_score = satisfaction_score(neg_sa_state, P, n)
neg_ls_state = local_search(neg_sa_state, n, m, P)
neg_ls_score = satisfaction_score(neg_ls_state, P, n)

print(f"Initial satisfaction score with negative greedy: {neg_initial_score}")
print(f"Satisfaction score with negative greedy: {neg_sa_score}")
print(f"Satisfaction after local search for negative greedy: {neg_ls_score}")


mix_assignment = mixed_greedy(n, m, P)
mix_initial_score = satisfaction_score(mix_assignment, P, n)
mix_temp = initial_temp_cal(mix_assignment, 200, n)
mix_sa_state = simulated_annealing(mix_assignment, n, m, P, mix_temp)
mix_sa_score = satisfaction_score(mix_sa_state, P, n)
mix_ls_state = local_search(mix_sa_state, n, m, P)
mix_ls_score = satisfaction_score(mix_ls_state, P, n)

print(f"initial satisfaction score with mix greedy: {mix_initial_score}")
print(f"Satisfaction score with mix greedy: {mix_sa_score}")
print(f"Satisfaction after local search for mix greedy: {mix_ls_score}")


pos_assignment = ordered_positive_greedy(n, m, P)
pos_initial_score = satisfaction_score(pos_assignment, P, n)
pos_temp = initial_temp_cal(pos_assignment, 200, n)
pos_sa_state = simulated_annealing(pos_assignment, n, m, P, pos_temp)
pos_sa_score = satisfaction_score(pos_sa_state, P, n)
pos_ls_state = local_search(pos_sa_state, n, m, P)
pos_ls_score = satisfaction_score(pos_ls_state, P, n)

print(f"initial satisfaction score with positive greedy: {pos_initial_score}")
print(f"Satisfaction score with positive greedy: {pos_sa_score}")
print(f"Satisfaction after local search for positive greedy: {pos_ls_score}")


bfs_assignment = BFS_greedy(build_graph_positive(P, n), n, m)
bfs_initial_score = satisfaction_score(bfs_assignment, P, n)
bfs_temp = initial_temp_cal(bfs_assignment, 100, n)
bfs_sa_state = simulated_annealing(bfs_assignment, n, m, P, bfs_temp)
bfs_sa_score = satisfaction_score(bfs_sa_state, P, n)
bfs_ls_state = local_search(bfs_sa_state, n, m, P)
bfs_ls_score = satisfaction_score(bfs_ls_state, P, n)

print(f"initial satisfaction score with bfs greedy: {bfs_initial_score}")
print(f"Satisfaction score with bfs greedy: {bfs_sa_score}")
print(f"Satisfaction after local search for bfs greedy: {bfs_ls_score}")

dsatur_assignment = BFS_greedy(build_graph_negative(P, n), n, m)
dsatur_initial_score = satisfaction_score(dsatur_assignment, P, n)
dsatur_temp = initial_temp_cal(dsatur_assignment, 100, n)
dsatur_sa_state = simulated_annealing(dsatur_assignment, n, m, P, dsatur_temp)
dsatur_sa_score = satisfaction_score(dsatur_sa_state, P, n)
dsatur_ls_state = local_search(dsatur_sa_state, n, m, P)
dsatur_ls_score = satisfaction_score(dsatur_ls_state, P, n)

print(f"initial satisfaction score with dsature: {dsatur_initial_score}")
print(f"Satisfaction score with dsatur: {dsatur_sa_score}")
print(f"Satisfaction after local search for dsatur: {dsatur_ls_score}")


dsatur_pos_assignment = BFS_greedy(build_graph_positive(P, n), n, m)
dsatur_pos_initial_score = satisfaction_score(dsatur_pos_assignment, P, n)
dsatur_pos_temp = initial_temp_cal(dsatur_pos_assignment, 100, n)
dsatur_pos_sa_state = simulated_annealing(dsatur_pos_assignment, n, m, P, dsatur_pos_temp)
dsatur_pos_sa_score = satisfaction_score(dsatur_pos_sa_state, P, n)
dsatur_pos_ls_state = local_search(dsatur_pos_sa_state, n, m, P)
dsatur_pos_ls_score = satisfaction_score(dsatur_pos_ls_state, P, n)


print(f"initial satisfaction score with dsature pos: {dsatur_pos_initial_score}")
print(f"Satisfaction score with dsatur pos: {dsatur_pos_sa_score}")
print(f"Satisfaction after local search for dsatur pos: {dsatur_pos_ls_score}")
