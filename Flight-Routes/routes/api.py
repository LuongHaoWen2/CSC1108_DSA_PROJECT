from flask import Blueprint, jsonify, request
from algo import find_fewest_layovers, find_routes, find_lowest_path, find_lowest_path_astar
# Assuming core/__init__.py allows this import:
from core import Route 

api_bp = Blueprint('api', __name__)

# --- Helper to get the graph from the main app ---
def get_graph():
    from app import graph
    return graph
# --- Helper to parse common filters ---
def get_common_filters():
    """
    Parse and normalize shared API filters from query params.
    Basically all the filters on the webpage will be gathered here for parsing around the different endpoints
    Returns (filters_dict, error_response_or_None)
    """
    start = request.args.get('start', '').upper().strip()
    end = request.args.get('end', '').upper().strip()
    avoid_airport = request.args.get('avoid', '').upper().strip() or None
    airline = request.args.get('airline', '').strip() or None
    
    if not start or not end:
        return None, (jsonify({"error": "start and end are required"}), 400)

    # Always parse max_stops for consistency and future-proofing
    raw_max = request.args.get('max_stops', 3)
    try:
        max_stops = int(raw_max)
    except ValueError:
        return None, (jsonify({"error": "Max stops must be an integer"}), 400)

    filters = {
        "start": start,
        "end": end,
        "avoid_airport": avoid_airport,
        "airline": airline,
        "max_stops": max_stops,
    }

    return filters, None

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
    selected_airline = kwargs.get('airline', None)

    for i in range(len(path) - 1):
        u, v = path[i], path[i+1]
        flights = graph.airports[u].connections[v]

        if selected_airline:
            flights = [
                f for f in flights
                if f.get('airline', '').lower() == selected_airline.lower()
            ]

        if not flights:
            continue
        
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


def build_route_summary(path, weight_type=None, **kwargs):
    """
    Build a segment-by-segment route receipt similar to the original project app.
    """
    graph = get_graph()
    if not path or len(path) < 2:
        return None

    summary = {
        "path": path,
        "segments": [],
        "total_distance": 0,
        "total_price": 0,
        "total_time": 0,
        "total_co2": 0,
    }
    selected_airline = kwargs.get("airline", None)

    for i in range(len(path) - 1):
        origin = path[i]
        destination = path[i + 1]
        flights = graph.airports.get(origin, None)

        if not flights:
            continue

        flights = flights.connections.get(destination, [])

        if selected_airline:
            flights = [
                f for f in flights
                if f.get("airline", "").lower() == selected_airline.lower()
            ]

        if not flights:
            continue

        chosen_flight = None

        if weight_type in ["distance", "price", "time", "co2"]:
            chosen_flight = min(flights, key=lambda f: f.get(weight_type, float("inf")))
        elif weight_type == "balanced":
            wd = kwargs.get("weight_distance", 0.25)
            wp = kwargs.get("weight_price", 0.25)
            wt = kwargs.get("weight_time", 0.25)
            wc = kwargs.get("weight_co2", 0.25)

            chosen_flight = min(
                flights,
                key=lambda f: (
                    (f["price"] * wp)
                    + (f["time"] * 2.0 * wt)
                    + (f["distance"] * 0.15 * wd)
                    + (f["co2"] * 1.3 * wc)
                ),
            )
        else:
            # DFS/BFS: show the first available carrier for display purposes.
            chosen_flight = flights[0]

        summary["segments"].append({
            "from": origin,
            "to": destination,
            "airline": chosen_flight["airline"],
            "distance": chosen_flight["distance"],
            "price": chosen_flight["price"],
            "time": chosen_flight["time"],
            "co2": chosen_flight["co2"],
        })

        summary["total_distance"] += chosen_flight["distance"]
        summary["total_price"] += chosen_flight["price"]
        summary["total_time"] += chosen_flight["time"]
        summary["total_co2"] += chosen_flight["co2"]

    summary["total_distance"] = round(summary["total_distance"], 2)
    summary["total_price"] = round(summary["total_price"], 2)
    summary["total_time"] = round(summary["total_time"], 2)
    summary["total_co2"] = round(summary["total_co2"], 2)
    return summary

# --- Dijkstra Routes ---
@api_bp.route('/api/shortest', methods=['GET'])
def shortest_path():
    params, err = get_common_filters()
    if err:
        return err

    graph = get_graph()
    path, _ = find_lowest_path(
        graph,
        params["start"],
        params["end"],
        weight_type='distance',
        airline=params["airline"],
    )
    
    route_obj = package_route(path, 'distance', airline=params["airline"])
    if not route_obj:
        return jsonify({"error": "No route found"}), 404
    return jsonify({
        "route": route_obj.to_dict(),
        "summary": build_route_summary(path, "distance", airline=params["airline"]),
    })

@api_bp.route('/api/cheapest', methods=['GET'])
def cheapest_path():
    params, err = get_common_filters()
    if err:
        return err

    graph = get_graph()
    path, _ = find_lowest_path(
        graph,
        params["start"],
        params["end"],
        weight_type='price',
        airline=params["airline"],
    )
    
    route_obj = package_route(path, 'price', airline=params["airline"])
    if not route_obj:
        return jsonify({"error": "No route found"}), 404
    return jsonify({
        "route": route_obj.to_dict(),
        "summary": build_route_summary(path, "price", airline=params["airline"]),
    })

@api_bp.route('/api/fastest', methods=['GET'])
def fastest_path():
    params, err = get_common_filters()
    if err:
        return err

    graph = get_graph()
    path, _ = find_lowest_path(
        graph,
        params["start"],
        params["end"],
        weight_type='time',
        airline=params["airline"],
    )
    
    route_obj = package_route(path, 'time', airline=params["airline"])
    if not route_obj:
        return jsonify({"error": "No route found"}), 404
    return jsonify({
        "route": route_obj.to_dict(),
        "summary": build_route_summary(path, "time", airline=params["airline"]),
    })

@api_bp.route('/api/greenest', methods=['GET'])
def greenest_path():
    """NEW: Optimized for CO2 Emissions"""
    params, err = get_common_filters()
    if err:
        return err

    graph = get_graph()
    path, _ = find_lowest_path(
        graph,
        params["start"],
        params["end"],
        weight_type='co2',
        airline=params["airline"],
    )
    
    route_obj = package_route(path, 'co2', airline=params["airline"])
    if not route_obj:
        return jsonify({"error": "No route found"}), 404
    return jsonify({
        "route": route_obj.to_dict(),
        "summary": build_route_summary(path, "co2", airline=params["airline"]),
    })

@api_bp.route('/api/balanced', methods=['GET'])
def balanced_path():
    """NEW: Multi-Criteria Optimization"""
    params, err = get_common_filters()
    if err:
        return err
    
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
    path, _ = find_lowest_path(graph, params["start"], params["end"], weight_type='balanced',
                               weight_distance=wd, weight_price=wp,
                               weight_time=wt, weight_co2=wc,
                               airline=params["airline"])

    route_obj = package_route(path, 'balanced', weight_distance=wd, weight_price=wp,
                              weight_time=wt, weight_co2=wc, airline=params["airline"])
    
    if not route_obj:
        return jsonify({"error": "No route found"}), 404
    return jsonify({
        "route": route_obj.to_dict(),
        "summary": build_route_summary(
            path,
            "balanced",
            weight_distance=wd,
            weight_price=wp,
            weight_time=wt,
            weight_co2=wc,
            airline=params["airline"],
        ),
    })

# -------- A* Routes --------
@api_bp.route('/api/astar-shortest', methods=['GET'])
def astar_shortest_path():
    params, err = get_common_filters()
    if err:
        return err

    graph = get_graph()
    path, _ = find_lowest_path_astar(
        graph,
        params["start"],
        params["end"],
        weight_type='distance',
        airline=params["airline"],
    )
    
    route_obj = package_route(path, 'distance', airline=params["airline"])
    if not route_obj:
        return jsonify({"error": "No route found"}), 404
    return jsonify({
        "route": route_obj.to_dict(),
        "summary": build_route_summary(path, "distance", airline=params["airline"]),
    })

@api_bp.route('/api/astar-cheapest', methods=['GET'])
def astar_cheapest_path():
    params, err = get_common_filters()
    if err:
        return err

    graph = get_graph()
    path, _ = find_lowest_path_astar(
        graph,
        params["start"],
        params["end"],
        weight_type='price',
        airline=params["airline"],
    )
    
    route_obj = package_route(path, 'price', airline=params["airline"])
    if not route_obj:
        return jsonify({"error": "No route found"}), 404
    return jsonify({
        "route": route_obj.to_dict(),
        "summary": build_route_summary(path, "price", airline=params["airline"]),
    })

@api_bp.route('/api/astar-fastest', methods=['GET'])
def astar_fastest_path():
    params, err = get_common_filters()
    if err:
        return err

    graph = get_graph()
    path, _ = find_lowest_path_astar(
        graph,
        params["start"],
        params["end"],
        weight_type='time',
        airline=params["airline"],
    )
    
    route_obj = package_route(path, 'time', airline=params["airline"])
    if not route_obj:
        return jsonify({"error": "No route found"}), 404
    return jsonify({
        "route": route_obj.to_dict(),
        "summary": build_route_summary(path, "time", airline=params["airline"]),
    })

@api_bp.route('/api/astar-greenest', methods=['GET'])
def astar_greenest_path():
    """A* Optimized for CO2 Emissions"""
    params, err = get_common_filters()
    if err:
        return err

    graph = get_graph()
    path, _ = find_lowest_path_astar(
        graph,
        params["start"],
        params["end"],
        weight_type='co2',
        airline=params["airline"],
    )
    
    route_obj = package_route(path, 'co2', airline=params["airline"])
    if not route_obj:
        return jsonify({"error": "No route found"}), 404
    return jsonify({
        "route": route_obj.to_dict(),
        "summary": build_route_summary(path, "co2", airline=params["airline"]),
    })

@api_bp.route('/api/astar-balanced', methods=['GET'])
def astar_balanced_path():
    """A* Multi-Criteria Optimization"""
    params, err = get_common_filters()
    if err:
        return err
    
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
    path, _ = find_lowest_path_astar(graph, params["start"], params["end"], weight_type='balanced',
                               weight_distance=wd, weight_price=wp,
                               weight_time=wt, weight_co2=wc,
                               airline=params["airline"])

    route_obj = package_route(path, 'balanced', weight_distance=wd, weight_price=wp,
                              weight_time=wt, weight_co2=wc, airline=params["airline"])
    
    if not route_obj:
        return jsonify({"error": "No route found"}), 404
    return jsonify({
        "route": route_obj.to_dict(),
        "summary": build_route_summary(
            path,
            "balanced",
            weight_distance=wd,
            weight_price=wp,
            weight_time=wt,
            weight_co2=wc,
            airline=params["airline"],
        ),
    })

# -------- BFS Routes --------
@api_bp.route('/api/fewest-layovers', methods=['GET'])
def fewest_layovers():
    """ Fewest Layovers between Two Airports"""
    params, err = get_common_filters()
    if err:
        return err

    graph = get_graph()
    path = find_fewest_layovers(
        graph,
        params["start"],
        params["end"],
        avoid_airport=params["avoid_airport"],
        max_stops=params["max_stops"],
        airline=params["airline"],
    )

    if path is None:
        return jsonify({"error": f"No route found from {params['start']} to {params['end']}"}), 404

    return jsonify({
        "path": path,
        "stops": len(path) - 2,
        "summary": build_route_summary(path, airline=params["airline"]),
    })


# -------- DFS Route --------
@api_bp.route('/api/all-routes', methods=['GET'])
def all_routes():
    """ All Possible Routes up to Max Stops"""
    params, err = get_common_filters()
    if err:
        return err

    graph = get_graph()
    routes = find_routes(
        graph,
        params["start"],
        params["end"],
        params["max_stops"],
        avoid_airport=params["avoid_airport"],
        airline=params["airline"],
    )

    if not routes:
        return jsonify({"error": f"No route found from {params['start']} to {params['end']}"}) , 404

    return jsonify({
        "routes": routes,
        "summaries": [build_route_summary(path, airline=params["airline"]) for path in routes],
        "total_found": len(routes),
    })
# ---- Airline List ----
@api_bp.route('/api/airlines', methods=['GET'])
def airlines():
    graph = get_graph()
    names = set()

    for airport in graph.airports.values():
        for flights in airport.connections.values():
            for f in flights:
                names.add(f.get("airline", "Unknown Airline"))

    return jsonify({"airlines": sorted(names)})
# ---- Airport Info ----
@api_bp.route('/api/airports', methods=['GET'])
def airports():
    """ List all airports code"""
    graph = get_graph()
    airports = [
        {
            "code": code,
            "name": airport.name,
            "country_code": airport.country_code,
            "label": f"{airport.name} ({code}) - {airport.country_code}" if airport.country_code else f"{airport.name} ({code})",
        }
        for code, airport in graph.airports.items()
    ]
    airports.sort(key=lambda a: a["label"])
    return jsonify({"airports": airports})

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
        "country_code": airport.country_code,
        "latitude": airport.latitude,
        "longitude": airport.longitude,
        "connections": list(airport.connections.keys())
    })