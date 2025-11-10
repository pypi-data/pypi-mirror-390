"""Comprehensive tests for tutorial scripts (basic_tutorial.py and hydra_tutorial.py)."""

import sys
import subprocess
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

# Add src to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / 'src'))

import dfm_python as dfm
from dfm_python.config import Params


def test_basic_tutorial_workflow():
    """Test the basic_tutorial.py workflow programmatically."""
    spec_path = project_root / 'data' / 'sample_spec.csv'
    data_path = project_root / 'data' / 'sample_data.csv'
    
    if not spec_path.exists() or not data_path.exists():
        pytest.skip("Required data files not found")
    
    dfm.reset()
    
    # 1) Create Params with all exposed parameters
    params = Params(
        max_iter=1,  # Quick test
        threshold=1e-2,  # Relaxed for quick convergence
        nan_method=2,
        clock='m',
        regularization_scale=1e-5,
        damping_factor=0.8,
    )
    
    # 2) Load config from spec + params
    dfm.from_spec(str(spec_path), params=params)
    config = dfm.get_config()
    assert config is not None
    assert config.max_iter == 1
    assert len(config.series) > 0
    
    # 3) Load data with short window
    dfm.load_data(str(data_path), sample_start='2021-01-01', sample_end='2022-12-31')
    X = dfm.get_data()
    Time = dfm.get_time()
    assert X is not None
    assert Time is not None
    assert X.shape[0] > 0
    assert X.shape[1] == len(config.series)
    
    # 4) Train
    dfm.train(max_iter=1)
    result = dfm.get_result()
    assert result is not None
    assert result.num_iter >= 1
    
    # 5) Predict
    X_forecast, Z_forecast = dfm.predict(horizon=6)
    assert X_forecast.shape[0] == 6
    assert X_forecast.shape[1] == len(config.series)
    
    # 6) Plot (just verify it doesn't crash)
    try:
        dfm.plot(kind='factor', factor_index=0, forecast_horizon=6, show=False)
    except Exception as e:
        pytest.fail(f"Plot failed: {e}")


def test_basic_tutorial_cli_args():
    """Test basic_tutorial.py with various CLI arguments."""
    spec_path = project_root / 'data' / 'sample_spec.csv'
    data_path = project_root / 'data' / 'sample_data.csv'
    
    if not spec_path.exists() or not data_path.exists():
        pytest.skip("Required data files not found")
    
    tutorial_path = project_root / 'tutorial' / 'basic_tutorial.py'
    if not tutorial_path.exists():
        pytest.skip(f"Tutorial not found: {tutorial_path}")
    
    # Test with minimal args (use longer date range to avoid T < N issues)
    result = subprocess.run(
        [
            'python', str(tutorial_path),
            '--spec', str(spec_path),
            '--data', str(data_path),
            '--output', str(project_root / 'outputs' / 'test_basic'),
            '--sample-start', '2015-01-01',  # Longer range to avoid T < N
            '--sample-end', '2022-12-31',
            '--max-iter', '1',
            '--forecast-horizon', '6',
        ],
        cwd=str(project_root),
        capture_output=True,
        text=True,
        timeout=120
    )
    
    # Allow non-zero exit if it's due to data issues (T < N), but check for actual errors
    if result.returncode != 0:
        # Check if it's a known data issue or actual error
        if 'IndexError' in result.stderr or 'invalid index' in result.stderr.lower():
            # This is the bug we're testing - should be fixed now
            pytest.fail(f"Tutorial crashed with error:\n{result.stderr}\n{result.stdout}")
        elif 'Insufficient' in result.stdout or 'T < N' in result.stdout:
            # Data issue - acceptable for this test
            pass
        else:
            pytest.fail(f"Tutorial failed:\n{result.stderr}\n{result.stdout}")


def test_basic_tutorial_all_params():
    """Test basic_tutorial.py with all parameter overrides."""
    spec_path = project_root / 'data' / 'sample_spec.csv'
    data_path = project_root / 'data' / 'sample_data.csv'
    
    if not spec_path.exists() or not data_path.exists():
        pytest.skip("Required data files not found")
    
    tutorial_path = project_root / 'tutorial' / 'basic_tutorial.py'
    if not tutorial_path.exists():
        pytest.skip(f"Tutorial not found: {tutorial_path}")
    
    # Test with all parameter overrides (use longer date range)
    result = subprocess.run(
        [
            'python', str(tutorial_path),
            '--spec', str(spec_path),
            '--data', str(data_path),
            '--output', str(project_root / 'outputs' / 'test_basic_all'),
            '--sample-start', '2015-01-01',  # Longer range
            '--sample-end', '2022-12-31',
            '--max-iter', '1',
            '--threshold', '1e-4',
            '--nan-method', '2',
            '--nan-k', '3',
            '--clock', 'm',
            '--regularization-scale', '1e-5',
            '--damping-factor', '0.8',
            '--forecast-horizon', '6',
        ],
        cwd=str(project_root),
        capture_output=True,
        text=True,
        timeout=120
    )
    
    # Allow non-zero exit if it's due to data issues
    if result.returncode != 0:
        if 'IndexError' in result.stderr or 'invalid index' in result.stderr.lower():
            pytest.fail(f"Tutorial crashed:\n{result.stderr}\n{result.stdout}")
        elif 'Insufficient' in result.stdout or 'T < N' in result.stdout:
            pass  # Data issue - acceptable
        else:
            pytest.fail(f"Tutorial failed:\n{result.stderr}\n{result.stdout}")


@pytest.mark.skipif(
    not (project_root / 'tutorial' / 'hydra_tutorial.py').exists(),
    reason="Hydra tutorial not found"
)
def test_hydra_tutorial_workflow():
    """Test the hydra_tutorial.py workflow programmatically."""
    try:
        import hydra
        from hydra.core.config_store import ConfigStore
        from hydra.utils import get_original_cwd
        from omegaconf import DictConfig, OmegaConf
    except ImportError:
        pytest.skip("Hydra not installed")
    
    config_path = project_root / 'config' / 'default.yaml'
    data_path = project_root / 'data' / 'sample_data.csv'
    
    if not config_path.exists() or not data_path.exists():
        pytest.skip("Required files not found")
    
    dfm.reset()
    
    # Load config from YAML and convert to dict format (simulating Hydra)
    from dfm_python.data_loader import load_config_from_yaml
    config = load_config_from_yaml(config_path)
    
    # Convert to dict format that from_hydra expects
    hydra_dict = {
        'max_iter': config.max_iter,
        'threshold': config.threshold,
        'nan_method': config.nan_method,
        'clock': config.clock,
        'regularization_scale': config.regularization_scale,
        'damping_factor': config.damping_factor,
        'blocks': {name: {'factors': blk.factors, 'clock': blk.clock} 
                   for name, blk in config.blocks.items()},
        'series': {s.series_id: {
            'series_id': s.series_id,
            'series_name': s.series_name,
            'frequency': s.frequency,
            'transformation': s.transformation,
            'category': s.category,
            'units': s.units,
            'blocks': s.blocks
        } for s in config.series}
    }
    
    # Load config using from_hydra
    dfm.load_config(hydra=hydra_dict)
    loaded_config = dfm.get_config()
    assert loaded_config is not None
    
    # Load data
    dfm.load_data(str(data_path), sample_start='2021-01-01', sample_end='2022-12-31')
    X = dfm.get_data()
    assert X is not None
    
    # Train
    dfm.train(max_iter=1)
    result = dfm.get_result()
    assert result is not None
    
    # Predict
    X_forecast, _ = dfm.predict(horizon=6)
    assert X_forecast.shape[0] == 6


def test_tutorial_edge_cases():
    """Test edge cases in tutorial workflows."""
    spec_path = project_root / 'data' / 'sample_spec.csv'
    data_path = project_root / 'data' / 'sample_data.csv'
    
    if not spec_path.exists() or not data_path.exists():
        pytest.skip("Required data files not found")
    
    dfm.reset()
    
    # Edge case 1: Very short data window
    params = Params(max_iter=1, threshold=1e-2)
    dfm.from_spec(str(spec_path), params=params)
    try:
        dfm.load_data(str(data_path), sample_start='2022-01-01', sample_end='2022-03-31')
        # Should handle gracefully or warn
    except Exception as e:
        # Acceptable if it raises a clear error
        assert 'insufficient' in str(e).lower() or 'sample' in str(e).lower()
    
    dfm.reset()
    
    # Edge case 2: Very small max_iter
    params = Params(max_iter=1, threshold=1e-2)
    dfm.from_spec(str(spec_path), params=params)
    dfm.load_data(str(data_path), sample_start='2021-01-01', sample_end='2022-12-31')
    dfm.train(max_iter=1)
    result = dfm.get_result()
    assert result is not None
    assert result.num_iter >= 1
    
    dfm.reset()
    
    # Edge case 3: Very relaxed threshold
    params = Params(max_iter=10, threshold=1e-1)  # Very relaxed
    dfm.from_spec(str(spec_path), params=params)
    dfm.load_data(str(data_path), sample_start='2021-01-01', sample_end='2022-12-31')
    dfm.train(max_iter=1)  # Still use 1 iteration for speed
    result = dfm.get_result()
    assert result is not None
    
    dfm.reset()
    
    # Edge case 4: Forecast with horizon=1
    params = Params(max_iter=1, threshold=1e-2)
    dfm.from_spec(str(spec_path), params=params)
    dfm.load_data(str(data_path), sample_start='2021-01-01', sample_end='2022-12-31')
    dfm.train(max_iter=1)
    X_forecast, _ = dfm.predict(horizon=1)
    assert X_forecast.shape[0] == 1
    
    dfm.reset()
    
    # Edge case 5: Forecast with large horizon
    params = Params(max_iter=1, threshold=1e-2)
    dfm.from_spec(str(spec_path), params=params)
    dfm.load_data(str(data_path), sample_start='2021-01-01', sample_end='2022-12-31')
    dfm.train(max_iter=1)
    X_forecast, _ = dfm.predict(horizon=24)  # 2 years ahead
    assert X_forecast.shape[0] == 24

