# agriculture_analysis.py
import pandas as pd
import numpy as np
from datetime import datetime
import json

print("PRECISION AGRICULTURE CLIMATE RESILIENCE ANALYZER")
print("Data Analyst Portfolio Project")
print("Water Optimization for Drought Conditions")

class AgricultureAnalyzer:
    def __init__(self):
        self.farm_name = "Sample Farm - Drought Prone Region"
        print("Initializing analyzer for:", self.farm_name)
        
    def generate_farm_data(self):
        print("Generating farm field data...")
        
        data = {
            'field_id': [1, 2, 3, 4, 5, 6, 7, 8],
            'field_name': ['North_Hills', 'South_Valley', 'East_Plateau', 'West_Plains', 
                          'Central_Basin', 'Northwest_Slope', 'Southeast_Meadow', 'Northeast_Ridge'],
            'area_hectares': [45, 68, 52, 78, 35, 62, 55, 48],
            'soil_moisture': [0.12, 0.28, 0.09, 0.32, 0.15, 0.22, 0.18, 0.11],
            'ndvi_health': [0.68, 0.42, 0.72, 0.51, 0.61, 0.55, 0.58, 0.70],
            'historical_yield': [3.4, 2.7, 3.6, 2.8, 3.2, 3.0, 3.3, 3.5],
            'water_requirement': [1200, 980, 1350, 890, 1100, 1050, 1150, 1300],
            'drought_risk': [0.85, 0.60, 0.90, 0.55, 0.75, 0.65, 0.70, 0.88]
        }
        
        df = pd.DataFrame(data)
        print("Generated data for", len(df), "fields")
        return df
    
    def calculate_priority(self, df, available_water=5000):
        print("Calculating irrigation priorities...")
        print("Available water:", available_water, "m3")
        
        df['yield_potential'] = (df['historical_yield'] - df['historical_yield'].min()) / (df['historical_yield'].max() - df['historical_yield'].min())
        df['crop_health'] = (df['ndvi_health'] - df['ndvi_health'].min()) / (df['ndvi_health'].max() - df['ndvi_health'].min())
        df['moisture_deficit'] = 1 - (df['soil_moisture'] / df['soil_moisture'].max())
        
        df['resilience_priority'] = (
            0.35 * df['yield_potential'] +
            0.30 * df['crop_health'] +
            0.25 * df['moisture_deficit'] +
            0.10 * df['drought_risk']
        )
        
        total_priority = df['resilience_priority'].sum()
        df['allocated_water'] = (df['resilience_priority'] / total_priority * available_water).astype(int)
        df['allocation_sufficiency'] = df['allocated_water'] / df['water_requirement']
        
        return df.sort_values('resilience_priority', ascending=False)
    
    def show_recommendations(self, df):
        print("IRRIGATION RECOMMENDATIONS")
        print("=" * 50)
        
        total_available = df['allocated_water'].sum()
        total_required = df['water_requirement'].sum()
        
        print("Water Status:", total_available, "m3 available vs", total_required, "m3 required")
        deficit = ((total_required - total_available) / total_required * 100)
        print("Deficit:", round(deficit, 1), "%")
        
        print("TOP PRIORITY FIELDS (Irrigate First):")
        print("-" * 40)
        
        for i, (_, row) in enumerate(df.head(3).iterrows(), 1):
            print(i, ".", row['field_name'], "Priority:", round(row['resilience_priority'], 3))
            print("   Allocate:", row['allocated_water'], "m3 | Sufficiency:", round(row['allocation_sufficiency'] * 100, 1), "%")
            print("   Yield:", row['historical_yield'], "t/ha | NDVI:", row['ndvi_health'])
            print()

def main():
    try:
        analyzer = AgricultureAnalyzer()
        farm_data = analyzer.generate_farm_data()
        prioritized_data = analyzer.calculate_priority(farm_data)
        
        print("FIELD PRIORITY ANALYSIS")
        print("=" * 50)
        
        print("Ranked by Water Allocation Priority:")
        print("-" * 50)
        print("Field Name           Priority   Water Alloc  Sufficiency  Yield")
        print("-" * 50)
        
        for _, row in prioritized_data.iterrows():
            print(f"{row['field_name']:20} {row['resilience_priority']:8.3f} {row['allocated_water']:8} m3 {row['allocation_sufficiency']:8.1%} {row['historical_yield']:7.1f} t/ha")
        
        analyzer.show_recommendations(prioritized_data)
        
        print("ANALYSIS COMPLETE - Ready for portfolio!")
        
    except Exception as e:
        print("Error:", e)
    
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()