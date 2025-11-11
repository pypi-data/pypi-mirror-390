def suggest_transport(distance_km):
    """Suggest transport mode based on distance."""
    if distance_km is None:
        return "Unknown distance – check area codes."
    if distance_km < 1.5:
        return "🚶‍♂️ It's a short walk!"
    elif distance_km < 5:
        return "🚴 Perfect for a quick cycle!"
    elif distance_km < 12:
        return "🚌 or 🚆 Take a bus or Luas."
    else:
        return "🚗 or 🚆 It's best to take a DART or drive."
