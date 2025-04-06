from fastapi import FastAPI, Query  # FastAPI for building the API, Query for request parameter validation
from geopy.geocoders import Nominatim  # Used to convert location name to coordinates (latitude, longitude)
from geopy.distance import geodesic  # Calculates real-world distance between two geo-coordinates
import pandas as pd  # Used to store and work with the property data
app = FastAPI()

geolocator = Nominatim(user_agent="moustache_api")

# Create a sample list of property locations with coordinates
properties = pd.DataFrame([
    {"name": "Jaipur", "latitude": 26.9124, "longitude": 75.7873},
    {"name": "Koksar", "latitude": 32.4006, "longitude": 77.0610},
    {"name": "Manali", "latitude": 32.2396, "longitude": 77.1887},
    {"name": "Delhi", "latitude": 28.7041, "longitude": 77.1025},
    {"name": "Mumbai", "latitude": 19.0760, "longitude": 72.8777},
])

# Extract just the names of the properties into a list (not used currently)
location_names = properties["name"].tolist()

# Define an endpoint `/nearest-property` that accepts a `location` query parameter
@app.get("/nearest-property")
def get_nearest_property(location: str = Query(..., description="Location query from caller")):
    try:
        # Use Nominatim to geocode the input location string into coordinates
        geocode = geolocator.geocode(location)
        if not geocode:
            # If geocoding fails (invalid location), return an error message
            return {"message": "Could not geocode the location."}
        
        # Extract latitude and longitude of the input location
        input_coords = (geocode.latitude, geocode.longitude)

    except:
        # Catch unexpected errors during geocoding
        return {"message": "Error finding coordinates."}

    nearby_properties = []  # To store properties that are within 50 km of the input location

    # Loop over each property in the DataFrame
    for _, row in properties.iterrows():
        prop_coords = (row["latitude"], row["longitude"])  # Coordinates of the property
        
        # Calculate geodesic distance between input location and property
        dist = geodesic(input_coords, prop_coords).km

        # If the property is within 50 kilometers, add it to the results
        if dist <= 50:
            nearby_properties.append({
                "name": row["name"],
                "distance_km": round(dist, 2)  # Round the distance to 2 decimal places
            })

    # Return list of nearby properties, or a message if none were found
    if nearby_properties:
        return {"nearest_properties": nearby_properties}
    else:
        return {"message": "No properties found within 50km."}
