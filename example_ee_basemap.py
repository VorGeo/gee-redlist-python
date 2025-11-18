"""Example usage of create_country_map with Earth Engine basemaps."""

import ee
from gee_redlist.map import create_country_map
import os

def main():
    """Generate example maps with Earth Engine imagery as basemaps."""

    # Initialize Earth Engine
    print("Initializing Earth Engine...")
    google_cloud_project = 'goog-rle-assessments'
    print(f"GOOGLE_CLOUD_PROJECT = {google_cloud_project!r}")
    ee.Initialize(project=google_cloud_project)
    print("✓ Earth Engine initialized")

    # Example 1: Elevation basemap for Nepal
    print("\nCreating elevation map of Nepal...")
    elevation = ee.Image('USGS/SRTMGL1_003')
    nepal_path = create_country_map(
        'NP',
        'temp/nepal_elevation.png',
        ee_image=elevation,
        fill_color='none',  # Make country transparent to see elevation
        show_border=True,
        edge_color='red',
        edge_width=2.0,
        title='Nepal - Elevation Map'
    )
    print(f"✓ Nepal elevation map saved to: {nepal_path}")

    # Example 2
    print("\nTry creating topography map...")

    dem_glo30 = ee.ImageCollection("COPERNICUS/DEM/GLO30").select('DEM').mosaic()
    rgb_image = dem_glo30

    map_path = create_country_map(
        country_code='MX',
        output_path='temp/mexico_rgb.png',
        ee_image=rgb_image,
        clip_ee_image=True,
        fill_color='none',
        show_border=True,
        edge_color='black',
        edge_width=2.0,
        show_grid=True,
        show_surrounding_countries=False
    )
    print(f"✓ RGB map saved to: {map_path}")

if __name__ == "__main__":
    main()
