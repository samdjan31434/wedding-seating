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
            Preference[i][j] = np.random.randint(-10, 10)
            Preference[j][i] = np.random.randint(-10, 10)
    
    return Preference

n=100
m=20
P = generate_guest(n,m)
print(np.count_nonzero(P == 0))
    

with open('Generated_instance.inc', 'w') as f:
    for i in range(n):
        for j in range(n):
            if P[i][j] != 0:
                f.write(f"P('g{i+1}','g{j+1}') = {P[i][j]} ;\n")



class Conflict_Graph:
  def __init__(self):
    self.vertices = {}
    self.edges = {}

  def add_vertex(self, vertex):
    self.vertices[vertex] = []

  def add_edge(self, source, target):
    self.vertices[source].append(target)

  def add_weight(self , source, target , weight):
     self.edges[(source,target)] = weight

  def get_adjacent_count(self, vertex):
    return len(self.vertices[vertex])
  
  def get_weight_sum(self, vertex):
     total = 0