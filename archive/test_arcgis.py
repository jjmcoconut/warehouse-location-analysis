import urllib.request
import urllib.parse
import json

def test_arcgis(query):
    # ArcGIS REST API
    url = f"https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates?SingleLine={urllib.parse.quote(query)}&f=json&maxLocations=1"
    print(f"Testing: {query}")
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            if 'candidates' in data and data['candidates']:
                loc = data['candidates'][0]['location']
                print(f"  Found: {data['candidates'][0]['address']} ({loc['y']}, {loc['x']})")
            else:
                print("  Not found")
    except Exception as e:
        print(f"  Error: {e}")

if __name__ == "__main__":
    queries = [
        "Amazon PHX3",
        "Amazon Bessemer Alabama",
        "Amazon Fulfillment Center MOB1",
        "Amazon Mobile Alabama"
    ]
    for q in queries:
        test_arcgis(q)
