import urllib.request
import urllib.parse
import json

def test_open_meteo(query):
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={urllib.parse.quote(query)}&count=1&format=json"
    print(f"Testing: {query}")
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            if 'results' in data:
                print(f"  Found: {data['results'][0]['name']} ({data['results'][0]['latitude']}, {data['results'][0]['longitude']})")
            else:
                print("  Not found")
    except Exception as e:
        print(f"  Error: {e}")

if __name__ == "__main__":
    queries = [
        "Amazon PHX3",
        "Amazon Bessemer",
        "Bessemer Alabama",
        "Amazon Fulfillment Center"
    ]
    for q in queries:
        test_open_meteo(q)
