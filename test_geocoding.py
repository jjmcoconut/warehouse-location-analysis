import urllib.request
import urllib.parse
import json

def test_geocoding():
    query = "Amazon BHM1 Bessemer Alabama"
    url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(query)}&format=json"
    headers = {'User-Agent': 'AntigravityAgent/1.0 (internal-test)'}
    
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_geocoding()
