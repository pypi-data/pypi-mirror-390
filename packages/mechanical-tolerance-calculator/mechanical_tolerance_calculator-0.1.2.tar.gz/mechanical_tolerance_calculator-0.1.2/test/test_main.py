"""
Unit tests for the tolerances package
Run with: pytest tests/
"""

import pytest
from tolerances import (
    get_all_tolerances_for,
    get_camco_standard_tolerances_for,
    check_one_measurement_for,
    check_multiple_measurements_for
)


class TestGetAllTolerances:
    """Tests for get_all_tolerances_for function"""
    
    def test_housing_tolerances(self):
        """Test getting housing tolerances"""
        result = get_all_tolerances_for("housing")
        assert "type" in result
        assert result["type"] == "housingBores"
        assert "specifications" in result
    
    def test_shaft_tolerances(self):
        """Test getting shaft tolerances"""
        result = get_all_tolerances_for("shaft")
        assert "type" in result
        assert result["type"] == "shafts"
        assert "specifications" in result
    
    def test_shell_tolerances(self):
        """Test getting shell tolerances"""
        result = get_all_tolerances_for("shell")
        assert "type" in result
        assert result["type"] == "shellBores"
        assert "specifications" in result
    
    def test_invalid_material_type(self):
        """Test error handling for invalid material type"""
        result = get_all_tolerances_for("invalid")
        assert "error" in result
        assert "Unknown material type" in result["error"]
    
    def test_empty_string(self):
        """Test error handling for empty string"""
        result = get_all_tolerances_for("")
        assert "error" in result
        assert "cannot be empty" in result["error"]
    
    def test_non_string_input(self):
        """Test error handling for non-string input"""
        result = get_all_tolerances_for(123)
        assert "error" in result
        assert "must be a string" in result["error"]


class TestGetCamcoStandard:
    """Tests for get_camco_standard_tolerances_for function"""
    
    def test_housing_camco(self):
        """Test getting Camco housing tolerances"""
        result = get_camco_standard_tolerances_for("housing")
        assert "type" in result
        assert result["type"] == "housingBores"
        assert "specification" in result
    
    def test_shaft_camco(self):
        """Test getting Camco shaft tolerances"""
        result = get_camco_standard_tolerances_for("shaft")
        assert "type" in result
        assert result["type"] == "shafts"
        assert "specification" in result
    
    def test_shell_camco(self):
        """Test getting Camco shell tolerances"""
        result = get_camco_standard_tolerances_for("shell")
        assert "type" in result
        assert result["type"] == "shellBores"
        assert "specification" in result


class TestCheckOneMeasurement:
    """Tests for check_one_measurement_for function"""
    
    def test_valid_shaft_measurement(self):
        """Test checking a valid shaft measurement"""
        result = check_one_measurement_for("shaft", 5.98)
        assert "measurement" in result
        assert "nominal" in result
        assert "specification" in result
        assert "meets_specification" in result
        assert "meets_IT_tolerance" in result
    
    def test_invalid_measurement_type(self):
        """Test error handling for invalid measurement"""
        result = check_one_measurement_for("shaft", "not a number")
        assert "error" in result
        assert result["error"] is True
    
    def test_invalid_material_type(self):
        """Test error handling for invalid material type"""
        result = check_one_measurement_for("invalid", 5.0)
        assert "error" in result


class TestCheckMultipleMeasurements:
    """Tests for check_multiple_measurements_for function"""
    
    def test_valid_measurements(self):
        """Test checking multiple valid measurements"""
        measurements = [5.97, 5.98, 5.99, 6.00]
        result = check_multiple_measurements_for("shaft", measurements)
        assert "meets_specification" in result
        assert "meets_IT_Tolerance" in result
        assert "meets_final_compliance" in result
    
    def test_empty_measurements_array(self):
        """Test error handling for empty measurements array"""
        result = check_multiple_measurements_for("shaft", [])
        assert "error" in result
        assert "cannot be empty" in result["error"]
    
    def test_non_array_input(self):
        """Test error handling for non-array input"""
        result = check_multiple_measurements_for("shaft", "not an array")
        assert "error" in result
        assert "must be an array" in result["error"]
    
    def test_single_measurement_in_array(self):
        """Test checking a single measurement in array"""
        result = check_multiple_measurements_for("shaft", [5.98])
        assert "meets_specification" in result


class TestBoundaryConditions:
    """Tests for boundary conditions"""
    
    def test_measurement_at_lower_bound(self):
        """Test measurement at lower specification bound"""
        # This test depends on your actual tolerance data
        result = check_one_measurement_for("shaft", 3.0)
        assert "measurement" in result
    
    def test_measurement_at_upper_bound(self):
        """Test measurement at upper specification bound"""
        # This test depends on your actual tolerance data
        result = check_one_measurement_for("shaft", 6.0)
        assert "measurement" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])