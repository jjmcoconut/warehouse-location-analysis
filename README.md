# Warehouse Location Analysis

This project analyzes the geographic distribution and proximity of Amazon and Walmart warehouses in the United States. It includes tools to geocode warehouse locations from raw text lists and visualizes them on an interactive map to identify areas of high competition.

## Features

-   **Geocoding**: Converts warehouse lists (text/CSV) into geographic coordinates using the Nominatim API.
-   **Optimization**: Implements city-level caching to minimize API usage and speed up processing.
-   **Visualization**: Generates an interactive HTML map using `folium` to display warehouse locations.
-   **Analysis**: Calculates spatial statistics, including the overlap of Walmart warehouses within a 20km radius of Amazon facilities.

## Results

-   **Amazon Warehouses**: ~427 locations mapped.
-   **Walmart Warehouses**: 36 locations mapped.
-   **Competition Analysis**:
    -   **66.7%** of Walmart warehouses are within 20km of an Amazon warehouse.
    -   The median distance from a Walmart facility to the nearest Amazon facility is **7.16 km**.

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
If you want to regenerate the coordinate files from raw data:

```bash
# Geocode Amazon warehouses
python3 fill_missing_coordinates.py

# Geocode Walmart warehouses
python3 geocode_walmart.py
```

### 2. Analysis & Visualization
To generate the map and view overlap statistics:

```bash
python3 analyze_locations.py
```

This will create `warehouse_map.html` which you can open in any web browser.

## Files

-   `analyze_locations.py`: Main script for mapping and analysis.
-   `fill_missing_coordinates.py`: Geocoding script for Amazon data.
-   `geocode_walmart.py`: Geocoding script for Walmart data.
-   `amazon_warehouses_filled.csv`: Processed Amazon data with coordinates.
-   `walmart_warehouses.csv`: Processed Walmart data with coordinates.
-   `warehouse_map.html`: Interactive output map.
