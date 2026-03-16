from collections import deque
def find_fewest_layovers(graph, start_code, end_code, avoid_airport=None):
    """
    Finds the route with the fewest connections using Breadth-First Search (BFS).
    """
    # 1. Safety check
    if start_code not in graph.airports or end_code not in graph.airports:
        return None

    # 2. Setup the Queue and Visited Set
    # We store a tuple in the queue: (current_airport, path_taken)
    queue = deque([(start_code, [start_code])])
    
    # We add the start node to visited immediately so we don't go backwards to it
    visited = set([start_code])

    # 3. The BFS Loop
    while queue:
        # Pop from the FRONT of the line (left side of the deque)
        current_node, path = queue.popleft()

        # Did we reach the destination? 
        # Because this is BFS, the FIRST time we hit this, it's guaranteed to be the fewest hops!
        if current_node == end_code:
            return path

        # 4. Explore neighbors
        current_airport_obj = graph.airports[current_node]
        
        # We only care about the keys (neighbor codes) here, not the weights (details)
        for neighbor in current_airport_obj.connections:
            if avoid_airport and neighbor == avoid_airport:
                continue   #avoid airport    
            if neighbor not in visited:
                        
                # Mark as visited the moment we see it to prevent duplicate work
                visited.add(neighbor)
                
                # Push the neighbor to the BACK of the line (right side of the deque)
                # and update the path we took to get there
                queue.append((neighbor, path + [neighbor]))

    # If the queue empties and we never returned, no route exists
    return None