import csv
import folium

INPUT_FILE = "amazon_global_filtered.csv"
OUTPUT_MAP = "amazon_global_filtered_map.html"

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
        "pakistan": "lightgreen",
        "usa": "orange"
    }
    
    print(f"Reading {INPUT_FILE}...")
    
    with open(INPUT_FILE, 'r') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            try:
                lat = float(row['Latitude'])
                lon = float(row['Longitude'])
                name = row['Name']
                city = row['City']
                country = row['Country']
                region = row['Region']
                
                color = colors.get(region, "cadetblue")
                
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=5,
                    popup=f"<b>{name}</b><br>{city}, {country}",
                    color=color,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.7
                ).add_to(m)
                count += 1
            except ValueError:
                continue
                
    m.save(OUTPUT_MAP)
    print(f"Map saved to {OUTPUT_MAP} with {count} locations.")

if __name__ == "__main__":
    main()
