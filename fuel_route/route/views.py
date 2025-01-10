from django.shortcuts import render
from geopy.geocoders import Nominatim 
from geopy.exc import GeocoderTimedOut
from django.http import JsonResponse
from .utils import get_route_with_fuel_stops


def get_route(request):
    start_location = request.GET.get('start_location')
    end_location = request.GET.get('end_location')

    if not start_location or not end_location:
        return JsonResponse({"error": "Both start and end locations are required."}, status=400)

    try:
        # Parse the coordinates
        start_coords = [float(coord) for coord in start_location.split(',')]
        end_coords = [float(coord) for coord in end_location.split(',')]

        # Ensure coordinates are in (longitude, latitude) order for Mapbox API
        start_coords = (start_coords[0], start_coords[1])  # longitude, latitude
        end_coords = (end_coords[0], end_coords[1])  # longitude, latitude

        route_data = get_route_with_fuel_stops(start_coords, end_coords)
        route = route_data['route']
        fuel_stops = route_data['fuel_stops']
        total_cost = route_data['total_cost']

        # Convert total distance from meters to miles
        total_distance_miles = route['distance'] * 0.000621371

        # Convert total duration from seconds to hours and minutes
        total_duration_seconds = route['duration']
        total_hours = total_duration_seconds // 3600
        total_minutes = (total_duration_seconds % 3600) // 60

        # Construct response
        response_data = {
            "route_summary": route['legs'][0]['summary'],
            "total_distance_miles": total_distance_miles,
            "total_duration": f"{total_hours} hours {total_minutes} minutes",
            "fuel_stops": [station.city for station in fuel_stops],  # You can also return more details
            "total_cost": total_cost,
            "success": "Route fetched successfully."
        }
        return JsonResponse(response_data)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)