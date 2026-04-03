# COMP2090SEF Task 2
## Usesr Guide for python matrix :

---

### Method of creating a 2D matrix:
<p><img src="/assert/image/create.png" height="500"></p>
Line 1:  Outcome with method 1 <br>
Line 3,4:  Outcome with method 2 (using numpy)

### Basic Matrix operation:
<p><img src="/assert/image/addition.png" height="500" width="500"></p>  Addition:   Simply use the add symbol to let two matrices add together.<br>

<br><p><img src="/assert/image/subtraction.png" height="500" width="500"></p> Subtraction: Similarly, use the minus symbol to conduct the subtraction of two matrices.

<br><p><img src="/assert/image/scalar.PNG" height="500" width="500"></p> Scalar Multiplication: Allowing matrix to multiply a real number.

*Scalar: the value without any positive, negative or direction meaning *

<br><p><img src="/assert/image/Multiple.PNG" height="500" width="500"></p> Matrix Multiplication (two ways):
1.	Use “@” symbol 
2.	Numpy built in function: .matmul()

Both ways perform the same result.

<br><p><img src="/assert/image/transpose.PNG" height="500" width="500"></p> Transpose:

Rearrange the matrix by column first. That is
default is order by row

---

### Major components about Dijkstra’s algorithm :
<p><img src="/assert/image/city_map.png" height="500" width="500"></p>
•	Create a dictionary storing known distance to each import min-heap priority queue.

<br><p><img src="/assert/image/function_1.png" height="1000" width="1500"></p>
•	Import min-heap priority queue. (A heap is a special tree-based structure where the smallest or largest element is always at the root.)

•	Function 1: dijkstra(graph, start): finds the shortest distance from the ‘start’ node to every other node:
  - ‘distances’:  is a dictionary storing shortest known distance to each node.
  - ‘pq’:  Priority queue (min-heap) to always process the closest node next.
  - ‘previous’: is a dictionary to track the path (who led to each node).

Procedure:
1. Initialize all distances to infinity, except the start node (0) lin13.
2. Use a priority queue to explore nodes with the smallest current distance.
3. For each node, calculate the new distance.
4. If it’s shorter than the known distance, update it and record the path.
5. Repeat until all nodes are processed.

<br><p><img src="/assert/image/function_2.png" height="1000" width="1500"></p>
•	Function 2: shortest_path(graph, start, end) By using the dijkstra(graph, start) function to find the shortest path from ‘start’ to ‘end’. 

Procedure:
1. Calls ‘dijkstra’ to get distances and previous nodes.
2. Reconstructs the path by walking backward from `end` to `start` using ‘previous’.
3. Reverses the path to get correct order.
4. Returns the path and the costing time.
