import pygrib
import pandas as pd
import numpy as np
import logging
import os
from tqdm import tqdm
from datetime import datetime
import geopandas as gpd
from shapely.geometry import Point

def load_world_countries(shapefile_path):
    """
    Load world countries from shapefile with optimization
    """
    try:
        # Use pathlib for robust path handling
        from pathlib import Path
        shapefile_path = Path(shapefile_path).resolve()
        
        # Read the shapefile using the resolved path
        world = gpd.read_file(str(shapefile_path))
        
        # Ensure CRS is set to WGS84
        world = world.to_crs("EPSG:4326")
        
        # Keep only necessary columns
        world = world[['NAME', 'ISO_A2', 'geometry']].copy()
        
        # Create spatial index
        world.sindex
        
        return world
    except Exception as e:
        print(f"Error loading shapefile: {e}")
        print(f"Attempted to load from path: {shapefile_path}")
        return None


def point_to_country(lat, lon, world_countries):
    """
    Convert lat/lon to country using spatial join
    
    :param lat: Latitude
    :param lon: Longitude
    :param world_countries: GeoDataFrame of countries
    :return: Dictionary with country information
    """
    if world_countries is None:
        return None
    
    point = Point(lon, lat)
    
    # Perform spatial join
    country_match = world_countries[world_countries.contains(point)]
    
    if not country_match.empty:
        return {
            'Country_code': country_match.iloc[0]['ISO_A2'],
            'Country': country_match.iloc[0]['NAME'],
            'WHO_region': ''  # You might want to map this separately
        }
    return None

def convert_grib_to_country_monthly_avg(grib_path, output_dir, shapefile_path):
    """
    Convert GRIB data to monthly country averages
    
    :param grib_path: Path to the GRIB file
    :param output_dir: Directory to save output CSV files
    :param shapefile_path: Path to the country boundaries shapefile
    """
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Load world countries
    world_countries = load_world_countries(shapefile_path)
    if world_countries is None:
        logger.error("Could not load world countries data. Exiting.")
        return
    
    logger.info(f"Opening GRIB file: {grib_path}")
    os.makedirs(output_dir, exist_ok=True)
    
    grbs = pygrib.open(grib_path)
    
    # Dictionary to store monthly averages by variable and country
    monthly_country_data = {}
    
    for grb in tqdm(grbs, desc="Processing GRIB messages"):
        data, lats, lons = grb.data()
        variable_name = grb.shortName
        valid_date = grb.validDate
        
        # Filter data from 2014 onwards
        if valid_date.year < 2014:
            continue
        
        # Ravel the data and coordinates
        flat_data = data.ravel()
        flat_lats = lats.ravel()
        flat_lons = lons.ravel()
        
        # Process each point
        for lat, lon, value in zip(flat_lats, flat_lons, flat_data):
            # Get country information
            country_info = point_to_country(lat, lon, world_countries)
            
            if country_info is None:
                continue
            
            # Create a unique key for month and country
            month_key = (valid_date.year, valid_date.month, 
                         country_info['Country_code'], 
                         country_info['Country'])
            
            # Initialize data structure if not exists
            if variable_name not in monthly_country_data:
                monthly_country_data[variable_name] = {}
            
            if month_key not in monthly_country_data[variable_name]:
                monthly_country_data[variable_name][month_key] = []
            
            monthly_country_data[variable_name][month_key].append(value)
    
    # Process and save results
    for variable_name, country_monthly_data in monthly_country_data.items():
        output_rows = []
        
        for (year, month, country_code, country), values in country_monthly_data.items():
            avg_value = np.mean(values)
            date_reported = datetime(year, month, 1)
            
            output_rows.append({
                'Date_reported': date_reported.strftime('%Y-%m-%d'),
                'Country_code': country_code,
                'Country': country,
                'WHO_region': '',  # You can map this if needed
                f'{variable_name}_avg': avg_value
            })
        
        # Convert to DataFrame and save
        output_df = pd.DataFrame(output_rows)
        output_file = os.path.join(output_dir, f"{variable_name}_monthly_country_avg.csv")
        output_df.to_csv(output_file, index=False)
        logger.info(f"Saved monthly averages for {variable_name} to {output_file}")

if __name__ == "__main__":
    # Paths - MODIFY THESE TO MATCH YOUR SYSTEM
    grib_file = "Datasets/environmental-data/5e1b8c695f14e2689a634453d41f3333.grib"
    output_dir = "environmental_data_monthly"
    
    # Path to the downloaded shapefile - YOU MUST UPDATE THIS
    shapefile_path = "ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp"
    
    convert_grib_to_country_monthly_avg(grib_file, output_dir, shapefile_path)