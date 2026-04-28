def graph_density(P, n):
    """Calculate the density of the preference graph."""

    total_pairs = (n * (n-1)) // 2
    non_zero_pairs = 0
    
    for i in range(n):
        for j in range(i+1, n):
            if P[i][j] != 0:
                non_zero_pairs += 1
    
    density = non_zero_pairs / total_pairs
    
    print(f"Total possible amount of pairs: {total_pairs}")
    print(f"Non zero pairs: {non_zero_pairs}")
    print(f"Graph density: {density:.4f}")

    return density


class ConnectionGraph:
  """Represents a weighted undirected graph of guest relationship."""

  def __init__(self):
    self.vertices = {}    # adjancency list
    self.edges = {}       # stores weight


  def add_vertex(self, vertex):
    self.vertices[vertex] = []     


  def add_edge(self, source, target):
    # add edges bewteen guest with preferences
    self.vertices[source].append(target)  


  def add_weight(self , source, target , weight):
     """Stores the preference score as weight
       for the edges in both direction."""
     self.edges[(source,target)] = weight 
     self.edges[(target, source)] = weight      


  def get_adjacent_count(self, vertex):
    """Return the degree of a specific guest."""
    return len(self.vertices[vertex])          


def build_graph(P, n, condition):
    """Builds a Connection graph based on specific weight conditions."""

    graph  = ConnectionGraph()
    for i in range(n):
        graph.add_vertex(i)

    # Intilialises edges with weight between guest with preference
    for i in range(n):
        for j in range(i + 1, n):
            weight = P[i][j]
            if condition(weight):
                graph.add_edge(i, j)
                graph.add_edge(j, i)
                graph.add_weight(i, j, P[i][j])
    
    return graph


def build_graph_negative(P, n):
    """Creates a graph with negative weights weighted edges."""
    return build_graph(P, n, lambda w: w < 0)


def build_graph_positive(P, n):
    """"Creates a graph with positive weighted edges."""
    return build_graph(P, n, lambda w: w > 0)


def initialize(m):
    """Creates a dictionary to store the number of guest at each table"""
    return {t: 0 for t in range(1, m + 1)}


def negative_greedy(n, m, P):
    """Assigns guest to tables using a greedy
      approach of trying to avoid conflicts.
    """

    graph = build_graph_negative(P, n)
    # dictionary key(guest ): value(table guest is assigned)
    assignment = {}
    # finds the table capacity
    capacity = n // m
    table_count = initialize(m)

    for guest in range(n):
        # find tables used by conflicting neighbours
        used_tables = set()
        for neighbour in graph.vertices[guest]:
            if neighbour in assignment:
                used_tables.add(assignment[neighbour])
        
        table = 1
        while table <= m:
            # Check if table has no conflicting guest and has space
            if table not in used_tables and table_count[table] < capacity:
                break
            table += 1
            # If there is no conflit free table, pick the least full table
            if table > m:
                table = min(table_count, key=table_count.get)
                break

        # Assigns a guest to a table
        assignment[guest] = table
        table_count[table] += 1

    return assignment


def mixed_greedy(n, m, P):
    """Assigns guest greedily by maximisng the total satisafaction 
        score with guest already sat their
    """
    assignment = {}
    capacity = n // m
    table_count = initialize(m)    
   
    for guest in range(n):
        best_score = -10000000
        best_table = 1 

        for table in range(1, m + 1):
            if table_count[table] < capacity:
                score = 0
                # Add weight of preference between current guest and guest already sat at this table
                for neighbours, table_assigned in assignment.items():
                    if table == table_assigned:
                        score += P[guest][neighbours]

                if score > best_score:
                    best_score = score
                    best_table = table
            
        assignment[guest] = best_table
        table_count[best_table] += 1

    return assignment    


def ordered_positive_greedy(n, m, P):
    """Sorts guests by their total preference
      contribution then applies greedy assignment
    """    
    assignment = {}
    capacity = n // m
    table_count = initialize(m)

    # Calculates the total positive connection score for each guest
    sums = {}
    for i in range(n):
        total = 0 
        for j in range(n):
            if P[i][j] > 0:
                total += P[i][j]
        sums[i] = total

    # Sorts guests with the most positive connections
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

     
def DSATUR(n, m, P):
    """Implement DSATUR heuristic using negative weighted graph."""

    graph = build_graph_negative(P, n)
    assignment = {}
    capacity = n // m
    table_count = initialize(m)

    # Initialises saturation degree: number of different table assigned to neighbouring guest
    saturation = {guest: 0 for guest in range(n)}

    # break ties by storing the number of conflict for each guest
    conflict_count  = {}
    for guest in range(n):
        conflict_count[guest] = graph.get_adjacent_count(guest)

    unnassigned  = set(range(n))

    while unnassigned:
        # find the guest with the highest saturation and break ties by looking at conflict count
        best_guest = None
        largest_satur , highest_conflict = -1

        for guest in unnassigned:
            if (saturation[guest]> largest_satur) or (
                saturation[guest] == largest_satur and conflict_count[guest] > highest_conflict):
                best_guest = guest
                highest_conflict = conflict_count[guest]
                largest_satur = saturation[guest]

        # finds lowest table number which has no conflicting guest and is not full
        used_tables = set()
        for neighbour in graph.vertices[best_guest]:
            if neighbour in assignment:
                used_tables.add(assignment[neighbour])

        # Find first avaialbe table without conflict
        found = False
        table = 1
        while table <= m:
            if table not in used_tables and table_count[table] < capacity:
                found = True
                break
            table += 1

        if not found:
                table = min(table_count, key = table_count.get)

        # Assigns guest to table        
        assignment[best_guest] = table
        table_count[table] += 1
        unnassigned.remove(best_guest)

        # Update saturation of neighberouing guests who arent seated
        for neighbour in graph.vertices[best_guest]:
            if neighbour in unnassigned:
                neighbour_tables = set()
                for neigh_table in graph.vertices[neighbour]:
                    if neigh_table in assignment:
                        neighbour_tables.add(assignment[neigh_table])
                saturation[neighbour] = len(neighbour_tables)

    return assignment 


def DSATUR_positive_greedy(n, m, P):
    """Modified DSATUR approach that priortises seating guest
        based on positive weight and try to maximise satisfaction score
    """
    graph = build_graph_positive(P, n)
    assignment = {}
    capacity = n // m
    table_count = initialize(m)

    saturation = {guest: 0 for guest in range(n)}

    # Used to break ties by storing the number of positive connection for each guest
    compatible_count = {}
    for guest in range(n):
        compatible_count[guest] = graph.get_adjacent_count(guest)

    unassigned = set(range(n))

    while unassigned:
        # Finds guest with the highest saturation neighbours
        best_guest = None
        largest_satur = -1
        highest_conflict = -1

        for guest in unassigned:
            if (saturation[guest] > largest_satur) or (
                saturation[guest] == largest_satur and 
                compatible_count[guest] > highest_conflict):
                best_guest = guest
                highest_conflict = compatible_count[guest]
                largest_satur = saturation[guest]

        # Finds the table that maximise preferenece score with already seated positive neighbours
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

        # Assign guest to best scoring table
        assignment[best_guest] = best_table
        table_count[best_table] += 1
        unassigned.remove(best_guest)
        
        # Update saturation of unassigned positive neighbours
        for neighbour in graph.vertices[best_guest]:
            if neighbour in unassigned:
                neighbour_tables = set()
                for nn in graph.vertices[neighbour]:
                    if nn in assignment:
                        neighbour_tables.add(assignment[nn])
                saturation[neighbour] = len(neighbour_tables)

    return assignment
