def find_routes(graph, start, end, max_stops, avoid_airport=None, airline=None):
    """
    Iterative DFS to find all routes from start to end up to max_stops.
    graph: FlightGraph instance
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
        current_airport_obj = graph.airports.get(current)
        if current_airport_obj:
            for neighbor in current_airport_obj.connections:
                if avoid_airport and neighbor == avoid_airport:
                    continue              #avoid airport

                if airline:
                    flights = current_airport_obj.connections.get(neighbor, [])
                    has_airline = False
                    for f in flights:
                        if f.get("airline", "").lower() == airline.lower():
                            has_airline = True
                            break
                    if not has_airline:
                        continue

                if neighbor not in path:  # avoid cycles
                    stack.append((neighbor, path + [neighbor]))

    return routes