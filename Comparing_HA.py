import matplotlib.pyplot as plt
from Hueristic_algorithms import negative_greedy, mixed_greedy, ordered_positive_greedy, BFS_greedy, DSATUR, DSATUR_positive_greedy
from extra import satisfaction_score
from Guest_Creations import generate_guest
import numpy as np
import csv


rng = np.random.default_rng()
instance_sizes = [10, 20, 30, 40, 50, 60, 70, 80, 100, 120, 150, 200, 300, 400]
m_sizes = [2,  5,  5,  5,  5,  6,  7,  8,  10,  12,  15,  20,  30, 40]
num_runs = 10

greedy_results = {
    'Negative Greedy':   [],
    'Mixed Greedy':      [],
    'Positive Ordered':  [],
    'BFS Greedy':        [],
    'DSATUR Negative':   [],
    'DSATUR Positive':   []
}

for n, m in zip(instance_sizes, m_sizes):
    
    
    graph_density = 0.1
    #graph_density = 0.4
    run_scores = {method: [] for method in greedy_results.keys()}

    for run in range(num_runs):

        # create new instane for each run
        P = generate_guest(n, graph_density, "easy", rng)
            

        neg_assignment  = negative_greedy(P, n, m)
        mix_assignment  = mixed_greedy(n, m, P)
        pos_assignment  = ordered_positive_greedy(n, m, P)
        bfs_assignment  = BFS_greedy(P, n, m)
        dsat_assignment = DSATUR(P, n, m)
        dsat_pos_assignment = DSATUR_positive_greedy(P, n, m, )


        # add score for each run
        run_scores['Negative Greedy'].append(satisfaction_score(neg_assignment, P, n))
        run_scores['Mixed Greedy'].append(satisfaction_score(mix_assignment, P, n))
        run_scores['Positive Ordered'].append(satisfaction_score(pos_assignment, P, n))
        run_scores['BFS Greedy'].append(satisfaction_score(bfs_assignment, P, n))
        run_scores['DSATUR Negative'].append(satisfaction_score(dsat_assignment, P, n))
        run_scores['DSATUR Positive'].append(satisfaction_score(dsat_pos_assignment, P, n))

    for method in greedy_results:
        average_score = np.mean(run_scores[method])
        greedy_results[method].append(average_score)




filename = "greedy_scores_easy_10_runs.csv"

with open(filename, 'w', newline='') as file:
    writer = csv.writer(file)
    
    # column names
    header = ['Num_Guests', 'Negative Greedy', 'Mixed Greedy', 'Positive Ordered', 
              'BFS Greedy', 'DSATUR Negative', 'DSATUR Positive']
    writer.writerow(header)
    
    # add average score for each instance size to each row
    for i, n in enumerate(instance_sizes):
        row = [
            n,
            greedy_results['Negative Greedy'][i],
            greedy_results['Mixed Greedy'][i],
            greedy_results['Positive Ordered'][i],
            greedy_results['BFS Greedy'][i],
            greedy_results['DSATUR Negative'][i],
            greedy_results['DSATUR Positive'][i]
        ]
        writer.writerow(row)


for method, scores in greedy_results.items():
    plt.plot(instance_sizes, scores, marker='o', label=method)

plt.xlabel('Number of guests')
plt.ylabel('Average Initial satisfaction score')
plt.title('Comparision of greedy algorithm across 10 runs for easy')
plt.legend()
plt.grid(True)
plt.show()
