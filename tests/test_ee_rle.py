"""Tests for ee_rle module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import ee
from gee_redlist import ee_rle


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

    @patch('gee_redlist.ee_rle.ee')
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
        # convexHull is called twice (workaround for GEE bug), so we check it was called with maxError=1
        mock_geometry.convexHull.assert_called_with(maxError=1)

        # # Verify the result is the final convex hull (after second call)
        # assert result == mock_hull.convexHull.return_value

    @patch('gee_redlist.ee_rle.ee')
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
            max_error=10,
            best_effort=False
        )

        # Verify custom parameters were passed correctly
        mock_masked.reduceToVectors.assert_called_once_with(
            scale=1,
            geometry=mock_geo,
            geometryType='polygon',
            bestEffort=False
        )
        # convexHull is called twice, check it was called with custom maxError
        mock_geometry.convexHull.assert_called_with(maxError=10)

    @patch('gee_redlist.ee_rle.ee')
    def test_make_eoo_returns_geometry(self, mock_ee):
        """Test that make_eoo returns an ee.Geometry object."""
        mock_image = Mock()
        mock_geo = Mock()
        mock_hull = Mock()
        mock_hull_final = Mock()

        # Setup the full chain - convexHull is called twice
        mock_hull.convexHull.return_value = mock_hull_final
        mock_image.updateMask.return_value.reduceToVectors.return_value.geometry.return_value.convexHull.return_value = mock_hull

        result = ee_rle.make_eoo(mock_image, mock_geo)

        assert result == mock_hull_final


class TestAreaKm2:
    """Tests for the area_km2 function."""

    @patch('gee_redlist.ee_rle.ee')
    def test_area_km2_basic(self, mock_ee):
        """Test that area_km2 calculates area correctly."""
        # Create mock geometry with area
        mock_geometry = Mock()
        mock_area = Mock()
        mock_area_km2 = Mock()

        mock_geometry.area.return_value = mock_area
        mock_area.divide.return_value = mock_area_km2

        result = ee_rle.area_km2(mock_geometry)

        # Verify area was called
        mock_geometry.area.assert_called_once()
        # Verify division by 1e6 (convert m² to km²)
        mock_area.divide.assert_called_once_with(1e6)
        # Verify result
        assert result == mock_area_km2

    @patch('gee_redlist.ee_rle.ee')
    def test_area_km2_returns_ee_number(self, mock_ee):
        """Test that area_km2 returns an ee.Number."""
        mock_geometry = Mock()
        mock_result = Mock()
        mock_geometry.area.return_value.divide.return_value = mock_result

        result = ee_rle.area_km2(mock_geometry)

        assert result == mock_result


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
        eoo_poly = ee_rle.make_eoo(test_image, test_geometry)

        # Verify result is an ee.Geometry
        assert isinstance(eoo_poly, ee.Geometry)

        # Verify the EOO is not empty (should have computed geometry)
        eoo_info = eoo_poly.getInfo()
        assert eoo_info is not None
        assert eoo_info['type'] in ['Polygon', 'MultiPolygon']

    def test_area_km2_with_real_geometry(self):
        """Test area_km2 with real Earth Engine geometry.
        
        Test based on:
        https://github.com/red-list-ecosystem/gee-redlist/blob/4c58f8d1adc2853dd9d1be295f9def37cbe9f4a6/Modules/functionTests
        """
        test_geometry = get_test_geometry()

        # Create a simple binary image
        elevation = ee.Image('USGS/SRTMGL1_003').clip(test_geometry)
        test_image = ee.Image(1).clip(test_geometry).updateMask(elevation.gte(4500))

        # Calculate EOO polygon
        eoo_poly = ee_rle.make_eoo(
            class_img=test_image,
            geo=test_geometry
        )

        # Calculate area using area_km2
        area = ee_rle.area_km2(eoo_poly)

        # Verify result is an ee.Number
        assert isinstance(area, ee.Number)

        # Get the actual value and verify it's reasonable
        area_val = area.getInfo()
        assert abs(area_val - 12634.46) < 1

    def test_export_fractional_coverage_on_aoo_grid(self):
        """Test export_fractional_coverage_on_aoo_grid with real Earth Engine objects."""
        test_geometry = get_test_geometry()

        # Create a simple binary image covering the test region
        test_image = ee.Image('projects/goog-rle-assessments/assets/mm_ecosys_v7b').eq(52).selfMask()

        # Call the export function
        task = ee_rle.export_fractional_coverage_on_aoo_grid(
            class_img=test_image,
            asset_id='projects/goog-rle-assessments/assets/integration_test_export',
            export_description='integration_test_export_fractionalCoverage',
            max_pixels=65536
        )

        # Verify a task was returned
        assert task is not None
        assert isinstance(task.id, str)
        assert len(task.id) > 0
        assert task.task_type == 'EXPORT_IMAGE'
        # assert task.state in ['READY', 'RUNNING', 'COMPLETED']

        # Verify the task was created in Earth Engine
        # We can check the task status
        task_list = ee.batch.Task.list()
        task_ids = [task.id for task in task_list]
        assert task.id in task_ids

        # Cancel the task to clean up (we don't actually want to export)
        task.cancel()
