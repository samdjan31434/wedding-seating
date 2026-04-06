import matplotlib.pyplot as plt
import os
import numpy as np
from Hueristic_algorithms import negative_greedy, mixed_greedy, ordered_positive_greedy, build_graph_negative, BFS_greedy, build_graph_positive, DSATUR, DSATUR_positive_greedy
from main import generate_guest, satisfaction_score


instance_sizes = [10, 20, 30, 40, 50, 60, 70, 80, 100, 120, 150, 200, 300]
m_sizes        = [2,  5,  5,  5,  5,  6,  7,  8,  10,  12,  15,  20,  30]

greedy_results = {
    'Negative Greedy':   [],
    'Mixed Greedy':      [],
    'Positive Ordered':  [],
    'BFS Greedy':        [],
    'DSATUR Negative':   [],
    'DSATUR Positive':   []
}

for n, m in zip(instance_sizes, m_sizes):
    """ create a new file if it doesnt does exit """
    filename= "instance.npy"
    graph_density = 0.1 # 0.4 for realistic
    if not os.path.exists(filename):
        P = generate_guest(n, graph_density, "easy")
        # P = generate_guest(n, graph_density, "realistic")
        np.save(filename, P)
    P = np.load(f'instance_{n}_easy.npy')
    #P = np.load(f'instance_{n}_realistic.npy')

    neg_assignment  = negative_greedy(build_graph_negative(P, n), n, m)
    mix_assignment  = mixed_greedy(n, m, P)
    pos_assignment  = ordered_positive_greedy(n, m, P)
    bfs_assignment  = BFS_greedy(build_graph_positive(P, n), n, m)
    dsat_assignment = DSATUR(build_graph_negative(P, n), n, m)
    dsat_pos_assignment = DSATUR_positive_greedy(build_graph_positive(P, n), n, m, P)

    greedy_results['Negative Greedy'].append(satisfaction_score(neg_assignment, P, n))
    greedy_results['Mixed Greedy'].append(satisfaction_score(mix_assignment, P, n))
    greedy_results['Positive Ordered'].append(satisfaction_score(pos_assignment, P, n))
    greedy_results['BFS Greedy'].append(satisfaction_score(bfs_assignment, P, n))
    greedy_results['DSATUR Negative'].append(satisfaction_score(dsat_assignment, P, n))
    greedy_results['DSATUR Positive'].append(satisfaction_score(dsat_pos_assignment, P, n))

for method, scores in greedy_results.items():
    plt.plot(instance_sizes, scores, marker='o', label=method)

plt.xlabel('Number of guests')
plt.ylabel('Initial satisfaction score')
plt.title('Greedy algorithm comparison across instance sizes for easy')
plt.legend()
plt.grid(True)
plt.show()