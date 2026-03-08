from flask import Flask, render_template_string
import folium

app = Flask(__name__)

@app.route("/")
def index():
    # Create a basic Folium map
    m = folium.Map(location=[20, 0], zoom_start=2)

    # Example markers
    folium.Marker([51.5074, -0.1278], popup="London").add_to(m)
    folium.Marker([40.7128, -74.0060], popup="New York").add_to(m)
    folium.Marker([-33.8688, 151.2093], popup="Sydney").add_to(m)

    # Render map as HTML
    map_html = m._repr_html_()

    # HTML template with 2-column layout
    html_template = """
    <html>
    <head>
        <title>Airline Map</title>
        <style>
            body { margin:0; padding:0; font-family: Arial, sans-serif; }
            .container {
                display: flex;
                height: 100vh;
            }
            .map {
                flex: 2; /* left column (map) takes 2/3 width */
            }
            .controls {
                flex: 1; /* right column takes 1/3 width */
                padding: 20px;
                box-sizing: border-box;
                background-color: #f2f2f2;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="map">
                {{ map_html|safe }}
            </div>
            <div class="controls">
                <h2>Controls</h2>
                <label for="country">Select Country:</label>
                <select id="country">
                    <option value="UK">United Kingdom</option>
                    <option value="US">United States</option>
                    <option value="AU">Australia</option>
                </select>
                <br><br>
                <button onclick="alert('Button clicked!')">Do Something</button>
            </div>
        </div>
    </body>
    </html>
    """

    return render_template_string(html_template, map_html=map_html)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)