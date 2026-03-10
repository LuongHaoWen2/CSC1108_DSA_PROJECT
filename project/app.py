from flask import Flask, render_template, request
import folium
import json
from graph import graph        # graph adjacency list
from algo.dfs import find_routes    # DFS function

app = Flask(__name__)

# Load dataset
with open("data/airline_routes.json") as f:
    data = json.load(f)

# List of all airports for dropdowns
all_airports = [(code, info["display_name"]) for code, info in data.items()]

@app.route("/", methods=["GET", "POST"])
def index():
    selected_origin = None
    selected_destination = None
    route_preference = None
    route_info = None
    max_stops = 2
    all_routes = []

    if request.method == "POST":
        selected_origin = request.form.get("origin")
        selected_destination = request.form.get("destination")
        route_preference = request.form.get("preference")
        max_stops = int(request.form.get("max_stops") or 2)

        # Call Depth First Search to find all routes up to max_stops
        if selected_origin and selected_destination:
            all_routes = find_routes(graph, selected_origin, selected_destination, max_stops)
            if all_routes:
                route_info = f"Found {len(all_routes)} route(s) from {selected_origin} to {selected_destination} with max {max_stops} stops."
            else:
                route_info = f"No routes found from {selected_origin} to {selected_destination} with max {max_stops} stops."

    # Folium map
    m = folium.Map(location=[20, 0], zoom_start=2)

    # Show first route on map (default)
    if all_routes:
        route = all_routes[0]  # display first route
        # Add markers with stop order
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
                # Stop number starts at 1 for first transfer
                stop_number = i  # i=1 is first transfer
                popup_text = f"{airport['display_name']} (Stop {stop_number})"

            folium.Marker(
                [lat, lon],
                popup=popup_text,
                icon=folium.Icon(color=color)
            ).add_to(m)

        # Draw lines between airports
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

    # Generate all routes using DFS
    all_routes = find_routes(graph, selected_origin, selected_destination, max_stops)

    if all_routes and 0 <= selected_route < len(all_routes):
        route = all_routes[selected_route]

        # Create map for this route
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
                # Stop number starts at 1 for first transfer
                stop_number = i  # i=1 is first transfer
                popup_text = f"{airport['display_name']} (Stop {stop_number})"

            folium.Marker(
                [lat, lon],
                popup=popup_text,
                icon=folium.Icon(color=color)
            ).add_to(m)

        # Draw lines between airports
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