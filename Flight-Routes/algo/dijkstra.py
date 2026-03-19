import heapq

def find_lowest_path(graph, start_code, end_code, weight_type='distance'):
    """
    Finds the optimal flight path between two airports using Dijkstra's algorithm.
    weight_type can be 'distance', 'price', or 'time'.

    Returns:
        tuple: (path as a list of strings, total cumulative weight)
               Example: (['SIN', 'DXB', 'LHR'], 850.50)
    """

    # Validate weight type
    valid_weights = ['distance', 'price', 'time']
    if weight_type not in valid_weights :
        raise ValueError(f"weight_type must be one of {valid_weights}, got '{weight_type}'")

    # 1. Safety Check: If either airport is not in dataset
    if start_code not in graph.airports or end_code not in graph.airports:
        return None, float('inf')

    # 2. Setup the Priority Queue
    # Format: (cumulative_weight, current_airport_code, path_taken)
    # The path is just a list containing the starting string
    pq = [(0, start_code, [start_code])]

    # Track min weight of path taken to reach each node to avoid loops/bad paths
    min_weights = {code: float('inf') for code in graph.airports}
    min_weights[start_code] = 0

    while pq:
        current_weight, current_node, path = heapq.heappop(pq)

        # End of path / found destination
        if current_node == end_code:
            return path, current_weight

        # If there is already a cheaper/faster way recorded to this node, skip it
        if current_weight > min_weights[current_node]:
            continue

        # Explore all outgoing flights from current airport/node
        current_airport_obj = graph.airports[current_node]

        # neighbor is the destination code (e.g., 'DXB')
        # flights_list is the list of dictionaries (e.g., [{'airline': 'Scoot', 'price': 400}, ...])
        for neighbor, flights_list in current_airport_obj.connections.items():

            # --- MULTIGRAPH LOGIC ---
            # Dig through the list of airlines to find the best deal for this specific hop
            best_flight_weight = float('inf')

            for flight in flights_list:
                if flight[weight_type] < best_flight_weight:
                    best_flight_weight = flight[weight_type]
            # ------------------------

            # Calculate the new total score if we take this flight
            new_total_weight = current_weight + best_flight_weight

            # If this new path beats the current record on the scoreboard, use it
            if new_total_weight < min_weights[neighbor]:
                min_weights[neighbor] = new_total_weight

                new_path = path + [neighbor]

                # Push the new, better path into priority queue
                heapq.heappush(pq, (new_total_weight, neighbor, new_path))

    # If the queue empties and did not hit destination
    return None, float('inf')