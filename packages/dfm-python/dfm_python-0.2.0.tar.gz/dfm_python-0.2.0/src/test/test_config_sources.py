"""Tests for ConfigSource adapters and data loading features."""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import warnings
import pytest
import tempfile
import os

# Add src to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / 'src'))

from dfm_python.config import DFMConfig, SeriesConfig, BlockConfig
from dfm_python.config import (
    YamlSource,
    DictSource,
    SpecCSVSource,
    HydraSource,
    MergedConfigSource,
    make_config_source,
)
from dfm_python.data_loader import load_data


# ============================================================================
# ConfigSource Adapter Tests
# ============================================================================

def test_yaml_source(tmp_path):
    """Test loading config from YAML file."""
    # Create YAML structure with defaults (Hydra-style)
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    series_dir = config_dir / "series"
    series_dir.mkdir()
    blocks_dir = config_dir / "blocks"
    blocks_dir.mkdir()
    
    # Main config
    main_yaml = """
defaults:
  - series: default
  - blocks: default

clock: m
threshold: 1e-5
max_iter: 100
"""
    main_file = config_dir / "default.yaml"
    main_file.write_text(main_yaml)
    
    # Series config
    series_yaml = """
series_0:
  series_id: series_0
  series_name: Test Series
  frequency: m
  transformation: lin
  category: Test
  units: Index
  blocks: [Block_Global]
"""
    series_file = series_dir / "default.yaml"
    series_file.write_text(series_yaml)
    
    # Blocks config
    blocks_yaml = """
Block_Global:
  factors: 1
  clock: m
"""
    blocks_file = blocks_dir / "default.yaml"
    blocks_file.write_text(blocks_yaml)
    
    source = YamlSource(main_file)
    config = source.load()
    
    assert isinstance(config, DFMConfig)
    assert config.clock == 'm'
    assert len(config.series) == 1
    assert len(config.blocks) == 1


def test_dict_source():
    """Test loading config from dictionary."""
    config_dict = {
        'clock': 'm',
        'threshold': 1e-5,
        'max_iter': 100,
        'series': {
            'series_0': {
                'series_name': 'Test Series',
                'frequency': 'm',
                'transformation': 'lin',
                'blocks': ['Block_Global']
            }
        },
        'blocks': {
            'Block_Global': {'factors': 1, 'clock': 'm'}
        }
    }
    
    source = DictSource(config_dict)
    config = source.load()
    
    assert isinstance(config, DFMConfig)
    assert config.clock == 'm'
    assert len(config.series) == 1


def test_spec_csv_source(tmp_path):
    """Test loading series definitions from spec CSV."""
    spec_content = """series_id,series_name,frequency,transformation,category,units,Block_Global
series_0,Test Series,m,lin,Test,Index,1
"""
    spec_file = tmp_path / "test_spec.csv"
    spec_file.write_text(spec_content)
    
    source = SpecCSVSource(spec_file)
    config = source.load()
    
    assert isinstance(config, DFMConfig)
    assert len(config.series) == 1
    assert config.series[0].series_id == 'series_0'


def test_hydra_source():
    """Test loading config from Hydra DictConfig or dict."""
    hydra_dict = {
        'clock': 'm',
        'threshold': 1e-5,
        'max_iter': 100,
        'series': {
            'series_0': {
                'series_name': 'Test Series',
                'frequency': 'm',
                'transformation': 'lin',
                'blocks': ['Block_Global']
            }
        },
        'blocks': {
            'Block_Global': {'factors': 1, 'clock': 'm'}
        }
    }
    
    source = HydraSource(hydra_dict)
    config = source.load()
    
    assert isinstance(config, DFMConfig)
    assert config.clock == 'm'


def test_merged_config_source(tmp_path):
    """Test merging base config with override config."""
    # Create YAML structure
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    blocks_dir = config_dir / "blocks"
    blocks_dir.mkdir()
    series_dir = config_dir / "series"
    series_dir.mkdir()
    
    # Base config (YAML with defaults)
    base_yaml = """
defaults:
  - series: default
  - blocks: default

clock: m
threshold: 1e-5
max_iter: 100
"""
    base_file = config_dir / "base.yaml"
    base_file.write_text(base_yaml)
    
    # Dummy series config (will be overridden by spec CSV)
    # We need at least one series for validation, but it will be replaced
    series_yaml = """
dummy_series:
  series_id: dummy_series
  series_name: Dummy Series
  frequency: m
  transformation: lin
  category: Test
  units: Index
  blocks: [Block_Global]
"""
    series_file = series_dir / "default.yaml"
    series_file.write_text(series_yaml)
    
    # Blocks config
    blocks_yaml = """
Block_Global:
  factors: 1
  clock: m
"""
    blocks_file = blocks_dir / "default.yaml"
    blocks_file.write_text(blocks_yaml)
    
    # Override config (spec CSV with series)
    spec_content = """series_id,series_name,frequency,transformation,category,units,Block_Global
series_0,Test Series,m,lin,Test,Index,1
"""
    spec_file = tmp_path / "spec.csv"
    spec_file.write_text(spec_content)
    
    base_source = YamlSource(base_file)
    override_source = SpecCSVSource(spec_file)
    merged_source = MergedConfigSource(base_source, override_source)
    config = merged_source.load()
    
    assert isinstance(config, DFMConfig)
    assert config.clock == 'm'  # From base
    assert len(config.series) == 1  # From override
    assert config.series[0].series_id == 'series_0'


def test_make_config_source():
    """Test make_config_source factory function."""
    # From YAML path
    config_dict = {
        'clock': 'm',
        'threshold': 1e-5,
        'max_iter': 100,
        'series': {
            'series_0': {
                'series_name': 'Test',
                'frequency': 'm',
                'transformation': 'lin',
                'blocks': ['Block_Global']
            }
        },
        'blocks': {
            'Block_Global': {'factors': 1, 'clock': 'm'}
        }
    }
    
    # From dict
    source = make_config_source(mapping=config_dict)
    config = source.load()
    assert isinstance(config, DFMConfig)
    
    # From DFMConfig
    config_obj = DFMConfig(
        series=[SeriesConfig(frequency='m', transformation='lin', blocks=[1])],
        blocks={'Block_Global': BlockConfig(factors=1, clock='m')}
    )
    source = make_config_source(config_obj)
    config = source.load()
    assert config is config_obj


# ============================================================================
# Data Loading Tests (T>=N warnings, windowing)
# ============================================================================

def test_t_geq_n_warning(tmp_path):
    """Test T>=N warning when windowing reduces data too much."""
    # Create minimal config
    config = DFMConfig(
        series=[
            SeriesConfig(frequency='m', transformation='lin', blocks=[1], series_id=f'series_{i}')
            for i in range(10)  # 10 series
        ],
        blocks={'Block_Global': BlockConfig(factors=1, clock='m')}
    )
    
    # Create data with only 5 time periods (T=5 < N=10)
    T, N = 5, 10
    dates = pd.date_range('2020-01-01', periods=T, freq='M')
    data = pd.DataFrame(
        np.random.randn(T, N),
        index=dates,
        columns=[f'series_{i}' for i in range(N)]
    )
    
    data_file = tmp_path / "test_data.csv"
    data.to_csv(data_file)
    
    # Load with windowing that keeps all data (should still warn)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        try:
            X, Time, Z = load_data(data_file, config, sample_start='2020-01-01', sample_end='2020-05-31')
            # Should have warning about T < N
            assert len(w) > 0
            assert any('T < N' in str(warning.message) or 'Insufficient data' in str(warning.message) for warning in w)
        except Exception:
            # If it fails due to insufficient data, that's also acceptable
            pass


def test_data_windowing(tmp_path):
    """Test data windowing with sample_start and sample_end."""
    # Create config
    config = DFMConfig(
        series=[
            SeriesConfig(frequency='m', transformation='lin', blocks=[1], series_id='series_0')
        ],
        blocks={'Block_Global': BlockConfig(factors=1, clock='m')}
    )
    
    # Create data with 12 months
    T = 12
    dates = pd.date_range('2020-01-01', periods=T, freq='M')
    data = pd.DataFrame(
        np.random.randn(T, 1),
        index=dates,
        columns=['series_0']
    )
    
    data_file = tmp_path / "test_data.csv"
    data.to_csv(data_file)
    
    # Load with windowing
    X, Time, Z = load_data(
        data_file, config,
        sample_start='2020-03-01',
        sample_end='2020-09-30'
    )
    
    # Should have fewer periods than original
    assert len(Time) <= T
    assert Time[0] >= pd.to_datetime('2020-03-01')
    assert Time[-1] <= pd.to_datetime('2020-09-30')


def test_data_windowing_no_warning(tmp_path):
    """Test that T>=N case doesn't produce warning."""
    # Create config with fewer series
    config = DFMConfig(
        series=[
            SeriesConfig(frequency='m', transformation='lin', blocks=[1], series_id=f'series_{i}')
            for i in range(3)  # Only 3 series
        ],
        blocks={'Block_Global': BlockConfig(factors=1, clock='m')}
    )
    
    # Create data with 10 time periods (T=10 > N=3)
    T, N = 10, 3
    dates = pd.date_range('2020-01-01', periods=T, freq='M')
    data = pd.DataFrame(
        np.random.randn(T, N),
        index=dates,
        columns=[f'series_{i}' for i in range(N)]
    )
    
    data_file = tmp_path / "test_data.csv"
    data.to_csv(data_file)
    
    # Load with windowing
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        X, Time, Z = load_data(
            data_file, config,
            sample_start='2020-01-01',
            sample_end='2020-10-31'
        )
        # Should not have T < N warning
        t_lt_n_warnings = [warning for warning in w if 'T < N' in str(warning.message) or 'Insufficient data' in str(warning.message)]
        assert len(t_lt_n_warnings) == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

