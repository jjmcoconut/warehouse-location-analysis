import csv
import re
import time
import urllib.request
import urllib.parse
import json
import os

INPUT_FILE = "amazon_global_raw.txt"
OUTPUT_DIR = "global_data"

# Define Groups
# Europe is a special group containing multiple countries.
EUROPE_COUNTRIES = [
    "Czech Republic", "France", "Germany", "Ireland", "Italy", "Poland", 
    "Slovakia", "Spain", "Turkey", "United Kingdom", "England", "Scotland", "Wales"
]

# Map sub-regions to main countries if needed (e.g. England -> UK if we wanted to group UK, but user said Europe is one group)
# Actually, the user said "Europe countries grouped into Europe one".
# So if I see "United Kingdom", it goes to "Europe" CSV.
# "England", "Scotland", "Wales" are under "United Kingdom" usually, but in the text they might be headers.
# Let's check the text structure.
# "United Kingdom" -> "England" -> ...
# So "England" is a sub-header of UK.
# But UK is in Europe. So it goes to Europe CSV.

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

def parse_global_data(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()

    data = {} # Key: Group Name, Value: List of warehouses
    
    current_group = None # The CSV file group (e.g. Canada, Europe, China)
    current_country = None # The actual country name (for geocoding context)
    current_state = None # State/Province
    
    # Heuristics for headers
    # We need to manually define the top-level sections based on the text provided.
    # The text has: Canada, Mexico, Europe, Asia, Oceania, South America, Africa.
    # Under Asia: China, Japan, India, Pakistan, Saudi Arabia, Singapore, UAE.
    # Under Oceania: Australia.
    # Under South America: Brazil.
    # Under Africa: Egypt.
    
    # Let's define a mapping of "Header" -> "Group"
    # If a header is a country in Europe, Group is Europe.
    # If a header is a country elsewhere, Group is that Country.
    
    # Known headers in the file (Top level or Country level)
    # We need to track hierarchy.
    
    # Let's try a state machine approach.
    
    # Top Level Regions (Context only, mostly)
    regions = ["North America", "Europe", "Asia", "Oceania", "South America", "Africa"] 
    # Note: "Canada" and "Mexico" are top level in the text provided (no "North America" header in the snippet? 
    # Wait, the snippet starts with "Canada".
    
    # Let's list known countries/regions to switch context.
    
    known_headers = {
        "Canada": "Canada",
        "Mexico": "Mexico",
        "Europe": "Europe", # Switch to Europe mode
        "Asia": "Asia", # Switch to Asia mode (expect countries next)
        "Oceania": "Oceania", # Switch context
        "South America": "South America",
        "Africa": "Africa",
        "United Kingdom": "Europe", # UK is in Europe group
        "Czech Republic": "Europe",
        "France": "Europe",
        "Germany": "Europe",
        "Ireland": "Europe",
        "Italy": "Europe",
        "Poland": "Europe",
        "Slovakia": "Europe",
        "Spain": "Europe",
        "Turkey": "Europe",
        "China": "China",
        "Japan": "Japan",
        "India": "India",
        "Pakistan": "Pakistan",
        "Saudi Arabia": "Saudi Arabia",
        "Singapore": "Singapore",
        "United Arab Emirates": "United Arab Emirates",
        "Australia": "Australia",
        "Brazil": "Brazil",
        "Egypt": "Egypt"
    }
    
    # Sub-headers that are NOT warehouses but states/provinces/regions
    # This is hard to distinguish from cities without a list.
    # But usually warehouses have codes like (YYC1) or are just city names.
    # States don't have codes usually.
    
    # Regex for codes: (ABC1)
    code_pattern = re.compile(r'\b([A-Z]{3,4}\d?)\b')
    
    # State tracking
    # If a line has no codes and is not a known header, it might be a state/province.
    # OR it might be a city with no code listed.
    # But most lines in the text have codes or are headers.
    
    # Let's iterate.
    
    # Special handling for "Asia", "Oceania", etc. -> These are just containers.
    # If we are in "Asia", the next header "China" sets Group=China.
    # If we are in "Europe", the next header "France" sets Group=Europe (keeps it), Country=France.
    
    context_region = None # Asia, Europe, etc.
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Clean citations
        clean_line = re.sub(r'\[.*?\]', '', line).strip()
        
        # Check if it's a known header
        if clean_line in known_headers:
            group = known_headers[clean_line]
            
            if clean_line in ["Asia", "Oceania", "South America", "Africa"]:
                context_region = clean_line
                current_group = None # Reset, wait for country
                current_country = None
                continue
                
            if clean_line == "Europe":
                context_region = "Europe"
                current_group = "Europe"
                current_country = None
                continue
                
            # It's a country
            if context_region == "Europe":
                current_group = "Europe"
                current_country = clean_line
            else:
                current_group = group
                current_country = clean_line
                
            current_state = None
            continue
            
        # If we have a current group, process as warehouse or state
        if current_group:
            # Check for codes
            parens_match = re.search(r'\((.*?)\)', clean_line)
            codes = []
            if parens_match:
                content = parens_match.group(1)
                found_codes = code_pattern.findall(content)
                for c in found_codes:
                    if c not in ["TBD", "TBA", "FC", "SC", "DS", "AL", "AMXL"]: # Filter noise
                        codes.append(c)
            
            # If no codes, is it a state?
            # Heuristic: If it doesn't look like a warehouse line (no parens, or parens with no codes), assume state.
            # Exception: "Beijing", "Shanghai" in China list have no codes in the text provided?
            # "Beijing" -> Just city name.
            # So for China, lines are cities.
            # For Canada, "Alberta" is state. "Calgary (YYC4...)" is city.
            
            # Let's assume if it has codes, it's a city/warehouse line.
            # If it has NO codes:
            #   If it's in China/Japan/India (Asia), it might be a city or state.
            #   In China list: "Beijing", "Chengdu" -> Cities.
            #   In Japan: "Chiba Prefecture" -> State. "Ichikawa (NRT1)" -> City.
            #   In UK: "England" -> Region. "Aylesford - DME4" -> City.
            
            # This is tricky. Let's try:
            # If line contains "Prefecture" or "Province" or "Region" -> State.
            # If line is in a list of known states? No.
            
            # Let's use the presence of codes as a strong signal.
            # If codes exist -> Warehouse Line.
            # If NO codes:
            #   If next line has codes -> Likely a State/Header.
            #   If next line has NO codes -> ???
            
            # Alternative: Just try to geocode it.
            # If it's a state, we might get a state centroid.
            # If it's a city, we get city.
            # But we want to associate the *next* lines with this state if it is one.
            
            # Let's look at specific patterns in the text.
            # Canada: "Alberta" (State), "Calgary..." (City)
            # UK: "England" (State-ish), "Aylesford..." (City)
            # China: "Beijing" (City, no code shown in snippet? Wait, snippet says "Beijing", "Chengdu". No codes?)
            #   Actually, the snippet for China just lists city names? "Beijing", "Chengdu".
            #   So for China, we treat lines as Cities.
            
            # Logic:
            # 1. Extract codes.
            # 2. Extract name (before parens).
            # 3. If codes found: It's a warehouse(s). Use Name as City.
            # 4. If NO codes found:
            #    Is it a known sub-region? (England, Scotland, Wales, ... Prefectures)
            #    Or is it China/Egypt where codes might be missing?
            #    If we are in China, assume it's a City.
            #    If we are in Canada/US/Europe/Japan, assume it's a State if no codes?
            #    Let's try: If line has no parens, treat as State, UNLESS Country is China/Egypt/Brazil (some parts).
            
            is_state_candidate = (not codes) and ("(" not in clean_line)
            
            # Special handling for China, Egypt, etc where codes might be missing
            if current_country in ["China", "Egypt", "Saudi Arabia", "United Arab Emirates"]:
                # Assume these are cities
                is_state_candidate = False
            
            if is_state_candidate:
                current_state = clean_line
                continue
                
            # It's a warehouse line
            # Name is text before parens
            if "(" in clean_line:
                city_name = clean_line.split("(")[0].strip()
            else:
                city_name = clean_line
                
            # Clean up " - " separators (UK: "Aylesford - DME4")
            if " - " in city_name:
                city_name = city_name.split(" - ")[0].strip()
            
            # If no codes, generate a dummy one or use City name
            if not codes:
                # If China, just use City Name
                codes = [city_name] # Placeholder code
            
            for code in codes:
                if current_group not in data:
                    data[current_group] = []
                
                # Construct full address for geocoding
                # City, State, Country
                query_parts = [city_name]
                if current_state:
                    query_parts.append(current_state)
                if current_country:
                    query_parts.append(current_country)
                elif current_group != "Europe": # If group is country
                    query_parts.append(current_group)
                
                full_query = ", ".join(query_parts)
                
                data[current_group].append({
                    "Name": f"Amazon_{code}",
                    "Code": code,
                    "City": city_name,
                    "State": current_state or "",
                    "Country": current_country or current_group,
                    "Query": full_query
                })

    return data

def process_and_save(data):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    # Cache
    cache = {}
    
    for group, items in data.items():
        filename = f"{OUTPUT_DIR}/amazon_{group.lower().replace(' ', '_')}.csv"
        print(f"Processing group: {group} ({len(items)} locations) -> {filename}")
        
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["Name", "Latitude", "Longitude", "City", "State", "Country", "Code"])
            writer.writeheader()
            
            for item in items:
                query = item['Query']
                
                # Check cache
                if query in cache:
                    lat, lon = cache[query]
                    print(f"  [Cache] {item['Name']}: {lat}, {lon}")
                else:
                    print(f"  Fetching {item['Name']} ({query})...")
                    lat, lon = get_coordinates(query)
                    time.sleep(1.1)
                    if lat:
                        cache[query] = (lat, lon)
                        print(f"    -> Found: {lat}, {lon}")
                    else:
                        print(f"    -> Not found")
                
                writer.writerow({
                    "Name": item['Name'],
                    "Latitude": lat if lat else "",
                    "Longitude": lon if lon else "",
                    "City": item['City'],
                    "State": item['State'],
                    "Country": item['Country'],
                    "Code": item['Code']
                })
                f.flush()

if __name__ == "__main__":
    data = parse_global_data(INPUT_FILE)
    process_and_save(data)
