# -*- coding: utf-8 -*-
# src/web_app/app.py
from flask import Flask, render_template_string, jsonify, request
import sys
import os
import json
import sqlite3

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

app = Flask(__name__)

class SimpleAgricultureDashboard:
    def __init__(self):
        self.db_path = self.get_database_path()
    
    def get_database_path(self):
        """Get database path that works on both local and Railway"""
        # Try Railway's data directory first
        if 'RAILWAY_VOLUME_MOUNT_PATH' in os.environ:
            db_path = os.path.join(os.environ['RAILWAY_VOLUME_MOUNT_PATH'], 'agriculture.db')
        else:
            # Local development
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            db_path = os.path.join(base_dir, 'data', 'agriculture.db')
            
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        print(f"Database path: {db_path}")
        return db_path
    
    def get_dashboard_data(self, farm_id=1):
        """Get dashboard data with better error handling"""
        try:
            print(f"Attempting to connect to database at: {self.db_path}")
            
            # Check if database file exists
            if not os.path.exists(self.db_path):
                print("Database file not found, using mock data")
                return self.get_mock_data()
                
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # [Keep your existing database query code here]
            # Your database queries...
            
            conn.close()
            return dashboard_data
            
        except Exception as e:
            print(f"Database error: {e}")
            return self.get_mock_data()
    
    def get_mock_data(self):
        """Return consistent mock data for demo purposes"""
        return {
            'farm_name': 'Demo Farm',
            'analysis_date': 'Current',
            'summary': {
                'total_fields': 14,
                'total_water_allocated': 1250000,
                'average_ndvi': 0.78,
                'high_priority_zones': 3,
                'water_stress_count': 1
            },
            'fields': [
                {
                    'name': 'North Plot',
                    'area_hectares': 45,
                    'historical_yield': 8.2,
                    'ndvi_value': 0.85,
                    'priority_score': 0.82,
                    'allocated_water': 145000,
                    'status': 'healthy',
                    'allocation_sufficiency': 0.95
                },
                {
                    'name': 'South Plot',
                    'area_hectares': 38,
                    'historical_yield': 6.1,
                    'ndvi_value': 0.45,
                    'priority_score': 0.68,
                    'allocated_water': 95000,
                    'status': 'stressed',
                    'allocation_sufficiency': 0.72
                },
                {
                    'name': 'East Plot',
                    'area_hectares': 52,
                    'historical_yield': 7.8,
                    'ndvi_value': 0.92,
                    'priority_score': 0.45,
                    'allocated_water': 165000,
                    'status': 'healthy',
                    'allocation_sufficiency': 0.98
                }
            ]
        }

dashboard = SimpleAgricultureDashboard()

@app.route('/')
def index():
    """Serve the dashboard HTML directly (no template file needed)"""
    html_content = """
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Precision Agriculture Dashboard</title>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background-color: #f0f7f4; 
            color: #333;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
        }
        .header { 
            background: linear-gradient(135deg, #2c3e50, #4a6572); 
            color: white; 
            padding: 25px; 
            border-radius: 10px; 
            margin-bottom: 25px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        .header h1 {
            margin: 0;
            font-size: 2.2rem;
        }
        .header p {
            margin: 8px 0 0;
            font-size: 1.1rem;
            opacity: 0.9;
        }
        .summary-cards { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); 
            gap: 25px; 
            margin-bottom: 25px; 
        }
        .card { 
            background: white; 
            padding: 25px; 
            border-radius: 10px; 
            box-shadow: 0 4px 8px rgba(0,0,0,0.08);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            border-top: 4px solid #27ae60;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 15px rgba(0,0,0,0.1);
        }
        .card h3 {
            margin-top: 0;
            color: #2c3e50;
            font-size: 1rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .card p {
            font-size: 1.8rem;
            font-weight: bold;
            margin: 10px 0 0;
            color: #2c3e50;
        }
        .field-list { 
            background: white; 
            padding: 25px; 
            border-radius: 10px; 
            box-shadow: 0 4px 8px rgba(0,0,0,0.08);
        }
        .field-list h2 {
            margin-top: 0;
            color: #2c3e50;
            border-bottom: 2px solid #f0f7f4;
            padding-bottom: 10px;
        }
        .field-item { 
            border-bottom: 1px solid #eee; 
            padding: 20px 0; 
            transition: background-color 0.2s;
        }
        .field-item:hover {
            background-color: #f9fdfb;
            padding-left: 10px;
            padding-right: 10px;
            margin-left: -10px;
            margin-right: -10px;
            border-radius: 8px;
        }
        .field-item:last-child { 
            border-bottom: none; 
        }
        .field-item h3 {
            margin: 0 0 10px;
            color: #2c3e50;
            font-size: 1.3rem;
        }
        .priority-high { 
            color: #e74c3c; 
            font-weight: bold; 
            background-color: rgba(231, 76, 60, 0.1);
            padding: 2px 8px;
            border-radius: 4px;
        }
        .priority-medium { 
            color: #f39c12; 
            background-color: rgba(243, 156, 18, 0.1);
            padding: 2px 8px;
            border-radius: 4px;
        }
        .priority-low { 
            color: #27ae60; 
            background-color: rgba(39, 174, 96, 0.1);
            padding: 2px 8px;
            border-radius: 4px;
        }
        .status-healthy { 
            color: #27ae60; 
            font-weight: bold;
        }
        .status-monitor { 
            color: #f39c12; 
            font-weight: bold;
        }
        .status-stressed { 
            color: #e74c3c; 
            font-weight: bold;
        }
        .water-bar {
            height: 8px;
            background-color: #ecf0f1;
            border-radius: 4px;
            margin-top: 8px;
            overflow: hidden;
        }
        .water-fill {
            height: 100%;
            border-radius: 4px;
            background: linear-gradient(90deg, #3498db, #2ecc71);
        }
        .metric-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin-top: 10px;
        }
        .metric {
            display: flex;
            justify-content: space-between;
            padding: 5px 0;
        }
        .metric-label {
            font-weight: 500;
            color: #7f8c8d;
        }
        .metric-value {
            font-weight: 600;
        }
        .loading { 
            color: #666; 
            font-style: italic; 
        }
        @media (max-width: 768px) {
            .summary-cards {
                grid-template-columns: repeat(2, 1fr);
            }
            .metric-grid {
                grid-template-columns: 1fr;
            }
        }
        @media (max-width: 480px) {
            .summary-cards {
                grid-template-columns: 1fr;
            }
            body {
                padding: 10px;
            }
        }
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
                        <div class="metric-grid">
                            <div class="metric">
                                <span class="metric-label">Area:</span>
                                <span class="metric-value">${field.area_hectares} ha</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">Yield:</span>
                                <span class="metric-value">${field.historical_yield} t/ha</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">NDVI:</span>
                                <span class="metric-value">${field.ndvi_value.toFixed(3)}</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">Priority:</span>
                                <span class="${priorityClass}">${field.priority_score.toFixed(3)}</span>
                            </div>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Status:</span>
                            <span class="status-${field.status}">${field.status.toUpperCase()}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Water Allocation:</span>
                            <span class="metric-value">${field.allocated_water.toLocaleString()} m3 (${(field.allocation_sufficiency * 100).toFixed(1)}% sufficient)</span>
                        </div>
                        <div class="water-bar">
                            <div class="water-fill" style="width: ${field.allocation_sufficiency * 100}%"></div>
                        </div>
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
        
        // Add some interactivity
        document.addEventListener('DOMContentLoaded', function() {
            // Simulate loading animation for better UX
            setTimeout(() => {
                const cards = document.querySelectorAll('.card p.loading');
                cards.forEach(card => {
                    if (card.textContent === 'Loading...') {
                        card.textContent = '--';
                    }
                });
            }, 1500);
        });
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

@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy', 
        'message': 'Precision Agriculture Dashboard is running',
        'environment': 'production' if 'RAILWAY' in os.environ else 'development'
    })

# Railway production configuration
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print("Starting Precision Agriculture Dashboard...")
    print(f"Access the dashboard at: http://localhost:{port}")
    app.run(debug=False, host='0.0.0.0', port=port)