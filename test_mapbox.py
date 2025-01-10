import requests

# Define the start and end locations (coordinates)
start_location = "-118.2437,34.0522"  # Los Angeles, CA
end_location = "-122.4194,37.7749"    # San Francisco, CA

# Replace with your actual Mapbox API key
api_key = "pk.eyJ1Ijoib2JoYWlzNDE3NCIsImEiOiJjbTVxbWU3NTMwMWc4MnFwYzg4Yjg4dXhpIn0.4wAwncKMTnS1Xhd55iUmlQ"  # Make sure to use your Mapbox API key here

# Construct the URL to fetch the route
url = f"https://api.mapbox.com/directions/v5/mapbox/driving/{start_location};{end_location}?access_token={api_key}&geometries=geojson"

# Send the GET request to the Mapbox API
response = requests.get(url)

# Print the response (this will help diagnose the issue)
print(response.json())  # This will print the response data or error from Mapbox
