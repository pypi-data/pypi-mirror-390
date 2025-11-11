import scipy.sparse as sp 
import numpy as np 

def remap(arr : np.array):
    rename = np.unique(arr)
    mapping = dict(zip(rename, list(range(1,len(rename)+1))))
    arr_remap = np.vectorize(mapping.get)(arr)
    return arr_remap

class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n
    
    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]  # compression de chemin
            x = self.parent[x]
        return x
    
    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        if self.rank[rx] < self.rank[ry]:
            self.parent[rx] = ry
        elif self.rank[ry] < self.rank[rx]:
            self.parent[ry] = rx
        else:
            self.parent[ry] = rx
            self.rank[rx] += 1
        return True

    def composantes(self):
        return [self.find(i) for i in range(len(self.parent))]

class Graph:
    def __init__(self):
        self.adj = dict() 

    def add_node(self, node):
        if node not in self.adj:
            self.adj[node] = set()

    def add_edge(self, u, v):
        if u not in self.adj:
            raise ValueError(f"Node {u} is not in the graph")
        if v not in self.adj:
            raise ValueError(f"Node {v} is not in the graph")
        self.adj[u].add(v)
        self.adj[v].add(u)

    def rename(self, u, new_name):
        if u==new_name:
            return 

        if new_name in self.adj:
            raise ValueError(f"Node {new_name} already in the graph")
        self.adj[new_name] = self.adj[u] 
        for n in self.adj[new_name]:
            self.adj[n].discard(u)
            self.adj[n].add(new_name)
        del self.adj[u]
        

    def merge_nodes(self, u, v, new_name):
        if u not in self.adj and v not in self.adj:
            # pas de connexion à faire, les noeuds n'existent pas et représentent
            # donc l'ensemble vide
            return
        if u not in self.adj:
            self.rename(v, new_name)
            return 
        if v not in self.adj:
            self.rename(u, new_name)
            return
        if u==v:
            self.rename(u,new_name)
            return

        neighbors = set.difference(self.adj[u].union(self.adj[v]),{u,v})

        del self.adj[u]
        del self.adj[v] 

        if new_name in self.adj:
            raise ValueError(f"Node {new_name} already in the graph")
        self.adj[new_name] = neighbors

        for n in neighbors: 
            self.adj[n].discard(u)
            self.adj[n].discard(v)
            self.adj[n].add(new_name)



def partition(G : sp.csr_matrix, cannot_link : np.ndarray):
    assert G.shape is not None 
    assert G.shape[0] == G.shape[1]
    assert cannot_link.shape[1] == 2
    m = G.shape[0]
    united = UnionFind(m)

    # Graph des cannot_link dans une structure 
    # de donnée permettant les merge des sommets
    forbidden = Graph()
    cannot_link_edges = [(i,j) for (i,j) in zip(cannot_link[:,0],cannot_link[:,1]) if i<j]
    nodes = np.unique(cannot_link)
    for node in nodes:
        forbidden.add_node(node)
    for edge in cannot_link_edges:
        forbidden.add_edge(edge[0],edge[1])

    # Trouver une partition en composante connexe de G 
    # qui ne sont pas connectés
    I, J, _ = sp.find(G)
    for (i,j) in zip(I,J): 
        if i < j: #No need to do anything if i>j
            composante0 = united.find(i)
            composante1 = united.find(j)
            if not composante0 in forbidden.adj or \
                    not composante1 in forbidden.adj[composante0]:
                united.union(composante0,composante1)
                forbidden.merge_nodes(composante0,composante1,new_name=united.find(composante0))
    partitioning = [united.find(i) for i in range(m)]
    return remap(partitioning)
