def graph_density(P, n):
    total_pairs = (n * (n-1)) // 2
    non_zero_pairs = 0
    
    for i in range(n):
        for j in range(i+1, n):
            if P[i][j] != 0:
                non_zero_pairs += 1
    
    density = non_zero_pairs / total_pairs
    
    print(f"Total possible amount of pairs:  {total_pairs}")
    print(f"Non zero pairs:        {non_zero_pairs}")
    print(f"Graph density:         {density:.4f}")

    return density


class Compatible_Graph:
  def __init__(self):
    self.vertices = {}    # store each guest and the list of conflciting vertices
    self.edges = {}       # stores weight for conflict between edges

  def add_vertex(self, vertex):
    self.vertices[vertex] = []     # add guest to an empty list since no conflict yet

  def add_edge(self, source, target):
    self.vertices[source].append(target)   # add edges bewteen guest with conflicts

  def add_weight(self , source, target , weight):
     self.edges[(source,target)] = weight 
     self.edges[(target, source)] = weight      # add the preference score as weight between conflicting guests

  def get_adjacent_count(self, vertex):
    return len(self.vertices[vertex])           # count number of guest they are in conflict wit


def build_graph(P, n, condition):
    graph  = Compatible_Graph()

    # inistialise the graph with n vertices
    for i in range(n):
        graph.add_vertex(i)

    # intilialises edges with weight between guest with preference
    for i in range(n):
        for j in range(i+1, n):
            weight = P[i][j]
            if condition(weight):
                graph.add_edge(i, j)
                graph.add_edge(j, i)
                graph.add_weight(i, j, P[i][j])
    
    return graph


def build_graph_negative(P, n):
    """return a graph with negative weights"""
    return build_graph(P, n, lambda w: w<0)

def build_graph_positive(P, n):
    """"return a graph with positive weight"""
    return build_graph(P, n, lambda w: w>0)


# greedy colouring algorihtm - find the first available table that is feasible for that guest and does not cause table capacity to overflow
def initialize(m):
    # create a dictionary
    # key(table number): value(guest count at each table)
    return {t: 0 for t in range(1,m+1)}


def negative_greedy(graph, n, m):
    # dictionary key(guest ): value(table guest is assigned)
    assignment = {}
    # finds the table capacity
    capacity = n // m

    table_count = initialize(m)

    # greedy colouring graph algorithm used to find an initial solution
    for guest in range(n):
        # find tables used by conflicting neighbours
        used_tables = set()
        for neighbour in graph.vertices[guest]:
            if neighbour in assignment:
                used_tables.add(assignment[neighbour])
        
        # used to find the lowest table number that has no conflicting guest and is not full
        # neutral guest are assinged to the lowest avaialbe table number since used table return an emtpy set
        table = 1
        while table <= m:
            if table not in used_tables and table_count[table] < capacity:
                break
            table += 1
            # this occur when there a seating choice would result in conflict therefore pick table with the least capacity 
            if table > m:
                table = min(table_count, key=table_count.get)
                break

        # assigns a guest to a table
        assignment[guest] = table
        table_count[table] += 1

    return assignment


def mixed_greedy(n,m, P):
    # dictionary key(guest ): value(table guest is assigned)
    assignment = {}
    # finds the table capacity
    capacity = n // m

    table_count = initialize(m)    
   

    for guest in range(n):
        best_score = -10000000
        best_table = 1 

        for table in range(1,m+1):

            if table_count[table] < capacity:
                score  =0
                for neighbours, table_assigned in assignment.items():
                    if table == table_assigned:
                        score += P[guest][neighbours]

                if score > best_score:
                    best_score =score
                    best_table = table
            
        assignment[guest] = best_table
        table_count[best_table] += 1

    return assignment    


def ordered_positive_greedy(n,m,P):
    # dictionary key(guest ): value(table guest is assigned)
    assignment = {}
    # finds the table capacity
    capacity = n // m
   
    table_count = initialize(m)
    
    sums = {}
    for i in range(n):
        total = 0 
        for j in range(n):
            if P[i][j]> 0:
                total += P[i][j]
        sums[i] = total


    guest_order = sorted(sums, key=sums.get,reverse=True)

    for guest in guest_order:
        best_score = -1000000
        best_table = 1

        for table in range(1, m+1):
            if table_count[table] < capacity:
                score = 0
                for neighbour, table_assigned in assignment.items():
                    if table_assigned == table:
                        score += P[guest][neighbour]

                if score > best_score:
                    best_score = score
                    best_table = table

        assignment[guest] = best_table
        table_count[best_table] += 1

    return assignment


def BFS_greedy(graph,n,m):
     # dictionary key(guest ): value(table guest is assigned)
    assignment = {}
    # computes the table capacity
    capacity = n // m

    table_count = initialize(m)

    visited =set()
    current_table = 1
    start_guest  =0 
    most_neighbours = 0
    for i in range(n):
        count = graph.get_adjacent_count(i)
        if most_neighbours > count:
            most_neighbours = count
            start_guest = i

    queue = [start_guest]

    while len(assignment) < n:
        guest = queue.pop(0)
        if guest in visited:
            continue

        visited.add(guest)

        if table_count[current_table]< capacity:
            assignment[guest] = current_table
            table_count[current_table] +=1
        else:
            current_table+=1 
            if current_table>m:
                current_table =m
            assignment[guest] = current_table
            table_count[current_table] += 1

        for neighbour in graph.vertices[guest]:
            if neighbour not in visited:
                queue.append(neighbour)

        for guest in range(n):
            if guest not in visited:
                queue.append(guest)
                break

    return assignment      


def DSATUR(graph,n,m):
    """performs dsatur heuristic on a negative weighted graph"""
    assignment = {}
    capacity = n // m
    
    table_count = initialize(m)


    # saturation degree - number of different table assigned to neighbouring guest
    saturation = {}
    for guest in range(n):
        saturation[guest] = 0

    # break ties by storing the number of conflict for each guest
    conflict_count  = {}
    for guest in range(n):
        conflict_count[guest] = graph.get_adjacent_count(guest)

    unnassigned  = set(range(n))

    while unnassigned:

        # find the guest with the highest saturation and break ties by looking at conflict count
        best_guest = None
        largest_satur = -1
        highest_conflict = -1
        for guest in unnassigned:
            if (saturation[guest]> largest_satur) or (saturation[guest] == largest_satur and conflict_count[guest] > highest_conflict):
                best_guest = guest
                highest_conflict = conflict_count[guest]
                largest_satur = saturation[guest]

        # used to find lowest table number which has not conflicting guest and is not full
        used_tables = set()
        for neighbour in graph.vertices[best_guest]:
            if neighbour in assignment:
                used_tables.add(assignment[neighbour])

        table = 1
        while table <= m:
            if table not in used_tables and table_count[table] < capacity:
                break
            table += 1
            if table > m:
                table = min(table_count,key= table_count.get)
                break

        # assing guest to table        
        assignment[best_guest] = table
        table_count[table] += 1
        unnassigned.remove(best_guest)

        # update saturation of neighberouing guests
        for neighbour in graph.vertices[best_guest]:
            if neighbour in unnassigned:
                neighbour_tables = set()
                for neigh_table in graph.vertices[neighbour]:
                    if neigh_table in assignment:
                        neighbour_tables.add(assignment[neigh_table])
                saturation[neighbour] = len(neighbour_tables)


    return assignment 


def DSATUR_positive_greedy(graph,n,m,P):
    assignment = {}
    capacity = n // m
    
    table_count = initialize(m)


    # saturation degree - number of different table assigned to neighbouring guest
    saturation = {}
    for guest in range(n):
        saturation[guest] = 0

    # break ties by storing the number of conflict for each guest
    conflict_count  = {}
    for guest in range(n):
        conflict_count[guest] = graph.get_adjacent_count(guest)

    unassigned  = set(range(n))

    while unassigned:

        # find the guest with the highest saturation and break ties by looking at conflict count
        best_guest = None
        largest_satur = -1
        highest_conflict = -1
        for guest in unassigned:
            if (saturation[guest]> largest_satur) or (saturation[guest] == largest_satur and conflict_count[guest] > highest_conflict):
                best_guest = guest
                highest_conflict = conflict_count[guest]
                largest_satur = saturation[guest]

        best_score = -1000000
        best_table = 1        

        for table in range(1, m+1):
            if table_count[table] < capacity:
                score = 0
                for neighbour in graph.vertices[best_guest]:
                    if neighbour in assignment:
                        if assignment[neighbour] == table:
                            score += P[best_guest][neighbour]
                if score > best_score:
                    best_score = score
                    best_table = table

        # assign guest to best table
        assignment[best_guest] = best_table
        table_count[best_table] += 1
        unassigned.remove(best_guest)
        
        
        # update saturation of unassigned positive neighbours
        for neighbour in graph.vertices[best_guest]:
            if neighbour in unassigned:
                neighbour_tables = set()
                for nn in graph.vertices[neighbour]:
                    if nn in assignment:
                        neighbour_tables.add(assignment[nn])
                saturation[neighbour] = len(neighbour_tables)

    return assignment