# src/data_collection/database_setup.py
import sqlite3
import json
import os
from datetime import datetime

class AgricultureDatabase:
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'agriculture.db')
        self.connection = None
        self.connect()
        
    def connect(self):
        """Connect to SQLite database (we'll upgrade to PostgreSQL later)"""
        try:
            # Create data directory if it doesn't exist
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            print("Connected to SQLite database")
            print(f"Database location: {self.db_path}")
        except Exception as e:
            print(f"Database connection failed: {e}")
    
    def setup_database(self):
        """Create the database schema"""
        try:
            cursor = self.connection.cursor()
            
            # Create farms table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS farms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    total_area_hectares REAL,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Create fields table (instead of PostGIS polygons, we'll use simple coordinates)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fields (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    farm_id INTEGER REFERENCES farms(id),
                    field_name TEXT NOT NULL,
                    area_hectares REAL,
                    center_lat REAL,
                    center_lon REAL,
                    soil_type TEXT,
                    historical_yield REAL
                );
            """)
            
            # Create satellite_data table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS satellite_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    field_id INTEGER REFERENCES fields(id),
                    capture_date DATE,
                    ndvi_value REAL,
                    cloud_cover REAL,
                    data_source TEXT
                );
            """)
            
            # Create management_zones table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS management_zones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    farm_id INTEGER REFERENCES farms(id),
                    zone_name TEXT NOT NULL,
                    soil_health_score REAL,
                    historical_yield REAL,
                    water_priority INTEGER,
                    ndvi_trend REAL
                );
            """)
            
            # Create weather_data table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS weather_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    farm_id INTEGER REFERENCES farms(id),
                    date DATE,
                    temperature_max REAL,
                    temperature_min REAL,
                    precipitation REAL,
                    evapotranspiration REAL
                );
            """)
            
            self.connection.commit()
            print("Database schema created successfully!")
            
        except Exception as e:
            print(f"Error creating schema: {e}")
    
    def create_sample_data(self):
        """Insert sample farm data for testing and demonstration"""
        try:
            cursor = self.connection.cursor()
            
            # Insert sample farm
            cursor.execute("""
                INSERT INTO farms (name, total_area_hectares)
                VALUES (?, ?)
            """, ('Drought-Prone Valley Farm', 200.0))
            
            farm_id = cursor.lastrowid
            
            # Insert sample fields
            fields = [
                (farm_id, 'North_Hills', 45, 36.85, -121.45, 'sandy_loam', 3.4),
                (farm_id, 'South_Valley', 68, 36.82, -121.35, 'clay', 2.7),
                (farm_id, 'East_Plateau', 52, 36.88, -121.32, 'sandy_loam', 3.6),
                (farm_id, 'West_Plains', 78, 36.83, -121.42, 'clay_loam', 2.8),
                (farm_id, 'Central_Basin', 35, 36.86, -121.38, 'loam', 3.2)
            ]
            
            cursor.executemany("""
                INSERT INTO fields (farm_id, field_name, area_hectares, center_lat, center_lon, soil_type, historical_yield)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, fields)
            
            # Insert sample management zones
            zones = [
                (farm_id, 'High_Productivity_Zone', 0.85, 3.8, 1, 0.75),
                (farm_id, 'Medium_Productivity_Zone', 0.65, 3.2, 2, 0.60),
                (farm_id, 'Low_Productivity_Zone', 0.45, 2.6, 3, 0.45)
            ]
            
            cursor.executemany("""
                INSERT INTO management_zones (farm_id, zone_name, soil_health_score, historical_yield, water_priority, ndvi_trend)
                VALUES (?, ?, ?, ?, ?, ?)
            """, zones)
            
            # Insert recent satellite data
            from datetime import date, timedelta
            recent_date = date.today() - timedelta(days=7)
            
            satellite_data = [
                (1, recent_date, 0.68, 0.10, 'Landsat_8'),
                (2, recent_date, 0.42, 0.15, 'Landsat_8'),
                (3, recent_date, 0.72, 0.05, 'Landsat_8'),
                (4, recent_date, 0.51, 0.20, 'Landsat_8'),
                (5, recent_date, 0.61, 0.12, 'Landsat_8')
            ]
            
            cursor.executemany("""
                INSERT INTO satellite_data (field_id, capture_date, ndvi_value, cloud_cover, data_source)
                VALUES (?, ?, ?, ?, ?)
            """, satellite_data)
            
            self.connection.commit()
            print(f"Sample data created for farm ID: {farm_id}")
            print("Created: 1 farm, 5 fields, 3 management zones, 5 satellite readings")
            return farm_id
            
        except Exception as e:
            print(f"Error creating sample data: {e}")
            return None
    
    def get_water_priority_data(self, farm_id):
        """Get management zones ordered by water priority for analysis"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                SELECT zone_name, soil_health_score, historical_yield, water_priority, ndvi_trend
                FROM management_zones 
                WHERE farm_id = ? 
                ORDER BY water_priority ASC;
            """, (farm_id,))
            
            zones = cursor.fetchall()
            return zones
            
        except Exception as e:
            print(f"Error fetching water priority data: {e}")
            return []
    
    def get_field_health_data(self, farm_id):
        """Get current field health data for analysis"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                SELECT f.field_name, f.area_hectares, f.historical_yield, 
                       s.ndvi_value, s.capture_date
                FROM fields f
                LEFT JOIN satellite_data s ON f.id = s.field_id
                WHERE f.farm_id = ?
                ORDER BY s.capture_date DESC;
            """, (farm_id,))
            
            fields = cursor.fetchall()
            return fields
            
        except Exception as e:
            print(f"Error fetching field health data: {e}")
            return []

def main():
    """Test the database setup - Phase 1 Implementation"""
    print("=== PRECISION AGRICULTURE DATABASE SETUP ===")
    print("Phase 1: Backend Database Implementation")
    print("Using SQLite for development (will upgrade to PostgreSQL+PostGIS later)")
    
    db = AgricultureDatabase()
    
    if db.connection:
        # Setup database schema
        db.setup_database()
        
        # Create sample data
        farm_id = db.create_sample_data()
        
        if farm_id:
            # Demonstrate data retrieval
            print("\n" + "="*50)
            print("WATER PRIORITY MANAGEMENT ZONES:")
            print("="*50)
            
            zones = db.get_water_priority_data(farm_id)
            for zone in zones:
                print(f"{zone['zone_name']}: Priority {zone['water_priority']}, "
                      f"Soil Health: {zone['soil_health_score']}, "
                      f"Yield: {zone['historical_yield']} t/ha")
            
            print("\n" + "="*50)
            print("FIELD HEALTH MONITORING:")
            print("="*50)
            
            fields = db.get_field_health_data(farm_id)
            for field in fields:
                print(f"{field['field_name']}: {field['area_hectares']} ha, "
                      f"NDVI: {field['ndvi_value']}, "
                      f"Yield: {field['historical_yield']} t/ha")
    
    print(f"\nDatabase file created at: {db.db_path}")
    print("Phase 1 Database setup completed successfully!")
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()