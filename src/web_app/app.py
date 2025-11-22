# src/web_app/app.py
from flask import Flask, render_template, jsonify, request
import sys
import os
import json
import sqlite3

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

app = Flask(__name__)

class SimpleAgricultureDashboard:
    def __init__(self):
        # Use absolute path for database
        self.db_path = self.get_database_path()
    
    def get_database_path(self):
        """Get the correct database path for both local and Railway deployment"""
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        db_path = os.path.join(base_dir, 'data', 'agriculture.db')
        
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        return db_path
    
    def get_dashboard_data(self, farm_id=1):
        """Get simple dashboard data directly from database"""
        try:
            print(f"Connecting to database at: {self.db_path}")
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get farm info
            cursor.execute("SELECT name, total_area_hectares FROM farms WHERE id = ?", (farm_id,))
            farm = cursor.fetchone()
            
            # Get fields data
            cursor.execute("""
                SELECT field_name, area_hectares, historical_yield, center_lat, center_lon 
                FROM fields WHERE farm_id = ?
            """, (farm_id,))
            fields = cursor.fetchall()
            
            # Get management zones
            cursor.execute("""
                SELECT zone_name, soil_health_score, historical_yield, water_priority 
                FROM management_zones WHERE farm_id = ? ORDER BY water_priority
            """, (farm_id,))
            zones = cursor.fetchall()
            
            # Get latest satellite data
            cursor.execute("""
                SELECT f.field_name, s.ndvi_value, s.capture_date
                FROM fields f
                LEFT JOIN satellite_data s ON f.id = s.field_id
                WHERE f.farm_id = ?
                ORDER BY s.capture_date DESC
            """, (farm_id,))
            satellite_data = cursor.fetchall()
            
            conn.close()
            
            # Create NDVI mapping
            ndvi_map = {}
            for row in satellite_data:
                if row['field_name'] not in ndvi_map:
                    ndvi_map[row['field_name']] = row['ndvi_value']
            
            # Prepare dashboard data
            dashboard_data = {
                'farm_name': farm['name'] if farm else 'Demo Farm',
                'analysis_date': 'Current',
                'fields': [],
                'summary': {
                    'total_fields': len(fields),
                    'total_area': sum(field['area_hectares'] for field in fields),
                    'high_priority_zones': len([zone for zone in zones if zone['water_priority'] == 1])
                }
            }
            
            # Add field data with simulated priorities
            for field in fields:
                ndvi_value = ndvi_map.get(field['field_name'], 0.5)
                
                # Simple priority calculation
                yield_factor = field['historical_yield'] / 4.0
                area_factor = field['area_hectares'] / 100.0
                priority_score = min(1.0, (yield_factor * 0.6 + area_factor * 0.3 + ndvi_value * 0.1))
                
                field_data = {
                    'name': field['field_name'],
                    'area_hectares': field['area_hectares'],
                    'historical_yield': field['historical_yield'],
                    'ndvi_value': ndvi_value,
                    'priority_score': round(priority_score, 3),
                    'allocated_water': int(field['area_hectares'] * 10 * priority_score),
                    'status': 'healthy' if ndvi_value > 0.6 else 'monitor' if ndvi_value > 0.4 else 'stressed'
                }
                field_data['allocation_sufficiency'] = field_data['allocated_water'] / (field['area_hectares'] * 15)
                
                dashboard_data['fields'].append(field_data)
            
            # Calculate summary stats
            if dashboard_data['fields']:
                dashboard_data['summary']['total_water_allocated'] = sum(f['allocated_water'] for f in dashboard_data['fields'])
                dashboard_data['summary']['average_ndvi'] = round(sum(f['ndvi_value'] for f in dashboard_data['fields']) / len(dashboard_data['fields']), 3)
                dashboard_data['summary']['water_stress_count'] = len([f for f in dashboard_data['fields'] if f['allocation_sufficiency'] < 0.5])
            
            return dashboard_data
            
        except Exception as e:
            print(f"Error getting dashboard data: {e}")
            return None

dashboard = SimpleAgricultureDashboard()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/dashboard-data')
def get_dashboard_data():
    farm_id = request.args.get('farm_id', 1, type=int)
    data = dashboard.get_dashboard_data(farm_id)
    
    if data is None:
        return jsonify({'error': 'No data found'}), 404
    
    return jsonify(data)

@app.route('/api/health')
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Precision Agriculture Dashboard is running'})

def create_basic_template(templates_dir):
    template_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Precision Agriculture Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
        .summary-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 20px; }
        .card { background: white; padding: 20px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .field-list { background: white; padding: 20px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .field-item { border-bottom: 1px solid #eee; padding: 10px 0; }
        .field-item:last-child { border-bottom: none; }
        .priority-high { color: #e74c3c; font-weight: bold; }
        .priority-medium { color: #f39c12; }
        .priority-low { color: #27ae60; }
        .status-healthy { color: #27ae60; }
        .status-monitor { color: #f39c12; }
        .status-stressed { color: #e74c3c; }
        .loading { color: #666; font-style: italic; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Precision Agriculture Dashboard</h1>
            <p>Climate Resilience & Water Optimization</p>
        </div>
        
        <div class="summary-cards" id="summaryCards">
            <div class="card">
                <h3>Total Fields</h3>
                <p id="totalFields" class="loading">Loading...</p>
            </div>
            <div class="card">
                <h3>Water Allocated</h3>
                <p id="waterAllocated" class="loading">Loading...</p>
            </div>
            <div class="card">
                <h3>Average NDVI</h3>
                <p id="averageNdvi" class="loading">Loading...</p>
            </div>
            <div class="card">
                <h3>High Priority</h3>
                <p id="highPriority" class="loading">Loading...</p>
            </div>
        </div>
        
        <div class="field-list">
            <h2>Field Analysis</h2>
            <div id="fieldList" class="loading">Loading field data...</div>
        </div>
    </div>

    <script>
        async function loadDashboardData() {
            try {
                console.log('Loading dashboard data...');
                const response = await fetch('/api/dashboard-data');
                const data = await response.json();
                
                console.log('Data received:', data);
                
                if (data.error) {
                    document.getElementById('fieldList').innerHTML = '<p>Error: ' + data.error + '</p>';
                    return;
                }
                
                // Update summary cards
                document.getElementById('totalFields').textContent = data.summary.total_fields;
                document.getElementById('totalFields').className = '';
                
                document.getElementById('waterAllocated').textContent = 
                    data.summary.total_water_allocated.toLocaleString() + ' m3';
                document.getElementById('waterAllocated').className = '';
                
                document.getElementById('averageNdvi').textContent = data.summary.average_ndvi;
                document.getElementById('averageNdvi').className = '';
                
                document.getElementById('highPriority').textContent = data.summary.high_priority_zones;
                document.getElementById('highPriority').className = '';
                
                // Update field list
                const fieldList = document.getElementById('fieldList');
                fieldList.innerHTML = '';
                fieldList.className = '';
                
                data.fields.forEach(field => {
                    const fieldItem = document.createElement('div');
                    fieldItem.className = 'field-item';
                    
                    const priorityClass = field.priority_score > 0.7 ? 'priority-high' : 
                                        field.priority_score > 0.5 ? 'priority-medium' : 'priority-low';
                    
                    fieldItem.innerHTML = `
                        <h3>${field.name}</h3>
                        <p>Area: ${field.area_hectares} ha | Yield: ${field.historical_yield} t/ha</p>
                        <p>NDVI: ${field.ndvi_value.toFixed(3)} | 
                           Priority: <span class="${priorityClass}">${field.priority_score.toFixed(3)}</span> | 
                           Status: <span class="status-${field.status}">${field.status.toUpperCase()}</span>
                        </p>
                        <p>Water: ${field.allocated_water} m3 (${(field.allocation_sufficiency * 100).toFixed(1)}% sufficient)</p>
                    `;
                    
                    fieldList.appendChild(fieldItem);
                });
                
            } catch (error) {
                console.error('Error loading dashboard data:', error);
                document.getElementById('fieldList').innerHTML = '<p>Error loading data. Check console for details.</p>';
            }
        }
        
        // Load data when page loads
        document.addEventListener('DOMContentLoaded', loadDashboardData);
    </script>
</body>
</html>"""
    
    with open(os.path.join(templates_dir, 'index.html'), 'w') as f:
        f.write(template_content)

# Railway production configuration
if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    # Create basic template
    template_file = os.path.join(templates_dir, 'index.html')
    if not os.path.exists(template_file):
        create_basic_template(templates_dir)
    
    # Get port from Railway environment variable or default to 5000
    port = int(os.environ.get("PORT", 5000))
    
    print("Starting Precision Agriculture Dashboard...")
    print(f"Access the dashboard at: http://localhost:{port}")
    app.run(debug=False, host='0.0.0.0', port=port)