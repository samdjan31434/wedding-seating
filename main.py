import numpy as np
import time
import random
import math
import os
import csv


rng = np.random.default_rng()
n = 60    # number of guest
m = 6   # number of tables


# Generate Guest Section
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


def create_couple_pairs(num_couples, adults, preference):
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

         
    couple_pairs , preference = create_couple_pairs(num_couples, adults, preference)   
    
    if difficulty == "hard" or difficulty == "realistic":
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
## end of section





# calculate the total satisfaction score 
def satisfaction_score(assignment, P, n):
   total_score = 0
   for i in range(n):
     for j in range(i+1, n):
         if assignment[i] == assignment[j]:
             total_score += P[i][j]
   return total_score  


# swap operator, changes assigment of guest at different tables
def generate_neighbour_state(assignment , n, v):
    new_assignment  = assignment.copy()

    # v is the number of swap operation to do 
    for i in range(v):
        guest1 = random.randint(0, n-1)
        guest2 = random.randint(0, n-1)

        while new_assignment[guest1] == new_assignment[guest2]:
            guest2 = random.randint(0, n-1)
        new_assignment[guest1], new_assignment[guest2] = new_assignment[guest2], new_assignment[guest1]

    return new_assignment


def initial_temp_cal(assignment, num_samples, n, acceptance_rate=0.8): 
    neg_change = []
    current_assignment = assignment.copy()

    for i in range(num_samples):
        guest1 = random.randint(0, n-1)
        guest2 = random.randint(0, n-1)
        retries = 0
        while current_assignment[guest1] == current_assignment[guest2]:
            guest2 = random.randint(0, n-1)
            retries += 1
            if retries > 100:
                break

        if current_assignment[guest1] == current_assignment[guest2]:
            continue 
               
        score_before = satisfaction_score(current_assignment, P, n)
        current_assignment[guest1] , current_assignment[guest2] = current_assignment[guest2],current_assignment[guest1]
        score_after  = satisfaction_score(current_assignment, P, n)

        if (score_after -score_before)< 0:
            neg_change.append(abs(score_after-score_before))
        
        current_assignment[guest1],current_assignment[guest2] = current_assignment[guest2],current_assignment[guest1]

    if neg_change:
        average_change = sum(neg_change) / len(neg_change)
    else:
        average_change = 1 

    T = average_change / (-math.log(acceptance_rate))

    return T


def simulated_annealing(initial_assignment, n, m, P, T):
    time_limit = 3   
    best_state = initial_assignment.copy()
    stagnation = 0
    v = 1
    il_limit = 100 
    x = initial_assignment.copy()
    start_time = time.time()
    max_stagnation  = 100
    gamma = 0.95
        
    # Simmulated annealing that continue while temperture is not zero or the time limit is not reached
    while T>0 and (time.time()- start_time)< time_limit:
        for il in range(il_limit):
            y = x.copy()
            y = generate_neighbour_state(y, n, v)
            f_x = satisfaction_score(x, P, n)
            f_y = satisfaction_score(y, P, n)

            if f_y > f_x:
                x = y
                stagnation =0
                v = 1
                if f_y > satisfaction_score(best_state, P, n):
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
                        stagnation = 0
                        v += 1
                        if v > m:
                            v = 1
            T = T * gamma  

    return best_state


# calculate the satisfaction score for each table
def satifaction_per_table(table_guest, P):
    current_scores = {}
    for table,guest  in table_guest.items():
        total = 0
        for i in range(len(guest)):
            for j in range(i+1, len(guest)):
                guest1 = guest[i]
                guest2 = guest[j]
                total += P[guest1][guest2]
        current_scores[table] = total

    return current_scores            


def local_search(assignment, n, m, P):
    improved = True
    while improved:
        improved = False

        table_guests = {table: [] for table in range(1, m+1)}
        for g in range(n):
            table_guests[assignment[g]].append(g)

        current_scores = satifaction_per_table(table_guests, P)
        sorted_table_scoring = sorted(current_scores, key=current_scores.get)
        worst_table1, worst_table2 = sorted_table_scoring[:2]

        before_score = satisfaction_score(assignment, P, n)

        for guest1 in table_guests[worst_table1]:
            for guest2 in table_guests[worst_table2]:
                
                assignment[guest1], assignment[guest2] = assignment[guest2], assignment[guest1]
                after_score = satisfaction_score(assignment, P, n)

                if after_score > before_score:
                    improved = True
                    break
                else:
                    assignment[guest1], assignment[guest2] = assignment[guest2], assignment[guest1]
            if improved:
                break

    return assignment             
 

def bellows_peterson_instance():
    n = 17
    P = np.zeros((n,n), dtype=int)

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

def run_three_seeds(initial_assignment, n, m, P):
    scores = []
    for seed in range(3):
        random.seed(seed)
        assignment_copy = initial_assignment.copy()
        T_0 = initial_temp_cal(assignment_copy, 200, n)
        sa_state = simulated_annealing(assignment_copy, n, m, P, T_0)
        ls_state = local_search(sa_state, n, m, P)
        score = satisfaction_score(ls_state, P, n)
        scores.append(score)

    best = max(scores)
    average = round(sum(scores) / len(scores), 2)
    worst = min(scores)

    return best, average, worst

def save_results_to_csv(results, ilp_score, best_possible, ilp_time, n, m, difficulty, filename='results.csv'):
    
    # check if file exists
    file_exists = os.path.exists(filename)
    
    with open(filename, 'a', newline='') as f:
        writer = csv.writer(f)
        
        # add header if file is new
        if not file_exists:
            writer.writerow([
                'Guests', 'Tables', 'Difficulty',
                'ILP Score', 'Best Possible', 'ILP Time',
                'Method', 'Best', 'Average', 'Worst'
            ])
        for method, (best, avg, worst) in results.items():
            writer.writerow([
                n, m, difficulty,
                ilp_score, best_possible, ilp_time,
                method, best, round(avg, 2), worst
            ])







"""    
def save_file_instances(n, filename='instance.npy'):
    P = generate_guest(n, 0.1, "easy")   
    np.save(filename, P)
    return P
"""
"""
# save the file as .inc to use in GAMS
with open('Generated_instance.inc', 'w') as f:
    for i in range(n):
        for j in range(n):
            if P[i][j] != 0:
                f.write(f"P('g{i+1}','g{j+1}') = {P[i][j]} ;\n")"""

#P = save_file_instances(n)

# used the pseudocode from https://www.researchgate.net/publication/354721896_A_Heuristic_Approach_in_Solving_the_Optimal_Seating_Chart_Problem
# variable and parameter used in simmulated annealing



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

dsatur_assignment = DSATUR(build_graph_negative(P, n), n, m)
dsatur_initial_score = satisfaction_score(dsatur_assignment, P, n)
dsatur_temp = initial_temp_cal(dsatur_assignment, 100, n)
dsatur_sa_state = simulated_annealing(dsatur_assignment, n, m, P, dsatur_temp)
dsatur_sa_score = satisfaction_score(dsatur_sa_state, P, n)
dsatur_ls_state = local_search(dsatur_sa_state, n, m, P)
dsatur_ls_score = satisfaction_score(dsatur_ls_state, P, n)

print(f"initial satisfaction score with dsatur: {dsatur_initial_score}")
print(f"Satisfaction score with dsatur: {dsatur_sa_score}")
print(f"Satisfaction after local search for dsatur: {dsatur_ls_score}")


dsatur_pos_assignment = DSATUR_positive_greedy(build_graph_positive(P, n), n, m)
dsatur_pos_initial_score = satisfaction_score(dsatur_pos_assignment, P, n)
dsatur_pos_temp = initial_temp_cal(dsatur_pos_assignment, 100, n)
dsatur_pos_sa_state = simulated_annealing(dsatur_pos_assignment, n, m, P, dsatur_pos_temp)
dsatur_pos_sa_score = satisfaction_score(dsatur_pos_sa_state, P, n)
dsatur_pos_ls_state = local_search(dsatur_pos_sa_state, n, m, P)
dsatur_pos_ls_score = satisfaction_score(dsatur_pos_ls_state, P, n)


print(f"initial satisfaction score with dsatur pos: {dsatur_pos_initial_score}")
print(f"Satisfaction score with dsatur pos: {dsatur_pos_sa_score}")
print(f"Satisfaction after local search for dsatur pos: {dsatur_pos_ls_score}")
"""



"""
# result from gams file
ilp_score =    1697
best_possible = 3343
ilp_time =   220


neg_best, neg_avg, neg_worst = run_three_seeds(
    negative_greedy(build_graph_negative(P, n), n, m), n, m, P)
print(f"Satisfaction after local search for negative greedy: {neg_avg}")

mix_best, mix_avg, mix_worst = run_three_seeds(
    mixed_greedy(n, m, P), n, m, P)
print(f"Satisfaction after local search for mix greedy: {mix_avg}")

pos_best, pos_avg, pos_worst = run_three_seeds(
    ordered_positive_greedy(n, m, P), n, m, P)
print(f"Satisfaction after local search for pos greedy: {pos_avg}")


bfs_best, bfs_avg, bfs_worst = run_three_seeds(
    BFS_greedy(build_graph_positive(P, n), n, m), n, m, P)
print(f"Satisfaction after local search for bfs greedy: {bfs_avg}")


dsatur_best, dsatur_avg, dsatur_worst = run_three_seeds(
    DSATUR(build_graph_negative(P, n), n, m,), n, m, P)
print(f"Satisfaction after local search for dsatur: {dsatur_avg}")


dsatur_pos_best, dsatur_pos_avg, dsatur_pos_worst = run_three_seeds(
    DSATUR_positive_greedy(build_graph_positive(P, n), n, m, P), n, m, P)
print(f"Satisfaction after local search for dsatur pos: {dsatur_pos_avg}")



results = {
    'Negative Greedy':  (neg_best,    neg_avg,    neg_worst),
    'Mixed Greedy':     (mix_best,    mix_avg,    mix_worst),
    'Positive Ordered': (pos_best,    pos_avg,    pos_worst),
    'BFS Greedy':       (bfs_best,    bfs_avg,    bfs_worst),
    'DSATUR Greedy':    (dsatur_best, dsatur_avg, dsatur_worst),
    'DSATUR pos Greedy':  (dsatur_pos_best, dsatur_pos_avg, dsatur_pos_worst),
}


save_results_to_csv(results, ilp_score, best_possible, ilp_time, n, m, "realistic", filename='results.csv')
"""