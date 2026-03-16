from flask import Flask, render_template, request
import folium
import json

from graphalgo import FlightGraph, load_flight_data
from algo.dfs import find_routes    # DFS function
from algo.dijkstra import find_lowest_path # Dijkstra function
from algo.bfs import find_fewest_layovers # BFS function

app = Flask(__name__)

# Load dataset
with open("data/airline_routes.json") as f:
    data = json.load(f)

# Initialize FlightGraph and load data into it
air_graph = FlightGraph()
load_flight_data(air_graph, "data/airline_routes.json")

# List of all airports for dropdowns (sorted by display_name)
all_airports = sorted(
    [(code, info["display_name"]) for code, info in data.items()],
    key=lambda x: x[1]  # sort alphabetically by airport name
)

@app.route("/", methods=["GET", "POST"])
def index():
    selected_origin = None
    selected_destination = None
    route_preference = None
    route_info = None
    max_stops = 2
    all_routes = []
    avoid_airport=None

    if request.method == "POST":
        selected_origin = request.form.get("origin")
        selected_destination = request.form.get("destination")
        route_preference = request.form.get("preference")
        max_stops = int(request.form.get("max_stops") or 2)
        avoid_airport = request.form.get("avoid_airport")

        # Call DFS to find all routes up to max_stops
        if selected_origin and selected_destination:
            if route_preference == "dfs":
                all_routes = find_routes(air_graph, selected_origin, selected_destination, max_stops, avoid_airport)
                route_info = f"Found {len(all_routes)} route(s) from {selected_origin} to {selected_destination} with max {max_stops} stops."
        
        # Call Dijkstra Algorithm to find the single optimal route
        # weight_type decides what the algorithm optimizes for
        # "distance", "price", "time"
            elif route_preference in ["distance", "price", "time"]:
                path, total = find_lowest_path(air_graph, selected_origin, selected_destination, weight_type=route_preference)
                all_routes = [path] if path else []
                if path:
                    if route_preference == "distance":
                        route_info = f"Optimal route for distance: {total} km"
                    elif route_preference == "price":
                        route_info = f"Optimal route for price: ${total}"
                    elif route_preference == "time":
                        route_info = f"Optimal route for fastest time: {total} minutes"
                else:
                    route_info = "No route found."
        
        # Call BFS to find the route with the fewest connections/layovers
            elif route_preference == "fewest_hops":
                path = find_fewest_layovers(air_graph, selected_origin, selected_destination, avoid_airport)
                all_routes = [path] if path else []
                route_info = f"Route with fewest layovers found." if path else "No route found."

      
        

    # Folium map
    m = folium.Map(location=[20, 0], zoom_start=2)

    # Show first route on map (default)
    if all_routes:
        route = all_routes[0]
        for i in range(len(route)):
            airport = data[route[i]]
            lat, lon = float(airport["latitude"]), float(airport["longitude"])

            if i == 0:
                color = "green"
                popup_text = f"{airport['display_name']} (Origin)"
            elif i == len(route) - 1:
                color = "red"
                popup_text = f"{airport['display_name']} (Destination)"
            else:
                color = "blue"
                stop_number = i
                popup_text = f"{airport['display_name']} (Stop {stop_number})"

            folium.Marker(
                [lat, lon],
                popup=popup_text,
                icon=folium.Icon(color=color)
            ).add_to(m)

        for i in range(len(route)-1):
            o = data[route[i]]
            d = data[route[i+1]]
            lat1, lon1 = float(o["latitude"]), float(o["longitude"])
            lat2, lon2 = float(d["latitude"]), float(d["longitude"])
            folium.PolyLine([[lat1, lon1], [lat2, lon2]], color="blue", weight=4, opacity=0.7).add_to(m)

    map_html = m._repr_html_()

    return render_template(
        "index.html",
        map_html=map_html,
        all_airports=all_airports,
        selected_origin=selected_origin,
        selected_destination=selected_destination,
        route_preference=route_preference,
        route_info=route_info,
        max_stops=max_stops,
        all_routes=all_routes
    )

@app.route("/update_map", methods=["POST"])
def update_map():
    selected_origin = request.form.get("origin")
    selected_destination = request.form.get("destination")
    max_stops = int(request.form.get("max_stops", 2))
    selected_route = int(request.form.get("route_index", 0))
    avoid_airport = request.form.get("avoid_airport")

    all_routes = find_routes(air_graph, selected_origin, selected_destination, max_stops)
    if avoid_airport:
        all_routes = [r for r in all_routes if avoid_airport not in r]

    if all_routes and 0 <= selected_route < len(all_routes):
        route = all_routes[selected_route]
        m = folium.Map(location=[20, 0], zoom_start=2)

        for i in range(len(route)):
            airport = data[route[i]]
            lat, lon = float(airport["latitude"]), float(airport["longitude"])

            if i == 0:
                color = "green"
                popup_text = f"{airport['display_name']} (Origin)"
            elif i == len(route) - 1:
                color = "red"
                popup_text = f"{airport['display_name']} (Destination)"
            else:
                color = "blue"
                stop_number = i
                popup_text = f"{airport['display_name']} (Stop {stop_number})"

            folium.Marker(
                [lat, lon],
                popup=popup_text,
                icon=folium.Icon(color=color)
            ).add_to(m)

        for i in range(len(route)-1):
            o = data[route[i]]
            d = data[route[i+1]]
            lat1, lon1 = float(o["latitude"]), float(o["longitude"])
            lat2, lon2 = float(d["latitude"]), float(d["longitude"])
            folium.PolyLine([[lat1, lon1], [lat2, lon2]], color="blue", weight=4, opacity=0.7).add_to(m)

        map_html = m._repr_html_()
        return {"map_html": map_html}

    return {"map_html": ""}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)