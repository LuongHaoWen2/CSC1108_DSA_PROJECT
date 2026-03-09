import json

with open("data/airline_routes.json") as f:
    data = json.load(f)

# adjacency list graph
graph = {
    airport: [
        {
            "to": route["iata"],
            "km": route.get("km"),
            "min": route.get("min")
        }
        for route in info.get("routes", [])
        if route["iata"] in data
    ]
    for airport, info in data.items()
}