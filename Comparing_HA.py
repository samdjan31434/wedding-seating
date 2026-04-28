import matplotlib.pyplot as plt
from Hueristic_algorithms import(
    negative_greedy, mixed_greedy, ordered_positive_greedy, DSATUR,
     DSATUR_positive_greedy
    )
from extra import satisfaction_score
from Guest_Creations import generate_guest
import numpy as np
import csv
import pandas as pd
from Simulated_annealing import simulated_annealing , initial_temp_cal
import seaborn as sns

# instance with there corresponding table sizes
rng = np.random.default_rng()
instance_sizes = [
    10, 20, 30, 40, 50, 60, 70, 80, 100, 120, 150, 200, 300, 400, 800]
m_sizes = [2, 5, 5, 5, 5, 6, 7, 8, 10, 12, 15, 20, 30, 40, 80]
num_runs = 3


instance_sizes = [10, 20, 50, 80, 120, 200, 400]
m_sizes        = [2,  5,  5,  8,  12,  20,  40]
num_runs       = 3

# Load initial greedy scores from existing csv for comparision
initial_df = pd.read_csv(f'greedy_scores_realistic_10_runs.csv')
initial_df = initial_df[initial_df['Num_Guests'].isin(instance_sizes)
].reset_index(drop=True)

# Store average SA score for each method
greedy_sa_results = {
    'Negative Greedy': [],
    'Mixed Greedy': [],
    'Positive Ordered': [],
    'DSATUR Negative': [],
    'DSATUR Positive': []
}


for n, m in zip(instance_sizes, m_sizes):
    sa_run_scores = {method: [] for method in greedy_sa_results.keys()}

    for run in range(num_runs):
        filename = f'instance_{n}_{m}_realistic_run{run}.npy'
        P = np.load(filename)

        assignments = {
            'Negative Greedy': negative_greedy(n, m, P),
            'Mixed Greedy': mixed_greedy(n, m, P),
            'Positive Ordered': ordered_positive_greedy(n, m, P),
            'DSATUR Negative': DSATUR(n, m, P),
            'DSATUR Positive': DSATUR_positive_greedy(n, m, P)
        }

        for method, assignment in assignments.items():
            sa_state = simulated_annealing(assignment, n, m, P, 3, 0.9)
            final_score = satisfaction_score(sa_state, P, n)
            sa_run_scores[method].append(final_score)

        print(f"n={n} m={m} run={run} done")

    for method in greedy_sa_results:
        greedy_sa_results[method].append(
            round(np.mean(sa_run_scores[method]), 2))

  
with open(f'greedy_vs_sa_easy.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    header = ['Num_Guests'] + \
             [f'{method} Initial' for method in greedy_sa_results] + \
             [f'{method} After SA' for method in greedy_sa_results]
    writer.writerow(header)

    for i, n in enumerate(instance_sizes):
        initial_row = [
            initial_df[method].iloc[i] for method in greedy_sa_results]
        sa_row = [greedy_sa_results[method][i] for method in greedy_sa_results]
        writer.writerow([n] + initial_row + sa_row)


methods = list(greedy_sa_results.keys())

def get_ranks(scores_dict):
    """Assign ranks, higher score better rank."""

    ranks = {}
    sorted_scores = sorted(set(scores_dict.values()), reverse=True)
    for method in scores_dict:
        ranks[method] = sorted_scores.index(scores_dict[method]) + 1
    return ranks

initial_rank_data  = {}
sa_rank_data       = {}
rank_change_data   = {}

for i, n in enumerate(instance_sizes):
    initial_scores = {method: initial_df[method].iloc[i] for method in methods}
    sa_scores = {method: greedy_sa_results[method][i]  for method in methods}

    initial_rank_data[n] = get_ranks(initial_scores)
    sa_rank_data[n]      = get_ranks(sa_scores)

    rank_change_data[n] = {}
    for method in methods:
        rank_change_data[n][method] = sa_rank_data[n][method] - initial_rank_data[n][method]

initial_rank_df  = pd.DataFrame(initial_rank_data,  index=methods)
sa_rank_df       = pd.DataFrame(sa_rank_data,        index=methods)
rank_change_df   = pd.DataFrame(rank_change_data,    index=methods)

# Create a heatmap
fig, axes = plt.subplots(1, 3, figsize=(18, 4))

sns.heatmap(initial_rank_df, annot=True, fmt='d', cmap='coolwarm',
            vmin=1, vmax=5, ax=axes[0])
axes[0].set_title('realistic initial greedy rankings')
axes[0].set_xlabel('Number of guests')
axes[0].set_ylabel('Method')

sns.heatmap(sa_rank_df, annot=True, fmt='d', cmap='coolwarm',
            vmin=1, vmax=5, ax=axes[1])
axes[1].set_title('realistic final SA rankings')
axes[1].set_xlabel('Number of guests')
axes[1].set_ylabel('Method')

sns.heatmap(rank_change_df, annot=True, fmt='d', cmap='coolwarm',
            center=0, ax=axes[2])
axes[2].set_title('Rank change after SA\nnegative = improved')
axes[2].set_xlabel('Number of guests')
axes[2].set_ylabel('Method')

plt.suptitle(f'Greedy ranking comparison before and after SA, realistic instances')
plt.tight_layout()
plt.savefig(f'ranking_heatmap_realistic.png')
plt.show()

print("\nInitial Greedy Rankings")
print(initial_rank_df.to_string())

print("\nFinal SA Rankings")
print(sa_rank_df.to_string())

print("\nRank Change After SA — negative means improved")
print(rank_change_df.to_string())


# Data Structures
greedy_results = {
    'Negative Greedy': [],
    'Mixed Greedy': [],
    'Positive Ordered': [],
    'DSATUR Negative': [],
    'DSATUR Positive': []
}

instance_sizes = [
    10, 20, 30, 40, 50, 60, 70, 80, 100, 120, 150, 200, 300, 400, 800]
m_sizes = [2, 5, 5, 5, 5, 6, 7, 8, 10, 12, 15, 20, 30, 40, 80]
num_runs = 10
filename = "greedy_scores_realistic_10_runs.csv"


for n, m in zip(instance_sizes, m_sizes):
    graph_density = 0.4
    run_scores = {method: [] for method in greedy_results.keys()}

    for run in range(num_runs):
        P = generate_guest(n, graph_density, "realistic")
        
        # Save instances to reuse
        inst_file = f'instance_{n}_{m}_realistic_run{run}.npy'
        np.save(inst_file, P)

        run_scores['Negative Greedy'].append(
            satisfaction_score(negative_greedy(n, m, P), P, n))
        run_scores['Mixed Greedy'].append(
            satisfaction_score(mixed_greedy(n, m, P), P, n))
        run_scores['Positive Ordered'].append(
            satisfaction_score(ordered_positive_greedy(n, m, P), P, n))
        run_scores['DSATUR Negative'].append(
            satisfaction_score(DSATUR(n, m, P), P, n))
        run_scores['DSATUR Positive'].append(
            satisfaction_score(DSATUR_positive_greedy(n, m, P), P, n))

    for method in greedy_results:
        average_score = np.mean(run_scores[method])
        greedy_results[method].append(average_score)


with open(filename, 'w', newline='') as file:
    writer = csv.writer(file)
    header = ['Num_Guests'] + list(greedy_results.keys())
    writer.writerow(header)
    
    for i, n in enumerate(instance_sizes):
        row = [n] + [greedy_results[m][i] for m in greedy_results]
        writer.writerow(row)


plt.figure(figsize=(12, 7))

with open(filename, 'r') as file:
    reader = csv.DictReader(file)
    # Extract data for plotting
    plot_data = {key: [] for key in header}
    for row in reader:
        for key in header:
            plot_data[key].append(float(row[key]))

# Plot each method against Num_Guests
x = plot_data['Num_Guests']
for method in greedy_results.keys():
    plt.plot(x, plot_data[method], marker='o', label=method)
"""
plt.xlabel('Number of Guests')
plt.ylabel('Average Initial Satisfaction Score')
plt.title('Comparison of Greedy Algorithms across 10 runs for realistic')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.7)
plt.savefig('run_realistic_10.png')
plt.show()
"""







