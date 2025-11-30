import csv
import folium
from geopy.distance import geodesic
import statistics

AMAZON_FILE = "amazon_warehouses_filled.csv"
WALMART_FILE = "walmart_warehouses.csv"
OUTPUT_MAP = "warehouse_map.html"
OVERLAP_RADIUS_KM = 20

def load_warehouses(filename, source):
    warehouses = []
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                lat = float(row['Latitude'])
                lon = float(row['Longitude'])
                warehouses.append({
                    'name': row['Name'],
                    'lat': lat,
                    'lon': lon,
                    'city': row['City'],
                    'state': row['State'],
                    'source': source
                })
            except ValueError:
                continue # Skip if lat/lon missing or invalid
    return warehouses

def main():
    amazon_wh = load_warehouses(AMAZON_FILE, 'Amazon')
    walmart_wh = load_warehouses(WALMART_FILE, 'Walmart')
    
    print(f"Loaded {len(amazon_wh)} Amazon warehouses.")
    print(f"Loaded {len(walmart_wh)} Walmart warehouses.")
    
    # 1. Create Map
    # Center map on US roughly
    m = folium.Map(location=[39.8283, -98.5795], zoom_start=4)
    
    # Add Amazon markers
    for wh in amazon_wh:
        folium.CircleMarker(
            location=[wh['lat'], wh['lon']],
            radius=5,
            popup=f"{wh['name']}<br>{wh['city']}, {wh['state']}",
            color='orange',
            fill=True,
            fill_color='orange'
        ).add_to(m)
        
    # Add Walmart markers
    for wh in walmart_wh:
        folium.CircleMarker(
            location=[wh['lat'], wh['lon']],
            radius=7, # Slightly bigger to distinguish
            popup=f"{wh['name']}<br>{wh['city']}, {wh['state']}",
            color='blue',
            fill=True,
            fill_color='blue'
        ).add_to(m)
        
    m.save(OUTPUT_MAP)
    print(f"Map saved to {OUTPUT_MAP}")
    
    # 2. Analysis
    print("\n--- Analysis ---")
    print(f"Overlap Radius: {OVERLAP_RADIUS_KM} km")
    
    overlap_count = 0
    distances = []
    
    for w_wh in walmart_wh:
        w_loc = (w_wh['lat'], w_wh['lon'])
        min_dist = float('inf')
        nearest_amazon = None
        
        for a_wh in amazon_wh:
            a_loc = (a_wh['lat'], a_wh['lon'])
            dist = geodesic(w_loc, a_loc).km
            if dist < min_dist:
                min_dist = dist
                nearest_amazon = a_wh
        
        distances.append(min_dist)
        
        if min_dist <= OVERLAP_RADIUS_KM:
            overlap_count += 1
            # print(f"  Overlap: {w_wh['name']} is {min_dist:.2f} km from {nearest_amazon['name']}")
            
    avg_dist = statistics.mean(distances)
    median_dist = statistics.median(distances)
    
    print(f"Walmart warehouses within {OVERLAP_RADIUS_KM}km of an Amazon warehouse: {overlap_count} / {len(walmart_wh)} ({overlap_count/len(walmart_wh)*100:.1f}%)")
    print(f"Average distance to nearest Amazon warehouse: {avg_dist:.2f} km")
    print(f"Median distance to nearest Amazon warehouse: {median_dist:.2f} km")

if __name__ == "__main__":
    main()
