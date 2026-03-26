# Flight Routes - Intelligent Route Finder

A web-based flight route optimization system that uses multiple graph search algorithms to find the best flight paths based on various criteria (distance, price, time, CO2 emissions) or a balanced multi-weighted approach.

## Features

- **Multiple Search Algorithms**: Dijkstra, A*, BFS, and DFS implementations
- **Flexible Optimization Types**:
  - **Shortest Distance**: Find routes with minimum total distance
  - **Cheapest Price**: Find the most economical routes
  - **Fastest Time**: Find routes with minimum travel time
  - **Greenest (CO2)**: Find environmentally friendly routes
  - **Balanced Route**: Multi-weighted optimization balancing all factors
- **Advanced Filtering**:
  - Avoid specific airports
  - Avoid entire continents
  - Filter by airline
  - Limit number of stops/layovers
- **Interactive Map**: Visualize routes on a Leaflet-based map
- **Route Comparison**: View detailed information for all found routes

## Project Structure

```
Flight-Routes/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── Dockerfile            # Docker configuration (optional)
├── algo/                 # Search algorithm implementations
│   ├── dijkstra.py      # Dijkstra's algorithm
│   ├── astar.py         # A* search algorithm
│   ├── bfs.py           # Breadth-First Search
│   └── dfs.py           # Depth-First Search
├── core/                 # Core data structures
│   ├── graph.py         # Graph representation
│   ├── airport.py       # Airport class
│   └── route.py         # Route class
├── routes/               # API endpoints
│   └── api.py           # Flask blueprints for all routes
├── data/                 # Data files
│   ├── airline_routes.json  # Complete flight network data
│   ├── airlines.csv      # Airline information
│   └── airports.csv      # Airport information
├── templates/            # Web UI
│   └── index.html       # Main web interface
```

## Technologies

- **Backend**: Flask 3.1.3 (Python web framework)
- **Algorithms**: Dijkstra, A*, BFS, DFS (implemented in Python)
- **Frontend**: HTML, JavaScript, jQuery
- **Mapping**: Leaflet.js with CARTO dark tiles
- **UI Components**: Select2.js for searchable dropdowns

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Windows PowerShell or terminal with Python capability

### Step 1: Create Virtual Environment

```powershell
# Navigate to the Flight-Routes directory
cd path\to\Flight-Routes

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
.\venv\Scripts\Activate.ps1

# If you encounter an execution policy error, run:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 2: Install Dependencies

```powershell
# Make sure your virtual environment is activated
pip install -r requirements.txt
```

### Step 3: Run the Application

```powershell
# The virtual environment should still be activated
python app.py
```

The application will start on `http://localhost:5001`

## Usage

### Web Interface

1. **Select Origin Airport**: Choose your starting airport from the dropdown
2. **Select Destination Airport**: Choose your destination airport
3. **Choose Optimization Type**: Select what you want to optimize for:
   - Shortest Distance
   - Cheapest Price
   - Fastest Time
   - Greenest (CO2 emissions)
   - Balanced Route (adjustable sliders)
4. **Balanced Route Preferences**: If selected, adjust the sliders for:
   - Distance Weight
   - Price Weight
   - Time Weight
   - CO2 Weight
   - _Sliders automatically normalize to 100%_
5. **Set Maximum Stops**: Limit the number of layovers (No limit, 1, 2, or 3)
6. **Optional Filters**:
   - **Avoid Airport**: Select an airport to exclude from routes
   - **Avoid Continent**: Select a continent to exclude from routes
   - **Airline Filter**: Filter routes to specific airlines (if enabled)
7. **Search**: Click "Find Routes" button
8. **View Results**: Results appear below the form with detailed route information

### Available Algorithms

#### Dijkstra's Algorithm
- **Type**: Weighted shortest path
- **Use Case**: Finding optimal routes for single-criterion optimization
- **Variants**: 5 endpoints for different optimization types
- **Complexity**: O((V + E) log V) with priority queue

#### A* Search
- **Type**: Heuristic-guided search (Dijkstra with heuristic)
- **Use Case**: Faster convergence than Dijkstra, especially for long-distance routes
- **Variants**: 5 endpoints for different optimization types
- **Complexity**: Better than Dijkstra in practice with good heuristic

#### Breadth-First Search (BFS)
- **Type**: Unweighted shortest path
- **Use Case**: Finding routes with fewest layovers
- **Endpoint**: `/fewest-layovers`
- **Complexity**: O(V + E)

#### Depth-First Search (DFS)
- **Type**: Exhaustive search
- **Use Case**: Finding all possible routes up to a maximum number of stops
- **Endpoint**: `/all-routes`
- **Complexity**: O(V + E)

## API Endpoints

All endpoints expect GET requests with the following common parameters:

**Required:**
- `start`: IATA code of origin airport
- `end`: IATA code of destination airport

**Optional:**
- `algorithm`: Which algorithm to use (dijkstra/astar/bfs/dfs)
- `avoid_airport`: IATA code of airport to avoid
- `avoid_continent`: 2-letter continent code to avoid (NA, SA, EU, AF, AS, OC, AN)
- `airline`: Filter by airline (if data available)
- `max_stops`: Maximum number of stops / layovers ("No Max Stop" or 1-3)

**Weight Parameters** (for balanced routes):
- `w_dist`: Distance weight (0-100)
- `w_price`: Price weight (0-100)
- `w_time`: Time weight (0-100)
- `w_co2`: CO2 emissions weight (0-100)

### Available Endpoints

- **GET** `/shortest` - Dijkstra shortest distance
- **GET** `/cheapest` - Dijkstra lowest price
- **GET** `/fastest` - Dijkstra minimum time
- **GET** `/greenest` - Dijkstra minimum CO2
- **GET** `/balanced` - Dijkstra with balanced weights
- **GET** `/astar-shortest` - A* shortest distance
- **GET** `/astar-cheapest` - A* lowest price
- **GET** `/astar-fastest` - A* minimum time
- **GET** `/astar-greenest` - A* minimum CO2
- **GET** `/astar-balanced` - A* with balanced weights
- **GET** `/fewest-layovers` - BFS fewest stops
- **GET** `/all-routes` - DFS all possible routes

## Continent Codes

- **NA** - North America
- **SA** - South America
- **EU** - Europe
- **AF** - Africa
- **AS** - Asia
- **OC** - Oceania
- **AN** - Antarctica

## Data Format

Flight route data is loaded from `data/airline_routes.json`. Each airport includes:
- IATA code
- City name
- Country
- Continent code
- Available routes with:
  - Distance (km)
  - Price
  - Duration (minutes)
  - CO2 emissions
  - Carrier information

## Configuration

Key settings in `config.py`:
- Flask debug mode
- Server host and port
- Logging configuration

## Troubleshooting

### Virtual Environment Issues

**Problem**: `'python' is not recognized`
- **Solution**: Ensure Python is installed and added to PATH

**Problem**: Activation script fails
- **Solution**: Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### Port Already in Use

**Problem**: "Address already in use" error
- **Solution**: Change the port in `app.py` or kill the process using port 5001

### Missing Dependencies

**Problem**: `ModuleNotFoundError` when running the app
- **Solution**: Ensure virtual environment is activated and `pip install -r requirements.txt` was run

## Acknowledgments
This markdown file is generated by Claude Haiku 4.5
Powered by graph algorithms and modern web technologies for intelligent route optimization.
