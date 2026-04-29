import numpy as np
from Hueristic_algorithms import negative_greedy, mixed_greedy, ordered_positive_greedy, DSATUR, DSATUR_positive_greedy
from Guest_Creations import generate_guest
from extra import local_search
import random
import os
import csv
from Simulated_annealing import simulated_annealing, satisfaction_score


rng = np.random.default_rng()
n = 60    # number of guest
m = 6   # number of tables


P = generate_guest(n, 0.4, "realistic")
#filename = f"realistic_instance_n{n}_m{m}.npy"
#file_path = os.path.join(output_folder, filename)
#np.save(file_path, P)

# save the file as .inc to use in GAMS
with open('Generated_instance.inc', 'w') as f:
    for i in range(n):
        for j in range(n):
            if P[i][j] != 0:
                f.write(f"P('g{i+1}','g{j+1}') = {P[i][j]} ;\n")


def run_three_seeds(initial_assignment, n, m, P):
    """Runs the Heuristic pipeline for 3 random seeds"""
    scores = []
    for seed in range(3):
        random.seed(seed)
        assignment_copy = initial_assignment.copy()
        sa_state = simulated_annealing(assignment_copy, n, m, P, 5, 0.9)
        ls_state = local_search(sa_state, n, m, P)
        score = satisfaction_score(ls_state, P, n)
        scores.append(score)

    average = round(sum(scores) / len(scores), 2)
    
    return average

def save_results_to_csv(results, ilp_score, best_possible, ilp_time, n, m, difficulty, filename='results.csv'):
    """Append experimental results to .csv file"""

    # check if file exists
    file_exists = os.path.exists(filename)
    
    with open(filename, 'a', newline='') as f:
        writer = csv.writer(f)
        
        # add header if file is new
        if not file_exists:
            writer.writerow([
                'Guests', 'Tables', 'Difficulty',
                'ILP Score', 'Best Possible', 'ILP Time', 'method'
                'Average'
            ])
        for method, avg in results.items():
            writer.writerow([
                n, m, difficulty,
                ilp_score, best_possible, ilp_time, method,
                round(avg, 2)
            ])


# replaces zero in csv file with result from GAMS
ilp_score = 0
best_possible = 0
ilp_time = 0

# run 3 seeds function for all greedy algorithm
neg_avg = run_three_seeds(
    negative_greedy(P, n, m), n, m, P)
print(f"Satisfaction after local search for negative greedy: {neg_avg}")

mix_avg = run_three_seeds(
    mixed_greedy(n, m, P), n, m, P)
print(f"Satisfaction after local search for mix greedy: {mix_avg}")

pos_avg = run_three_seeds(
    ordered_positive_greedy(n, m, P), n, m, P)
print(f"Satisfaction after local search for pos greedy: {pos_avg}")

dsatur_avg = run_three_seeds(
    DSATUR(n, m, P), n, m, P)
print(f"Satisfaction after local search for dsatur: {dsatur_avg}")

dsatur_pos_avg = run_three_seeds(
    DSATUR_positive_greedy(n, m, P), n, m, P)
print(f"Satisfaction after local search for dsatur pos: {dsatur_pos_avg}")


results = {
    'Negative Greedy': neg_avg,
    'Mixed Greedy': mix_avg,
    'Positive Ordered': pos_avg,
    'DSATUR Greedy': dsatur_avg,
    'DSATUR pos Greedy': dsatur_pos_avg,
}

"""
save_results_to_csv(results,
 ilp_score, 
 best_possible, 
 ilp_time,
    n,
   m, 
 "realistic", 
 filename ='score_comparision.csv')
"""



