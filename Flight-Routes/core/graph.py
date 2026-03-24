import json
import random
from core.airport import AirportNode

random.seed(42)

class FlightGraph:
    def __init__(self):
        self.airports = {}

    def add_airport(self, code, name, lat, lon, continent, country_code=""):
        if code not in self.airports:
            self.airports[code] = AirportNode(code, name, lat, lon, continent, country_code)

    def add_flight(self, origin, destination, airline, distance, price, time, co2):
        if origin in self.airports and destination in self.airports:
            self.airports[origin].add_connection(destination, airline, distance, price, time, co2)

    def get_airport(self, code):
        return self.airports.get(code, None)

    def get_all_codes(self):
        return list(self.airports.keys())

    def has_airport(self, code):
        return code in self.airports

def load_flight_data(graph, filepath):
    with open(filepath, "r") as file:
        data = json.load(file)

    # Create airport nodes
    for code, info in data.items():
        try:
            lat = float(info["latitude"])
            lon = float(info["longitude"])
            name = info.get("name", "Unknown Airport")
            country_code = info.get("country_code", "")
            continent = info.get("continent", "")
            graph.add_airport(code, name, lat, lon, continent, country_code)
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

            if distance <=0 or time <=0:
                continue

            # Extract Airline name, default if none found
            carriers = route.get("carriers", [])

            if not carriers:
                carriers = [{"name": "Unknown Airline"}]

            for carrier in carriers:
                # Extract carrier name, default if missing
                airline_name = carrier.get("name", "Unknown Airline")

                # Generate consistent price per airline brand
                if airline_name not in airline_multiplier:
                    airline_multiplier[airline_name] = random.uniform(0.5, 1.5)

                # Calculate price
                tier_multiplier = airline_multiplier[airline_name]
                base_fare = 50 * tier_multiplier
                cost_per_km = 0.12 * tier_multiplier
                random_variance = random.uniform(0.95, 1.05)
                price = round((base_fare + distance * cost_per_km) * random_variance, 2)

                # Calculate co2
                eco_variance = random.uniform(0.85, 1.15)
                co2 = round(distance * 0.115 * eco_variance, 2)

                # Add flight with calculated price and co2
                graph.add_flight(origin, dest, airline_name, distance, price, time, co2)

