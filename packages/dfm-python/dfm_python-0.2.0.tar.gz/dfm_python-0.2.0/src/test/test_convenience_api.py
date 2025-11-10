"""Smoke tests for convenience API constructors (from_yaml, from_spec, from_dict)."""

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


def test_from_yaml():
    """Test from_yaml convenience constructor."""
    config_path = project_root / 'config' / 'default.yaml'
    if not config_path.exists():
        pytest.skip(f"Config file not found: {config_path}")
    
    dfm.reset()
    dfm.from_yaml(str(config_path))
    config = dfm.get_config()
    assert config is not None
    assert len(config.series) > 0
    assert len(config.block_names) > 0


def test_from_spec_with_params():
    """Test from_spec convenience constructor with Params."""
    spec_path = project_root / 'data' / 'sample_spec.csv'
    if not spec_path.exists():
        pytest.skip(f"Spec file not found: {spec_path}")
    
    dfm.reset()
    params = Params(max_iter=1, threshold=1e-4)
    dfm.from_spec(str(spec_path), params=params)
    config = dfm.get_config()
    assert config is not None
    assert config.max_iter == 1
    assert config.threshold == 1e-4
    assert len(config.series) > 0


def test_from_spec_defaults():
    """Test from_spec convenience constructor with default Params."""
    spec_path = project_root / 'data' / 'sample_spec.csv'
    if not spec_path.exists():
        pytest.skip(f"Spec file not found: {spec_path}")
    
    dfm.reset()
    dfm.from_spec(str(spec_path))  # Uses Params() defaults
    config = dfm.get_config()
    assert config is not None
    assert config.max_iter == 5000  # Default from Params
    assert len(config.series) > 0


def test_from_spec_df():
    """Test from_spec_df convenience constructor."""
    spec_path = project_root / 'data' / 'sample_spec.csv'
    if not spec_path.exists():
        pytest.skip(f"Spec file not found: {spec_path}")
    
    dfm.reset()
    spec_df = pd.read_csv(spec_path)
    params = Params(max_iter=1)
    dfm.from_spec_df(spec_df, params=params)
    config = dfm.get_config()
    assert config is not None
    assert config.max_iter == 1
    assert len(config.series) > 0


def test_from_dict():
    """Test from_dict convenience constructor."""
    dfm.reset()
    config_dict = {
        'clock': 'm',
        'max_iter': 100,
        'threshold': 1e-5,
        'blocks': {
            'Block_Global': {
                'factors': 1,
                'clock': 'm'
            }
        },
        'series': [
            {
                'series_id': 'test_series',
                'series_name': 'Test Series',
                'frequency': 'm',
                'transformation': 'lin',
                'category': 'Test',
                'units': 'Index',
                'blocks': [1]  # Loads on first block (must be 1, not 0)
            }
        ]
    }
    dfm.from_dict(config_dict)
    config = dfm.get_config()
    assert config is not None
    assert config.clock == 'm'
    assert config.max_iter == 100
    assert len(config.series) == 1
    assert config.series[0].series_id == 'test_series'


def test_params_validation():
    """Test Params dataclass validation."""
    # Valid params
    params = Params(max_iter=100, threshold=1e-5)
    assert params.max_iter == 100
    assert params.threshold == 1e-5
    
    # Invalid threshold
    with pytest.raises(ValueError, match="threshold must be positive"):
        Params(threshold=-1)
    
    # Invalid max_iter
    with pytest.raises(ValueError, match="max_iter must be at least 1"):
        Params(max_iter=0)
    
    # Invalid AR clip range
    with pytest.raises(ValueError):
        Params(ar_clip_min=0.5, ar_clip_max=0.3)  # min > max


def test_convenience_api_integration():
    """Integration test: load config, data, train (1 iteration)."""
    spec_path = project_root / 'data' / 'sample_spec.csv'
    data_path = project_root / 'data' / 'sample_data.csv'
    
    if not spec_path.exists() or not data_path.exists():
        pytest.skip("Required data files not found")
    
    dfm.reset()
    
    # Load config using convenience API
    params = Params(max_iter=1, threshold=1e-2)  # Fast convergence for testing
    dfm.from_spec(str(spec_path), params=params)
    
    # Load data with short window
    dfm.load_data(str(data_path), sample_start='2021-01-01', sample_end='2022-12-31')
    
    # Train (1 iteration)
    dfm.train(max_iter=1)
    
    # Check results
    result = dfm.get_result()
    assert result is not None
    assert result.num_iter >= 1
    
    # Predict
    X_forecast, Z_forecast = dfm.predict(horizon=6)
    assert X_forecast.shape[0] == 6
    assert X_forecast.shape[1] > 0

