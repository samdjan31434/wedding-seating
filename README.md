Summary

Comparing_HA.py  - Code evaluates and compares different greedy heuristics and their improvement after using Simulated Annealing to optimise guest seating at a wedding by trying to maximise the satisfaction score of guests sat at the tables.
Run multiple experiment across different instances sizes and stores satisfaction score in csv and visualise the performance using line graph and heatmap to look at how the ranking changes.

extra.py - gives a helper function for evaluation and improving guest seating assignment. contain a function to compute guest satisfaction scores, a local search heuristic, and generate a benchmark preference matrix from Bellows and Petersons. Also, save the matrix to be used in GAMS. A small example preference matrix is used for testing.

Guest_generation.py - this file creates a guest preference matrix using for the problem and try to simulate a real social structure by assigning ages, making couples, grouping children and parent together, and conflict with guest. It also allows for different difficulty levels, sparse and realistic, also control the graph density parameter by using a random positive relationship. For realistic difficulty preference, remaining neutral guests are weighted based on the absolute age difference.

Heuristic_Algorithm.py - This file contains all the greedy initialisation algorithm. uses also A connection class for some of the algorithms 
method include basic greedy, ordering based heuristic, and DSATUR inspired graph colouring algorithm. also provide utilities for building graphs, measuring graph density, and handling table assignment.

ILP_vs_heuristic.py - This file is executed to perform a complete experiment to find an overall solution for both difficulty levels and each method is evaluated over multiple random seeds, the average is taken, and the results are saved to a CSV file and are compared against the implemented ILP in GAMS scores.

Simulated_Annealing.py - this file contains the implementation of a Simulated Annealing algorithm for guest seating. It also runs experiments to evaluate how performance varies and cooling rates(gamma), and compares SA versus SA combined with local search, and CSV files are saved and visualised using plots.



The gamma_testing folder contains saved instances and experiment results in CSV and as a plot for chapter 4.1.2

greedy_comparision folder - contains all saved instances as .npy files for all tests, and result saved in a CSV with a graph for chapter 4.1.4

heatmap folder - contains the two heatmaps for chapter 4.1.4, Effect of Starting solution on SA, and the other parts of the images are in the appendix

instances_result_ILP_vs_Heuristic folder - contains all the saved preference matrix instances when doing ILP vs Heuristic pipeline comparison from chapter 4.1.3

larger_timelimit_experiment - Contains the CSV and PNG for chapter 4.1.5


