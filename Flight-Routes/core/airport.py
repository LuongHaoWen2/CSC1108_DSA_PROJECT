
class AirportNode:
    def __init__(self, code, name, latitude, longitude, continent,country_code=""):
        self.code = code
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.country_code = country_code
        self.continent = continent
        self.connections = {}

    def add_connection(self, destination, airline, distance, price, time, co2):
        if destination not in self.connections:
            self.connections[destination] = []

        self.connections[destination].append({
            "airline": airline,
            "distance": distance,
            "price": price,
            "time": time,
            "co2": co2
        })
