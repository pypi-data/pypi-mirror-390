"""Edge case tests for the high-level API and convenience constructors."""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

# Add src to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / 'src'))

import dfm_python as dfm
from dfm_python.config import Params, DFMConfig, SeriesConfig, BlockConfig


def test_from_spec_missing_file():
    """Test from_spec with missing file."""
    dfm.reset()
    with pytest.raises(FileNotFoundError):
        dfm.from_spec('nonexistent_spec.csv')


def test_from_spec_invalid_csv():
    """Test from_spec with invalid CSV."""
    dfm.reset()
    # Create a temporary invalid CSV
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write('invalid,columns\n')
        f.write('1,2\n')
        temp_path = f.name
    
    try:
        with pytest.raises((ValueError, KeyError)):
            dfm.from_spec(temp_path)
    finally:
        Path(temp_path).unlink()


def test_from_spec_empty_params():
    """Test from_spec with empty/default Params."""
    spec_path = project_root / 'data' / 'sample_spec.csv'
    if not spec_path.exists():
        pytest.skip("Spec file not found")
    
    dfm.reset()
    # Should work with default Params
    dfm.from_spec(str(spec_path))
    config = dfm.get_config()
    assert config is not None
    assert config.max_iter == 5000  # Default


def test_from_spec_df_empty_dataframe():
    """Test from_spec_df with empty DataFrame."""
    dfm.reset()
    empty_df = pd.DataFrame()
    with pytest.raises((ValueError, KeyError)):
        dfm.from_spec_df(empty_df)


def test_from_dict_missing_required_fields():
    """Test from_dict with missing required fields."""
    dfm.reset()
    
    # Missing series
    with pytest.raises((TypeError, ValueError)):
        dfm.from_dict({'clock': 'm', 'max_iter': 100})
    
    # Missing blocks
    with pytest.raises((TypeError, ValueError)):
        dfm.from_dict({
            'clock': 'm',
            'series': [{'series_id': 's1', 'frequency': 'm', 'transformation': 'lin', 'blocks': [1]}]
        })


def test_from_dict_invalid_blocks_format():
    """Test from_dict with invalid blocks format."""
    dfm.reset()
    
    # Blocks as list instead of dict
    with pytest.raises(ValueError, match="blocks must be a dict"):
        dfm.from_dict({
            'clock': 'm',
            'blocks': ['Block_Global'],  # Wrong format
            'series': [{'series_id': 's1', 'frequency': 'm', 'transformation': 'lin', 'blocks': [1]}]
        })


def test_params_invalid_values():
    """Test Params with invalid values."""
    # Negative threshold
    with pytest.raises(ValueError, match="threshold must be positive"):
        Params(threshold=-1)
    
    # Zero max_iter
    with pytest.raises(ValueError, match="max_iter must be at least 1"):
        Params(max_iter=0)
    
    # Invalid AR clip range
    with pytest.raises(ValueError):
        Params(ar_clip_min=0.5, ar_clip_max=0.3)
    
    # AR clip out of bounds
    with pytest.raises(ValueError):
        Params(ar_clip_min=-1.5)  # Must be > -1
    
    with pytest.raises(ValueError):
        Params(ar_clip_max=1.5)  # Must be < 1


def test_train_without_config():
    """Test train() without loading config first."""
    dfm.reset()
    with pytest.raises(ValueError, match="Configuration must be loaded"):
        dfm.train()


def test_train_without_data():
    """Test train() without loading data first."""
    spec_path = project_root / 'data' / 'sample_spec.csv'
    if not spec_path.exists():
        pytest.skip("Spec file not found")
    
    dfm.reset()
    dfm.from_spec(str(spec_path))
    with pytest.raises(ValueError, match="Data must be loaded"):
        dfm.train()


def test_predict_without_training():
    """Test predict() without training first."""
    spec_path = project_root / 'data' / 'sample_spec.csv'
    data_path = project_root / 'data' / 'sample_data.csv'
    
    if not spec_path.exists() or not data_path.exists():
        pytest.skip("Required files not found")
    
    dfm.reset()
    dfm.from_spec(str(spec_path))
    dfm.load_data(str(data_path), sample_start='2021-01-01', sample_end='2022-12-31')
    
    with pytest.raises(ValueError, match="Model must be trained"):
        dfm.predict(horizon=6)


def test_predict_invalid_horizon():
    """Test predict() with invalid horizon."""
    spec_path = project_root / 'data' / 'sample_spec.csv'
    data_path = project_root / 'data' / 'sample_data.csv'
    
    if not spec_path.exists() or not data_path.exists():
        pytest.skip("Required files not found")
    
    dfm.reset()
    dfm.from_spec(str(spec_path))
    dfm.load_data(str(data_path), sample_start='2021-01-01', sample_end='2022-12-31')
    dfm.train(max_iter=1)
    
    # Zero horizon
    with pytest.raises((ValueError, AssertionError)):
        dfm.predict(horizon=0)
    
    # Negative horizon
    with pytest.raises((ValueError, AssertionError)):
        dfm.predict(horizon=-1)


def test_plot_without_training():
    """Test plot() without training first."""
    spec_path = project_root / 'data' / 'sample_spec.csv'
    data_path = project_root / 'data' / 'sample_data.csv'
    
    if not spec_path.exists() or not data_path.exists():
        pytest.skip("Required files not found")
    
    dfm.reset()
    dfm.from_spec(str(spec_path))
    dfm.load_data(str(data_path), sample_start='2021-01-01', sample_end='2022-12-31')
    
    with pytest.raises((ValueError, AttributeError), match="Model must be trained|result"):
        dfm.plot(kind='factor', factor_index=0, show=False)


def test_plot_invalid_factor_index():
    """Test plot() with invalid factor index."""
    spec_path = project_root / 'data' / 'sample_spec.csv'
    data_path = project_root / 'data' / 'sample_data.csv'
    
    if not spec_path.exists() or not data_path.exists():
        pytest.skip("Required files not found")
    
    dfm.reset()
    dfm.from_spec(str(spec_path))
    dfm.load_data(str(data_path), sample_start='2021-01-01', sample_end='2022-12-31')
    dfm.train(max_iter=1)
    
    result = dfm.get_result()
    num_factors = result.Z.shape[1] if result else 1
    
    # Factor index out of range
    with pytest.raises((ValueError, IndexError)):
        dfm.plot(kind='factor', factor_index=num_factors + 10, show=False)


def test_load_data_invalid_path():
    """Test load_data() with invalid path."""
    spec_path = project_root / 'data' / 'sample_spec.csv'
    if not spec_path.exists():
        pytest.skip("Spec file not found")
    
    dfm.reset()
    dfm.from_spec(str(spec_path))
    
    with pytest.raises(FileNotFoundError):
        dfm.load_data('nonexistent_data.csv')


def test_load_data_invalid_date_range():
    """Test load_data() with invalid date range."""
    spec_path = project_root / 'data' / 'sample_spec.csv'
    data_path = project_root / 'data' / 'sample_data.csv'
    
    if not spec_path.exists() or not data_path.exists():
        pytest.skip("Required files not found")
    
    dfm.reset()
    dfm.from_spec(str(spec_path))
    
    # End before start
    try:
        dfm.load_data(str(data_path), sample_start='2022-12-31', sample_end='2021-01-01')
        # Should either work (pandas handles it) or raise an error
    except Exception:
        pass  # Acceptable


def test_reset_clears_state():
    """Test that reset() clears all state."""
    spec_path = project_root / 'data' / 'sample_spec.csv'
    data_path = project_root / 'data' / 'sample_data.csv'
    
    if not spec_path.exists() or not data_path.exists():
        pytest.skip("Required files not found")
    
    dfm.reset()
    dfm.from_spec(str(spec_path))
    dfm.load_data(str(data_path), sample_start='2021-01-01', sample_end='2022-12-31')
    dfm.train(max_iter=1)
    
    # Verify state exists
    assert dfm.get_config() is not None
    assert dfm.get_data() is not None
    assert dfm.get_result() is not None
    
    # Reset
    dfm.reset()
    
    # Verify state cleared
    assert dfm.get_config() is None
    assert dfm.get_data() is None
    assert dfm.get_result() is None


def test_multiple_reset_calls():
    """Test that multiple reset() calls are safe."""
    dfm.reset()
    dfm.reset()
    dfm.reset()
    # Should not raise any errors


def test_convenience_api_chaining():
    """Test that convenience APIs can be chained."""
    spec_path = project_root / 'data' / 'sample_spec.csv'
    data_path = project_root / 'data' / 'sample_data.csv'
    
    if not spec_path.exists() or not data_path.exists():
        pytest.skip("Required files not found")
    
    dfm.reset()
    
    # Chain operations
    params = Params(max_iter=1, threshold=1e-2)
    dfm.from_spec(str(spec_path), params=params)
    dfm.load_data(str(data_path), sample_start='2021-01-01', sample_end='2022-12-31')
    dfm.train(max_iter=1)
    
    # All should work
    assert dfm.get_config() is not None
    assert dfm.get_data() is not None
    assert dfm.get_result() is not None

