from flask import Flask, render_template, request, jsonify
from core.graph import FlightGraph, load_flight_data
from routes import api_bp
from config import HOST, PORT, DEBUG, DATA_PATH

# --- Init App ---
app = Flask(__name__)

# --- Load graph once at startup ---
graph = FlightGraph()
load_flight_data(graph, DATA_PATH)

# --- Register Blueprint
app.register_blueprint(api_bp)

# --- Root Route ---
@app.route("/", methods=["GET", "POST"])
def index():
    all_airports = sorted([
        (code, node.name)
        for code, node in graph.airports.items()
    ], key=lambda x: x[1])

    return render_template("index.html",
                           all_airports=all_airports,
                           selected_origin="",
                           selected_destination="",
                           route_preference="distance",
                           max_stops=3,
                           route_info=None,
                           all_routes=None)

if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=DEBUG)
