"""High-level API for Dynamic Factor Model.

This module provides an object-oriented interface for DFM estimation.
Use this for a simpler, more intuitive API compared to the functional interface.

Example:
    >>> import dfm_python as dfm
    >>> dfm.load_config('config/default.yaml')
    >>> dfm.load_data('data/sample_data.csv')
    >>> dfm.train()
    >>> factors = dfm.result.Z
"""

from typing import Optional, Union
from pathlib import Path
import numpy as np
import pandas as pd
import os

from .config import DFMConfig
from .data_loader import (
    load_config as _load_config_func,
    load_config_from_yaml as _load_config_from_yaml,
    load_config_from_spec as _load_config_from_spec,
    load_data as _load_data,
)
from .dfm import dfm as _dfm, DFMResult


class DFM:
    """High-level API for Dynamic Factor Model estimation.
    
    This class provides a simple, object-oriented interface for DFM operations.
    It maintains state (config, data, results) and provides convenient methods
    for loading configuration, data, and training models.
    
    Example:
        >>> import dfm_python as dfm
        >>> dfm.load_config('config/default.yaml')
        >>> dfm.load_data('data/sample_data.csv')
        >>> dfm.train()
        >>> print(dfm.result.converged)
        >>> factors = dfm.result.Z
    """
    
    def __init__(self):
        """Initialize DFM instance with empty state."""
        self._config: Optional[DFMConfig] = None
        self._data: Optional[np.ndarray] = None
        self._time: Optional[np.ndarray] = None
        self._original_data: Optional[np.ndarray] = None
        self._result: Optional[DFMResult] = None
    
    @property
    def config(self) -> Optional[DFMConfig]:
        """Get current configuration."""
        return self._config
    
    @property
    def data(self) -> Optional[np.ndarray]:
        """Get current data matrix (T x N)."""
        return self._data
    
    @property
    def time(self) -> Optional[np.ndarray]:
        """Get time index for data."""
        return self._time
    
    @property
    def original_data(self) -> Optional[np.ndarray]:
        """Get original (untransformed) data matrix."""
        return self._original_data
    
    @property
    def result(self) -> Optional[DFMResult]:
        """Get training result."""
        return self._result
    
    def load_config(self, config: Union[str, Path, DFMConfig]) -> 'DFM':
        """Load configuration from file or use provided DFMConfig.
        
        Parameters
        ----------
        config : str, Path, or DFMConfig
            Configuration file path (YAML) or DFMConfig object.
            
        Returns
        -------
        DFM
            Self for method chaining.
            
        Example:
            >>> dfm.load_config('config/default.yaml')
            >>> # or
            >>> dfm.load_config(DFMConfig(...))
        """
        if isinstance(config, DFMConfig):
            self._config = config
        else:
            self._config = _load_config_func(config)
        return self
    
    def load_config_from_yaml(self, yaml_path: Union[str, Path]) -> 'DFM':
        """Load configuration from YAML file.
        
        Parameters
        ----------
        yaml_path : str or Path
            Path to YAML configuration file.
            
        Returns
        -------
        DFM
            Self for method chaining.
            
        Example:
            >>> dfm.load_config_from_yaml('config/default.yaml')
        """
        self._config = _load_config_from_yaml(yaml_path)
        return self
    
    def load_config_from_spec(self, spec_path: Union[str, Path]) -> 'DFM':
        """Load configuration from spec CSV file.
        
        Parameters
        ----------
        spec_path : str or Path
            Path to spec CSV file.
            
        Returns
        -------
        DFM
            Self for method chaining.
            
        Example:
            >>> dfm.load_config_from_spec('data/sample_spec.csv')
        """
        self._config = _load_config_from_spec(spec_path)
        return self
    
    def load_data(self, 
                  data_path: Optional[Union[str, Path]] = None,
                  data: Optional[np.ndarray] = None,
                  **kwargs) -> 'DFM':
        """Load data from file or use provided array.
        
        Parameters
        ----------
        data_path : str or Path, optional
            Path to data file (CSV). If None, must provide `data`.
        data : np.ndarray, optional
            Data matrix directly (T x N). If None, must provide `data_path`.
        **kwargs
            Additional arguments passed to `load_data()`:
            - sample_start: Start date for data sampling
            - sample_end: End date for data sampling
            
        Returns
        -------
        DFM
            Self for method chaining.
            
        Example:
            >>> dfm.load_data('data/sample_data.csv')
            >>> # or
            >>> dfm.load_data(data=X, sample_start=pd.Timestamp('2000-01-01'))
        """
        if self._config is None:
            raise ValueError("Configuration must be loaded before loading data. "
                           "Call load_config() first.")
        
        if data_path is not None:
            self._data, self._time, self._original_data = _load_data(
                data_path, self._config, **kwargs
            )
        elif data is not None:
            # If data is provided directly, we still need to transform it
            # For now, assume it's already in the right format
            # In the future, we might want to add transform_data() call here
            self._data = data
            if 'time' in kwargs:
                self._time = kwargs['time']
            else:
                # Generate default time index
                self._time = pd.date_range(
                    start='2000-01-01', 
                    periods=len(data), 
                    freq='M'
                )
            self._original_data = data
        else:
            raise ValueError("Either data_path or data must be provided.")
        
        return self
    
    def train(self, 
              threshold: Optional[float] = None,
              max_iter: Optional[int] = None,
              fast: bool = False,
              **kwargs) -> 'DFM':
        """Train the DFM model.
        
        Parameters
        ----------
        threshold : float, optional
            EM convergence threshold. If None, uses config.threshold.
        max_iter : int, optional
            Maximum EM iterations. If None, uses config.max_iter.
        fast : bool, default False
            If True (or env DFM_FAST=1), use quick settings (threshold=1e-2, max_iter=5)
            unless explicitly overridden.
        **kwargs
            Additional arguments (for future extensibility).
            
        Returns
        -------
        DFM
            Self for method chaining.
            
        Example:
            >>> dfm.train(threshold=1e-4, max_iter=100)
        """
        if self._config is None:
            raise ValueError("Configuration must be loaded before training. "
                           "Call load_config() first.")
        if self._data is None:
            raise ValueError("Data must be loaded before training. "
                           "Call load_data() first.")
        
        # Determine fast mode (env or argument)
        is_fast = fast or os.environ.get('DFM_FAST', '').lower() in ("1", "true", "yes")

        # Apply quick defaults when fast mode is enabled
        effective_threshold = threshold
        effective_max_iter = max_iter
        if is_fast:
            if effective_threshold is None:
                effective_threshold = 1e-2
            if effective_max_iter is None:
                effective_max_iter = 5

        self._result = _dfm(
            self._data,
            self._config,
            threshold=effective_threshold,
            max_iter=effective_max_iter,
            **kwargs
        )
        # Attach metadata for convenient OOP access
        try:
            if self._time is not None:
                self._result.time_index = self._time
            if hasattr(self._config, 'get_series_ids'):
                self._result.series_ids = self._config.get_series_ids()
            if hasattr(self._config, 'block_names'):
                self._result.block_names = self._config.block_names
        except Exception:
            pass
        return self
    
    def reset(self) -> 'DFM':
        """Reset all state (config, data, results).
        
        Returns
        -------
        DFM
            Self for method chaining.
            
        Example:
            >>> dfm.reset()  # Clear everything
        """
        self._config = None
        self._data = None
        self._time = None
        self._original_data = None
        self._result = None
        return self


# Create a singleton instance for module-level usage
_dfm_instance = DFM()


# Module-level convenience functions that delegate to the singleton
def load_config(config: Union[str, Path, DFMConfig]) -> DFM:
    """Load configuration (module-level convenience function).
    
    This is a convenience function that uses the global DFM instance.
    For multiple models, create separate DFM() instances.
    """
    return _dfm_instance.load_config(config)


def load_config_from_yaml(yaml_path: Union[str, Path]) -> DFM:
    """Load configuration from YAML (module-level convenience function)."""
    return _dfm_instance.load_config_from_yaml(yaml_path)


def load_config_from_spec(spec_path: Union[str, Path]) -> DFM:
    """Load configuration from spec CSV (module-level convenience function)."""
    return _dfm_instance.load_config_from_spec(spec_path)


def load_data(data_path: Optional[Union[str, Path]] = None,
               data: Optional[np.ndarray] = None,
               **kwargs) -> DFM:
    """Load data (module-level convenience function)."""
    return _dfm_instance.load_data(data_path=data_path, data=data, **kwargs)


def train(threshold: Optional[float] = None,
          max_iter: Optional[int] = None,
          fast: bool = False,
          **kwargs) -> DFM:
    """Train the model (module-level convenience function)."""
    return _dfm_instance.train(threshold=threshold, max_iter=max_iter, fast=fast, **kwargs)


def reset() -> DFM:
    """Reset state (module-level convenience function)."""
    return _dfm_instance.reset()


# Expose singleton instance for direct access
# Users can access: dfm.config, dfm.data, dfm.result, etc.
__all__ = ['DFM', 'load_config', 'load_config_from_yaml', 'load_config_from_spec', 
           'load_data', 'train', 'reset']

