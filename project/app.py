from flask import Flask, render_template_string
import folium

app = Flask(__name__)

@app.route("/")
def index():
    # Placeholder map
    m = folium.Map(location=[20, 0], zoom_start=2)
    map_html = m._repr_html_()

    # HTML template with two columns
    html = """
    <html>
    <head>
        <title>Airline Routes</title>
        <style>
            body { margin:0; font-family: Arial; }
            .container { display: flex; height: 100vh; }
            .map { flex: 2; }
            .controls { flex: 1; padding: 20px; background: #f2f2f2; overflow-y: auto; }
            label { display: block; margin-top: 15px; }
            select, input, button { width: 100%; padding: 8px; margin-top: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="map">
                {{ map_html|safe }}
            </div>
            <div class="controls">
                <h2>Flight Route Finder</h2>
                <label for="origin">Origin Airport:</label>
                <select id="origin">
                    <option value="">Select Origin</option>
                    <option value="JFK">JFK</option>
                    <option value="LHR">LHR</option>
                    <option value="SIN">SIN</option>
                </select>

                <label for="destination">Destination Airport:</label>
                <select id="destination">
                    <option value="">Select Destination</option>
                    <option value="JFK">JFK</option>
                    <option value="LHR">LHR</option>
                    <option value="SIN">SIN</option>
                </select>

                <label for="max_stops">Max Stops (optional):</label>
                <input type="number" id="max_stops" placeholder="e.g., 2">

                <button onclick="alert('Button clicked!')">Find Shortest Route</button>
            </div>
        </div>
    </body>
    </html>
    """

    return render_template_string(html, map_html=map_html)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)