import csv
import folium
import os
import glob

INPUT_DIR = "global_data"
OUTPUT_MAP = "amazon_global_map.html"

def main():
    # Create map centered on Europe/Africa view to start, zoom out
    m = folium.Map(location=[20, 0], zoom_start=2)
    
    # Colors for different regions/groups
    colors = {
        "canada": "red",
        "mexico": "green",
        "europe": "blue",
        "china": "purple",
        "japan": "orange",
        "india": "darkred",
        "australia": "darkblue",
        "brazil": "darkgreen",
        "egypt": "black",
        "saudi_arabia": "gray",
        "united_arab_emirates": "gray",
        "singapore": "pink",
        "pakistan": "lightgreen"
    }
    
    csv_files = glob.glob(os.path.join(INPUT_DIR, "*.csv"))
    
    for filename in csv_files:
        group_name = os.path.basename(filename).replace("amazon_", "").replace(".csv", "")
        color = colors.get(group_name, "cadetblue")
        
        print(f"Adding {group_name} ({color})...")
        
        with open(filename, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    lat = float(row['Latitude'])
                    lon = float(row['Longitude'])
                    name = row['Name']
                    city = row['City']
                    country = row['Country']
                    
                    folium.CircleMarker(
                        location=[lat, lon],
                        radius=5,
                        popup=f"<b>{name}</b><br>{city}, {country}",
                        color=color,
                        fill=True,
                        fill_color=color,
                        fill_opacity=0.7
                    ).add_to(m)
                except ValueError:
                    continue
                    
    # Add US Amazon Warehouses
    us_file = "amazon_warehouses_filled.csv"
    if os.path.exists(us_file):
        print(f"Adding United States (orange)...")
        with open(us_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    lat = float(row['Latitude'])
                    lon = float(row['Longitude'])
                    name = row['Name']
                    city = row['City']
                    state = row['State']
                    
                    folium.CircleMarker(
                        location=[lat, lon],
                        radius=5,
                        popup=f"<b>{name}</b><br>{city}, {state}, USA",
                        color="orange",
                        fill=True,
                        fill_color="orange",
                        fill_opacity=0.7
                    ).add_to(m)
                except ValueError:
                    continue

    m.save(OUTPUT_MAP)
    print(f"Map saved to {OUTPUT_MAP}")

if __name__ == "__main__":
    main()
