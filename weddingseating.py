import numpy as np

def generate_guest(n,m):
    np.random.seed(20)
    Preference = np.zeros((n,n),dtype =int)


    # assume about 25 % are couple that must sit together
    for i in range(0, n//4, 2):
        Preference[i][i+1] = 10
        Preference[i+1][i] = 10
    
    for guest in range(n):
        i = np.random.randint(0,n)
        j = np.random.randint(0,n)
        if i!=j and Preference[i][j] ==0:
            random_score = np.random.randint(-10,10)
            Preference[i][j] = random_score
            Preference[j][i] = random_score
    
    return Preference

n=20
m= 4
P = generate_guest(n,m)
print(np.count_nonzero(P == 0))
    

with open('Generated_instance.inc', 'w') as f:
    for i in range(n):
        for j in range(n):
            if P[i][j] != 0:
                f.write(f"P('g{i+1}','g{j+1}') = {P[i][j]} ;\n")



class Conflict_Graph:
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
    return len(self.vertices[vertex])           # count number of guest they are in conflict with
  
  def get_weight_sum(self, vertex):
     total = 0
     for neighbour in self.vertices[vertex]:
        total += self.edges[(vertex, neighbour)]

     return total
  
     


       

graph  = Conflict_Graph()

for i in range(n):
   graph.add_vertex(i)


for i in range(n):
   for j in range(i+1,n):
      if P[i][j]<0:
         graph.add_edge(i,j)
         graph.add_edge(j, i)
         graph.add_weight(i,j,P[i][j])

conflict_guest = {}

for i in range(n):
    if graph.get_adjacent_count(i) > 0:
       conflict_guest[i] = graph.get_weight_sum(i)


        


table1 = [0] * 5
table1 = [0] * 5
table1 = [0] * 5

min_guest = min(conflict_guest, key=conflict_guest.get)
print(min_guest)
