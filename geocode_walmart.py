import csv
import time
import urllib.request
import urllib.parse
import json
import os
import re

INPUT_FILE = "walmart_warehouses.txt"
OUTPUT_FILE = "walmart_warehouses.csv"

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

def parse_walmart_data(filename):
    warehouses = []
    with open(filename, 'r') as f:
        lines = f.readlines()
        
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Try splitting by tab first
        parts = line.split('\t')
        
        # If not enough parts, maybe it's spaces? But addresses have spaces.
        # Let's assume the user provided format is consistent-ish.
        # Code Address City State Zip
        # If tab split works (>= 3 parts), use it.
        
        code = ""
        address = ""
        city = ""
        state = ""
        zip_code = ""
        
        if len(parts) >= 4:
            code = parts[0].strip()
            address = parts[1].strip()
            city = parts[2].strip()
            state = parts[3].strip()
            if len(parts) > 4:
                zip_code = parts[4].strip()
        else:
            # Fallback for messy lines or space separated
            # "PHL2 Walmart PHL2n 2785 Commerce Center Blvd Bethlehem, PA 18015 PA PA 18015"
            # This looks like a mess. Let's try to extract what we can.
            # Maybe just use the first token as code?
            tokens = line.split()
            code = tokens[0]
            # It's hard to parse address from space separated without heuristics.
            # But let's look at the specific messy line:
            # PHL2	Walmart PHL2n 2785 Commerce Center Blvd Bethlehem, PA 18015	PA	PA	18015
            # If it was tab separated, it might be:
            # PHL2 [TAB] Walmart PHL2n ... [TAB] PA [TAB] PA ...
            # Let's trust the tab split if it exists.
            if len(parts) >= 2:
                 code = parts[0].strip()
                 # Maybe the address is the whole second part?
                 address = parts[1].strip()
                 # If city/state are missing, we might extract from address if it contains commas?
                 # "Bethlehem, PA 18015"
                 if "," in address:
                     addr_parts = address.split(',')
                     if len(addr_parts) >= 2:
                         city = addr_parts[-2].strip().split()[-1] # Last word before comma? No.
                         # "2785 Commerce Center Blvd Bethlehem"
                         # This is getting complicated.
                         # Let's just use the address as the query if city is missing.
            else:
                # No tabs?
                pass

        warehouses.append({
            "Name": f"Walmart_{code}",
            "Code": code,
            "Address": address,
            "City": city,
            "State": state,
            "Zip": zip_code
        })
    return warehouses

def main():
    warehouses = parse_walmart_data(INPUT_FILE)
    
    # City cache for fallback
    city_cache = {}
    
    with open(OUTPUT_FILE, 'w', newline='') as f:
        fieldnames = ['Name', 'Latitude', 'Longitude', 'City', 'State', 'Code', 'Address', 'Zip']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        total = len(warehouses)
        for i, w in enumerate(warehouses):
            print(f"Processing {i+1}/{total}: {w['Name']}")
            
            lat, lon = None, None
            
            # Strategy 1: Full Address
            query = f"{w['Address']}, {w['City']}, {w['State']} {w['Zip']}".strip()
            # Clean up double spaces or commas
            query = re.sub(r'\s+', ' ', query).strip(', ')
            
            print(f"  Query 1: {query}")
            lat, lon = get_coordinates(query)
            
            # Strategy 2: Address + City + State (No Zip)
            if not lat and w['Zip']:
                query = f"{w['Address']}, {w['City']}, {w['State']}".strip()
                print(f"  Query 2: {query}")
                lat, lon = get_coordinates(query)
                time.sleep(1.1)

            # Strategy 3: City + State (Cacheable)
            if not lat:
                # Check cache
                key = (w['City'], w['State'])
                if key in city_cache:
                    lat, lon = city_cache[key]
                    print(f"  Used cache for {w['City']}, {w['State']}")
                else:
                    query = f"{w['City']}, {w['State']}"
                    if not w['City'] or not w['State']:
                         # Fallback for messy lines: Try extracting from address if possible or just skip
                         pass
                    else:
                        print(f"  Query 3: {query}")
                        lat, lon = get_coordinates(query)
                        if lat:
                            city_cache[key] = (lat, lon)
                        time.sleep(1.1)
            
            if lat:
                print(f"  -> Found: {lat}, {lon}")
                writer.writerow({
                    'Name': w['Name'],
                    'Latitude': lat,
                    'Longitude': lon,
                    'City': w['City'],
                    'State': w['State'],
                    'Code': w['Code'],
                    'Address': w['Address'],
                    'Zip': w['Zip']
                })
            else:
                print(f"  -> Not found.")
                writer.writerow({
                    'Name': w['Name'],
                    'Latitude': '',
                    'Longitude': '',
                    'City': w['City'],
                    'State': w['State'],
                    'Code': w['Code'],
                    'Address': w['Address'],
                    'Zip': w['Zip']
                })
            
            f.flush()
            time.sleep(1.1)

if __name__ == "__main__":
    main()
