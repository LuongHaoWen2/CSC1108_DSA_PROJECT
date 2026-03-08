from flask import Flask, render_template, request
import folium
import json

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

    if request.method == "POST":
        selected_origin = request.form.get("origin")
        selected_destination = request.form.get("destination")
        route_preference = request.form.get("preference")
        if selected_origin and selected_destination:
            route_info = f"Selected route from {selected_origin} to {selected_destination} with preference '{route_preference}'."

    # Folium map
    m = folium.Map(location=[20, 0], zoom_start=2)

    # Add markers and line if both origin and destination are selected
    if selected_origin and selected_destination:
        try:
            origin_airport = data[selected_origin]
            dest_airport = data[selected_destination]

            lat1, lon1 = float(origin_airport["latitude"]), float(origin_airport["longitude"])
            lat2, lon2 = float(dest_airport["latitude"]), float(dest_airport["longitude"])

            # Markers
            folium.Marker([lat1, lon1], popup=origin_airport["display_name"], icon=folium.Icon(color='green')).add_to(m)
            folium.Marker([lat2, lon2], popup=dest_airport["display_name"], icon=folium.Icon(color='red')).add_to(m)

            # Line connecting origin and destination
            folium.PolyLine(
                locations=[[lat1, lon1], [lat2, lon2]],
                color="blue",
                weight=4,
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
        route_preference=route_preference,
        route_info=route_info
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)