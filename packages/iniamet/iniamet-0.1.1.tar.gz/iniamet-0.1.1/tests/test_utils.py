"""
Tests for utility functions.
"""
from iniamet.utils import (
    get_region_code,
    REGION_MAP,
    VARIABLE_INFO
)


class TestRegionMapping:
    """Test region code mapping."""
    
    def test_get_region_code_by_name(self):
        """Test getting region code by name."""
        assert get_region_code("Ñuble") == "R16"
        assert get_region_code("Maule") == "R07"
        assert get_region_code("Metropolitana") == "R13"
    
    def test_get_region_code_case_insensitive(self):
        """Test region code lookup is case insensitive."""
        assert get_region_code("ñuble") == "R16"
        assert get_region_code("MAULE") == "R07"
    
    def test_get_region_code_by_code(self):
        """Test getting region code when already a code."""
        assert get_region_code("R16") == "R16"
        assert get_region_code("R07") == "R07"
    
    def test_get_region_code_invalid(self):
        """Test getting region code for invalid input."""
        assert get_region_code("Invalid Region") is None
    
    def test_region_map_completeness(self):
        """Test that REGION_MAP has all 16 regions."""
        assert len(REGION_MAP) == 16
        assert "R01" in REGION_MAP
        assert "R16" in REGION_MAP


class TestVariableMapping:
    """Test variable mapping functionality."""
    
    def test_variable_info_has_temperature(self):
        """Test that temperature variables are in the map."""
        assert 2002 in VARIABLE_INFO
        assert VARIABLE_INFO[2002]["nombre"].lower().find("temperatura") != -1
    
    def test_variable_info_has_precipitation(self):
        """Test that precipitation variable is in the map."""
        # Precipitation might be 2003 or check what's actually in VARIABLE_INFO
        found_precip = False
        for var_id, var_info in VARIABLE_INFO.items():
            if "precipitación" in var_info["nombre"].lower():
                found_precip = True
                break
        assert found_precip
    
    def test_variable_info_structure(self):
        """Test that variable map entries have correct structure."""
        for var_id, var_info in VARIABLE_INFO.items():
            assert isinstance(var_id, int)
            assert "nombre" in var_info
            assert "unidad" in var_info
            assert isinstance(var_info["nombre"], str)
            assert isinstance(var_info["unidad"], str)


class TestUtilityHelpers:
    """Test utility helper functions."""
    
    def test_region_list_valid(self):
        """Test that all regions in REGION_MAP are valid."""
        for code, name in REGION_MAP.items():
            assert code.startswith("R")
            assert len(code) == 3  # R01, R02, etc.
            assert isinstance(name, str)
            assert len(name) > 0
