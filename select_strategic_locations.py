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
        self.clusters = []

    def fit(self, data):
        # Initialize centroids randomly from data points
        if len(data) <= self.n_clusters:
            self.centroids = data
            self.clusters = [[p] for p in data]
            return

        self.centroids = random.sample(data, self.n_clusters)
        
        for _ in range(self.max_iter):
            # Assign points to nearest centroid
            self.clusters = [[] for _ in range(self.n_clusters)]
            for point in data:
                distances = [math.sqrt((point[0]-c[0])**2 + (point[1]-c[1])**2) for c in self.centroids]
                closest_idx = distances.index(min(distances))
                self.clusters[closest_idx].append(point)
            
            # Update centroids
            new_centroids = []
            for i, cluster in enumerate(self.clusters):
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

def calculate_silhouette_score(data, clusters, centroids):
    if len(clusters) < 2 or len(data) <= len(clusters):
        return -1

    scores = []
    
    # Flatten clusters to map points to their cluster index
    point_to_cluster = {}
    for i, cluster in enumerate(clusters):
        for point in cluster:
            point_to_cluster[point] = i

    for point in data:
        cluster_idx = point_to_cluster[point]
        own_cluster = clusters[cluster_idx]
        
        # Calculate a (mean intra-cluster distance)
        if len(own_cluster) > 1:
            a = sum(math.sqrt((point[0]-p[0])**2 + (point[1]-p[1])**2) for p in own_cluster if p != point) / (len(own_cluster) - 1)
        else:
            a = 0
            
        # Calculate b (mean nearest-cluster distance)
        b = float('inf')
        for i, cluster in enumerate(clusters):
            if i == cluster_idx:
                continue
            if not cluster:
                continue
            dist = sum(math.sqrt((point[0]-p[0])**2 + (point[1]-p[1])**2) for p in cluster) / len(cluster)
            b = min(b, dist)
            
        if b == float('inf'): # Should not happen if k > 1
            b = 0

        score = (b - a) / max(a, b) if max(a, b) > 0 else 0
        scores.append(score)
        
    return sum(scores) / len(scores)

def find_optimal_k(data, min_k=2, max_k=10):
    best_k = min_k
    best_score = -1
    
    # Ensure limits are valid relative to data size
    # We need at least k points to have k clusters
    effective_max = min(len(data), max_k)
    effective_min = min(len(data), min_k)
    
    if effective_max < 2:
        return effective_max
        
    if effective_min > effective_max:
        effective_min = effective_max

    print(f"  Searching for optimal k ({effective_min} to {effective_max})...")

    # If min and max are same, just return that
    if effective_min == effective_max:
        return effective_min

    for k in range(effective_min, effective_max + 1):
        kmeans = SimpleKMeans(n_clusters=k)
        kmeans.fit(data)
        score = calculate_silhouette_score(data, kmeans.clusters, kmeans.centroids)
        print(f"    k={k}: Silhouette Score = {score:.4f}")
        
        if score > best_score:
            best_score = score
            best_k = k
            
    return best_k

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
        
        # Define constraints based on region
        if region in ["usa", "europe"]:
            min_k = 4
            max_k = 7
        else:
            min_k = 2
            max_k = 4
            
        # Prepare data for clustering
        coords = [(w['Latitude'], w['Longitude']) for w in items]
        
        # Determine optimal K
        if count <= min_k:
            optimal_k = count
            print(f"Processing {region}: {count} locations (Too few for clustering, keeping all)")
        else:
            print(f"Processing {region}: {count} locations (Target k: {min_k}-{max_k})")
            optimal_k = find_optimal_k(coords, min_k=min_k, max_k=max_k)
        
        print(f"  -> Selected optimal k={optimal_k}")
        
        # Run Custom K-Means with optimal K
        kmeans = SimpleKMeans(n_clusters=optimal_k)
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
