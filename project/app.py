from flask import Flask, render_template_string, request
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

    # Add markers and route line only if both selected and valid
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

    # HTML template (same layout as before)
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Flight Route Finder</title>
        <style>
            body { margin:0; font-family: Arial, sans-serif; }
            .container { display: flex; height: 100vh; }
            .map { flex: 2; }
            .controls { flex: 1; padding: 20px; background: #f2f2f2; overflow-y: auto; }
            label { display: block; margin-top: 15px; font-weight: bold; }
            select, input, button { width: 100%; padding: 8px; margin-top: 5px; }
            h2 { margin-top: 0; }
            .results { margin-top: 20px; background: #fff; padding: 10px; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="map">
                {{ map_html|safe }}
            </div>
            <div class="controls">
                <h2>Flight Route Finder</h2>
                <form method="POST">
                    <label for="origin">Origin Airport:</label>
                    <select name="origin" onchange="this.form.submit()">
                        <option value="">Select Origin</option>
                        {% for code, name in all_airports %}
                            <option value="{{ code }}" {% if code == selected_origin %}selected{% endif %}>{{ name }}</option>
                        {% endfor %}
                    </select>

                    <label for="destination">Destination Airport:</label>
                    <select name="destination">
                        <option value="">Select Destination</option>
                        {% for code, name in destination_options %}
                            <option value="{{ code }}" {% if code == selected_destination %}selected{% endif %}>{{ name }}</option>
                        {% endfor %}
                    </select>

                    <label for="preference">Route Preference:</label>
                    <select name="preference">
                        <option value="shortest" {% if route_preference=="shortest" %}selected{% endif %}>Shortest Distance</option>
                        <option value="cheapest" {% if route_preference=="cheapest" %}selected{% endif %}>Lowest Price</option>
                        <option value="fewest" {% if route_preference=="fewest" %}selected{% endif %}>Fewest Stops</option>
                        <option value="cost-effective" {% if route_preference=="cost-effective" %}selected{% endif %}>Most Cost-Effective</option>
                    </select>

                    <label for="max_stops">Max Stops (optional):</label>
                    <input type="number" name="max_stops" placeholder="e.g., 2">

                    <button type="submit">Find Route</button>
                </form>

                {% if route_info %}
                    <div class="results">
                        <h3>Route Info:</h3>
                        <p>{{ route_info }}</p>
                    </div>
                {% endif %}
            </div>
        </div>
    </body>
    </html>
    """

    return render_template_string(html_template,
                                  map_html=map_html,
                                  all_airports=all_airports,
                                  selected_origin=selected_origin,
                                  selected_destination=selected_destination,
                                  destination_options=destination_options,
                                  route_preference=route_preference,
                                  route_info=route_info)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)