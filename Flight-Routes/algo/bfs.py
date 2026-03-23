from collections import deque


def find_fewest_layovers(graph, start_code, end_code, avoid_airport=None, max_stops=None, airline=None):
    """
    Finds the route with the fewest connections using Breadth-First Search (BFS).
    If max_stops is provided, paths that exceed the limit are ignored
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

        layovers = len(path) - 2  # Number of layovers is number of flights minus 1 (for the starting airport)
        # Keep BFS consistent with DFS semantics: len(path)-2 is number of flights.
        if max_stops is not None and layovers > max_stops:
            continue

        # Did we reach the destination?
        # Because this is BFS, the FIRST time we hit this, it's guaranteed to be the fewest hops!
        if current_node == end_code:
            return path

        # 4. Explore neighbors
        current_airport_obj = graph.airports[current_node]

        # We only care about the keys (neighbor codes) here, not the weights (details)
        for neighbor in current_airport_obj.connections:
            if avoid_airport and neighbor == avoid_airport:
                continue  # avoid airport

            if airline:
                flights = current_airport_obj.connections.get(neighbor, [])
                has_airline = False
                for f in flights:
                    if f.get("airline", "").lower() == airline.lower():
                        has_airline = True
                        break
                if not has_airline:
                    continue

            if neighbor not in visited:
                # Mark as visited the moment we see it to prevent duplicate work
                visited.add(neighbor)

                # Push the neighbor to the BACK of the line (right side of the deque)
                # and update the path we took to get there
                queue.append((neighbor, path + [neighbor]))

    # If the queue empties and we never returned, no route exists
    return None