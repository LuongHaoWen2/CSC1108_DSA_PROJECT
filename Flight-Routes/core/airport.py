
class AirportNode:
    def __init__(self, code, name, latitude, longitude):
        self.code = code
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
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
