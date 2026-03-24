import heapq

def find_lowest_path(graph, start_code, end_code, weight_type='distance', **kwargs):
    """
    Finds the optimal flight path between two airports using Dijkstra's algorithm.
    weight_type can be 'distance', 'price', 'time', 'co2', or 'balanced'.
    """
    valid_weights = ['distance', 'price', 'time', 'co2', 'balanced']
    if weight_type not in valid_weights:
        raise ValueError(f"weight_type must be one of {valid_weights}, got '{weight_type}'")

    if start_code not in graph.airports or end_code not in graph.airports:
        return None, float('inf')

    selected_airline = kwargs.get('airline', None)
    max_stops = kwargs.get('max_stops', float('inf'))
    avoid_airport = kwargs.get('avoid_airport', None)
    avoid_continent = kwargs.get('avoid_continent', None)

    pq = [(0, start_code, [start_code])]
    min_stops = {code: float('inf') for code in graph.airports}
    min_stops[start_code] = 0

    while pq:
        current_weight, current_node, path = heapq.heappop(pq)

        # Check if we've exceeded the maximum number of stops
        layovers = len(path) - 2

        if layovers > max_stops:
            continue
        if layovers >= min_stops[current_node] and current_node != start_code:
            continue
        if current_node == end_code:
            return path, current_weight
        
        min_stops[current_node] = layovers
        current_airport_obj = graph.airports[current_node]

        for neighbor, flights_list in current_airport_obj.connections.items():
            if avoid_airport and neighbor == avoid_airport:
                    continue              #avoid airport

            if avoid_continent:
                if graph.airports[neighbor].continent == avoid_continent:
                    continue          #avoid continent
            if selected_airline:
                filtered_flights = []
                for f in flights_list:
                    if f.get('airline', '').lower() == selected_airline.lower():
                        filtered_flights.append(f)
                flights_list = filtered_flights

            if not flights_list:
                continue

            best_flight_weight = float('inf')
            
            for flight in flights_list:
                # --- BALANCED ROUTE MATH ---
                if weight_type == 'balanced':
                    w_price = kwargs.get('weight_price', 0.25)
                    w_time = kwargs.get('weight_time', 0.25)
                    w_co2 = kwargs.get('weight_co2', 0.25)
                    w_dist = kwargs.get('weight_distance', 0.25)
                    
                    # ==========================================
                    # BALANCED ROUTE NORMALIZATION MATH
                    # ==========================================
                    # To calculate a single composite score, we must normalize 
                    # completely different units ($, mins, kg, km) to a common baseline. 
                    #
                    # BASELINE: A standard 1,000 km flight costs ~$150. 
                    # We apply global multipliers to force all metrics to equal ~150:
                    # - Price: ~$150      (Multiplier: 1.0)  -> 150
                    # - Time: ~75 mins    (Multiplier: 2.0)  -> 150
                    # - CO2: ~115 kg      (Multiplier: 1.3)  -> 149.5
                    # - Distance: 1000 km (Multiplier: 0.15) -> 150
                    # ==========================================
                    balanced_score = (flight['price'] * w_price) + \
                                     (flight['time'] * 2.0 * w_time) + \
                                     (flight['co2'] * 1.3 * w_co2) + \
                                     (flight['distance'] * 0.15 * w_dist)
                                     
                    if balanced_score < best_flight_weight:
                        best_flight_weight = balanced_score
                
                # --- STANDARD MATH ---
                else:
                    if flight[weight_type] < best_flight_weight:
                        best_flight_weight = flight[weight_type]

            new_total_weight = current_weight + best_flight_weight
            new_path = path + [neighbor]
            
            heapq.heappush(pq, (new_total_weight, neighbor, new_path))

    return None, float('inf')