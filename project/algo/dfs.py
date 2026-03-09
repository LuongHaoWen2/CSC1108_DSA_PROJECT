def find_routes(graph, start, end, max_stops):
    """
    Iterative DFS to find all routes from start to end up to max_stops.
    Returns a list of paths (each path is a list of airport codes).
    """
    stack = [(start, [start])]  # stack of tuples: (current_airport, path_so_far)
    routes = []

    while stack:
        current, path = stack.pop()

        # If reached the destination, save the path
        if current == end:
            routes.append(path)
            continue

        # Stop if path exceeds max_stops
        if len(path) - 1 >= max_stops:
            continue

        # Explore neighbors
        for neighbor in graph.get(current, []):
            next_airport = neighbor["to"]
            if next_airport not in path:  # avoid cycles
                stack.append((next_airport, path + [next_airport]))

    return routes