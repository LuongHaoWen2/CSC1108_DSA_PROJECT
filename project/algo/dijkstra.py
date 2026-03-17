import heapq
from collections import deque

"""
Find the best route by distance, cost, or time

"""
def find_lowest_path(graph, start_code, end_code, weight_type='distance'):
    # Finds optimal path between two airports using Dijkstra's algorithm
    # weight_type can be 'distance', 'price', or 'time'
    """
    Finds the optimal flight path between two airports using Dijkstra's algorithm.

    This function traverses a multigraph where edges contain multiple airlines. 
    It evaluates all available flights on a route and calculates the path with 
    the lowest cumulative weight based on the user's chosen metric.

    Args:
        graph (FlightGraph): The graph object containing all airport nodes and flight connections.
        start_code (str): The 3-letter IATA code of the origin airport (e.g., 'SIN').
        end_code (str): The 3-letter IATA code of the destination airport (e.g., 'LHR').
        weight_type (str, optional): The specific flight attribute to optimize for. 
            Accepts 'distance', 'price', or 'time'. Defaults to 'distance'.

    Returns:
        tuple: A tuple containing two elements:
            - path (list): The step-by-step route. Each step is represented as a tuple of 
              (airport_code, airline_name). Example: [('SIN', 'Origin'), ('DXB', 'Scoot')].
            - total_weight (float): The total cumulative value of the chosen weight_type.
            
        Returns (None, float('inf')) if no valid path exists between the two airports.
    """

    # If either airports not in dataset
    if start_code not in graph.airports or end_code not in graph.airports:
        return None, float('inf')
    
    # Initialise Priority Queue
    # Format: (cumulative weight, current_airport_code, path_taken)
    # Store a tuple in the path: (Airport Code, Airline Used to get there)
    # Origin node has no incoming airline, so label "Origin"
    pq = [(0, start_code, [(start_code, "Origin")])]

    # Track min weight of path taken to reach each node to avoid loops/bad path
    # Defaults every path weight to 'inf' and set start/origin node to 0
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

        for neighbours, flight_lists in current_airport_obj.connections.items():

            # See which airline is cheaper
            best_flight_weight = float('inf')
            best_airline = "Unknown"


            for flight in flight_lists:
                if flight[weight_type] < best_flight_weight:
                    best_flight_weight = flight[weight_type]
                    best_airline = flight["airline"]

            new_total_weight = current_weight + best_flight_weight

            # IF new path is better than old path, use new path
            if new_total_weight < min_weight[neighbours]:
                min_weight[neighbours] = new_total_weight

                new_path = path + [(neighbours, best_airline)]
                # Push new, better path into priority queue
                heapq.heappush(pq, (new_total_weight, neighbours, new_path))
    
    return None, float('inf')