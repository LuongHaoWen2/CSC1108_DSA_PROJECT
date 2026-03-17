import json
import random

random.seed(42)

class AirportNode:
    def __init__(self, code, name, latitude, longitude):
        self.code = code
        self.name = name
        self.latitude = latitude
        self.longitude = longitude

        # adjacency list
        # {DEST_CODE: [{"airline": "airlineName1", "distance": xxx, "price": xxx, "time": xxx}, {"airline": "airlineName2", "distance": xxx, "price": xxx, "time": xxx}]}
        # Example:
        # {
        # "DXB": [
        #         {"airline": "Emirates", "distance": 5840, "price": 850.50, "time": 430},
        #         {"airline": "Singapore Airlines", "distance": 5840, "price": 920.00, "time": 425},
        #         {"airline": "Scoot", "distance": 5840, "price": 410.20, "time": 450}
        #     ],
        #     "BKK": [
        #         {"airline": "AirAsia", "distance": 1430, "price": 120.00, "time": 150}
        #     ]
        # }
        self.connections = {}

    def add_connection(self, destination, airline, distance, price, time):
        if destination not in self.connections:
            self.connections[destination] = []
        self.connections[destination].append({
            "airline": airline,
            "distance": distance,
            "price": price,
            "time": time
        })


class FlightGraph:
    def __init__(self):
        # dictionary of airport nodes
        # {"SIN": AirportNode, "NRT": AirportNode}
        self.airports = {}

    def add_airport(self, code, name, lat, lon):
        if code not in self.airports:
            self.airports[code] = AirportNode(code, name, lat, lon)

    def add_flight(self, origin, destination, airline, distance, price, time):
        if origin in self.airports and destination in self.airports:
            self.airports[origin].add_connection(destination, airline, distance, price, time)


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

    # For adding price to different airlines (for price calculation)
    airline_multiplier = {}

    # Create flight connections
    for origin, info in data.items():
        for route in info.get("routes", []):
            dest = route["iata"]

            # Only add flight IF there is actually both airport nodes
            if dest not in graph.airports:
                continue

            distance = route.get("km", 0)
            time = route.get("min", 0)

            # Extract Airline name
            carriers = route.get("carriers", [])
            # If list not empty/there is carriers, its True
            if carriers:
                # Extract carrier name, if fail, sets name to Unknown Airline
                airline_name = carriers[0].get("name", "Unknown Airline")
            else:
                airline_name = "Unknown Airline"

            # generate artificial plane 'brand' price
            if airline_name not in airline_multiplier:
                airline_multiplier[airline_name] = random.uniform(0.5, 1.5)

            # retrival of multiplier of airline for calculation
            tier_multiplier = airline_multiplier[airline_name]

            # generate artificial ticket price
            base_fare = 50 * tier_multiplier
            cost_per_km = 0.12 * tier_multiplier

            # so two flights by same airline of same distance  
            # does not have the exact same price.
            random_variance = random.uniform(0.95, 1.05)

            price = round((base_fare + distance * cost_per_km) * random_variance, 2)

            graph.add_flight(origin, dest, airline_name, distance, price, time)