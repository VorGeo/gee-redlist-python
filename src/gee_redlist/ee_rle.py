"""
Google Earth Engine functions for Red List Ecosystem (RLE) assessments.

This module provides functions for calculating spatial metrics used in
IUCN Red List of Ecosystems assessments, including Extent of Occurrence (EOO).
"""

import ee
from typing import Optional


def make_eoo(
    class_img: ee.Image,
    geo: ee.Geometry,
    scale: int = 1,
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
    standardised method is comparable across ecosystem types. In addition, these features
    contribute to spreading risks across the distribution of the ecosystem by making
    different parts of its distribution more spatially independent.

    Args:
        class_img: A binary ee.Image where pixels with value 1 represent presence
                   and 0/masked pixels represent absence.
        geo: The geometry to use for the reduction. Should encompass the area
             of interest for the analysis.
        scale: The scale in meters at which to perform the reduction. Default is 1.
               Larger values will be faster but less precise.
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
        >>> region_geo = region.geometry()
        >>> eoo_polygon = make_eoo(habitat, region_geo, scale=30)
        >>> print(eoo_polygon.area().getInfo())

    Note:
        The input image should be a binary classification where:
        - Value 1 indicates presence (included in EOO)
        - Value 0 or masked indicates absence (excluded from EOO)
    """
    # Mask the image to only include presence pixels (value = 1)
    # Then reduce to vectors to get all polygons
    eoo_poly = (
        class_img
        .updateMask(1)
        .reduceToVectors(
            scale=scale,
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