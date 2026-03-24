import heapq
import math
# This is using the same Dijkstra Algorithm as the base and making small changes to add the heuristic function to it
def find_lowest_path_astar(graph, start_code, end_code, weight_type='distance', **kwargs):
    """
    Finds the route with the lowest total cost using A* Search.
    If max_stops is provided, paths that exceed the limit are ignored.
    weight_type can be 'distance', 'price', 'time', 'co2', or 'balanced'.
    """
    valid_weights = ['distance', 'price', 'time', 'co2', 'balanced']
    if weight_type not in valid_weights:
        raise ValueError(f"weight_type must be one of {valid_weights}, got '{weight_type}'")
    # Safety Check
    if start_code not in graph.airports or end_code not in graph.airports:
        return None, float('inf')
    
    selected_airline = kwargs.get('airline', None)
    max_stops = kwargs.get('max_stops', float('inf'))
    avoid_airport = kwargs.get('avoid_airport', None)
    avoid_continent = kwargs.get('avoid_continent', None)

    # Setup the Priority Queue and Visited Set
    # Store a tuple in the priority queue: (f_score, actual cost, current_airport (node), path_taken)
    # Cost in this case will be the weights of the flights taken so far (e.g. total distance, total price, etc.)
    pq = [(0, 0, start_code, [start_code])]
    min_stops = {code: float('inf') for code in graph.airports}
    min_stops[start_code] = 0

    while pq:
        f_score, current_weight, current_node, path = heapq.heappop(pq)

        layovers = len(path) - 2

        if layovers > max_stops:
            continue
        if layovers >= min_stops[current_node] and current_node != start_code:
            continue
        if current_node == end_code:
            return path, current_weight
        
        # Update the minimum stops to reach this node
        min_stops[current_node] = layovers

        current_airport_obj = graph.airports[current_node]

        for neighbor, flights_list in current_airport_obj.connections.items():
            if avoid_airport and neighbor == avoid_airport:
                    continue              #avoid airport

            if avoid_continent:
                if graph.airports[neighbor].continent == avoid_continent:
                    continue          #avoid continent
            # Filter by Airline if Specified
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

            # For Heuristic Calculation
            neighbor_obj = graph.airports[neighbor]
            end_obj = graph.airports[end_code]

            # Since the airport node itself has lat and lon separately, we combine them together called coordinates.
            neighbor_coords = (neighbor_obj.latitude, neighbor_obj.longitude)
            end_coords = (end_obj.latitude, end_obj.longitude)
            
            h_score = calculate_heuristic(neighbor_coords, end_coords, weight_type, **kwargs)
            new_f_score = new_total_weight + h_score
            
            heapq.heappush(pq, (new_f_score, new_total_weight, neighbor, new_path))

    return None, float('inf')

def calculate_heuristic(current_coords, dest_coords, weight_type, **kwargs):
    # Get the absolute shortest physical distance possible
    straight_line_km = haversine_distance(current_coords, dest_coords)

    # --- CONSTANTS: The "Best Case Scenario" Multipliers ---
    # Based on the absolute minimums values from the dataset.
    MAX_PLANE_SPEED_KMH = 1000.0   # Fastest possible commercial flight based off of google rough estimates.
    MIN_PRICE_PER_KM = 0.057       # Calculated from reverse engineering the price generated from the graph.
    MIN_CO2_PER_KM = 0.09775       # Same thing reverse engineered.

    # Convert the distance into the requested unit based off what the user choose
    if weight_type == 'distance':
        return straight_line_km

    elif weight_type == 'time':
        # Distance / Speed = Hours. Multiply by 60 for minutes.
        best_possible_hours = straight_line_km / MAX_PLANE_SPEED_KMH
        return best_possible_hours * 60.0

    elif weight_type == 'price':
        return straight_line_km * MIN_PRICE_PER_KM

    elif weight_type == 'co2':
        return straight_line_km * MIN_CO2_PER_KM

    elif weight_type == 'balanced':
        # Apply your exact normalization math to the "best case" estimates
        w_price = kwargs.get('weight_price', 0.25)
        w_time = kwargs.get('weight_time', 0.25)
        w_co2 = kwargs.get('weight_co2', 0.25)
        w_dist = kwargs.get('weight_distance', 0.25)

        # Get the individual best-case guesses
        est_price = straight_line_km * MIN_PRICE_PER_KM
        est_time = (straight_line_km / MAX_PLANE_SPEED_KMH) * 60.0
        est_co2 = straight_line_km * MIN_CO2_PER_KM

        # Combine them using your group's normalization multipliers
        balanced_guess = (est_price * w_price) + \
                         (est_time * 2.0 * w_time) + \
                         (est_co2 * 1.3 * w_co2) + \
                         (straight_line_km * 0.15 * w_dist)
                         
        return balanced_guess

    return 0

# This is the haversine formula used to calculate a straight line towards the destination.
def haversine_distance(coord1, coord2):
    """
    Calculates the straight-line distance in kilometers between two GPS coordinates.
    coord1 and coord2 should be tuples of (latitude, longitude).
    """
    lat1, lon1 = float(coord1[0]), float(coord1[1])
    lat2, lon2 = float(coord2[0]), float(coord2[1])
    R = 6371.0 # Radius of the Earth in kilometers

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (math.sin(dlat / 2)**2 + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2)
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    
    return distance