# charts.py
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def create_agriculture_charts(df):
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    
    # Chart 1: Water Allocation
    fields = df['field_name']
    water_alloc = df['allocated_water']
    ax1.barh(fields, water_alloc, color='skyblue')
    ax1.set_xlabel('Water Allocation m3')
    ax1.set_title('Water Allocation by Field')
    ax1.grid(axis='x', alpha=0.3)
    
    # Chart 2: Priority Scores
    ax2.bar(fields, df['resilience_priority'], color='lightgreen', alpha=0.7)
    ax2.set_ylabel('Priority Score')
    ax2.set_title('Field Priority Scores')
    ax2.tick_params(axis='x', rotation=45)
    ax2.grid(axis='y', alpha=0.3)
    
    # Chart 3: Yield vs NDVI
    scatter = ax3.scatter(df['historical_yield'], df['ndvi_health'], s=100, c=df['resilience_priority'], cmap='viridis')
    ax3.set_xlabel('Historical Yield t/ha')
    ax3.set_ylabel('NDVI Health Index')
    ax3.set_title('Yield vs Crop Health')
    plt.colorbar(scatter, ax=ax3)
    
    # Chart 4: Water Sufficiency
    colors = []
    for x in df['allocation_sufficiency']:
        if x < 0.5:
            colors.append('red')
        elif x < 0.7:
            colors.append('orange')
        else:
            colors.append('green')
            
    ax4.bar(fields, df['allocation_sufficiency']*100, color=colors, alpha=0.7)
    ax4.set_ylabel('Allocation Sufficiency %')
    ax4.set_title('Water Allocation Sufficiency')
    ax4.tick_params(axis='x', rotation=45)
    ax4.axhline(y=50, color='red', linestyle='--', alpha=0.5, label='Critical Level')
    ax4.legend()
    ax4.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('agriculture_charts.png', dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    data = {
        'field_name': ['North_Hills', 'South_Valley', 'East_Plateau', 'West_Plains'],
        'allocated_water': [885, 104, 1053, 210],
        'resilience_priority': [0.773, 0.091, 0.920, 0.184],
        'historical_yield': [3.4, 2.7, 3.6, 2.8],
        'ndvi_health': [0.68, 0.42, 0.72, 0.51],
        'allocation_sufficiency': [0.738, 0.106, 0.780, 0.236]
    }
    df = pd.DataFrame(data)
    create_agriculture_charts(df)
    print("Charts created successfully!")
    input("Press Enter to exit...")