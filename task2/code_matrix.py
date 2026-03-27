# Creat a matrix :
  matrix_name = [
    [n1, n2,..],            # method_1
    [.....], 
    [.....]
]
# the number of rows and columns are determined by user 


import numpy                 # import numpy to operate numerical data and scientific computing

A = numpy.array([[1, 2], [3, 4]]) # method_2
B = numpy.array([[5, 6], [7, 8]]) 

-----------------------------------------

# Matrix operations
print(A + B)   # Matrix addition 

print(A-B)     # Matrix subtraction

print(A*4)     # Scalar Multiplication

print(A @ B)   OR  print(np.matmul(A,B))    # Matrix multiplication 

print(A.T)     # Transpose. Element in matrix A will be re-arranged order by column. 



# Adjacency Matrix
import numpy as np

def create_adjacency_matrix(graph):
    nodes = list(graph.keys())
    n = len(nodes)
    
    # Initialize matrix with infinity (no connection)
    matrix = [[float('inf')] * n for _ in range(n)]
    
    # Fill in edges
    for i, node in enumerate(nodes):
        for neighbor, weight in graph[node].items():
            j = nodes.index(neighbor)
            matrix[i][j] = weight
    
    return nodes, matrix

# Example usage
nodes, adj_matrix = create_adjacency_matrix(city_map)

# Pretty print
print("Nodes:", nodes)
print("Adjacency Matrix:")
print(np.array(adj_matrix))
