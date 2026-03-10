import json
import random
import heapq
from collections import deque


def load_flight_data(graph, filepath):
    with open(filepath, 'r') as file:
        data = json.load(file)

    # -- Create All Airplane Nodes -- #
    for iata_code, info in data.items():
        try:
            lat = float(info['latitude'])
            lon = float(info['longitude'])
            name = info.get('name', 'Unknown Airport')

            graph.add_airport(iata_code, name, lat, lon)

        except(ValueError, TypeError, KeyError):
            # IF latitude/longitude is missing, null, or bad string, skip this airport
            continue

    # -- Connection of Airplane Nodes -- #
    for origin_code, info in data.items():
        for route in info['routes']:
            dest_code = route['iata']
            distance_km = route['km']
            flight_time_min = route['min']

            # -- Artificial Price Generation -- #
            base_fare = 50
            cost_per_km = 0.12
            random_multiplier = random.uniform(0.8, 1.3) # Price vary from 80% to 130%

            calculated_price = round((base_fare + (distance_km * cost_per_km)) * random_multiplier, 2)

            # -- Safety Check -- #
            # only adds flight if destination airport 
            # actually exists in graph dataset
            if dest_code in graph.airports:
                graph.add_flight(origin_code, dest_code, distance_km, calculated_price, flight_time_min)

class AirportNode:
    def __init__(self, code, name, latitude, longitude):
        self.code = code
        self.name = name
        self.latitude = latitude
        self.longitude = longitude

        # Format: {'DESTINATION_CODE': {'distance': 500, 'price: 500', 'time: 46'} }
        self.connections = {}

    def add_connections(self, destination, distance, price, time_mins):
        self.connections[destination] = {
            'distance': distance,
            'price': price,
            'time': time_mins
        }

class FlightGraph:
    def __init__(self):
        # Format: {'SIN': AirportNode(...), 'NRT': AirportNode(...)}
        self.airports = {}
    
    def add_airport(self, code, name, lat, lon):
        # Create new AirportNode
        if code not in self.airports:
            new_node = AirportNode(code, name, lat, lon)
            self.airports[code] = new_node

    def add_flight(self, origin, destination, distance, price, time_min):
        # -- Creates directional edge between 2 existing airports -- #
        if origin in self.airports and destination in self.airports:
            self.airports[origin].add_connections(destination, distance, price, time_min)

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
        
def find_fewest_layovers(graph, start_code, end_code):
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
            if neighbor not in visited:
                # Mark as visited the moment we see it to prevent duplicate work
                visited.add(neighbor)
                
                # Push the neighbor to the BACK of the line (right side of the deque)
                # and update the path we took to get there
                queue.append((neighbor, path + [neighbor]))

    # If the queue empties and we never returned, no route exists
    return None


if __name__ == "__main__":
    # 1. Initialize the empty graph
    air_graph = FlightGraph()
    
    # 2. Load the data
    # Safely join that directory path with your file name
    with open("data/airline_routes.json") as f:
    
        try:
            load_flight_data(air_graph, f)
            print("✅ Data loaded successfully!\n")
        except FileNotFoundError:
            print(f"❌ Error: Could not find the file '{f}'.")
            exit()

    # # 3. Test Pass 1: Check if an airport node was created
    # test_airport_code = 'AAE' # Using Annaba from your sample data
    
    # if test_airport_code in air_graph.airports:
    #     node = air_graph.airports[test_airport_code]
    #     print(f"--- Airport Node Test ---")
    #     print(f"Code: {node.code}")
    #     print(f"Name: {node.name}")
    #     print(f"Coordinates: {node.latitude}, {node.longitude}")
    #     print(f"Total Connections: {len(node.connections)}\n")
        
    #     # 4. Test Pass 2: Check the connections and weights
    #     print(f"--- Outbound Flights from {test_airport_code} ---")
    #     for dest, details in node.connections.items():
    #         dist = details['distance']
    #         price = details['price']
    #         time = details['time']
    #         print(f"To {dest}: Distance = {dist}km, Price = ${price}, Time = {time}mins")
            
    # else:
    #     print(f"❌ Error: Airport {test_airport_code} not found in the graph.")
    # ... (Keep your previous data loading code) ...

    print("\n--- Testing Dijkstra's Algorithm ---")
    start = 'AAE'
    end = 'IST' # Istanbul
    

    # 1. Optimize for SHORTEST DISTANCE
    # Pass 'distance' so the algorithm looks at details['distance']
    path_dist, total_km = find_lowest_path(air_graph, start, end, weight_type='distance')
    print(f"\n📍 Shortest Distance:")
    print(" -> ".join(path_dist))
    print(f"Total: {total_km} km")

    # 2. Optimize for LOWEST COST (Price)
    # Pass 'price' so the algorithm looks at details['price']
    path_cost, total_price = find_lowest_path(air_graph, start, end, weight_type='price')
    print(f"\n💰 Lowest Cost:")
    print(" -> ".join(path_cost))
    print(f"Total: ${total_price}")

    # 3. Optimize for FASTEST TIME
    # Pass 'time' so the algorithm looks at details['time']
    path_time, total_mins = find_lowest_path(air_graph, start, end, weight_type='time')
    print(f"\n⏱️ Fastest Time:")
    print(" -> ".join(path_time))
    print(f"Total: {total_mins} minutes")

    # ... (Keep previous Dijkstra tests) ...

    print(f"\n--- Optimizing for Fewest Layovers ---")
    
    path_hops = find_fewest_layovers(air_graph, start, end)
    
    if path_hops:
        print(f"\n✈️ Fewest Connections:")
        print(" -> ".join(path_hops))
        print(f"Total Flights: {len(path_hops) - 1}") # Hops is nodes minus 1
    else:
        print(f"No valid route found between {start} and {end}.")