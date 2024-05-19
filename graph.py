import numpy as np
from typing import List, Tuple
import math

ROUND_DIGITS = 2

class Graph:
    def __init__(self, adj_matrix : np.array = np.empty([0, 0])) -> None:
        self.adj_matrix : np.array = adj_matrix
        self.size : int = self.adj_matrix.size

        self.changed : bool = True  # For UI

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
        self.changed = True
    
    # Removes a vertex from the graph. CAREFUL: if you are keeping track of certain vertex
    # indexes, this will reduce all indexes that are greater than the one provided by one.
    def remove_vertex(self, vertex_index : int) -> None:
        if vertex_index >= self.size:
            print(f"ERROR: could not remove vertex {vertex_index}: Out of bounds.")
            return
        self.adj_matrix = np.delete(self.adj_matrix, vertex_index, 0)
        self.adj_matrix = np.delete(self.adj_matrix, vertex_index, 1)
        self.size -= 1
        self.changed = True

    # Returns list of 1s and 0s. A 1 represents a connection or edge between the
    # vertex given and the index of the 1, and a 0 represents no connection.
    def get_connections(self, vertex_index : int) -> np.array:
        return self.adj_matrix[vertex_index]
    
    # Gets cartesian coordinates of each vertex using eigenvectors.
    # Result is a list of two dimensional arrays (x, y) for each vertex.
    def get_coords(self) -> np.array:
        (x_coords_index, y_coords_index) =  find_smallest_eigs(self.adj_matrix)
        return calc_graph_eig(self.adj_matrix, x_coords_index, y_coords_index)
    
# _________________________________
# ----- MATH HELPER FUNCTIONS -----
# _________________________________

# Returns two smallest non-zero eigenvalues of a matrix.
def find_smallest_eigs(adj_matrix : np.array) -> Tuple[int]:
    diag = np.diag(np.sum(adj_matrix, axis=0))
    laplacian = np.subtract(diag, adj_matrix)
    eig_vals = np.linalg.eig(laplacian).eigenvalues

    lowest_is = [0,0]
    lowest_vals = [math.inf, math.inf]
    i = -1
    for e in eig_vals:
        i += 1
        # We round because a number that is very close to 0 will result in a bad graph.
        e_r = round(e, ROUND_DIGITS)

        if e_r <= 0: continue
        if e_r < lowest_vals[0]:
            lowest_is = [i, lowest_is[0]]
            lowest_vals = [eig_vals[i], lowest_vals[0]]
            continue
        if e_r < lowest_vals[1]:
            lowest_is[1] = i
            lowest_vals[1] = eig_vals[i]
    print(lowest_is[0])
    return lowest_is

# Returns list of object coordinates after applying eigenvector conversions to
# cartesian coordinates.
# Format of array: each row is a node: [x, y]
def calc_graph_eig(adj_matrix : np.array, x_coords_index : int = 0,
        y_coords_index : int = 1) -> np.array:
    diag = np.diag(np.sum(adj_matrix, axis=0))
    laplacian = np.subtract(diag, adj_matrix)

    eigs = np.linalg.eig(laplacian).eigenvectors

    x_pos = eigs[:, x_coords_index]
    y_pos = eigs[:, y_coords_index]

    coords = np.flip(
        np.rot90([x_pos, y_pos], k=1),
        axis=0
    ).tolist()
    return coords