from flask import Flask, render_template, request
import folium
import json

app = Flask(__name__)

# Load dataset
with open("data/airline_routes.json") as f:
    data = json.load(f)

# List of all airports
all_airports = [(code, info["display_name"]) for code, info in data.items()]

@app.route("/", methods=["GET", "POST"])
def index():
    selected_origin = None
    selected_destination = None
    route_preference = None
    route_info = None
    destination_options = []

    if request.method == "POST":
        selected_origin = request.form.get("origin")
        selected_destination = request.form.get("destination")
        route_preference = request.form.get("preference")

        # Dataset-aware destination list
        if selected_origin:
            destination_codes = [route["iata"] for route in data[selected_origin].get("routes", [])]
            destination_options = [(code, data[code]["display_name"]) for code in destination_codes if code in data]

        # Only allow route info if destination is in reachable routes
        if selected_origin and selected_destination and selected_destination in [c for c, _ in destination_options]:
            route_info = f"Route from {selected_origin} to {selected_destination} using '{route_preference}' preference."

    # Folium map
    m = folium.Map(location=[20, 0], zoom_start=2)
    if selected_origin and selected_destination and selected_destination in [c for c, _ in destination_options]:
        o = data[selected_origin]
        d = data[selected_destination]
        try:
            lat1, lon1 = float(o["latitude"]), float(o["longitude"])
            lat2, lon2 = float(d["latitude"]), float(d["longitude"])
            folium.Marker([lat1, lon1], popup=o["display_name"]).add_to(m)
            folium.Marker([lat2, lon2], popup=d["display_name"]).add_to(m)
            folium.PolyLine(
                locations=[[lat1, lon1], [lat2, lon2]],
                color="blue" if route_preference=="shortest" else "green",
                weight=5,
                opacity=0.7
            ).add_to(m)
        except (ValueError, TypeError):
            pass

    map_html = m._repr_html_()

    return render_template(
        "index.html",
        map_html=map_html,
        all_airports=all_airports,
        selected_origin=selected_origin,
        selected_destination=selected_destination,
        destination_options=destination_options,
        route_preference=route_preference,
        route_info=route_info
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)