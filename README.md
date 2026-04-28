# wedding seating
Summary

Comparing_HA.py  - Code evaluates and compares different greedy heuristic and their improvement after using Simulated Annealing to optimise guest seating at wedding by trying to maximise satisfaction score of guests sat at the tables
Run multiple experiment across different instances sizes and stores satisfaction score in csv and visualise performance using line graph and heatmap to look of how ranking changes.

extra.py - gives helper function for evaluation and improving guest seating assignment. contain function to computes guest satisfaction scores, local search heuristic, and generate a benchmark preference matrix from bellows and Petersons. Also save matrix to be used in GAMS. A small example preference matrix is used for testing

Guest_generation - this file creates guest preference matrix using for the problem and try to simulate real social structure by assigning ages, making couples, grouping children and parent together, and conflict with guest. It also allows for different difficulty levels sparse and realistic also control the graph density parameter by using a random positive relationship. For realistic difficulty preference for remaining neutral guest are weighted based on absolute age difference

Heuristic Algorithm - This file contains all the greedy initialisation algorithm. uses also A connection class for some of the algorithms 
method include basic greedy, ordering based heuristic and DSATUR inspired graph colouring algorithm. also provide utilities for building graphs, measuring graph density and handle table assignment.

ILP vs Heuristic - This file is executed to perform a complete experiment to find overall solution for both difficulty levels and each method is evaluated over multiple randoms seeds and average is takes and result are saved to a csv file and are compares against the implemented ILP in GAMS scores

Simulated_Annealing - this file contains implementation of a Simulated Annealing algorithm for guest seating. it also runs experiment to evaluate how performance varies and cooling rates(gamma), and comparing SA versus SA combined with local search, and csv files are saved and visualised using plots



gamma_testing folder contains saved instances and experiment result in csv and as a plot for chapter 4.1.2

greedy_comparision folder - contains all saved instances as .npy files for all test, and result saved in csv with also a graph for chapter 4.1.4

heatmap folder - contains the two heatmap for chapter 4.1.4, Effect of Starting solution on SA and other part of the images are in the appendix

instances_result_ILP_vs_Heuristic folder - contain all the saved preference matrix instances when doing ILP vs Heuristic pipeline comparison from chapter 4.1.3

larger_timelimit_experiment - Contains the csv and png for chapter 4.1.5


