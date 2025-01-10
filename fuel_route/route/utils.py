import requests
from django.conf import settings
from django.db.models import Avg
from .models import FuelStation
from geopy.distance import geodesic


def get_route_with_fuel_stops(start_location, end_location, max_range=500, mpg=10):
    api_key = settings.MAPBOX_API_KEY
    # Ensure coordinates are in (longitude, latitude) order for Mapbox API
    url = f"https://api.mapbox.com/directions/v5/mapbox/driving/{start_location[0]},{start_location[1]};{end_location[0]},{end_location[1]}?access_token={api_key}&geometries=geojson"
    
    response = requests.get(url)
    
    print(f"API Request URL: {url}")  # Debug: Print the request URL
    print(f"API Response Status: {response.status_code}")  # Debug: Print status code
    print(f"API Response Body: {response.text}")  # Debug: Print response content

    data = response.json()
    if response.status_code != 200 or 'routes' not in data:
        raise Exception("Error fetching route from Mapbox API.")

    route = data['routes'][0]
    total_distance_meters = route['distance']
    total_distance_miles = total_distance_meters * 0.000621371  # Convert to miles

    fuel_stops = []
    total_distance_travelled = 0

    coordinates = route['geometry']['coordinates']
    for i in range(1, len(coordinates)):
        start_point = (coordinates[i-1][1], coordinates[i-1][0])  # lat, lon
        end_point = (coordinates[i][1], coordinates[i][0])  # lat, lon
        segment_distance = geodesic(start_point, end_point).miles

        total_distance_travelled += segment_distance

        # Add a fuel stop if we've exceeded the max range (500 miles)
        if total_distance_travelled >= max_range:
            fuel_stops.append((total_distance_travelled, end_point))
            total_distance_travelled = 0  # Reset distance after a stop

    total_gallons = total_distance_miles / mpg
    average_price = FuelStation.objects.aggregate(Avg('price_per_gallon'))['price_per_gallon__avg']
    total_cost = total_gallons * average_price

    fuel_station_details = []
    for stop_distance, stop_coords in fuel_stops:
        nearest_station = get_nearest_fuel_station(stop_coords)
        fuel_station_details.append(nearest_station)

    return {
        'route': route,
        'fuel_stops': fuel_station_details,
        'total_cost': total_cost
    }


def get_nearest_fuel_station(stop_coords):
    nearest_station = None
    min_distance = float('inf')
    
    # Query all fuel stations and find the nearest one
    for station in FuelStation.objects.all():
        station_coords = (station.latitude, station.longitude)

        if not validate_coordinates(station_coords):
            continue

        distance = geodesic(stop_coords, station_coords).miles
        if distance < min_distance:
            nearest_station = station
            min_distance = distance
    
    return nearest_station

def validate_coordinates(coords):
    lat, lon = coords
    if lat < -90 or lat > 90 or lon < -180 or lon > 180:
        return False
    return True