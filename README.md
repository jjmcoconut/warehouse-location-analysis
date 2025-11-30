# Warehouse Location Analysis

This project analyzes the geographic distribution and proximity of Amazon and Walmart warehouses globally, with a specific focus on the US market. It includes tools to geocode locations, visualize them on interactive maps, and perform strategic analysis using clustering algorithms.

## Features

-   **Global Geocoding**: Parses and geocodes warehouse lists for multiple countries (US, Europe, Asia, etc.) using the Nominatim API.
-   **Optimization**: Implements city-level caching to minimize API usage.
-   **Visualization**: Generates interactive HTML maps using `folium`.
-   **Proximity Filtering**: Reduces map clutter by filtering out warehouses within a 10km radius of each other.
-   **Strategic Selection**: Uses **K-Means Clustering** to identify a limited number of "strategic" locations (e.g., Max 7 for US/Europe) that best cover the regions.
-   **Competition Analysis**: Calculates the overlap of Walmart warehouses within a 20km radius of Amazon facilities in the US.

## Results

### Global Analysis
-   **Total Locations**: ~716 warehouses processed globally.
-   **Filtered Map**: Reduced to **503** locations after removing duplicates within 10km.
-   **Strategic Selection**: Selected **50** key locations globally (7 for US, 7 for Europe, 4 for other regions) to represent the network.

### US Competition (Amazon vs Walmart)
-   **Overlap**: **66.7%** of Walmart warehouses are within 20km of an Amazon warehouse.
-   **Proximity**: The median distance from a Walmart facility to the nearest Amazon facility is **7.16 km**.

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/YOUR_USERNAME/warehouse-location-analysis.git
    cd warehouse-location-analysis
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### 1. Geocoding (Optional)
Regenerate coordinate files from raw data:

```bash
# US Data
python3 fill_missing_coordinates.py
python3 geocode_walmart.py

# Global Data
python3 process_global_warehouses.py
```

### 2. Mapping & Analysis

**Global Maps:**
```bash
# Generate map of ALL locations
python3 map_global_warehouses.py

# Generate map with reduced clutter (10km filter)
python3 filter_warehouses.py
python3 map_filtered_warehouses.py

# Generate map of STRATEGIC locations (K-Means)
python3 select_strategic_locations.py
python3 map_strategic_locations.py
```

**US Competition Analysis:**
```bash
python3 analyze_locations.py
```

## Output Files

-   **Maps**:
    -   `amazon_global_map.html`: All global locations.
    -   `amazon_global_filtered_map.html`: Filtered (less cluttered) map.
    -   `amazon_strategic_map.html`: Strategic selection map (Top 50).
    -   `warehouse_map.html`: US Amazon vs Walmart comparison.
-   **Data**:
    -   `global_data/*.csv`: CSV files for each country/region.
    -   `amazon_global_filtered.csv`: Filtered global list.
    -   `amazon_strategic_locations.csv`: Strategic locations list.
