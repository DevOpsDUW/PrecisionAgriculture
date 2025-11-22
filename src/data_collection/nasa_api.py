# src/data_collection/nasa_api.py
import requests
import json
import os
from datetime import datetime, timedelta
import pandas as pd

class NASAEarthData:
    def __init__(self):
        self.base_url = "https://modis.earthdata.nasa.gov"
        self.landsat_url = "https://landsatlook.usgs.gov/stac-server"
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'raw')
        os.makedirs(self.data_dir, exist_ok=True)
        
        print("NASA EarthData API Client Initialized")
        print("Note: For full access, register at https://urs.earthdata.nasa.gov")
    
    def search_landsat_data(self, latitude, longitude, date=None, cloud_cover=20):
        """
        Search for Landsat imagery around specified coordinates
        This uses the public STAC API - no authentication required for basic searches
        """
        if date is None:
            date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
        print(f"Searching Landsat data for coordinates: {latitude}, {longitude}")
        print(f"Date range: {date} to present")
        print(f"Max cloud cover: {cloud_cover}%")
        
        try:
            # STAC API search for Landsat data
            search_url = f"{self.landsat_url}/collections/landsat-c2l2-sr/items"
            
            # Create a bounding box around the point (0.1 degree buffer)
            bbox = [
                longitude - 0.1,  # min_lon
                latitude - 0.1,   # min_lat  
                longitude + 0.1,  # max_lon
                latitude + 0.1    # max_lat
            ]
            
            params = {
                'bbox': ','.join(str(coord) for coord in bbox),
                'datetime': f"{date}T00:00:00Z/{datetime.now().strftime('%Y-%m-%d')}T23:59:59Z",
                'cloud_cover': f'0,{cloud_cover}',
                'limit': 10
            }
            
            response = requests.get(search_url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                features = data.get('features', [])
                
                print(f"Found {len(features)} Landsat scenes")
                
                # Process the results
                scenes = []
                for feature in features:
                    scene_data = {
                        'scene_id': feature['id'],
                        'date': feature['properties']['datetime'][:10],
                        'cloud_cover': feature['properties'].get('eo:cloud_cover', 0),
                        'thumbnail': feature['assets'].get('thumbnail', {}).get('href'),
                        'coordinates': [longitude, latitude]
                    }
                    scenes.append(scene_data)
                
                # Save results
                output_file = os.path.join(self.data_dir, f'landsat_search_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
                with open(output_file, 'w') as f:
                    json.dump(scenes, f, indent=2)
                
                print(f"Search results saved to: {output_file}")
                return scenes
                
            else:
                print(f"API request failed with status: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error searching Landsat data: {e}")
            return []
    
    def calculate_ndvi_simulation(self, field_data):
        """
        Simulate NDVI calculation since actual raster processing requires more setup
        In a full implementation, this would process actual satellite imagery
        """
        print("Simulating NDVI calculation based on field characteristics...")
        
        ndvi_results = []
        for field in field_data:
            # Simulate NDVI based on field properties and random variation
            base_health = field.get('soil_health_score', 0.5)
            base_yield = field.get('historical_yield', 3.0) / 4.0  # Normalize
            
            # Simulate seasonal variation
            current_month = datetime.now().month
            if 4 <= current_month <= 9:  # Growing season
                seasonal_factor = 0.7 + (current_month - 4) * 0.05
            else:
                seasonal_factor = 0.3
            
            # Calculate simulated NDVI (0.2 to 0.8 range)
            simulated_ndvi = 0.2 + (base_health * 0.3) + (base_yield * 0.2) + (seasonal_factor * 0.1)
            simulated_ndvi = min(0.8, max(0.2, simulated_ndvi))
            
            result = {
                'field_name': field['field_name'],
                'ndvi_value': round(simulated_ndvi, 3),
                'calculation_date': datetime.now().strftime('%Y-%m-%d'),
                'data_source': 'simulated_based_on_field_properties',
                'health_status': 'healthy' if simulated_ndvi > 0.5 else 'stressed'
            }
            ndvi_results.append(result)
        
        return ndvi_results
    
    def get_weather_data_simulation(self, latitude, longitude, days=7):
        """
        Simulate weather data - in Phase 3 we'll integrate real weather APIs
        """
        print(f"Simulating weather data for {latitude}, {longitude} for past {days} days...")
        
        weather_data = []
        base_temp = 20 + (latitude - 35) * 0.5  # Adjust base temp by latitude
        
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            
            # Simulate realistic weather patterns
            temp_variation = (i % 7) * 2  # Weekly pattern
            precipitation = 0 if (i + 2) % 5 != 0 else round((i * 0.8) % 15, 1)  # Occasional rain
            
            daily_weather = {
                'date': date,
                'temperature_max': round(base_temp + temp_variation + 5, 1),
                'temperature_min': round(base_temp + temp_variation - 5, 1),
                'precipitation': precipitation,
                'evapotranspiration': round(3.5 + (temp_variation * 0.1), 1),
                'data_source': 'simulated_for_demonstration'
            }
            weather_data.append(daily_weather)
        
        return weather_data

def main():
    """Test NASA API integration - Phase 2 Implementation"""
    print("=== NASA EARTHDATA API INTEGRATION ===")
    print("Phase 2: Satellite Data Collection")
    
    nasa_client = NASAEarthData()
    
    # Test coordinates (California agricultural region)
    test_lat, test_lon = 36.85, -121.45
    
    print(f"\n1. Testing Landsat data search...")
    landsat_results = nasa_client.search_landsat_data(test_lat, test_lon)
    
    print(f"\n2. Testing NDVI simulation...")
    sample_fields = [
        {'field_name': 'North_Hills', 'soil_health_score': 0.85, 'historical_yield': 3.4},
        {'field_name': 'South_Valley', 'soil_health_score': 0.60, 'historical_yield': 2.7},
        {'field_name': 'East_Plateau', 'soil_health_score': 0.90, 'historical_yield': 3.6}
    ]
    
    ndvi_results = nasa_client.calculate_ndvi_simulation(sample_fields)
    for result in ndvi_results:
        print(f"{result['field_name']}: NDVI {result['ndvi_value']} ({result['health_status']})")
    
    print(f"\n3. Testing weather data simulation...")
    weather_data = nasa_client.get_weather_data_simulation(test_lat, test_lon)
    print(f"Generated {len(weather_data)} days of weather data")
    
    print(f"\nPhase 2 NASA API integration completed!")
    print("Next: Integrate real satellite data processing")
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()