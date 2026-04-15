import time
import math
import random
from Hueristic_algorithms import DSATUR
from Guest_Creations import generate_guest
import numpy as np
import csv
import random
import matplotlib.pyplot as plt
import pandas as pd



rng = np.random.default_rng()

#calculates the total satisfaction score 
def satisfaction_score(assignment, P, n):
   total_score = 0
   for i in range(n):
     for j in range(i+1, n):
         if assignment[i] == assignment[j]:
             total_score += P[i][j]
   return total_score  


# swap operator, changes assigment of guest at different tables
def generate_neighbour_state(assignment, n, v):
    new_assignment = assignment.copy()

    # v is the number of swap operation to do 
    for i in range(v):
        guest1 = random.randint(0, n-1)
        guest2 = random.randint(0, n-1)

        while new_assignment[guest1] == new_assignment[guest2]:
            guest2 = random.randint(0, n-1)
        new_assignment[guest1], new_assignment[guest2] = new_assignment[guest2], new_assignment[guest1]

    return new_assignment


def initial_temp_cal(assignment, num_samples, n, P, acceptance_rate = 0.8): 
    neg_change = []
    current_assignment = assignment.copy()

    unique_tables = set(assignment.values())
    if len(unique_tables) <= 1:
        return 1.0
    else:

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
            
            current_assignment[guest1], current_assignment[guest2] = current_assignment[guest2],current_assignment[guest1]

        if neg_change:
            average_change = sum(neg_change) / len(neg_change)
        else:
            average_change = 1 

        T = average_change / (-math.log(acceptance_rate))

        return T

def simulated_annealing(initial_assignment, n, m, P, time_limit):
    x = initial_assignment.copy()
    best_state = x.copy()
    best_score = satisfaction_score(x, P, n)
    stagnation = 0
    v = 1
    il_limit = 100 
    T = initial_temp_cal(initial_assignment, 200, n, P)
    start_time = time.time()
    max_stagnation  = 100
    gamma = 0.9
    if m == 1:
        return initial_assignment
    else:
        
        # Simmulated annealing that continue while temperture is not zero or the time limit is not reached
        while T > 1e-6 and (time.time() - start_time) < time_limit:
            for i in range(il_limit):
                y = generate_neighbour_state(x, n, v)
                f_x = satisfaction_score(x, P, n)
                f_y = satisfaction_score(y, P, n)
                delta = f_y - f_x

                if delta > 0:
                    x = y
                    stagnation = 0
                    v = 1
                    if f_y > best_score:
                        best_state = y.copy()
                        best_score = f_y
                else:
                    r = random.random()
                    try:
                        prob_y = 1 / (1 + math.exp(-(delta) / T))
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



"""
time_limits = [3, 5, 10, 30, 60]
seeds = [20, 100, 300]

easy_sizes = [50, 200, 400]
easy_table_sizes= [5, 20, 40]
easy_SA_results = {}

realistic_sizes = [20, 100, 200, 400]
realistic_table_sizes = [2, 10, 20, 40]
realistic_SA_results = {}

easy_instance = {}
for n, m in zip(easy_sizes, easy_table_sizes):
    easy_instance[n] = generate_guest(n, 0.1, 'easy', rng)

realistic_instance = {}
for n, m in zip(realistic_sizes, realistic_table_sizes):
    realistic_instance[n] = generate_guest(n, 0.4, 'realistic', rng)


ls_easy_result = {}
ls_realistic_result = {}


# Easy
for time_limit in time_limits:
    easy_SA_results[time_limit] = {}
    ls_easy_result[time_limit] = {}

    for n, m in zip(easy_sizes, easy_table_sizes ):
        P = easy_instance[n]
        average_sa_scores = []
        ls_average_scores = []

        for seed in seeds:
            random.seed(seed)
            np.random.seed(seed)

            dsatur_assignment = DSATUR(P, n, m)
            # T0 = initial_temp_cal(dsatur_assignment, 200, n, P)
            sa_state = simulated_annealing(dsatur_assignment, n, m, P, time_limit)
            #ls_state = local_search(sa_state, n, m, P)

            average_sa_scores.append(satisfaction_score(sa_state, P, n))
            #ls_average_scores.append(satisfaction_score(ls_state, P, n))

        sa_avg = round(sum(average_sa_scores) / len(average_sa_scores), 2)
        #ls_avg = round(sum(ls_average_scores) / len(ls_average_scores), 2)

        easy_SA_results[time_limit][n] = sa_avg
        #ls_easy_result[time_limit][n]  = ls_avg
        #print(f"Easy Time: {time_limit}s n={n} SA: {sa_avg} LS: {ls_avg}")


with open('local_search_easy.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    
    header = ['Time Limit']
    for size in easy_sizes:
        header.append(f'n={size} SA')
        header.append(f'n={size} LS')
    writer.writerow(header)
    
    for i in time_limits:
        row = [i]
        for size in easy_sizes:
            row.append(easy_SA_results[i][size])
            row.append(ls_easy_result[i][size])
        writer.writerow(row)


for time_limit in time_limits:
    realistic_SA_results[time_limit] = {}
    ls_realistic_result[time_limit]  = {}

    for n, m in zip(realistic_sizes, realistic_table_sizes):
        P = realistic_instance[n]
        sa_scores = []
        ls_scores = []

        for seed in seeds:
            random.seed(seed)
            np.random.seed(seed)
            dsatur_assignment = DSATUR(P, n, m)
            # T0 = initial_temp_cal(dsatur_assignment, 200, n)
            sa_state = simulated_annealing(dsatur_assignment, n, m, P, time_limit)
            ls_state = local_search(sa_state, n, m, P)
            sa_scores.append(satisfaction_score(sa_state, P, n))
            ls_scores.append(satisfaction_score(ls_state, P, n))

        realistic_SA_results[time_limit][n] = round(sum(sa_scores) / len(sa_scores), 2)
        ls_realistic_result[time_limit][n]  = round(sum(ls_scores) / len(ls_scores), 2)
        print(f"Realistic Time: {time_limit}s n={n} SA: {realistic_SA_results[time_limit][n]} LS: {ls_realistic_result[time_limit][n]}")


with open('local_search_realistic.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    header = ['Time Limit']
    for size in realistic_sizes:
        header.append(f'n={size} SA')
        header.append(f'n={size} LS')
    writer.writerow(header)
    for tl in time_limits:
        row = [tl]
        for size in realistic_sizes:
            row.append(realistic_SA_results[tl][size])
            row.append(ls_realistic_result[tl][size])
        writer.writerow(row)




easy_df = pd.read_csv('local_search_easy.csv')

plt.figure(figsize=(10, 6))
for n in easy_sizes:
    plt.plot(easy_df['Time Limit'], easy_df[f'n={n} SA'], 
             marker='o', linestyle='--', label=f'n={n} SA')
    plt.plot(easy_df['Time Limit'], easy_df[f'n={n} LS'], 
             marker='s', linestyle='-', label=f'n={n} SA+LS')
plt.xlabel('Time limit (seconds)')
plt.ylabel('Average satisfaction score')
plt.title('SA vs SA + Local Search for easy instances')
plt.legend()
plt.grid(True)
plt.savefig('ls_comparison_easy.png')
plt.show()   



# Realistic 
realistic_df = pd.read_csv('local_search_realistic.csv')

plt.figure(figsize=(10, 6))
for n in realistic_sizes:
    plt.plot(realistic_df['Time Limit'], realistic_df[f'n={n} SA'], 
             marker='o', linestyle='--', label=f'n={n} SA')
    plt.plot(realistic_df['Time Limit'], realistic_df[f'n={n} LS'], 
             marker='s', linestyle='-', label=f'n={n} SA+LS')
plt.xlabel('Time limit (seconds)')
plt.ylabel('Average satisfaction score')
plt.title('SA vs SA + Local Search for realistic instances')
plt.legend()
plt.grid(True)
plt.savefig('ls_comparison_realistic.png')
plt.show()



gamma_values = [0.80, 0.85, 0.90, 0.95, 0.99]
seeds = [20, 100, 300]
time_limit = 3

easy_sizes      = [50,  80,  150, 200, 300]
easy_m_sizes    = [5,   8,   15,  20,  30]

realistic_sizes   = [20,  50,  80,  150, 200]
realistic_m_sizes = [5,   5,   8,   15,  20]


easy_instances = {}
for n in easy_sizes:
    easy_instances[n] = generate_guest(n, 0.1, 'easy', rng)

realistic_instances = {}
for n in realistic_sizes:
    realistic_instances[n] = generate_guest(n, 0.4, 'realistic', rng)

gamma_easy_results      = {}
gamma_realistic_results = {}
 
for gamma in gamma_values:
    gamma_easy_results[gamma] = {}

    for n, m in zip(easy_sizes, easy_m_sizes):
        P = easy_instances[n]
        scores = []

        for seed in seeds:
            random.seed(seed)
            np.random.seed(seed)
            dsatur_assignment = DSATUR(P, n, m)
            T0 = initial_temp_cal(dsatur_assignment, 200, n, P)
            sa_state = simulated_annealing(dsatur_assignment, n, m, P, time_limit, gamma)
            score = satisfaction_score(sa_state, P, n)
            scores.append(score)

        average = round(sum(scores) / len(scores), 2)
        gamma_easy_results[gamma][n] = average
        print(f"Easy Gamma: {gamma} n={n} Avg: {average}")



# Realistic 
for gamma in gamma_values:
    gamma_realistic_results[gamma] = {}

    for n, m in zip(realistic_sizes, realistic_m_sizes):
        P = realistic_instances[n]
        scores = []

        for seed in seeds:
            random.seed(seed)
            np.random.seed(seed)
            dsatur_assignment = DSATUR(P, n, m)
            T0       = initial_temp_cal(dsatur_assignment, 200, n, P)
            sa_state = simulated_annealing(dsatur_assignment, n, m, P, time_limit, gamma)
            score    = satisfaction_score(sa_state, P, n)
            scores.append(score)

        average = round(sum(scores) / len(scores), 2)
        gamma_realistic_results[gamma][n] = average
        print(f"Realistic Gamma: {gamma} n={n} Avg: {average}")


with open('gamma_easy.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    header = ['Gamma']
    for n in easy_sizes:
        header.append(f'n={n}')
    writer.writerow(header)
    for gamma in gamma_values:
        row = [gamma]
        for n in easy_sizes:
            row.append(gamma_easy_results[gamma][n])
        writer.writerow(row)

with open('gamma_realistic.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    header = ['Gamma']
    for n in realistic_sizes:
        header.append(f'n={n}')
    writer.writerow(header)
    for gamma in gamma_values:
        row = [gamma]
        for n in realistic_sizes:
            row.append(gamma_realistic_results[gamma][n])
        writer.writerow(row)

easy_df = pd.read_csv('gamma_easy.csv')

plt.figure(figsize=(10, 6))
for col in easy_df.columns[1:]:
    plt.plot(easy_df['Gamma'], easy_df[col], marker='o', label=col)
plt.xlabel('Gamma value')
plt.ylabel('Average satisfaction score')
plt.title('Effect of gamma on DSATUR + SA — easy instances')
plt.legend()
plt.grid(True)
plt.savefig('gamma_easy.png')
plt.show()

# Plot Realistic
realistic_df = pd.read_csv('gamma_realistic.csv')

plt.figure(figsize=(10, 6))
for col in realistic_df.columns[1:]:
    plt.plot(realistic_df['Gamma'], realistic_df[col], marker='o', label=col)
plt.xlabel('Gamma value')
plt.ylabel('Average satisfaction score')
plt.title('Effect of gamma on DSATUR + SA — realistic instances')
plt.legend()
plt.grid(True)
plt.savefig('gamma_realistic.png')
plt.show()
"""



