import heapq

def dijkstra(graph, start)
    distances = {node: float('inf') for node in graph}      # Initialize distances
    distances[start] = 0
    

    pq = [(0, start)]      # Priority queue (min-heap)
    
    while pq:
        current_distance, current_node = heapq.heappop(pq)
        
       
        if current_distance > distances[current_node]:  # Skip if we already found a shorter path
            continue
        
        # Explore neighbors
        for neighbor, weight in graph[current_node].items():
            distance = current_distance + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(pq, (distance, neighbor))
    
    return distances

# City map (graph representation)
city_map = {
    'A': {'B': 4, 'C': 2},
    'B': {'A': 4, 'C': 1, 'D': 5},
    'C': {'A': 2, 'B': 1, 'D': 8, 'E': 10},
    'D': {'B': 5, 'C': 8, 'E': 2},
    'E': {'C': 10, 'D': 2}
}

# Find shortest paths from home (A)
shortest_paths = dijkstra(city_map, 'A')
print(shortest_paths)

