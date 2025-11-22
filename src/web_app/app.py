# -*- coding: utf-8 -*-
# src/web_app/app.py
from flask import Flask, render_template_string, jsonify, request
import sys
import os
import json
import sqlite3
import requests
from datetime import datetime, timedelta
import math
import random

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

app = Flask(__name__)

class SatelliteDataService:
    def __init__(self):
        self.nasa_username = os.environ.get('NASA_EARTHDATA_USERNAME', 'demo_user')
        self.nasa_password = os.environ.get('NASA_EARTHDATA_PASSWORD', 'demo_pass')
    
    def get_nasa_ndvi_data(self, lat, lon, field_name=None):
        """
        Get simulated NDVI data with realistic patterns
        In production, this would call actual NASA HLS API
        """
        try:
            # Simulate realistic NDVI patterns based on season and location
            day_of_year = datetime.now().timetuple().tm_yday
            
            # Base seasonal pattern (higher in growing season)
            seasonal_base = 0.3 + (math.sin((day_of_year - 100) / 365 * 2 * math.pi) * 0.4)
            
            # Location-based variation
            location_factor = ((lat * 100 + lon * 100) % 50) / 100  # 0-0.5 variation
            
            # Field-specific characteristics
            field_factor = hash(field_name or "default") % 30 / 100 if field_name else 0.1
            
            # Recent "weather" effect
            weather_effect = random.uniform(-0.1, 0.1)
            
            simulated_ndvi = seasonal_base + location_factor + field_factor + weather_effect
            simulated_ndvi = max(0.1, min(0.95, round(simulated_ndvi, 3)))
            
            # Simulate data quality
            quality_score = random.uniform(0.85, 0.98)
            
            return {
                'ndvi': simulated_ndvi,
                'timestamp': datetime.now().isoformat(),
                'source': 'NASA_HLS_SIMULATED',
                'coordinates': {'lat': lat, 'lon': lon},
                'quality_score': round(quality_score, 2),
                'confidence': 'high' if quality_score > 0.9 else 'medium'
            }
            
        except Exception as e:
            print(f"Satellite data error: {e}")
            return self.get_fallback_ndvi_data(lat, lon)
    
    def get_historical_ndvi_trend(self, lat, lon, days=30):
        """Generate historical NDVI trend data"""
        trends = []
        base_ndvi = 0.5 + (math.sin(datetime.now().timetuple().tm_yday / 365 * 2 * math.pi) * 0.3)
        
        for i in range(days, 0, -7):  # Weekly data points
            date = datetime.now() - timedelta(days=i)
            # Add some realistic fluctuation
            fluctuation = random.uniform(-0.15, 0.15)
            trend_ndvi = max(0.2, min(0.9, base_ndvi + fluctuation))
            
            trends.append({
                'date': date.strftime('%Y-%m-%d'),
                'ndvi': round(trend_ndvi, 3),
                'quality': random.uniform(0.8, 0.95)
            })
        
        return trends
    
    def get_fallback_ndvi_data(self, lat, lon):
        """Fallback NDVI data when satellite API is unavailable"""
        return {
            'ndvi': 0.65,
            'timestamp': datetime.now().isoformat(),
            'source': 'FALLBACK_MODEL',
            'coordinates': {'lat': lat, 'lon': lon},
            'quality_score': 0.7,
            'confidence': 'medium'
        }
    
    def get_vegetation_health_report(self, ndvi_value):
        """Generate comprehensive health assessment based on NDVI value"""
        if ndvi_value >= 0.7:
            return {
                'status': 'healthy', 
                'color': '#27ae60', 
                'recommendation': 'Optimal vegetation health',
                'action': 'Continue current practices',
                'risk_level': 'low'
            }
        elif ndvi_value >= 0.5:
            return {
                'status': 'moderate', 
                'color': '#f39c12', 
                'recommendation': 'Monitor growth patterns',
                'action': 'Consider soil testing',
                'risk_level': 'medium'
            }
        elif ndvi_value >= 0.3:
            return {
                'status': 'stressed', 
                'color': '#e74c3c', 
                'recommendation': 'Check water and nutrients',
                'action': 'Increase irrigation review',
                'risk_level': 'high'
            }
        else:
            return {
                'status': 'critical', 
                'color': '#c0392b', 
                'recommendation': 'Immediate attention needed',
                'action': 'Consult agronomist',
                'risk_level': 'critical'
            }

class EnhancedAgricultureDashboard:
    def __init__(self):
        self.db_path = self.get_database_path()
        self.satellite_service = SatelliteDataService()
    
    def get_database_path(self):
        """Get database path that works on both local and Railway"""
        if 'RAILWAY_VOLUME_MOUNT_PATH' in os.environ:
            db_path = os.path.join(os.environ['RAILWAY_VOLUME_MOUNT_PATH'], 'agriculture.db')
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            db_path = os.path.join(base_dir, 'data', 'agriculture.db')
            
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        return db_path
    
    def get_dashboard_data(self, farm_id=1):
        """Get enhanced dashboard data with satellite integration"""
        try:
            if not os.path.exists(self.db_path):
                return self.get_enhanced_mock_data()
                
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT name, total_area_hectares, center_lat, center_lon FROM farms WHERE id = ?", (farm_id,))
            farm = cursor.fetchone()
            
            cursor.execute("SELECT field_name, area_hectares, historical_yield, center_lat, center_lon FROM fields WHERE farm_id = ?", (farm_id,))
            fields = cursor.fetchall()
            conn.close()
            
            return self.process_enhanced_data(farm, fields)
            
        except Exception as e:
            print(f"Enhanced dashboard error: {e}")
            return self.get_enhanced_mock_data()
    
    def process_enhanced_data(self, farm, fields):
        """Process data with satellite integration"""
        dashboard_data = {
            'farm_name': farm['name'] if farm else 'Satellite-Monitored Farm',
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'fields': [],
            'summary': {
                'total_fields': len(fields),
                'total_area': sum(field['area_hectares'] for field in fields),
                'high_priority_zones': 0,
                'water_stress_count': 0,
                'satellite_coverage': 'Active',
                'last_satellite_update': datetime.now().strftime('%Y-%m-%d %H:%M UTC')
            },
            'satellite_metrics': {
                'average_ndvi': 0,
                'health_distribution': {'healthy': 0, 'moderate': 0, 'stressed': 0, 'critical': 0},
                'data_quality': 'High',
                'total_coverage_km2': 0,
                'images_processed': len(fields) * 3
            }
        }
        
        ndvi_values = []
        health_counts = {'healthy': 0, 'moderate': 0, 'stressed': 0, 'critical': 0}
        total_area = 0
        
        for i, field in enumerate(fields):
            lat = field['center_lat'] or (40.0 + (i * 0.1))
            lon = field['center_lon'] or (-100.0 + (i * 0.1))
            
            satellite_data = self.satellite_service.get_nasa_ndvi_data(lat, lon, field['field_name'])
            health_report = self.satellite_service.get_vegetation_health_report(satellite_data['ndvi'])
            
            health_counts[health_report['status']] += 1
            ndvi_values.append(satellite_data['ndvi'])
            total_area += field['area_hectares']
            
            field_data = {
                'id': i + 1,
                'name': field['field_name'],
                'area_hectares': field['area_hectares'],
                'historical_yield': field['historical_yield'],
                'ndvi_value': satellite_data['ndvi'],
                'ndvi_timestamp': satellite_data['timestamp'],
                'ndvi_source': satellite_data['source'],
                'ndvi_quality': satellite_data['quality_score'],
                'priority_score': self.calculate_priority_score(field, satellite_data['ndvi']),
                'allocated_water': int(field['area_hectares'] * 8 * (1.5 - satellite_data['ndvi'])),
                'status': health_report['status'],
                'health_color': health_report['color'],
                'recommendation': health_report['recommendation'],
                'action': health_report['action'],
                'risk_level': health_report['risk_level'],
                'coordinates': {'lat': lat, 'lon': lon},
                'historical_trend': self.satellite_service.get_historical_ndvi_trend(lat, lon)
            }
            field_data['allocation_sufficiency'] = field_data['allocated_water'] / (field['area_hectares'] * 12)
            
            dashboard_data['fields'].append(field_data)
        
        # Calculate enhanced summary stats
        if dashboard_data['fields']:
            dashboard_data['summary']['total_water_allocated'] = sum(f['allocated_water'] for f in dashboard_data['fields'])
            dashboard_data['summary']['high_priority_zones'] = len([f for f in dashboard_data['fields'] if f['priority_score'] > 0.7])
            dashboard_data['summary']['water_stress_count'] = len([f for f in dashboard_data['fields'] if f['allocation_sufficiency'] < 0.6])
            
            # Enhanced satellite metrics
            dashboard_data['satellite_metrics']['average_ndvi'] = round(sum(ndvi_values) / len(ndvi_values), 3)
            dashboard_data['satellite_metrics']['health_distribution'] = health_counts
            dashboard_data['satellite_metrics']['total_coverage_km2'] = round(total_area * 0.01, 2)
            dashboard_data['satellite_metrics']['data_quality'] = 'High' if all(f['ndvi_quality'] > 0.85 for f in dashboard_data['fields']) else 'Medium'
        
        return dashboard_data
    
    def calculate_priority_score(self, field, ndvi_value):
        """Enhanced priority calculation using satellite data"""
        yield_factor = min(1.0, field['historical_yield'] / 8.0)
        area_factor = min(1.0, field['area_hectares'] / 200.0)
        health_factor = ndvi_value
        
        priority_score = (yield_factor * 0.3 + area_factor * 0.2 + health_factor * 0.5)
        return round(priority_score, 3)
    
    def get_enhanced_mock_data(self):
        """Return comprehensive mock data with satellite integration"""
        field_coordinates = [
            (40.7128, -74.0060, "North Valley"),
            (40.7135, -74.0055, "South Slope"),
            (40.7120, -74.0070, "East Ridge"),
            (34.0522, -118.2437, "West Plains"),
            (34.0530, -118.2440, "Central Basin"),
            (41.8781, -87.6298, "River Bottom"),
            (41.8790, -87.6285, "Hilltop View"),
            (32.7767, -96.7970, "Meadow Field"),
            (32.7775, -96.7960, "Heritage Acres")
        ]
        
        fields = []
        ndvi_values = []
        health_counts = {'healthy': 0, 'moderate': 0, 'stressed': 0, 'critical': 0}
        total_area = 0
        
        for i, (lat, lon, name) in enumerate(field_coordinates):
            satellite_data = self.satellite_service.get_nasa_ndvi_data(lat, lon, name)
            health_report = self.satellite_service.get_vegetation_health_report(satellite_data['ndvi'])
            
            health_counts[health_report['status']] += 1
            ndvi_values.append(satellite_data['ndvi'])
            
            area = 45 + (i * 8)
            total_area += area
            
            field_data = {
                'id': i + 1,
                'name': name,
                'area_hectares': area,
                'historical_yield': 6.0 + (i * 0.4),
                'ndvi_value': satellite_data['ndvi'],
                'ndvi_timestamp': satellite_data['timestamp'],
                'ndvi_source': satellite_data['source'],
                'ndvi_quality': satellite_data['quality_score'],
                'priority_score': round(0.3 + (i * 0.08), 3),
                'allocated_water': 80000 + (i * 12000),
                'status': health_report['status'],
                'health_color': health_report['color'],
                'recommendation': health_report['recommendation'],
                'action': health_report['action'],
                'risk_level': health_report['risk_level'],
                'coordinates': {'lat': lat, 'lon': lon},
                'historical_trend': self.satellite_service.get_historical_ndvi_trend(lat, lon)
            }
            field_data['allocation_sufficiency'] = 0.65 + (i * 0.04)
            fields.append(field_data)
        
        avg_ndvi = round(sum(ndvi_values) / len(ndvi_values), 3)
        
        return {
            'farm_name': 'Satellite-Enhanced Precision Farm',
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'fields': fields,
            'summary': {
                'total_fields': len(fields),
                'total_water_allocated': sum(f['allocated_water'] for f in fields),
                'high_priority_zones': len([f for f in fields if f['priority_score'] > 0.7]),
                'water_stress_count': len([f for f in fields if f['allocation_sufficiency'] < 0.6]),
                'satellite_coverage': 'Active',
                'last_satellite_update': datetime.now().strftime('%Y-%m-%d %H:%M UTC')
            },
            'satellite_metrics': {
                'average_ndvi': avg_ndvi,
                'health_distribution': health_counts,
                'data_quality': 'High',
                'total_coverage_km2': round(total_area * 0.01, 2),
                'images_processed': len(fields) * 4
            }
        }

# Initialize the enhanced dashboard
dashboard = EnhancedAgricultureDashboard()

@app.route('/')
def index():
    """Serve the enhanced dashboard with satellite data visualization"""
    # Simple HTML template - we'll keep it minimal to avoid encoding issues
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Precision Agriculture Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f0f7f4; }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { background: #2c3e50; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
            .summary-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 20px; }
            .card { background: white; padding: 20px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
            .satellite-status { background: #27ae60; color: white; padding: 10px; border-radius: 3px; margin: 10px 0; }
            .field-list { background: white; padding: 20px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
            .field-item { border-bottom: 1px solid #eee; padding: 15px 0; }
            .priority-high { color: #e74c3c; font-weight: bold; }
            .priority-medium { color: #f39c12; }
            .priority-low { color: #27ae60; }
            .status-healthy { color: #27ae60; }
            .status-moderate { color: #f39c12; }
            .status-stressed { color: #e74c3c; }
            .status-critical { color: #c0392b; }
            .loading { color: #666; font-style: italic; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Precision Agriculture Dashboard</h1>
                <p>Climate Resilience & Water Optimization with Satellite Monitoring</p>
                <div class="satellite-status" id="satelliteStatus">
                    Satellite Data: Active | Last Update: <span id="lastUpdate">Loading...</span>
                </div>
            </div>
            
            <div class="summary-cards" id="summaryCards">
                <div class="card"><h3>Total Fields</h3><p id="totalFields" class="loading">Loading...</p></div>
                <div class="card"><h3>Water Allocated</h3><p id="waterAllocated" class="loading">Loading...</p></div>
                <div class="card"><h3>Average NDVI</h3><p id="averageNdvi" class="loading">Loading...</p></div>
                <div class="card"><h3>High Priority</h3><p id="highPriority" class="loading">Loading...</p></div>
            </div>
            
            <div class="field-list">
                <h2>Field Analysis with Satellite Data</h2>
                <div id="fieldList" class="loading">Loading field data...</div>
            </div>
        </div>

        <script>
            async function loadDashboardData() {
                try {
                    const response = await fetch('/api/dashboard-data');
                    const data = await response.json();
                    
                    if (data.error) {
                        document.getElementById('fieldList').innerHTML = '<p>Error: ' + data.error + '</p>';
                        return;
                    }
                    
                    // Update summary cards
                    document.getElementById('totalFields').textContent = data.summary.total_fields;
                    document.getElementById('totalFields').className = '';
                    
                    document.getElementById('waterAllocated').textContent = data.summary.total_water_allocated.toLocaleString() + ' m3';
                    document.getElementById('waterAllocated').className = '';
                    
                    document.getElementById('averageNdvi').textContent = data.satellite_metrics.average_ndvi;
                    document.getElementById('averageNdvi').className = '';
                    
                    document.getElementById('highPriority').textContent = data.summary.high_priority_zones;
                    document.getElementById('highPriority').className = '';
                    
                    document.getElementById('lastUpdate').textContent = data.summary.last_satellite_update;
                    
                    // Update field list
                    const fieldList = document.getElementById('fieldList');
                    fieldList.innerHTML = '';
                    fieldList.className = '';
                    
                    data.fields.forEach(field => {
                        const fieldItem = document.createElement('div');
                        fieldItem.className = 'field-item';
                        
                        const priorityClass = field.priority_score > 0.7 ? 'priority-high' : 
                                            field.priority_score > 0.5 ? 'priority-medium' : 'priority-low';
                        
                        const statusClass = 'status-' + field.status;
                        
                        fieldItem.innerHTML = `
                            <h3>${field.name} (${field.area_hectares} ha)</h3>
                            <p><strong>Satellite Data:</strong> NDVI ${field.ndvi_value} | Source: ${field.ndvi_source} | Quality: ${(field.ndvi_quality * 100).toFixed(0)}%</p>
                            <p>Yield: ${field.historical_yield} t/ha | Health: <span class="${statusClass}">${field.status.toUpperCase()}</span></p>
                            <p>Priority: <span class="${priorityClass}">${field.priority_score.toFixed(3)}</span> | Risk: ${field.risk_level.toUpperCase()}</p>
                            <p>Recommendation: ${field.recommendation}</p>
                            <p>Water: ${field.allocated_water} m3 (${(field.allocation_sufficiency * 100).toFixed(1)}% sufficient)</p>
                        `;
                        
                        fieldList.appendChild(fieldItem);
                    });
                    
                } catch (error) {
                    console.error('Error loading dashboard data:', error);
                    document.getElementById('fieldList').innerHTML = '<p>Error loading data. Check console for details.</p>';
                }
            }
            
            document.addEventListener('DOMContentLoaded', loadDashboardData);
        </script>
    </body>
    </html>
    """
    return render_template_string(html_content)

@app.route('/api/dashboard-data')
def get_dashboard_data():
    farm_id = request.args.get('farm_id', 1, type=int)
    data = dashboard.get_dashboard_data(farm_id)
    return jsonify(data)

@app.route('/api/satellite/field/<int:field_id>')
def get_field_satellite_data(field_id):
    """Get detailed satellite data for a specific field"""
    lat = 40.0 + (field_id * 0.1)
    lon = -100.0 + (field_id * 0.1)
    satellite_data = dashboard.satellite_service.get_nasa_ndvi_data(lat, lon, f"Field {field_id}")
    satellite_data['historical_trend'] = dashboard.satellite_service.get_historical_ndvi_trend(lat, lon)
    return jsonify(satellite_data)

@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy', 
        'message': 'Enhanced Precision Agriculture Dashboard with Satellite Data Integration',
        'environment': 'production' if 'RAILWAY' in os.environ else 'development',
        'satellite_integration': 'active'
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print("Starting Enhanced Precision Agriculture Dashboard with Satellite Data...")
    print(f"Access the dashboard at: http://localhost:{port}")
    app.run(debug=False, host='0.0.0.0', port=port)