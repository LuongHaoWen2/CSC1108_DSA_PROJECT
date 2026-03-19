from flask import Blueprint, jsonify, request
from algo import find_fewest_layovers, find_routes, find_lowest_path
# Assuming core/__init__.py allows this import:
from core import Route 

api_bp = Blueprint('api', __name__)

# --- Helper to get the graph from the main app ---
def get_graph():
    from app import graph
    return graph

# --- Helper to package the Dijkstra result into a full Route object ---
def package_route(path, weight_type, **kwargs):
    """
    Dijkstra only returns one total. This helper re-scans the path 
    to get the actual Distance, Price, Time, and CO2 for the UI receipt.
    """
    graph = get_graph()
    if not path:
        return None

    total_dist = 0
    total_price = 0
    total_time = 0
    total_co2 = 0
    airlines = []

    for i in range(len(path) - 1):
        u, v = path[i], path[i+1]
        flights = graph.airports[u].connections[v]
        
        # Pick the flight that Dijkstra actually chose
        best_f = None
        min_score = float('inf')
        
        for f in flights:
            if weight_type == 'balanced':
                # Use the same normalization math as Dijkstra
                wd = kwargs.get('weight_distance', 0.25)
                wp = kwargs.get('weight_price', 0.25)
                wt = kwargs.get('weight_time', 0.25)
                wc = kwargs.get('weight_co2', 0.25)
                score = (f['price']*wp) + (f['time']*2.0*wt) + (f['co2']*1.3*wc) + (f['distance']*0.15*wd)
            else:
                score = f.get(weight_type, f['distance'])
            
            if score < min_score:
                min_score = score
                best_f = f
        
        if best_f:
            total_dist += best_f['distance']
            total_price += best_f['price']
            total_time += best_f['time']
            total_co2 += best_f.get('co2', 0)
            airlines.append(best_f['airline'])

    # Return the teammate's Route object (which handles the rounding)
    return Route(path, total_dist, total_price, total_time, total_co2, airlines)

# --- Dijkstra Routes ---
@api_bp.route('/api/shortest', methods=['GET'])
def shortest_path():
    start = request.args.get('start', '').upper()
    end = request.args.get('end', '').upper()
    graph = get_graph()
    path, _ = find_lowest_path(graph, start, end, weight_type='distance')
    
    route_obj = package_route(path, 'distance')
    if not route_obj:
        return jsonify({"error": "No route found"}), 404
    return jsonify(route_obj.to_dict())

@api_bp.route('/api/cheapest', methods=['GET'])
def cheapest_path():
    start = request.args.get('start', '').upper()
    end = request.args.get('end', '').upper()
    graph = get_graph()
    path, _ = find_lowest_path(graph, start, end, weight_type='price')
    
    route_obj = package_route(path, 'price')
    if not route_obj:
        return jsonify({"error": "No route found"}), 404
    return jsonify(route_obj.to_dict())

@api_bp.route('/api/fastest', methods=['GET'])
def fastest_path():
    start = request.args.get('start', '').upper()
    end = request.args.get('end', '').upper()
    graph = get_graph()
    path, _ = find_lowest_path(graph, start, end, weight_type='time')
    
    route_obj = package_route(path, 'time')
    if not route_obj:
        return jsonify({"error": "No route found"}), 404
    return jsonify(route_obj.to_dict())

@api_bp.route('/api/greenest', methods=['GET'])
def greenest_path():
    """NEW: Optimized for CO2 Emissions"""
    start = request.args.get('start', '').upper()
    end = request.args.get('end', '').upper()
    graph = get_graph()
    path, _ = find_lowest_path(graph, start, end, weight_type='co2')
    
    route_obj = package_route(path, 'co2')
    if not route_obj:
        return jsonify({"error": "No route found"}), 404
    return jsonify(route_obj.to_dict())

@api_bp.route('/api/balanced', methods=['GET'])
def balanced_path():
    """NEW: Multi-Criteria Optimization"""
    start = request.args.get('start', '').upper()
    end = request.args.get('end', '').upper()
    
    # Grab slider values from URL parameters
    try:
        w_dist = float(request.args.get('w_dist', 25))
        w_price = float(request.args.get('w_price', 25))
        w_time = float(request.args.get('w_time', 25))
        w_co2 = float(request.args.get('w_co2', 25))
    except ValueError:
        return jsonify({"error": "Weights must be numbers"}), 400

    # Normalization
    total = w_dist + w_price + w_time + w_co2
    if total == 0:
        wd = wp = wt = wc = 0.25
    else:
        wd, wp, wt, wc = w_dist/total, w_price/total, w_time/total, w_co2/total

    graph = get_graph()
    path, _ = find_lowest_path(graph, start, end, weight_type='balanced',
                               weight_distance=wd, weight_price=wp, 
                               weight_time=wt, weight_co2=wc)

    route_obj = package_route(path, 'balanced', weight_distance=wd, weight_price=wp, 
                              weight_time=wt, weight_co2=wc)
    
    if not route_obj:
        return jsonify({"error": "No route found"}), 404
    return jsonify(route_obj.to_dict())

# -------- BFS Routes --------
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