import json
import random


class AirportNode:
    def __init__(self, code, name, latitude, longitude):
        self.code = code
        self.name = name
        self.latitude = latitude
        self.longitude = longitude

        # adjacency list
        # {DEST_CODE: {distance: x, price: y, time: z}}
        self.connections = {}

    def add_connection(self, destination, distance, price, time):
        self.connections[destination] = {
            "distance": distance,
            "price": price,
            "time": time
        }


class FlightGraph:
    def __init__(self):
        # dictionary of airport nodes
        # {"SIN": AirportNode, "NRT": AirportNode}
        self.airports = {}

    def add_airport(self, code, name, lat, lon):
        if code not in self.airports:
            self.airports[code] = AirportNode(code, name, lat, lon)

    def add_flight(self, origin, destination, distance, price, time):
        if origin in self.airports and destination in self.airports:
            self.airports[origin].add_connection(destination, distance, price, time)


def load_flight_data(graph, filepath):
    with open(filepath, "r") as file:
        data = json.load(file)

    # Create airport nodes
    for code, info in data.items():
        try:
            lat = float(info["latitude"])
            lon = float(info["longitude"])
            name = info.get("name", "Unknown Airport")

            graph.add_airport(code, name, lat, lon)

        except (ValueError, TypeError, KeyError):
            continue

    # Create flight connections
    for origin, info in data.items():

        for route in info.get("routes", []):

            dest = route["iata"]

            if dest not in graph.airports:
                continue

            distance = route.get("km", 0)
            time = route.get("min", 0)

            # generate artificial ticket price
            base_fare = 50
            cost_per_km = 0.12
            random_multiplier = random.uniform(0.8, 1.3)

            price = round((base_fare + distance * cost_per_km) * random_multiplier, 2)

            graph.add_flight(origin, dest, distance, price, time)