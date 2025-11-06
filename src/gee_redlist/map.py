"""Generate PNG maps of countries using cartopy."""

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.io.shapereader import natural_earth
import cartopy.io.shapereader as shpreader


def create_country_map(
    country_name: str,
    output_path: str = None,
    show_surrounding_countries: bool = True,
    show_grid: bool = True,
    show_border: bool = True,
    title: str = None,
    fill_color: str = None,
    edge_color: str = 'black',
    edge_width: float = 1.5,
) -> str:
    """
    Create a PNG map of a specified country.

    Parameters
    ----------
    country_name : str
        Name of the country to map (e.g., 'Singapore', 'France', 'Brazil')
    output_path : str, optional
        Path where the PNG file should be saved. If None, defaults to '{country_name}.png'
    show_surrounding_countries : bool, optional
        Whether to show labels for surrounding countries. Default is True.
    show_grid : bool, optional
        Whether to show gridlines with lat/lon labels. Default is True.
    show_border : bool, optional
        Whether to show a border around the target country. Default is True.
    title : str, optional
        Custom title for the map. If None, defaults to 'Map of {country_name}'.
    fill_color : str, optional
        Color to fill the target country. Default is None (uses 'grey').
        Accepts any matplotlib color (named colors, hex codes, RGB tuples).
    edge_color : str, optional
        Color of the border around the target country. Default is 'black'.
        Only used if show_border is True.
    edge_width : float, optional
        Width of the border around the target country. Default is 1.5.
        Only used if show_border is True.

    Returns
    -------
    str
        Path to the saved PNG file

    Examples
    --------
    >>> create_country_map('Singapore')
    'Singapore.png'
    >>> create_country_map('France', 'maps/france_map.png')
    'maps/france_map.png'
    >>> create_country_map('Brazil', show_surrounding_countries=False)
    'brazil.png'
    >>> create_country_map('Kenya', show_grid=False, show_border=False, title='Kenya Wildlife Regions')
    'kenya.png'
    >>> create_country_map('Japan', fill_color='#ff6b6b', edge_color='darkred', edge_width=2.0)
    'japan.png'
    >>> create_country_map('Australia', fill_color='green', show_border=False)
    'australia.png'
    """
    if output_path is None:
        output_path = f"{country_name.lower().replace(' ', '_')}.png"

    # Create a figure and axis with a map projection
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

    # Add country borders and find the target country
    shpfilename = natural_earth(
        resolution='10m',
        category='cultural',
        name='admin_0_countries'
    )

    # Load country geometries
    reader = shpreader.Reader(shpfilename)
    countries = list(reader.records())

    # Find the target country and get its extent
    target_geometry = None
    target_name = None
    for country in countries:
        # Check multiple name fields for a match
        names_to_check = [
            country.attributes.get('NAME', ''),
            country.attributes.get('NAME_LONG', ''),
            country.attributes.get('ADMIN', '')
        ]

        if any(country_name.lower() in name.lower() for name in names_to_check):
            target_geometry = country.geometry
            target_name = country.attributes.get('NAME', country_name)
            break

    if target_geometry is None:
        raise ValueError(
            f"Country '{country_name}' not found. Please check the spelling or try a different name variant."
        )

    # Set map extent based on country bounds with some padding
    bounds = target_geometry.bounds
    padding = 2  # degrees
    extent = [
        bounds[0] - padding,
        bounds[2] + padding,
        bounds[1] - padding,
        bounds[3] + padding
    ]
    ax.set_extent(extent)

    # Add map features
    if show_surrounding_countries:
        ax.add_feature(cfeature.LAND, facecolor='white')
        ax.add_feature(cfeature.OCEAN, facecolor='lightblue')
        ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
        ax.add_feature(cfeature.BORDERS, linewidth=0.5, linestyle='-', alpha=0.5)
    else:
        # When not showing surrounding countries, show only white background
        ax.add_feature(cfeature.OCEAN, facecolor='white')
        ax.add_feature(cfeature.LAND, facecolor='white')

    geometry_kwargs = {
        'alpha': 0.7
    }
    if fill_color:
        geometry_kwargs['facecolor'] = fill_color
    else:
        geometry_kwargs['facecolor'] = 'white'
    if edge_color:
        geometry_kwargs['edgecolor'] = edge_color
    if edge_width:
        geometry_kwargs['linewidth'] = edge_width
 
    ax.add_geometries(
        [target_geometry],
        ccrs.PlateCarree(),
        **geometry_kwargs
    )

    # Label surrounding countries that are visible in the extent
    if show_surrounding_countries:
        from shapely.geometry import box
        extent_box = box(extent[0], extent[2], extent[1], extent[3])

        # Estimate label dimensions in map units (rough approximation)
        # Font size 8 with padding ~0.3 degrees per character
        lon_range = extent[1] - extent[0]
        lat_range = extent[3] - extent[2]
        char_width = lon_range * 0.02  # Approximate width per character
        char_height = lat_range * 0.03  # Approximate height

        for country in countries:
            # Skip the target country
            country_name_attr = country.attributes.get('NAME', '')
            if country_name_attr == target_name:
                continue

            # Check if country intersects with the map extent
            if country.geometry.intersects(extent_box):
                # Get the centroid for label placement using the visible portion
                try:
                    # Get the intersection of the country with the extent box
                    visible_portion = country.geometry.intersection(extent_box)

                    # Calculate centroid of the visible portion
                    if not visible_portion.is_empty:
                        centroid = visible_portion.centroid

                        # Verify centroid is within extent (should always be true, but safety check)
                        if (extent[0] <= centroid.x <= extent[1] and
                            extent[2] <= centroid.y <= extent[3]):

                            # Estimate label bounding box
                            label_width = len(country_name_attr) * char_width
                            label_height = char_height
                            label_box = box(
                                centroid.x - label_width / 2,
                                centroid.y - label_height / 2,
                                centroid.x + label_width / 2,
                                centroid.y + label_height / 2
                            )

                            # Check if label box fits within the visible portion of the country
                            if visible_portion.contains(label_box):
                                ax.text(
                                    centroid.x, centroid.y,
                                    country_name_attr.upper(),
                                    transform=ccrs.PlateCarree(),
                                    fontsize=8,
                                    ha='center',
                                    va='center',
                                    color='#333333',
                                    weight='normal',
                                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7, edgecolor='none')
                                )
                except:
                    # Skip if centroid calculation fails (e.g., for invalid geometries)
                    continue

    # Add gridlines
    if show_grid:
        gl = ax.gridlines(draw_labels=True, alpha=0.3)
        gl.top_labels = False
        gl.right_labels = False
    else:
        # When grid is off, remove the axes frame/border
        # For cartopy GeoAxes, we need to set the spines to invisible
        for spine in ax.spines.values():
            spine.set_visible(False)

    if title:  # Only add title if not empty string
        plt.title(title, fontsize=16, fontweight='bold')

    # Save the figure
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)

    return output_path


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) > 1:
        country = sys.argv[1]
        output = sys.argv[2] if len(sys.argv) > 2 else None
        result = create_country_map(country, output)
        print(f"Map saved to: {result}")
    else:
        print("Usage: python map.py <country_name> [output_path]")
        print("Example: python map.py Singapore")
