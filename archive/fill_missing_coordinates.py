import csv
import time
import urllib.request
import urllib.parse
import json
import os

INPUT_FILE = "amazon_warehouses_1.csv"
OUTPUT_FILE = "amazon_warehouses_filled.csv"

def get_coordinates(query):
    url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(query)}&format=json&limit=1"
    headers = {'User-Agent': 'AntigravityAgent/1.0 (internal-project)'}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            if data:
                return data[0]['lat'], data[0]['lon']
    except Exception as e:
        print(f"Error fetching {query}: {e}")
    return None, None

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return

    rows = []
    with open(INPUT_FILE, 'r') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            rows.append(row)

    # 1. Build Cache from existing data
    city_cache = {}
    for row in rows:
        city = row['City']
        state = row['State']
        lat = row['Latitude']
        lon = row['Longitude']
        
        if city and state and lat and lon:
            key = (city, state)
            # Only store if we don't have it, or maybe overwrite? 
            # First one found is fine.
            if key not in city_cache:
                city_cache[key] = (lat, lon)
    
    print(f"Initial cache size: {len(city_cache)} cities.")

    # 2. Fill missing data
    updated_rows = []
    total = len(rows)
    
    with open(OUTPUT_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for i, row in enumerate(rows):
            name = row['Name']
            city = row['City']
            state = row['State']
            lat = row['Latitude']
            lon = row['Longitude']
            
            if not lat or not lon:
                key = (city, state)
                if key in city_cache:
                    # Cache Hit
                    row['Latitude'], row['Longitude'] = city_cache[key]
                    print(f"[{i+1}/{total}] {name}: Used cache for {city}, {state}")
                else:
                    # Cache Miss - Fetch from API
                    query = f"{city}, {state}"
                    print(f"[{i+1}/{total}] {name}: Fetching '{query}'...")
                    new_lat, new_lon = get_coordinates(query)
                    
                    if new_lat and new_lon:
                        row['Latitude'] = new_lat
                        row['Longitude'] = new_lon
                        city_cache[key] = (new_lat, new_lon)
                        print(f"  -> Found: {new_lat}, {new_lon}")
                    else:
                        print(f"  -> Not found.")
                    
                    time.sleep(1.1) # Rate limit
            
            writer.writerow(row)
            updated_rows.append(row)

    print(f"Done. Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
