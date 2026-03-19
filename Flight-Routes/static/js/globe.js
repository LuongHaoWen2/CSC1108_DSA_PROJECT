// Initialize map
const map = L.map('map-container').setView([20, 0], 2);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap'
}).addTo(map);

let currentRouteLayer = null;

// Draw route on map given list of airport codes
async function drawRoute(path) {
    // Remove existing route
    if (currentRouteLayer) {
        map.removeLayer(currentRouteLayer);
    }

    const coords = [];

    for (const code of path) {
        const res  = await fetch(`/api/airports/${code}`);
        const data = await res.json();
        coords.push([data.latitude, data.longitude]);

        // Add marker
        L.marker([data.latitude, data.longitude])
            .addTo(map)
            .bindPopup(`<b>${code}</b><br>${data.name}`);
    }

    // Draw polyline connecting airports
    currentRouteLayer = L.polyline(coords, {
        color: '#007bff',
        weight: 2,
        opacity: 0.8
    }).addTo(map);

    // Zoom map to fit the route
    map.fitBounds(currentRouteLayer.getBounds(), { padding: [40, 40] });
}