import time
import math
import random
from Hueristic_algorithms import DSATUR, ordered_positive_greedy
from Guest_Creations import generate_guest
import numpy as np
import csv
import matplotlib.pyplot as plt
import pandas as pd
from extra import local_search, satisfaction_score



rng = np.random.default_rng()

def generate_neighbour_state(assignment, n, v):
    """Creates a new candidate solution by swapping guests table assignment"""

    new_assignment = assignment.copy()
    # v is the number of swap operation to do 
    for i in range(v):
        guest1 = random.randint(0, n-1)
        guest2 = random.randint(0, n-1)

        # Check that the two swaped guest are sat at different tables
        while new_assignment[guest1] == new_assignment[guest2]:
            guest2 = random.randint(0, n-1)
        new_assignment[guest1], new_assignment[guest2] = new_assignment[guest2], new_assignment[guest1]

    return new_assignment


def initial_temp_cal(assignment, num_samples, n, P, acceptance_rate = 0.8): 
    """Estimates the starting temperature for Simulated Annealing"""
    neg_change = []
    current_assignment = assignment.copy()

    # Edge case: if every guest is sat at one table, cant swap
    unique_tables = set(assignment.values())
    if len(unique_tables) <= 1:
        return 1.0
    else:
        for i in range(num_samples):
            guest1 = random.randint(0, n-1)
            guest2 = random.randint(0, n-1)
            retries = 0
            while current_assignment[guest1] == current_assignment[guest2]:
                guest2 = random.randint(0, n - 1)
                retries += 1
                if retries > 100:
                    break

            if current_assignment[guest1] == current_assignment[guest2]:
                continue 
                
            score_before = satisfaction_score(current_assignment, P, n)
            # Temporary swap
            current_assignment[guest1], current_assignment[guest2] = \
            current_assignment[guest2],current_assignment[guest1]

            score_after = satisfaction_score(current_assignment, P, n)

            delta = score_after - score_before
            if delta < 0:
                neg_change.append(abs(delta))
            
            # Reverse temporary swap
            current_assignment[guest1], current_assignment[guest2] = \
            current_assignment[guest2], current_assignment[guest1]

        if neg_change:
            average_change = sum(neg_change) / len(neg_change)
        else:
            average_change = 1 

        T = average_change / (-math.log(acceptance_rate))

        return T

def simulated_annealing(initial_assignment, n, m, P, time_limit, gamma):
    """Improve guest seating using Simulated annealing"""
    x = initial_assignment.copy()
    best_state = x.copy()
    best_score = satisfaction_score(x, P, n)
    stagnation = 0
    v = 1           # Number of swaps per move  
    il_limit = 100  # Iterations per temperature level
    T = initial_temp_cal(initial_assignment, 100, n, P)
    start_time = time.time()
    max_stagnation = 100
    if m == 1:
        return initial_assignment
    else:
        
        # Loop until temperture is not zero or the time limit is not reached
        while T > 1e-6 and (time.time() - start_time) < time_limit:
            for i in range(il_limit):
                y = generate_neighbour_state(x, n, v)
                f_x = satisfaction_score(x, P, n)
                f_y = satisfaction_score(y, P, n)
                delta = f_y - f_x

                # Accepts new state if better
                if delta > 0:
                    x = y
                    stagnation = 0
                    v = 1
                    if f_y > best_score:
                        best_state = y.copy()
                        best_score = f_y
                else:
                    # if new state is worst accept based on probability
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
                    
                    # Change neighberhood if stuck
                    if stagnation == max_stagnation:
                        stagnation = 0
                        v += 1
                        if v > m:
                            v = 1

            # Cooling schedule                
            T *= gamma  

    return best_state


time_limit = [3, 5, 10, 30, 60]
seeds = [20, 100, 300]


def run_time_experiment(difficulty, sizes, table_sizes, density):
    """Runs sa and local search for different time limits and instances"""
        
    instances = {n: generate_guest(n, density, difficulty) for n in sizes}
    np.save(f"{difficulty}_time_instances.npy", instances, allow_pickle=True)

    results = {tl: {} for tl in time_limit}

    for tl in time_limit:
        for n, m in zip(sizes, table_sizes):
            P = instances[n]
            average_sa_scores = []
            ls_average_scores = []

            for seed in seeds:
                random.seed(seed)
                np.random.seed(seed)

                dsatur_assignment = DSATUR(P, n, m)
                sa_state = simulated_annealing(dsatur_assignment, n, m, P, tl, 0.9)
                ls_state = local_search(sa_state, n, m, P)

                average_sa_scores.append(satisfaction_score(sa_state, P, n))
                ls_average_scores.append(satisfaction_score(ls_state, P, n))

            
            results[tl][n] = {
                "sa": round(sum(average_sa_scores) / len(average_sa_scores), 2),
                "ls": round(sum(ls_average_scores) / len(ls_average_scores), 2),
            }

            print(f"Time {tl}s | n={n} | SA={results[tl][n]['sa']} | LS={results[tl][n]['ls']}")

    return results


def save_results(csv_filename, sizes, results):
    """Save result to CSV."""

    with open(csv_filename, 'w', newline='') as f:
        writer = csv.writer(f)

        header = ['Time Limit']
        for n in sizes:
            header += [f'n={n} SA', f'n={n} LS']
        writer.writerow(header)

        for tl in time_limit:
            row = [tl]
            for n in sizes:
                row += [results[tl][n]['sa'], results[tl][n]['ls']]
            writer.writerow(row)


def plot_results(csv_filename, sizes, title, png_filename):
    """Plot SA vs SA+LS results from CSV."""

    df = pd.read_csv(csv_filename)
    plt.figure(figsize=(10, 6))
    for n in sizes:
        plt.plot(df['Time Limit'], df[f'n={n} SA'],
                 marker='o', linestyle='--', label=f'n={n} SA')
        plt.plot(df['Time Limit'], df[f'n={n} LS'],
                 marker='s', linestyle='-', label=f'n={n} SA+LS')

    plt.xlabel('Time limit (seconds)')
    plt.ylabel('Average satisfaction score')
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.savefig(png_filename)
    plt.show()

# Result for larger instances sizes
def larger_result_time_limit():
    """Run time experiment for larger instances"""

    easy_sizes = [100, 200, 300, 400]
    easy_tables = [10, 20, 30, 40]

    easy_results = run_time_experiment('sparse', easy_sizes, easy_tables, 0.1)

    save_results('larger_easy_time_results.csv', easy_sizes, easy_results)
    plot_results('larger_easy_time_results.csv', easy_sizes,
                'SA vs SA + Local Search (sparse)',
                'larger_easy_time_plot.png')

    realistic_sizes = [100, 200, 300, 400]
    realistic_tables = [10, 20, 30, 40]

    realistic_results = run_time_experiment('realistic', realistic_sizes, realistic_tables, 0.4)
    save_results('larger_realistic_time_results.csv', realistic_sizes, realistic_results)
    plot_results('larger_realistic_time_results.csv', realistic_sizes,
                'SA vs SA + Local Search (Realistic)',
                'larger_realistic_time_plot.png')


def result_easy_time_limit():
    "Run time limit experiment on sparse instances."

    easy_sizes = [20, 40, 60, 80]
    easy_tables = [2, 4, 6, 8]

    easy_results = run_time_experiment('sparse', easy_sizes, easy_tables, 0.1)
    save_results('easy_time_results.csv', easy_sizes, easy_results)
    plot_results('easy_time_results.csv', easy_sizes,
                'SA vs SA + Local Search (sparse)',
                'easy_time_plot.png')

    realistic_sizes = [20, 40, 60, 80]
    realistic_tables = [2, 4, 6, 8]


    realistic_results = run_time_experiment(
        'realistic', realistic_sizes, realistic_tables, 0.4
    )
    save_results('realistic_time_results.csv', realistic_sizes, realistic_results)
    plot_results('realistic _time_results.csv', realistic_sizes,
                'SA vs SA + Local Search (Realistic)',
                'realistic_time_plot.png')

#Parameter for gamma experiment
gamma_values = [0.80, 0.85, 0.90, 0.95, 0.99]
seeds = [20, 100, 300]
time_limit = 5

easy_realistic_sizes      = [20, 40, 60, 80]
easy_realistic_m_sizes    = [2, 4, 6, 8]



def gamma_experiment(instances, difficulty):
    """Runs experiment for gamma on different instances size on SA."""

    result ={}
    for gamma in gamma_values:
        result[gamma] = {}

        for n, m in zip(easy_realistic_sizes, easy_realistic_m_sizes):
            P = instances[n]
            scores = []

            for seed in seeds:
                random.seed(seed)
                np.random.seed(seed)

                pos_assignment = ordered_positive_greedy(n, m,  P)
                sa_state = simulated_annealing(pos_assignment, n, m, P, time_limit, gamma)
                score = satisfaction_score(sa_state, P, n)
                scores.append(score)

            # Calculate the mean across all seeds
            average = round(sum(scores) / len(scores), 2)
            result[gamma][n] = average
            print(f"{difficulty} Gamma: {gamma} n={n} Avg: {average}")
    
    return result



def save_and_plot(results, filename, title):
    """Saves result to CSV and generate a plot of performance."""

    csv_file = f'{filename}.csv'

    # Write result to CSV file 
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        header = ['Gamma']
        for n in easy_realistic_sizes:
            header.append(f'n={n}')
        writer.writerow(header)
        for gamma in gamma_values:
            row = [gamma] + [results[gamma][n] for n in easy_realistic_sizes]
            writer.writerow(row)

    # Plot the results
    df = pd.read_csv(csv_file)
    plt.figure(figsize=(10, 6))

    for col in df.columns[1:]:
        plt.plot(df['Gamma'], df[col], marker='o', label=col)

    plt.xlabel('Gamma value')
    plt.ylabel('Average satisfaction score')
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.savefig(f'{filename}.png')
    plt.show()


# Generates and save instances for easy and realistic
easy_instances = {}
for n in easy_realistic_sizes:
        filename = f'instance_{n}_easy.npy'
        P = generate_guest(n, 0.1, 'sparse')
        np.save(filename, P)
        easy_instances[n] = np.load(filename)

realistic_instances = {}
for n in easy_realistic_sizes:
       filename = f'instance_{n}_realistic.npy'
       P = generate_guest(n, 0.4, 'realistic')
       np.save(filename, P)
       realistic_instances[n] = np.load(filename)


gamma_easy_results = gamma_experiment(easy_instances, "sparse")
gamma_realistic_results = gamma_experiment(realistic_instances, "Realistic")

save_and_plot(
    gamma_easy_results, 
    'Gamma_sparse', 
    'Effect of Gamma on Sparse Instances'
)

save_and_plot(
    gamma_realistic_results, 
    'Gamma_realistic', 
    'Effect of Gamma on Realistic Instances '
)
