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

# Helper function for drawing map
def generate_folium_map(route, data):
    """Helper function to draw the Folium map for a given route."""
    m = folium.Map(location=[20, 0], zoom_start=2)
    
    if not route:
        return m

    # --- Draw Markers ---
    for i in range(len(route)):
        airport_code = route[i]
        
        airport = data[airport_code]
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

    # --- Draw Lines ---
    for i in range(len(route)-1):
        code_origin = route[i]
        code_dest = route[i+1]
        

        o = data[code_origin]
        d = data[code_dest]
        
        lat1, lon1 = float(o["latitude"]), float(o["longitude"])
        lat2, lon2 = float(d["latitude"]), float(d["longitude"])
        folium.PolyLine([[lat1, lon1], [lat2, lon2]], color="blue", weight=4, opacity=0.7).add_to(m)

    return m

def build_route_summary(route, graph, weight_type=None, **kwargs):
    summary = {
        "segments": [],
        "total_distance": 0,
        "total_price": 0,
        "total_time": 0,
        "total_co2":0
    }

    # Loop through each flight segment
    for i in range(len(route) - 1):
        origin = route[i]
        destination = route[i + 1]

        # Get the list of all airlines flying this specific segment
        flights = graph.airports[origin].connections.get(destination, [])

        if not flights:
            continue  # Safety net in case of bad data

        chosen_flight = None

        # --- THE SMART SELECTOR ---
        # If the user optimized for distance, price, or time (Dijkstra),
        # re-scan the list and grab the exact flight that won the algorithm.
        if weight_type in ['distance', 'price', 'time','co2']:
            best_val = float('inf')
            for f in flights:
                if f[weight_type] < best_val:
                    best_val = f[weight_type]
                    chosen_flight = f
        # for 'balanced'
        elif weight_type == "balanced":
            best_val = float('inf')
            w_price = kwargs.get('weight_price', 0.25)
            w_time = kwargs.get('weight_time', 0.25)
            w_dist = kwargs.get('weight_distance', 0.25)
            w_co2 = kwargs.get('weight_co2', 0.25)

            for f in flights:
                score = (f['price'] * w_price) + (f['time'] * 2.0 * w_time) + (f['distance'] * 0.15 * w_dist) + (f['co2'] * 1.3 * w_co2)
                if score < best_val:
                    best_val = score
                    chosen_flight = f
        else:
            # If it's DFS or BFS (which don't care about weights), 
            # just grab the very first flight on the list to show on the UI.
            chosen_flight = flights[0]
        # --------------------------

        if chosen_flight:
            summary["segments"].append({
                "from": origin,
                "to": destination,
                "airline": chosen_flight["airline"],
                "distance": chosen_flight["distance"],
                "price": chosen_flight["price"],
                "time": chosen_flight["time"],
                "co2": chosen_flight["co2"]
            })

            summary["total_distance"] += chosen_flight["distance"]
            summary["total_price"] += chosen_flight["price"]
            summary["total_time"] += chosen_flight["time"]
            summary["total_co2"] += chosen_flight["co2"]

    # Round the final totals so they look pretty on your UI (e.g., $850.50 instead of $850.50000001)
    summary["total_price"] = round(summary["total_price"], 2)
    summary["total_distance"] = round(summary["total_distance"], 2)
    summary["total_time"] = round(summary["total_time"], 2)
    summary["total_co2"] = round(summary["total_co2"], 2)

    return summary

@app.route("/", methods=["GET", "POST"])
def index():
    selected_origin = None
    selected_destination = None
    route_preference = None
    route_info = None
    max_stops = 2
    all_routes = []
    avoid_airport = None
    summary = None 

    if request.method == "POST":
        selected_origin = request.form.get("origin")
        selected_destination = request.form.get("destination")
        route_preference = request.form.get("preference")
        max_stops = int(request.form.get("max_stops") or 2)
        avoid_airport = request.form.get("avoid_airport")

        # --- Normalize sliders
        raw_price = float(request.form.get("weight_price", 25))
        raw_time = float(request.form.get("weight_time", 25))
        raw_dist = float(request.form.get("weight_distance", 25))
        raw_co2 = float(request.form.get("weight_co2", 25))

        total_weight = raw_price + raw_time + raw_dist + raw_co2 

        if total_weight == 0:
            w_price, w_time, w_dist, w_co2 = 0.25, 0.25, 0.25, 0.25
        else:
            w_price = raw_price / total_weight
            w_time = raw_time / total_weight
            w_dist = raw_dist / total_weight
            w_co2 = raw_co2 / total_weight
        # -----------------------------------------------
        
        if selected_origin and selected_destination:
            if route_preference == "dfs":
                all_routes = find_routes(air_graph, selected_origin, selected_destination, max_stops, avoid_airport)
                route_info = f"Found {len(all_routes)} route(s) from {selected_origin} to {selected_destination} with max {max_stops} stops."
        
            elif route_preference in ["distance", "price", "time", "co2", "balanced"]:
                path, total = find_lowest_path(air_graph, selected_origin, selected_destination, weight_type=route_preference, 
                                               weight_price=w_price, weight_time=w_time, weight_distance=w_dist, weight_co2=w_co2)
                all_routes = [path] if path else []
                if path:
                    if route_preference == "distance":
                        route_info = f"Optimal route for distance: {total} km"
                    elif route_preference == "price":
                        route_info = f"Optimal route for price: ${total}"
                    elif route_preference == "time":
                        route_info = f"Optimal route for fastest time: {total} minutes"
                    elif route_preference == "co2":
                        route_info = f"Optimal route for lowest CO2: {total} kg"
                    elif route_preference == "balanced":
                        route_info = "Optimal balanced route found based on your preference"
                else:
                    route_info = "No route found."
        
            elif route_preference == "fewest_hops":
                path = find_fewest_layovers(air_graph, selected_origin, selected_destination, avoid_airport)
                all_routes = [path] if path else []
                route_info = "Route with fewest layovers found." if path else "No route found."

    if all_routes:
        route = all_routes[0]
        m = generate_folium_map(route, data) 
    else:
        m = folium.Map(location=[20, 0], zoom_start=2)
    
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
        all_routes=all_routes,
        summary=summary  
    )


@app.route("/update_map", methods=["POST"])
def update_map():
    selected_origin = request.form.get("origin")
    selected_destination = request.form.get("destination")
    max_stops = int(request.form.get("max_stops", 2))
    selected_route = int(request.form.get("route_index", 0))
    avoid_airport = request.form.get("avoid_airport")
    route_preference = request.form.get("preference") 

    # Slider math
    raw_price = float(request.form.get("weight_price", 25))
    raw_time = float(request.form.get("weight_time", 25))
    raw_dist = float(request.form.get("weight_distance", 25))
    raw_co2 = float(request.form.get("weight_co2", 25))
    total_weight = raw_price + raw_time + raw_dist + raw_co2

    if total_weight == 0:
        w_price, w_time, w_dist, w_co2 = 0.25, 0.25, 0.25, 0.25
    else:
        w_price = raw_price / total_weight
        w_time = raw_time / total_weight
        w_dist = raw_dist / total_weight
        w_co2 = raw_co2 / total_weight
    # -----------------------------------------

    all_routes = []

    if selected_origin and selected_destination:
        if route_preference == "dfs":
            all_routes = find_routes(air_graph, selected_origin, selected_destination, max_stops)
            if avoid_airport:
                all_routes = [r for r in all_routes if avoid_airport not in r]

        elif route_preference in ["distance", "price", "time", "co2", "balanced"]:
            path, total = find_lowest_path(air_graph, selected_origin, selected_destination, weight_type=route_preference,
                                           weight_price=w_price, weight_time=w_time,weight_distance=w_dist, weight_co2=w_co2)
            all_routes = [path] if path else []

        elif route_preference == "fewest_hops":
            path = find_fewest_layovers(air_graph, selected_origin, selected_destination, avoid_airport)
            all_routes = [path] if path else []

    if all_routes and 0 <= selected_route < len(all_routes):
        route = all_routes[selected_route]
        m = generate_folium_map(route, data)
        map_html = m._repr_html_()

        # Generates summary when path button is clicked
        summary = build_route_summary(route, air_graph, route_preference,
                                      weight_price=w_price, weight_time=w_time, weight_distance=w_dist, weight_co2=w_co2)

        return {"map_html": map_html, "summary": summary}

    return {"map_html": ""}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)