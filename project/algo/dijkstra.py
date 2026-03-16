import heapq
from collections import deque

def find_lowest_path(graph, start_code, end_code, weight_type='distance'):
    # Finds optimal path between two airports using Dijkstra's algorithm
    # weight_type can be 'distance', 'price', or 'time'

    # If either airports not in dataset
    if start_code not in graph.airports or end_code not in graph.airports:
        return None, float('inf')
    
    # Initialise Priority Queue
    # Format: (cumulative weight, current_airport_code, path_taken)
    pq = [(0, start_code, [start_code])]

    # Track min weight of path taken to reach each node to avoid loops/bad path
    min_weight = {code: float('inf') for code in graph.airports}
    min_weight[start_code] = 0

    while pq:
        current_weight, current_node, path = heapq.heappop(pq)

        # End of path/found destination
        if current_node == end_code:
            return path, current_weight
        
        # IF there is a cheaper/faster way to this node, skip it
        if current_weight > min_weight[current_node]:
            continue

        # Explore all outgoing flights from current airport/node
        current_airport_obj = graph.airports[current_node]
        for neighbours, details in current_airport_obj.connections.items():

            # Grab specific weights we sort by (e.g. 'distance', 'price', 'time')
            edge_weight = details[weight_type]
            new_total_weight = current_weight + edge_weight

            # IF new path is better than old path, use new path
            if new_total_weight < min_weight[neighbours]:
                min_weight[neighbours] = new_total_weight
                # Push new, better path into priority queue
                heapq.heappush(pq, (new_total_weight, neighbours, path + [neighbours]))
    
    return None, float('inf')