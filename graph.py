import numpy as np
from typing import List

class Graph:
    def __init__(self, adj_matrix : np.array = np.empty([0, 0])) -> None:
        self.adj_matrix : np.array = adj_matrix
        self.size : int = self.adj_matrix.size

    # Adds a new vertex to the graph. Connections is a list of vertex indices
    # that it is connected to. For example, if the vertex we are adding is connected to
    # vertices 2, 3, and 5, the list should be [2, 3, 5], not [0, 0, 1, 1, 0, 1].
    # TODO: Should it be done this way? Option for either? 
    def add_vertex(self, connections : List[int] = [], connected_to_self : bool = False) -> None:
        # Shortcut if we are adding the first value
        # TODO: Dont know if this is the best way to go about doing this.
        if self.size == 0:
            self.adj_matrix = np.array([[connected_to_self]], dtype = np.int64)
            self.size += 1
            return

        # Generate edge connections
        adj_vals = np.zeros((self.size, 1), dtype = np.int64)
        for c in connections:
            if c > self.size:
                print(f"ERROR: could not add connection to vertex {c}: Out of bounds.")
            else: adj_vals[c][0] = 1
        
        # Add column to adj matrix
        self.adj_matrix = np.append(self.adj_matrix, adj_vals, 1)

        # Append connected to self value, then transpose
        adj_vals = np.append(adj_vals, [connected_to_self])
        adj_vals = np.transpose(adj_vals)

        # Add row to adj matrix
        self.adj_matrix = np.vstack((self.adj_matrix, adj_vals.flatten()))

        self.size += 1
    
    # Removes a vertex from the graph. CAREFUL: if you are keeping track of certain vertex
    # indexes, this will reduce all indexes that are greater than the one provided by one.
    def remove_vertex(self, vertex_index : int) -> None:
        if vertex_index >= self.size:
            print(f"ERROR: could not remove vertex {vertex_index}: Out of bounds.")
            return
        self.adj_matrix = np.delete(self.adj_matrix, vertex_index, 0)
        self.adj_matrix = np.delete(self.adj_matrix, vertex_index, 1)
        self.size -= 1

    # Returns list of 1s and 0s. A 1 represents a connection or edge between the
    # vertex given and the index of the 1, and a 0 represents no connection.
    def get_connections(self, vertex_index : int) -> np.array:
        return self.adj_matrix[vertex_index]
        

g = Graph()
g.add_vertex()
g.add_vertex()
g.add_vertex([0, 1])
g.add_vertex([2])
g.add_vertex([3], True)

print(g.adj_matrix)

# a = np.array([
#     [1, 2, 3],
#     [4, 5, 6],
#     [7, 8, 9]
# ])

# b = np.transpose(np.array([[9, 9, 9]]))
# print(b)
# print(np.append(a, b, 1))