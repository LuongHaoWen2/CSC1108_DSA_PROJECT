class Route:
    def __init__(self, path, total_distance, total_price, total_time, total_co2, airlines):
        self.path = path
        self.total_distance = total_distance
        self.total_price = total_price
        self.total_time = total_time
        self.total_co2 = total_co2
        self.airlines = airlines

    def to_dict(self):
        return {
            "path": self.path,
            "distance": round(self.total_distance, 2),
            "price": round(self.total_price, 2),
            "time": round(self.total_time),
            "co2": round(self.total_co2, 2),
            "airlines": self.airlines
        }