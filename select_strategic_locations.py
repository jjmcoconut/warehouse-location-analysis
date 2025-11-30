import csv
import glob
import os
import random
import math
from geopy.distance import geodesic

GLOBAL_DATA_DIR = "global_data"
US_FILE = "amazon_warehouses_filled.csv"
OUTPUT_FILE = "amazon_strategic_locations.csv"

# Configuration
LIMITS = {
    "usa": 7,
    "europe": 7,
    "default": 4
}

class SimpleKMeans:
    def __init__(self, n_clusters, max_iter=100):
        self.n_clusters = n_clusters
        self.max_iter = max_iter
        self.centroids = []

    def fit(self, data):
        # Initialize centroids randomly from data points
        if len(data) <= self.n_clusters:
            self.centroids = data
            return

        self.centroids = random.sample(data, self.n_clusters)
        
        for _ in range(self.max_iter):
            # Assign points to nearest centroid
            clusters = [[] for _ in range(self.n_clusters)]
            for point in data:
                distances = [math.sqrt((point[0]-c[0])**2 + (point[1]-c[1])**2) for c in self.centroids]
                closest_idx = distances.index(min(distances))
                clusters[closest_idx].append(point)
            
            # Update centroids
            new_centroids = []
            for i, cluster in enumerate(clusters):
                if not cluster: # Handle empty cluster
                    new_centroids.append(self.centroids[i])
                    continue
                
                lat_sum = sum(p[0] for p in cluster)
                lon_sum = sum(p[1] for p in cluster)
                new_centroids.append((lat_sum/len(cluster), lon_sum/len(cluster)))
            
            # Check convergence (simple check)
            if new_centroids == self.centroids:
                break
            self.centroids = new_centroids

    def predict(self, data):
        pass # Not needed for this use case

def load_warehouses():
    warehouses_by_region = {}
    
    # Load Global Data
    csv_files = glob.glob(os.path.join(GLOBAL_DATA_DIR, "*.csv"))
    for filename in csv_files:
        group = os.path.basename(filename).replace("amazon_", "").replace(".csv", "")
        if group not in warehouses_by_region:
            warehouses_by_region[group] = []
            
        with open(filename, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    lat = float(row['Latitude'])
                    lon = float(row['Longitude'])
                    warehouses_by_region[group].append({
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
        if "usa" not in warehouses_by_region:
            warehouses_by_region["usa"] = []
        with open(US_FILE, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    lat = float(row['Latitude'])
                    lon = float(row['Longitude'])
                    warehouses_by_region["usa"].append({
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
                    
    return warehouses_by_region

def select_strategic(warehouses_by_region):
    selected_warehouses = []
    
    for region, items in warehouses_by_region.items():
        count = len(items)
        limit = LIMITS.get(region, LIMITS["default"])
        
        print(f"Processing {region}: {count} locations (Limit: {limit})")
        
        if count <= limit:
            print(f"  -> Keeping all {count} locations.")
            selected_warehouses.extend(items)
            continue
            
        # Prepare data for clustering
        coords = [(w['Latitude'], w['Longitude']) for w in items]
        
        # Run Custom K-Means
        kmeans = SimpleKMeans(n_clusters=limit)
        kmeans.fit(coords)
        centers = kmeans.centroids
        
        # Find closest actual warehouse to each center
        for center in centers:
            min_dist = float('inf')
            closest_wh = None
            
            for wh in items:
                dist = geodesic(center, (wh['Latitude'], wh['Longitude'])).km
                if dist < min_dist:
                    min_dist = dist
                    closest_wh = wh
            
            if closest_wh and closest_wh not in selected_warehouses:
                selected_warehouses.append(closest_wh)
                print(f"  -> Selected: {closest_wh['Name']} ({closest_wh['City']})")
                
    return selected_warehouses

def save_strategic(warehouses):
    with open(OUTPUT_FILE, 'w', newline='') as f:
        fieldnames = ['Name', 'Latitude', 'Longitude', 'City', 'State', 'Country', 'Region']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(warehouses)
    print(f"Saved {len(warehouses)} strategic locations to {OUTPUT_FILE}")

def main():
    data = load_warehouses()
    strategic = select_strategic(data)
    save_strategic(strategic)

if __name__ == "__main__":
    main()
