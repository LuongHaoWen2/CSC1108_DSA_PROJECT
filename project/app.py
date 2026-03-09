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

        # Call DFS to find all routes up to max_stops
        if selected_origin and selected_destination:
            all_routes = find_routes(graph, selected_origin, selected_destination, max_stops)
            if all_routes:
                route_info = f"Found {len(all_routes)} route(s) from {selected_origin} to {selected_destination} with max {max_stops} stops."
            else:
                route_info = f"No routes found from {selected_origin} to {selected_destination} with max {max_stops} stops."

    # Folium map
    m = folium.Map(location=[20, 0], zoom_start=2)

    # Show first route on map for testing
    if all_routes:
        route = all_routes[0]  # display only the first route
        for i in range(len(route)-1):
            o = data[route[i]]
            d = data[route[i+1]]
            lat1, lon1 = float(o["latitude"]), float(o["longitude"])
            lat2, lon2 = float(d["latitude"]), float(d["longitude"])

            # Markers
            folium.Marker([lat1, lon1], popup=o["display_name"], icon=folium.Icon(color='green')).add_to(m)
            folium.Marker([lat2, lon2], popup=d["display_name"], icon=folium.Icon(color='red')).add_to(m)

            # Line connecting airports
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
        all_routes=all_routes  # pass routes to template
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)