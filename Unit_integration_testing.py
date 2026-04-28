import pytest
import numpy as np
from collections import Counter
from Hueristic_algorithms import negative_greedy, mixed_greedy, ordered_positive_greedy, DSATUR, DSATUR_positive_greedy, build_graph_negative, build_graph_positive, initialize
from extra import satisfaction_score, local_search
from Guest_Creations import generate_guest
from Simulated_annealing import simulated_annealing

@pytest.fixture
def sparse_instance():
    """4 guest 2 table manual instance"""
    P = np.array([
        [0,  7, -6,  0],
        [7,  0,  0,  3],
        [-6, 0,  0, 10],
        [0,  3, 10,  0]
    ])
    assignment = {0: 1, 1: 1, 2: 2, 3: 2}
    return P, assignment

@pytest.fixture
def realistic_instance():
    """20 guest and 5 tables"""
    n = 20
    m = 5
    # Use 0.1 if you want to test on a sparse non manual instance 
    P = generate_guest(n, 0.4, 'realistic')
    return P, n, m

def test_satisfaction_score_(sparse_instance):
    """Check satisfaction score returns correct value on sparse manual instance"""
    P, assignment = sparse_instance
    score = satisfaction_score(assignment, P, 4)
    assert score == 17

def test_satisfaction_score_zero_matrix():
    """Check satisfaction score returns 0 for all zero preference matrix"""
    P = np.zeros((5, 5), dtype=int)
    assignment = {0: 1, 1: 1, 2: 2, 3: 2,4:2 }
    score = satisfaction_score(assignment, P, 5)
    assert score == 0


def test_satisfaction_score_different_tables():
    """Check satisfaction score is zero if all guest sit at their own
    table"""
    P = np.array([
        [0, 10,  0,  0],
        [10, 0,  0,  0],
        [0,  0,  0, 10],
        [0,  0, 10,  0]
    ])
    assignment = {0: 1, 1: 2, 2: 3, 3: 4}
    score = satisfaction_score(assignment, P, 4)
    assert score == 0

def test_symmetry(realistic_instance):
    """Check preference matrix is symmetric"""
    P, n, m = realistic_instance
    assert np.array_equal(P, P.T)

def test_diagonal_zero(realistic_instance):
    """Check diagonal entries are all zero"""
    P, n, m = realistic_instance
    for i in range(n):
        assert P[i][i] == 0

def check_feasibility(assignment, n, m, name):
    """Check feasibility for any assignment"""
    capacity = n // m
    assert len(assignment) == n, f"{name} not all guests assigned"
    for guest in range(n):
        table = assignment[guest]
        assert 1 <= table <= m, f"{name} guest {guest} assigned to invalid table {table}"
    table_counts = Counter(assignment.values())
    for table, count in table_counts.items():
        assert count <= capacity, f"{name} table {table} exceeds capacity"

def test_negative_greedy_feasibility(realistic_instance):
    P, n, m  = realistic_instance
    assignment = negative_greedy(n, m, P)
    check_feasibility(assignment, n, m, 'Negative Greedy')

def test_mixed_greedy_feasibility(realistic_instance):
    P, n, m = realistic_instance
    assignment = mixed_greedy(n, m, P)
    check_feasibility(assignment, n, m, 'Mixed Greedy')

def test_positive_ordered_feasibility(realistic_instance):
    P, n, m  = realistic_instance
    assignment = ordered_positive_greedy(n, m, P)
    check_feasibility(assignment, n, m, 'Positive Ordered')


def test_dsatur_feasibility(realistic_instance):
    P, n, m = realistic_instance
    assignment = DSATUR(n, m, P)
    check_feasibility(assignment, n, m, 'DSATUR Negative')

def test_dsatur_positive_feasibility(realistic_instance):
    P, n, m = realistic_instance
    assignment = DSATUR_positive_greedy(n, m, P)
    check_feasibility(assignment, n, m, 'DSATUR Positive')


def test_negative_graph(realistic_instance):
    """Check negative graph has only negative edges"""
    P, n, m = realistic_instance
    graph = build_graph_negative(P, n)
    for (i, j), weight in graph.edges.items():
        assert weight < 0

def test_positive_graph(realistic_instance):
    """Check positive graph has only positive edges"""
    P, n, m = realistic_instance
    graph = build_graph_positive(P, n)
    for (i, j), weight in graph.edges.items():
        assert weight > 0

# Integration testing

def test_sa_doesnt_worsen_greedy(realistic_instance):
    """Check SA score is greater than or equal to greedy score"""
    P, n, m  = realistic_instance
    assignment = negative_greedy(n, m, P)
    greedy_score = satisfaction_score(assignment, P, n)
    sa_state   = simulated_annealing(assignment, n, m, P, 3, 0.9)
    sa_score     = satisfaction_score(sa_state, P, n)
    assert sa_score >= greedy_score

def test_ls_doesnt_worsen_sa(realistic_instance):
    """Check local search score is greater than or equal to SA score"""
    P, n, m    = realistic_instance
    assignment = negative_greedy(n, m, P)
    sa_state   = simulated_annealing(assignment, n, m, P, 3, 0.9)
    sa_score   = satisfaction_score(sa_state, P, n)
    ls_state   = local_search(sa_state, n, m, P)
    ls_score   = satisfaction_score(ls_state, P, n)
    assert ls_score >= sa_score


