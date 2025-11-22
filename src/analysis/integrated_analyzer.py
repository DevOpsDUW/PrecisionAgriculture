# src/analysis/integrated_analyzer.py
import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from data_collection.database_setup import AgricultureDatabase
from data_collection.nasa_api import NASAEarthData

class IntegratedAgricultureAnalyzer:
    def __init__(self):
        self.db = AgricultureDatabase()
        self.nasa = NASAEarthData()
        print("Integrated Agriculture Analyzer Initialized")
        print("Combining database, satellite data, and analytics")
    
    def get_complete_farm_analysis(self, farm_id=1):
        print(f"\nCOMPREHENSIVE FARM ANALYSIS")
        print(f"Farm ID: {farm_id}")
        
        zones = self.db.get_water_priority_data(farm_id)
        fields = self.db.get_field_health_data(farm_id)
        
        if not zones or not fields:
            print("No data found for farm ID:", farm_id)
            return None
        
        zones_df = pd.DataFrame([dict(zone) for zone in zones])
        fields_df = pd.DataFrame([dict(field) for field in fields])
        
        print(f"Analyzing {len(zones_df)} management zones and {len(fields_df)} fields")
        
        # Get NDVI data for fields
        field_data_for_ndvi = []
        for _, field in fields_df.iterrows():
            field_data_for_ndvi.append({
                'field_name': field['field_name'],
                'soil_health_score': 0.7,
                'historical_yield': field['historical_yield']
            })
        
        ndvi_results = self.nasa.calculate_ndvi_simulation(field_data_for_ndvi)
        ndvi_df = pd.DataFrame(ndvi_results)
        
        # Debug: Check what data we have
        print("Fields data columns:", fields_df.columns.tolist())
        print("NDVI data columns:", ndvi_df.columns.tolist())
        
        # Merge the data carefully
        if 'ndvi_value' in ndvi_df.columns:
            # Create a mapping from field_name to ndvi_value
            ndvi_mapping = dict(zip(ndvi_df['field_name'], ndvi_df['ndvi_value']))
            
            # Add NDVI values to fields data
            fields_df['ndvi_value'] = fields_df['field_name'].map(ndvi_mapping)
            
            # Fill any missing NDVI values with a default
            fields_df['ndvi_value'] = fields_df['ndvi_value'].fillna(0.5)
            
            print("NDVI data successfully merged")
        else:
            print("Warning: No NDVI data found, using default values")
            fields_df['ndvi_value'] = 0.5
        
        analysis_results = self.calculate_comprehensive_priority(fields_df, zones_df)
        
        self.generate_irrigation_recommendations(analysis_results)
        
        return analysis_results
    
    def calculate_comprehensive_priority(self, fields_data, zones_data):
        print("\nCalculating comprehensive water allocation priorities...")
        
        fields_data = fields_data.copy()
        
        # Calculate scores with safety checks
        fields_data['yield_score'] = (fields_data['historical_yield'] - fields_data['historical_yield'].min()) / (fields_data['historical_yield'].max() - fields_data['historical_yield'].min())
        
        if 'ndvi_value' in fields_data.columns:
            fields_data['health_score'] = (fields_data['ndvi_value'] - fields_data['ndvi_value'].min()) / (fields_data['ndvi_value'].max() - fields_data['ndvi_value'].min())
        else:
            fields_data['health_score'] = 0.5
        
        fields_data['area_score'] = (fields_data['area_hectares'] - fields_data['area_hectares'].min()) / (fields_data['area_hectares'].max() - fields_data['area_hectares'].min())
        
        # Comprehensive priority score
        fields_data['comprehensive_priority'] = (
            0.35 * fields_data['yield_score'] +
            0.30 * fields_data['health_score'] +
            0.25 * fields_data['area_score'] +
            0.10 * np.random.uniform(0.7, 0.9, len(fields_data))
        )
        
        available_water = 5000
        total_priority = fields_data['comprehensive_priority'].sum()
        fields_data['allocated_water'] = (fields_data['comprehensive_priority'] / total_priority * available_water).astype(int)
        fields_data['allocation_sufficiency'] = fields_data['allocated_water'] / (fields_data['area_hectares'] * 15)
        
        fields_data = fields_data.sort_values('comprehensive_priority', ascending=False)
        
        print("Comprehensive priority calculation completed")
        return fields_data
    
    def generate_irrigation_recommendations(self, analysis_data):
        print("\n" + "="*60)
        print("CLIMATE-RESILIENT IRRIGATION STRATEGY")
        print("="*60)
        
        total_allocated = analysis_data['allocated_water'].sum()
        total_required = (analysis_data['area_hectares'] * 15).sum()
        
        print(f"WATER ALLOCATION SUMMARY:")
        print(f"   Total Available: {total_allocated:,} m3")
        print(f"   Total Required:  {total_required:,.0f} m3")
        print(f"   Allocation Rate: {(total_allocated/total_required*100):.1f}%")
        
        print(f"\nTOP PRIORITY FIELDS - IRRIGATE FIRST:")
        print("-" * 50)
        
        high_priority = analysis_data.head(3)
        for i, (_, field) in enumerate(high_priority.iterrows(), 1):
            if 'ndvi_value' in analysis_data.columns:
                status = "HEALTHY" if field['ndvi_value'] > 0.6 else "MONITOR" if field['ndvi_value'] > 0.4 else "STRESSED"
                ndvi_display = f"NDVI: {field['ndvi_value']:.3f} ({status})"
            else:
                ndvi_display = "NDVI: Data not available"
                
            print(f"{i}. {field['field_name']:20} Priority: {field['comprehensive_priority']:.3f}")
            print(f"   Water: {field['allocated_water']:4} m3 | Sufficiency: {field['allocation_sufficiency']:.1%}")
            print(f"   {ndvi_display} | Yield: {field['historical_yield']:.1f} t/ha")
            print()
        
        print("CLIMATE RESILIENCE RECOMMENDATIONS:")
        print("1. Implement staggered irrigation based on priority ranking")
        print("2. Monitor NDVI weekly for early stress detection")
        print("3. Focus soil moisture conservation on lower-priority fields")
        print("4. Consider drought-resistant cover crops for next season")
        
        stressed_fields = len(analysis_data[analysis_data['allocation_sufficiency'] < 0.5])
        total_fields = len(analysis_data)
        stress_percentage = (stressed_fields / total_fields) * 100
        
        print(f"\nRISK ASSESSMENT:")
        print(f"   {stressed_fields}/{total_fields} fields ({stress_percentage:.1f}%) at high water stress risk")
        
        return analysis_data
    
    def create_comprehensive_report(self, analysis_data, farm_id=1):
        print("\nGenerating comprehensive analysis report...")
        
        report_data = {
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'farm_id': farm_id,
            'total_fields_analyzed': len(analysis_data),
            'total_water_allocated': int(analysis_data['allocated_water'].sum()),
            'priority_fields': analysis_data[['field_name', 'comprehensive_priority', 'allocated_water']].head().to_dict('records'),
            'water_stress_risk': len(analysis_data[analysis_data['allocation_sufficiency'] < 0.5]) / len(analysis_data)
        }
        
        # Add NDVI data if available
        if 'ndvi_value' in analysis_data.columns:
            report_data['average_ndvi'] = round(analysis_data['ndvi_value'].mean(), 3)
        
        report_file = os.path.join('data', 'processed', f'farm_analysis_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        os.makedirs(os.path.dirname(report_file), exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"Analysis report saved to: {report_file}")
        
        return report_data

def main():
    print("=== PHASE 3: INTEGRATED AGRICULTURE ANALYSIS ===")
    print("Combining Database + Satellite Data + Analytics")
    
    analyzer = IntegratedAgricultureAnalyzer()
    
    results = analyzer.get_complete_farm_analysis(farm_id=1)
    
    if results is not None:
        report = analyzer.create_comprehensive_report(results)
        
        print("\n" + "="*70)
        print("PHASE 3 COMPLETED SUCCESSFULLY!")
        print("="*70)
        print("Database integration")
        print("Satellite data processing") 
        print("Climate resilience analytics")
        print("Irrigation optimization")
        print("Comprehensive reporting")
        print(f"Analysis date: {report['analysis_date']}")
        print(f"Fields analyzed: {report['total_fields_analyzed']}")
        print(f"Water allocated: {report['total_water_allocated']:,} m3")
        if 'average_ndvi' in report:
            print(f"Average NDVI: {report['average_ndvi']}")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()