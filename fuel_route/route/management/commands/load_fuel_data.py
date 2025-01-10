from django.core.management.base import BaseCommand
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from route.models import FuelStation
import pandas as pd
import time

class Command(BaseCommand):
    help = "Load fuel data into the database"

    def handle(self, *args, **kwargs):
        # Load CSV
        file_path = r"C:\Users\Omaar\OneDrive\سطح المكتب\Pop\fuel-prices-for-be-assessment.csv"
        data = pd.read_csv(file_path)

        # Geocoder setup with timeout parameter
        geolocator = Nominatim(user_agent="fuel_route_geocoder", timeout=10)  # Timeout set to 10 seconds

        # Function to handle geocoding with retry logic
        def get_location_with_retry(city, state, retries=3):
            for attempt in range(retries):
                try:
                    location = geolocator.geocode(f"{city}, {state}")
                    if location:
                        return location
                    else:
                        print(f"No location found for {city}, {state}")
                        return None
                except GeocoderTimedOut:
                    if attempt < retries - 1:
                        print(f"Geocoding timed out for {city}, {state}. Retrying...")
                        time.sleep(2)  # Wait for 2 seconds before retrying
                        continue
                    print(f"Geocoding failed for {city}, {state} after {retries} retries")
                    return None

        # Process each row in the CSV
        for _, row in data.iterrows():
            city = row['City']
            state = row['State']
            price_per_gallon = row['Retail Price']

            # Get the location (latitude and longitude) for each city and state
            location = get_location_with_retry(city, state)

            if location:
                try:
                    FuelStation.objects.create(
                        city=city,
                        state=state,
                        latitude=location.latitude,
                        longitude=location.longitude,
                        price_per_gallon=price_per_gallon
                    )
                    print(f"Added fuel station: {city}, {state}")
                except Exception as e:
                    print(f"Error processing {city}, {state}: {e}")
            else:
                print(f"Skipping {city}, {state} due to geocoding failure")

        self.stdout.write(self.style.SUCCESS("Fuel data loaded successfully"))

