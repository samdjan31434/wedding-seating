import numpy as np
import random

rng = np.random.default_rng()

def age_score(age_diff):
    """Calculates a preferene core based on age different between two guests"""

    if age_diff <= 5:
        return 10
    elif age_diff <= 10:
        return 5
    elif age_diff <= 20:
        return 2
    elif age_diff <= 30:
        return 0
    elif age_diff <= 40:
        return -5
    else:
        return -10


def assign_random_positive_preferences(preference, n, graph_density):
    """Add prefernce score to empty cell in preference matrix with random 
    positive values"""
    max_pairs = (n * (n-1)) // 2
    
    # Calculate the number of relationship that already exists
    existing_pairs = 0
    for i in range(n):
        for j in range(i+1, n):
            if preference[i][j] != 0:
                existing_pairs += 1
    
    # Calculate the number of more positive connection needed to reach density value
    random_positive_pairs = int(max_pairs * graph_density) - existing_pairs
    count = 0

    for i in range(n):
        for j in range(i+1, n):
            if preference[i][j] == 0:
                if count < random_positive_pairs:
                    score = np.random.randint(1, 9)
                    preference[i][j] = score
                    preference[j][i] = score
                    count += 1

    return preference


def create_couple_pairs(num_couples, adults, preference):
    """Pairs adults together as couples and assign them max preference score"""
    couple_pairs = []
    for i in range(0, num_couples * 2, 2):
        if (i + 1) >= len(adults):
            break
        g1 = adults[i]
        g2 = adults[i+1]
        preference[g1][g2] = 10
        preference[g2][g1] = 10
        couple_pairs.append((g1, g2))

    return couple_pairs, preference


# Generates guest matrix
def generate_guest(n, graph_density, difficulty):
    """Creates a full guest list based on constraints"""
    # Initialislisses an  n x n matrix
    preference = np.zeros((n,n), dtype =int)

    # Generate ages using a normal distribution mean=35 , std = 10
    ages = {
    i: int(min(100, max(0, rng.normal(34, 10))))
    for i in range(n)}

    young_children  = []    # Age 0 to 7 sit with parents
    teen = []   # Age 8 to 17 sit at their own table
    adults = []  # Age 18+ Singles and couples

    for i in range(n):
        if ages[i] <= 7:
            young_children.append(i)
        elif ages[i] <= 17:
            teen.append(i)
        else:
            adults.append(i)
   
    if difficulty == "sparse":
        # Create a sparse matrix, assume no children and dont care for ages
        num_couples = int(len(adults) * 0.2) // 2
        conflict_rate  =  0.01
         # Assigns conflict
        num_conflicts = int(n * conflict_rate)
        conflicts_assigned = 0
        while conflicts_assigned < num_conflicts:
            i = rng.integers(0, n)
            j = rng.integers(0, n)
            if i != j and preference[i][j] == 0:
                score = rng.integers(-10, -1)
                preference[i][j] = score
                preference[j][i] = score
                conflicts_assigned += 1

        preference = assign_random_positive_preferences(preference, n, graph_density)

        return preference

    if difficulty == "realistic":
        # children sit with parent wedding 
        num_couples = int(len(adults) * 0.55) // 2
        conflict_rate = 0.05
         
        couple_pairs , preference = create_couple_pairs(num_couples, adults, preference)   

        child_index = 0
        half_couples = len(couple_pairs) // 2
        for parent1, parent2 in couple_pairs[:half_couples]:
            if child_index >= len(young_children):
                break
            child = young_children[child_index]
            preference[child][parent1] = 10
            preference[parent1][child] = 10
            preference[child][parent2] = 10
            preference[parent2][child] = 10
            child_index += 1

    # try to make teenager sit at own table and not sit with adults
    for teenager in teen:
        for adult in adults:
            if preference[teenager][adult] == 0:
                preference[teenager][adult] = -5
                preference[adult][teenager] = -5

    couple_guests = set()
    for g1, g2 in couple_pairs:
        couple_guests.add(g1)
        couple_guests.add(g2)

    single_adults = []
    for a in adults:
        if a not in couple_guests:   
            single_adults.append(a)

    for g1, g2 in couple_pairs:
        for single in single_adults:
            if preference[g1][single] == 0:
                preference[g1][single] = -3
                preference[single][g1] = -3
            if preference[g2][single] == 0:
                preference[g2][single] = -3
                preference[single][g2] = -3

    # Assigns conflict
    num_conflicts = int(n * conflict_rate)
    conflicts_assigned = 0
    while conflicts_assigned < num_conflicts:
        i = rng.integers(0, n)
        j = rng.integers(0, n)
        if i != j and preference[i][j] == 0:
            score = rng.integers(-10, -1)
            preference[i][j] = score
            preference[j][i] = score
            conflicts_assigned += 1

    preference = assign_random_positive_preferences(preference, n, graph_density)

    # Age scoring for remaining neutral pairs for j > i
    for i in range(n):
        for j in range(i + 1, n):
            if preference[i][j] == 0:
                age_diff = abs(ages[i] - ages[j])
                score = age_score(age_diff)
                preference[i][j] = score
                preference[j][i] = score

    return preference
