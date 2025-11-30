import urllib.request
import urllib.parse
import json

def test_query(query):
    url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(query)}&format=json"
    headers = {'User-Agent': 'AntigravityAgent/1.0 (internal-test)'}
    print(f"Testing: {query}")
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            if data:
                print(f"  Found: {data[0]['display_name']} ({data[0]['lat']}, {data[0]['lon']})")
            else:
                print("  Not found")
    except Exception as e:
        print(f"  Error: {e}")

if __name__ == "__main__":
    queries = [
        "Amazon MOB1 Mobile Alabama",
        "Amazon Fulfillment Center MOB1",
        "Amazon MOB1",
        "Amazon Fulfillment Center Mobile AL",
        "Amazon Mobile Alabama"
    ]
    for q in queries:
        test_query(q)
