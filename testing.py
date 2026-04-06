from collections import Counter
import numpy as np

"""Check that each guest is asssigned to only one table and table capacity is not exceeded"""
def testing_feasibility(assignment, n, m):
    capacity = n // m
    

    # Check if all guest are assigned
    assert len(assignment) == n, "not all guest are assigned tables"

    # Check guest are assigned to a valid table number
    for guest in range(n):
        table = assignment[guest]
        assert table < 1 or table > m, " guest are assigned to invalid table number"
           
    
    table_counts = Counter(assignment.values())

    for table,count in table_counts.items():
        assert count > capacity , "table capacity exceeded"

    print("produces feasible solution")
           

"""Check if preferene matrix is symmetric """
def test_symmetry(P):
    assert np.array_equal(P, P.T), " not symmetric"
    print("Preference matrix is symmetric")

#test_symmetry(P)    

        
"""check if the SA score is greater than or equal to the greedy score"""
def test_sa_score(greedy_score, sa_score, greedy_name):
    assert sa_score >= greedy_score, f"Simulated annealing produce worst solution for {greedy_name}"
    print("SA score passed for {greedy_name}")        


"""check if the local score is greater than or equal to the SA score"""
def test_local_search(sa_score, ls_score, greedy_name):
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

#test_satisfaction_score()