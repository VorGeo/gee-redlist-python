"""
Google Earth Engine functions for Red List Ecosystem (RLE) assessments.

This module provides functions for calculating spatial metrics used in
IUCN Red List of Ecosystems assessments, including Extent of Occurrence (EOO).
"""

import ee
from typing import Optional


def get_default_ee_projection() -> ee.Projection:
    """
    Returns the default projection to use for RLE Assessments.

    Projection ESRI:54034 (World Cylindrical Equal Area)
    is used based on the grid defined in the document:
    `Global 10 x 10-km grids suitable for use in IUCN Red List of Ecosystems assessments`
    available at: https://www.iucnrle.org/rle-material-and-tools
    """

    wkt1 = """
        PROJCS["World_Cylindrical_Equal_Area",
            GEOGCS["WGS 84",
                DATUM["WGS_1984",
                    SPHEROID["WGS 84",6378137,298.257223563,
                        AUTHORITY["EPSG","7030"]],
                    AUTHORITY["EPSG","6326"]],
                PRIMEM["Greenwich",0],
                UNIT["Degree",0.0174532925199433]],
            PROJECTION["Cylindrical_Equal_Area"],
            PARAMETER["standard_parallel_1",0],
            PARAMETER["central_meridian",0],
            PARAMETER["false_easting",0],
            PARAMETER["false_northing",0],
            UNIT["metre",1,
                AUTHORITY["EPSG","9001"]],
            AXIS["Easting",EAST],
            AXIS["Northing",NORTH],
            AUTHORITY["ESRI","54034"]]
    """
    scale = 1e4
    proj = ee.Projection(
        crs=wkt1,
        transform=[scale, 0, 0, 0, scale, 0]
    )
    return proj


def make_eoo(
    class_img: ee.Image,
    geo: ee.Geometry = None,
    projection: ee.Projection = None,
    # scale: int = 1,
    max_error: int = 1,
    best_effort: bool = True
) -> ee.Geometry:
    """
    Calculate the Extent of Occurrence (EOO) polygon from a binary image.

    Takes a binary classification image and returns its Extent of Occurrence
    as a convex hull polygon. This is commonly used in IUCN Red List assessments
    to estimate the geographic range of a species or ecosystem.

    EOO is defined in
    Guidelines for the application of IUCN Red List of Ecosystems Categories and Criteria
    6.3.2. Methods for assessing criteria B1 and B2

    Extent of occurrence (EOO). The EOO of an ecosystem is the area (km2) of a minimum
    convex polygon – the smallest polygon in which no internal angle exceeds 180° that
    encompasses all known current spatial occurrences of the ecosystem type. The
    minimum convex polygon (also known as a convex hull) must not exclude any areas,
    discontinuities or disjunctions, regardless of whether the ecosystem can occur in those
    areas or not. Regions such as oceans (for terrestrial ecosystems), land (for coastal or
    marine ecosystems), or areas outside the study area (such as in a different country)
    must remain included within the minimum convex polygon to ensure that this
    standardized method is comparable across ecosystem types. In addition, these features
    contribute to spreading risks across the distribution of the ecosystem by making
    different parts of its distribution more spatially independent.

    Args:
        class_img: A binary ee.Image where pixels with value 1 represent presence
                   and 0/masked pixels represent absence.
        geo: The geometry to use for the reduction. Should encompass the area
             of interest for the analysis. If not provided, the geometry will be
             inferred from the class_img.
        projection: The projection to use for the reduction. Default is the 
                    World Cylindrical Equal_Area projection (ESRI:54034).
        max_error: The maximum error in meters for the convex hull calculation.
                   Default is 1.
        best_effort: If True, uses best effort mode which may be less accurate
                     but more likely to succeed for large areas. Default is True.

    Returns:
        An ee.Geometry representing the convex hull (EOO polygon) of all
        presence pixels in the input image.

    Example:
        >>> import ee
        >>> ee.Initialize()
        >>> # Create a binary habitat map
        >>> habitat = ee.Image(1).clip(region)
        >>> eoo_polygon = make_eoo(habitat)
        >>> print(eoo_polygon.area().getInfo())

    Note:
        The input image should be a binary classification where:
        - Value 1 indicates presence (included in EOO)
        - Value 0 or masked indicates absence (excluded from EOO)
    """
    
    if projection is None:
        projection = get_default_ee_projection()

    if geo is None:
        geo = class_img.geometry()

    # Mask the image to only include presence pixels (value = 1)
    # Then reduce to vectors to get all polygons
    eoo_poly = (
        class_img
        .updateMask(1)
        .reduceToVectors(
            crs=projection,
            geometry=geo,
            geometryType='polygon',
            bestEffort=best_effort
        )
        .geometry()
        .convexHull(maxError=max_error)
    )

    return eoo_poly


def area_km2(
    eoo_poly: ee.Geometry,
) -> ee.Number:
    """
    Calculate the area of the Extent of Occurrence (EOO) in square kilometers.

    Args:
        eoo_poly: An ee.Geometry representing the EOO polygon.

    Returns:
        An ee.Number representing the EOO area in square kilometers.
    """
    return eoo_poly.area().divide(1e6)