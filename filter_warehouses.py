import csv
import glob
import os
from geopy.distance import geodesic

GLOBAL_DATA_DIR = "global_data"
US_FILE = "amazon_warehouses_filled.csv"
OUTPUT_FILE = "amazon_global_filtered.csv"
FILTER_RADIUS_KM = 10.0

def load_warehouses():
    warehouses = []
    
    # Load Global Data
    csv_files = glob.glob(os.path.join(GLOBAL_DATA_DIR, "*.csv"))
    for filename in csv_files:
        group = os.path.basename(filename).replace("amazon_", "").replace(".csv", "")
        with open(filename, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    lat = float(row['Latitude'])
                    lon = float(row['Longitude'])
                    warehouses.append({
                        'Name': row['Name'],
                        'Latitude': lat,
                        'Longitude': lon,
                        'City': row['City'],
                        'State': row['State'],
                        'Country': row['Country'],
                        'Region': group
                    })
                except ValueError:
                    continue

    # Load US Data
    if os.path.exists(US_FILE):
        with open(US_FILE, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    lat = float(row['Latitude'])
                    lon = float(row['Longitude'])
                    warehouses.append({
                        'Name': row['Name'],
                        'Latitude': lat,
                        'Longitude': lon,
                        'City': row['City'],
                        'State': row['State'],
                        'Country': "USA",
                        'Region': "usa"
                    })
                except ValueError:
                    continue
                    
    return warehouses

def filter_warehouses(warehouses):
    kept = []
    skipped_count = 0
    
    print(f"Total warehouses before filtering: {len(warehouses)}")
    
    for i, wh in enumerate(warehouses):
        wh_loc = (wh['Latitude'], wh['Longitude'])
        is_too_close = False
        
        for kept_wh in kept:
            kept_loc = (kept_wh['Latitude'], kept_wh['Longitude'])
            distance = geodesic(wh_loc, kept_loc).km
            
            if distance <= FILTER_RADIUS_KM:
                is_too_close = True
                # print(f"Skipping {wh['Name']} (too close to {kept_wh['Name']}, {distance:.2f}km)")
                break
        
        if not is_too_close:
            kept.append(wh)
        else:
            skipped_count += 1
            
    print(f"Filtered out {skipped_count} warehouses.")
    print(f"Remaining warehouses: {len(kept)}")
    return kept

def save_filtered(warehouses):
    with open(OUTPUT_FILE, 'w', newline='') as f:
        fieldnames = ['Name', 'Latitude', 'Longitude', 'City', 'State', 'Country', 'Region']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(warehouses)
    print(f"Saved filtered list to {OUTPUT_FILE}")

def main():
    all_wh = load_warehouses()
    filtered_wh = filter_warehouses(all_wh)
    save_filtered(filtered_wh)

if __name__ == "__main__":
    main()
