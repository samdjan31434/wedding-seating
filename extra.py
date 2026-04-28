import numpy as np


rng = np.random.default_rng()




def satisfaction_score(assignment, P, n):
   """Calculates the total satisfaction score for all table """
   total_score = 0
   for i in range(n):
     for j in range(i+1, n):
         if assignment[i] == assignment[j]:
             total_score += P[i][j]
   return total_score  


def satifaction_per_table(table_guest, P):
    """Calculate the satisfaction score for each individual table"""
    current_scores = {}
    for table,guest  in table_guest.items():
        total = 0
        for i in range(len(guest)):
            for j in range(i+1, len(guest)):
                guest1 = guest[i]
                guest2 = guest[j]
                total += P[guest1][guest2]
        current_scores[table] = total

    return current_scores            


def local_search(assignment, n, m, P):
    """does local search by swapping guests between two lowest scoring tables"""

    if m == 1:
        return assignment
    else:
        improved = True
        while improved:
            improved = False

            # Groups guest by the table they are assigned to
            table_guests = {table: [] for table in range(1, m + 1)}
            for g in range(n):
                table_guests[assignment[g]].append(g)
            
            # Find the two table with lowest satisfaciton score
            current_scores = satifaction_per_table(table_guests, P)
            sorted_table_scoring = sorted(current_scores, key=current_scores.get)
            worst_table1, worst_table2 = sorted_table_scoring[:2]

            before_score = satisfaction_score(assignment, P, n)

            # Try to swap guest between these two table 
            for guest1 in table_guests[worst_table1]:
                for guest2 in table_guests[worst_table2]:
                    # Swaps 2 guests
                    assignment[guest1], assignment[guest2] = assignment[guest2], assignment[guest1]
                    after_score = satisfaction_score(assignment, P, n)

                    if after_score > before_score:
                        improved = True
                        break
                    else:
                        # Reverse the swap
                        assignment[guest1], assignment[guest2] = assignment[guest2], assignment[guest1]
                if improved:
                    break

        return assignment             
    

def bellows_peterson_instance():
    """Reproduce bellows and peterson preference matrix"""    
    
    n = 17
    P = np.zeros((n,n), dtype=int)

    couples = [(1,2), (3,4), (5,6), (7,8), (10,11)]
    for i, j in couples:
        P[i][j] = 50
        P[j][i] = 50
    
    P[3][9] = 10
    P[9][3] = 10 

    for i in range(9):
        for j in range(i + 1, 9):
            if P[i][j] == 0:
                P[i][j] = 1
                P[j][i] = 1

    for i in range(9, 17):
        for j in range(i + 1, 17):
            if P[i][j] == 0:
                P[i][j] = 1
                P[j][i] = 1

    return n, P




n, P = bellows_peterson_instance()

# make a file for GAMS
with open('bellows_instance.inc', 'w') as f:
    for i in range(n):
        for j in range(n):
            if P[i][j] != 0:
                f.write(f"P('g{i+1}','g{j+1}') = {P[i][j]} ;\n")


P = np.array([
        [0, 7, -6, 0],
        [7, 0,  0, 3],
        [-6, 0,  0, 10],
        [0,  3,  10, 0]
])
n= 4
m=2



