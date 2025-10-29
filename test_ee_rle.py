"""Tests for ee_rle module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import ee
import ee_rle


# Test geometry coordinates - region in Asia
TEST_GEOMETRY_COORDS = [[[96.90049099947396, 28.66344485978154],
                          [96.63681912447396, 28.185183529731013],
                          [97.71347928072396, 27.46620702497436],
                          [98.94340660274452, 27.72538824708764],
                          [97.93320584322396, 28.528398342301788],
                          [97.38422117062748, 28.654760045064048]]]


def get_test_geometry():
    """Get test geometry (only call after ee.Initialize())."""
    return ee.Geometry.Polygon(TEST_GEOMETRY_COORDS)


class TestMakeEOO:
    """Tests for the make_eoo function."""

    @patch('ee_rle.ee')
    def test_make_eoo_basic(self, mock_ee):
        """Test that make_eoo calls the correct Earth Engine methods."""
        # Create mock objects for the chain of method calls
        mock_image = Mock()
        mock_masked = Mock()
        mock_vectors = Mock()
        mock_geometry = Mock()
        mock_hull = Mock()

        # Setup the chain of method calls
        mock_image.updateMask.return_value = mock_masked
        mock_masked.reduceToVectors.return_value = mock_vectors
        mock_vectors.geometry.return_value = mock_geometry
        mock_geometry.convexHull.return_value = mock_hull

        # Create a mock geometry for the region
        mock_geo = Mock()

        # Call the function
        result = ee_rle.make_eoo(mock_image, mock_geo)

        # Verify the chain of calls
        mock_image.updateMask.assert_called_once_with(1)
        mock_masked.reduceToVectors.assert_called_once_with(
            scale=1,
            geometry=mock_geo,
            geometryType='polygon',
            bestEffort=True
        )
        mock_vectors.geometry.assert_called_once()
        mock_geometry.convexHull.assert_called_once_with(maxError=1)

        # Verify the result is the convex hull
        assert result == mock_hull

    @patch('ee_rle.ee')
    def test_make_eoo_custom_parameters(self, mock_ee):
        """Test make_eoo with custom parameters."""
        mock_image = Mock()
        mock_masked = Mock()
        mock_vectors = Mock()
        mock_geometry = Mock()
        mock_hull = Mock()

        mock_image.updateMask.return_value = mock_masked
        mock_masked.reduceToVectors.return_value = mock_vectors
        mock_vectors.geometry.return_value = mock_geometry
        mock_geometry.convexHull.return_value = mock_hull

        mock_geo = Mock()

        # Call with custom parameters
        result = ee_rle.make_eoo(
            mock_image,
            mock_geo,
            scale=30,
            max_error=10,
            best_effort=False
        )

        # Verify custom parameters were passed correctly
        mock_masked.reduceToVectors.assert_called_once_with(
            scale=30,
            geometry=mock_geo,
            geometryType='polygon',
            bestEffort=False
        )
        mock_geometry.convexHull.assert_called_once_with(maxError=10)

    @patch('ee_rle.ee')
    def test_make_eoo_returns_geometry(self, mock_ee):
        """Test that make_eoo returns an ee.Geometry object."""
        mock_image = Mock()
        mock_geo = Mock()
        mock_hull = Mock()

        # Setup the full chain
        mock_image.updateMask.return_value.reduceToVectors.return_value.geometry.return_value.convexHull.return_value = mock_hull

        result = ee_rle.make_eoo(mock_image, mock_geo)

        assert result == mock_hull


class TestIntegrationWithRealEE:
    """Integration tests using real Earth Engine objects (requires authentication)."""

    @pytest.fixture(autouse=True)
    def setup_ee(self):
        """Initialize Earth Engine before each test."""
        try:
            ee.Initialize()
        except Exception:
            pytest.skip("Earth Engine not authenticated - skipping integration tests")

    def test_make_eoo_with_real_geometry(self):
        """Test make_eoo with real Earth Engine geometry."""
        test_geometry = get_test_geometry()

        # Create a simple binary image covering the test region
        # Using a constant image with value 1 (presence)
        test_image = ee.Image(1).clip(test_geometry)

        # Calculate EOO
        eoo_poly = ee_rle.make_eoo(test_image, test_geometry, scale=1000)

        # Verify result is an ee.Geometry
        assert isinstance(eoo_poly, ee.Geometry)

        # Verify the EOO is not empty (should have computed geometry)
        eoo_info = eoo_poly.getInfo()
        assert eoo_info is not None
        assert eoo_info['type'] in ['Polygon', 'MultiPolygon']

    def test_eoo_with_partial_coverage(self):
        """Test EOO calculation with partial habitat coverage."""
        test_geometry = get_test_geometry()

        # Create an image with only partial coverage (random sample)
        test_image = (
            ee.Image.random(42)
            .gt(0.7)  # Only keep pixels > 0.7 (30% coverage)
            .clip(test_geometry)
        )

        # Calculate EOO
        eoo_poly = ee_rle.make_eoo(test_image, test_geometry, scale=1000)

        # Verify result
        assert isinstance(eoo_poly, ee.Geometry)
        eoo_info = eoo_poly.getInfo()
        assert eoo_info is not None
