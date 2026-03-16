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

 # Matrix multiplication
print(A @ B)   OR  print(np.matmul(A,B)) 

print(A.T)     # Transpose. Element in matrix A will be re-arranged order by column. 
