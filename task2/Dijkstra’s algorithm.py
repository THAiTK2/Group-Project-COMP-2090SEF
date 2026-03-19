city_map = {
    'Home': {'A': 5, 'B': 2},
    'A': {'Home': 5, 'C': 4},
    'B': {'Home': 2, 'C': 1, 'D': 7},
    'C': {'A': 4, 'B': 1, 'Work': 3},
    'D': {'B': 7, 'Work': 2},
    'Work': {'C': 3, 'D': 2}
}

import heapq

def dijkstra(graph, start):
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    pq = [(0, start)]
    previous = {node: None for node in graph}  # track path
    
    while pq:
        current_distance, current_node = heapq.heappop(pq)
        
        if current_distance > distances[current_node]:
            continue
        
        for neighbor, weight in graph[current_node].items():
            distance = current_distance + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = current_node
                heapq.heappush(pq, (distance, neighbor))
    
    return distances, previous

def shortest_path(graph, start, end):
    distances, previous = dijkstra(graph, start)
    path = []
    current = end
    while current is not None:
        path.append(current)
        current = previous[current]
    path.reverse()
    return path, distances[end]

# Example usage
path, time = shortest_path(city_map, 'Home', 'Work')
print("Shortest path:", path)
print("Travel time:", time)

