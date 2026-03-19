import heapq

def find_lowest_path(graph, start_code, end_code, weight_type='distance', **kwargs):
    """
    Finds the optimal flight path between two airports using Dijkstra's algorithm.
    weight_type can be 'distance', 'price', 'time', 'co2', or 'balanced'.
    
    Returns:
        tuple: (path as a list of strings, total cumulative weight)
               Example: (['SIN', 'DXB', 'LHR'], 850.50)
    """
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
                # --- NEW: BALANCED ROUTE MATH ---
                if weight_type == 'balanced':
                    w_price = kwargs.get('weight_price', 0.25)
                    w_time = kwargs.get('weight_time', 0.25)
                    w_dist = kwargs.get('weight_distance', 0.25)
                    w_co2 = kwargs.get('weight_co2', 0.25)
                    
                    # Apply global multipliers to put them on an even playing field
                    # due to the way they are calculated
                    # ==========================================
                    # BALANCED ROUTE NORMALIZATION MATH
                    # ==========================================
                    # To calculate a single composite score, we must normalize 
                    # completely different units ($, mins, kg, km) to a common baseline. 
                    # Otherwise, large raw numbers (like 1000 km) would mathematically 
                    # overpower smaller numbers (like $150) and ruin the slider weights.
                    #
                    # BASELINE: A standard 1,000 km flight costs ~$150. 
                    # We apply global multipliers to force all metrics to equal ~150:
                    # - Price: ~$150      (Multiplier: 1.0)  -> 150
                    # - Time: ~75 mins    (Multiplier: 2.0)  -> 150
                    # - CO2: ~115 kg      (Multiplier: 1.3)  -> 149.5
                    # - Distance: 1000 km (Multiplier: 0.15) -> 150
                    #
                    # By leveling the playing field, a 25/25/25/25 slider split ensures 
                    # every metric contributes exactly equal "voting power" to the score.
                    # ==========================================
                    balanced_score = (flight['price'] * w_price) + \
                                     (flight['time'] * 2.0 * w_time) + \
                                     (flight['distance'] * 0.15 * w_dist) + \
                                     (flight['co2'] * 1.3 * w_co2)
                                     
                    if balanced_score < best_flight_weight:
                        best_flight_weight = balanced_score
                
                # STANDARD MODE (Cost, Time, CO2, Distance)
                else:
                    if flight[weight_type] < best_flight_weight:
                        best_flight_weight = flight[weight_type]

            new_total_weight = current_weight + best_flight_weight

            if new_total_weight < min_weights[neighbor]:
                min_weights[neighbor] = new_total_weight
                new_path = path + [neighbor]
                heapq.heappush(pq, (new_total_weight, neighbor, new_path))

    # If the queue empties and did not hit destination
    return None, float('inf')