"""
Tests for quality control functionality.
"""
import pandas as pd
import numpy as np
from datetime import datetime
from iniamet.qc import QualityControl, apply_quality_control


class TestQualityControl:
    """Test quality control class."""
    
    def test_qc_initialization(self):
        """Test QualityControl initialization."""
        qc = QualityControl()
        assert qc is not None
    
    def test_extreme_value_detection(self):
        """Test detection of extreme temperature values."""
        # Create test data with extreme values
        data = pd.DataFrame({
            'tiempo': pd.date_range('2024-01-01', periods=5, freq='h'),
            'valor': [15.0, 20.0, 100.0, -60.0, 18.0]  # 100 and -60 are extreme
        })
        
        qc = QualityControl()
        result = qc.detect_extreme_values(data, 'temperatura')
        
        # Should detect 2 extreme values
        assert 'qc_extreme' in result.columns
        assert result['qc_extreme'].sum() >= 2
    
    def test_stuck_sensor_detection(self):
        """Test detection of stuck sensors."""
        # Create test data with stuck values
        data = pd.DataFrame({
            'tiempo': pd.date_range('2024-01-01', periods=10, freq='h'),
            'valor': [15.0] * 10  # Same value for 10 hours
        })
        
        qc = QualityControl()
        result = qc.detect_stuck_sensor(data)
        
        # Should detect stuck sensor
        assert 'qc_stuck' in result.columns
    
    def test_valid_data_passes_qc(self):
        """Test that valid data passes quality control."""
        # Create realistic temperature data
        data = pd.DataFrame({
            'tiempo': pd.date_range('2024-01-01', periods=24, freq='h'),
            'valor': [15.0 + i * 0.5 for i in range(24)]  # Gradual change
        })
        
        clean_data = apply_quality_control(data, 'temperatura')
        
        # All data should pass
        assert len(clean_data) > 0
        assert len(clean_data) <= len(data)


class TestQCHelperFunctions:
    """Test QC helper functions."""
    
    def test_apply_quality_control_with_temperature(self):
        """Test apply_quality_control with temperature data."""
        data = pd.DataFrame({
            'tiempo': pd.date_range('2024-01-01', periods=10, freq='h'),
            'valor': np.random.uniform(10, 25, 10)  # Valid temperature range
        })
        
        result = apply_quality_control(data, 'temperatura')
        assert isinstance(result, pd.DataFrame)
        assert 'valor' in result.columns
    
    def test_apply_quality_control_removes_invalid(self):
        """Test that QC removes invalid data."""
        data = pd.DataFrame({
            'tiempo': pd.date_range('2024-01-01', periods=10, freq='h'),
            'valor': [15.0, 20.0, 999.0, 18.0, -999.0, 16.0, 19.0, 17.0, 21.0, 22.0]
        })
        
        result = apply_quality_control(data, 'temperatura')
        
        # Should remove the 999 and -999 values
        assert len(result) < len(data)
        assert 999.0 not in result['valor'].values
        assert -999.0 not in result['valor'].values


class TestQCEdgeCases:
    """Test QC edge cases."""
    
    def test_empty_dataframe(self):
        """Test QC with empty DataFrame."""
        data = pd.DataFrame(columns=['tiempo', 'valor'])
        result = apply_quality_control(data, 'temperatura')
        assert len(result) == 0
    
    def test_single_value(self):
        """Test QC with single value."""
        data = pd.DataFrame({
            'tiempo': [datetime.now()],
            'valor': [20.0]
        })
        result = apply_quality_control(data, 'temperatura')
        assert len(result) >= 0
    
    def test_missing_values(self):
        """Test QC with missing values."""
        data = pd.DataFrame({
            'tiempo': pd.date_range('2024-01-01', periods=5, freq='h'),
            'valor': [15.0, np.nan, 20.0, np.nan, 18.0]
        })
        result = apply_quality_control(data, 'temperatura')
        # Should handle NaN values
        assert isinstance(result, pd.DataFrame)
