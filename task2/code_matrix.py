# Create a matrix :
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



#Application of matrix : Adjacency Matrix for undirected graph 
def add_edge(mat, i, j):
  
    # Add an edge between two vertices
    mat[i][j] = 1  # Graph is 
    mat[j][i] = 1  # Undirected

def display_matrix(mat):
  
    # Display the adjacency matrix
    for row in mat:
        print(" ".join(map(str, row)))  

# Main function to run the program
if __name__ == "__main__":
    V = 4  # Number of vertices
    mat = [[0] * V for _ in range(V)]  

    # Add edges to the graph
    add_edge(mat, 0, 1)
    add_edge(mat, 0, 2)
    add_edge(mat, 1, 2)
    add_edge(mat, 2, 3)

    # Optionally, initialize matrix directly
    """
    mat = [
        [0, 1, 0, 0],
        [1, 0, 1, 0],
        [0, 1, 0, 1],
        [0, 0, 1, 0]
    ]
    """

    # Display adjacency matrix
    print("Adjacency Matrix:")
    display_matrix(mat)


