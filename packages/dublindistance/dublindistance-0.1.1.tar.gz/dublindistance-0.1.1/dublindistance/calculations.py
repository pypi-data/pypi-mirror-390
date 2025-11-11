from geopy.distance import geodesic

# Approximate Dublin postal coordinates (just examples)
POSTAL_COORDS = {
    "D1": (53.3498, -6.2603),
    "D2": (53.3378, -6.2597),
    "D8": (53.3379, -6.2783),
    "D12": (53.3206, -6.3299),
    "D15": (53.3932, -6.4176),
}

def calculate_distance(area1, area2):
    """Return distance in km between two Dublin area codes."""
    if area1 not in POSTAL_COORDS or area2 not in POSTAL_COORDS:
        return None
    coord1, coord2 = POSTAL_COORDS[area1], POSTAL_COORDS[area2]
    return round(geodesic(coord1, coord2).km, 2)
