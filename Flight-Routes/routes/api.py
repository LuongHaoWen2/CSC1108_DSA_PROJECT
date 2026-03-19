from flask import Blueprint, jsonify, request
from algo import find_fewest_layovers, find_routes, find_lowest_path

api_bp = Blueprint('api', __name__)

# --- Helper ---
def get_graph():
    from app import graph
    return graph

# --- Dijkstra routes ---

@api_bp.route('/api/shortest', methods=['GET'])
def shortest_path():
    """Shortest Distance Between Two Airports"""
    start = request.args.get('start', '').upper()
    end = request.args.get('end', '').upper()

    if not start or not end:
        return jsonify({"error": "start and end are required"}) , 400

    graph = get_graph()
    path, total = find_lowest_path(graph, start, end, weight_type = 'distance')

    if path is None:
        return jsonify({"error": f"No route found from {start} to {end}"}) , 404

    return jsonify({"path": path, "total_distance": total})

@api_bp.route('/api/cheapest', methods=['GET'])
def cheapest_path():
    """ Cheapest Price Between Two Airports"""
    start = request.args.get('start', '').upper()
    end = request.args.get('end', '').upper()

    if not start or not end:
        return jsonify({"error": "start and end are required"}) , 400

    graph = get_graph()
    path, total = find_lowest_path(graph, start, end, weight_type = 'price')

    if path is None:
        return jsonify({"error": f"No route found from {start} to {end}"}) , 404

    return jsonify({"path": path, "total_price": total})

@api_bp.route('/api/fastest', methods=['GET'])
def fastest_path():
    """ Fastest time between Two Airports"""
    start = request.args.get('start', '').upper()
    end = request.args.get('end', '').upper()

    if not start or not end:
        return jsonify({"error": "start and end are required"}), 400

    graph = get_graph()
    path, total = find_lowest_path(graph, start, end, weight_type='time')

    if path is None:
        return jsonify({"error": f"No route found from {start} to {end}"}), 404

    return jsonify({"path": path, "total_time": total})

# -------- BFS Route --------
@api_bp.route('/api/fewest-layovers', methods=['GET'])
def fewest_layovers():
    """ Fewest Layovers between Two Airports"""
    start = request.args.get('start', '').upper()
    end = request.args.get('end', '').upper()
    avoid_airport = request.args.get('avoid', None)

    if avoid_airport:
        avoid_airport = avoid_airport.upper()

    if not start or not end:
        return jsonify({"error": "start and end are required"}) , 400

    graph = get_graph()
    path = find_fewest_layovers(graph, start, end, avoid_airport=avoid_airport)

    if path is None:
        return jsonify({"error": f"No route found from {start} to {end}"}), 404

    return jsonify({"path": path, "stops": len(path) - 2})

# -------- DFS Route --------
@api_bp.route('/api/all-routes', methods=['GET'])
def all_routes():
    """ All Possible Routes up to Max Stops"""
    start = request.args.get('start', '').upper()
    end = request.args.get('end', '').upper()
    max_stops = request.args.get('max_stops', 3)
    avoid_airport = request.args.get('avoid', None)

    if avoid_airport:
        avoid_airport = avoid_airport.upper()

    try:
        max_stops = int(max_stops)
    except ValueError:
        return jsonify({"error": f"Max stops must be an integer"}) , 400

    graph = get_graph()
    routes = find_routes(graph, start, end, max_stops, avoid_airport=avoid_airport)

    if not routes:
        return jsonify({"error": f"No route found from {start} to {end}"}) , 404

    return jsonify({"routes": routes})

# ---- Airport Info ----
@api_bp.route('/api/airports', methods=['GET'])
def airports():
    """ List all airports code"""
    graph = get_graph()
    return jsonify({"airports": graph.get_all_codes()})

@api_bp.route('/api/airports/<code>', methods=['GET'])
def airport_info(code):
    """ Specific airport info"""
    graph = get_graph()
    airport = graph.get_airport(code.upper())

    if airport is None:
        return jsonify({"error": f"No airport found from {code}"}) , 404

    return jsonify({
        "code": airport.code,
        "name": airport.name,
        "latitude": airport.latitude,
        "longitude": airport.longitude,
        "connections": list(airport.connections.keys())
    })