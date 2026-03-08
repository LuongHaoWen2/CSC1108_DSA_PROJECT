from flask import Flask, render_template_string
import folium

app = Flask(__name__)

@app.route("/")
def world_map():
    # Create a Folium map centered at [0, 0] with zoom level 2
    m = folium.Map(location=[0, 0], zoom_start=2)

    # Add some example markers
    folium.Marker([51.5074, -0.1278], popup="London").add_to(m)
    folium.Marker([40.7128, -74.0060], popup="New York").add_to(m)
    folium.Marker([-33.8688, 151.2093], popup="Sydney").add_to(m)

    # Render map as HTML
    map_html = m._repr_html_()

    # Render in Flask
    return render_template_string("""
        <html>
            <head><title>Interactive World Map</title></head>
            <body>
                <h1>Interactive World Map Example</h1>
                {{ map_html|safe }}
            </body>
        </html>
    """, map_html=map_html)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)