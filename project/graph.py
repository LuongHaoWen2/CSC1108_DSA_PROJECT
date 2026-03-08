import json

class Flight:
    def __init__(self, destination, distance, duration):
        self.destination = destination
        self.distance = distance
        self.duration = duration

class Airport:
    def __init__(self, code, name, city, country, latitude, longitude):
        self.code = code
        self.name = name
        self.city = city
        self.country = country
        self.latitude = float(latitude) if latitude else None
        self.longitude = float(longitude) if longitude else None

class FlightGraph:
    def __init__(self):
        self.graph = {}          # adjacency list
        self.airport_coords = {} # {airport: (lat, lon)}

    def add_airport(self, airport):
        if airport.code not in self.graph:
            self.graph[airport.code] = []
            self.airport_coords[airport.code] = (airport.latitude, airport.longitude)

    def add_flight(self, origin, flight):
        if origin not in self.graph:
            self.graph[origin] = []
        self.graph[origin].append(flight)

    def load_from_json(self, filepath):
        with open(filepath, "r") as f:
            data = json.load(f)

        for code, info in data.items():
            lat = info.get("latitude")
            lon = info.get("longitude")
            if not lat or not lon:  # skip airports without coordinates
                continue

            airport = Airport(
                code=info.get("iata"),
                name=info.get("name"),
                city=info.get("city_name"),
                country=info.get("country"),
                latitude=lat,
                longitude=lon
            )
            self.add_airport(airport)

            for route in info.get("routes", []):
                flight = Flight(
                    destination=route.get("iata"),
                    distance=route.get("km"),
                    duration=route.get("min")
                )
                self.add_flight(code, flight)