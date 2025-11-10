"""Configuration models for DFM nowcasting using OmegaConf and Hydra.

This module defines the configuration structure for Dynamic Factor Models,
providing a unified interface for specifying:
- Series definitions (frequency, transformation, block loadings)
- Block structure and factor dimensions
- Estimation parameters (EM algorithm settings, missing data handling)
- Clock frequency for mixed-frequency synchronization

The configuration system supports YAML files (with Hydra/OmegaConf) or direct
DFMConfig object creation, with validation and type checking to ensure model
specifications are correct before estimation.
"""

import numpy as np
from typing import List, Optional, Dict, Any, Union
from pathlib import Path
import warnings
from dataclasses import dataclass, field

try:
    from hydra.core.config_store import ConfigStore
    HYDRA_AVAILABLE = True
except ImportError:
    HYDRA_AVAILABLE = False
    ConfigStore = None

# Valid frequency codes
_VALID_FREQUENCIES = {'d', 'w', 'm', 'q', 'sa', 'a'}

# Valid transformation codes
_VALID_TRANSFORMATIONS = {
    'lin', 'chg', 'ch1', 'pch', 'pc1', 'pca', 
    'cch', 'cca', 'log'
}

# Transformation to readable units mapping
_TRANSFORM_UNITS_MAP = {
    'lin': 'Levels (No Transformation)',
    'chg': 'Change (Difference)',
    'ch1': 'Year over Year Change (Difference)',
    'pch': 'Percent Change',
    'pc1': 'Year over Year Percent Change',
    'pca': 'Percent Change (Annual Rate)',
    'cch': 'Continuously Compounded Rate of Change',
    'cca': 'Continuously Compounded Annual Rate of Change',
    'log': 'Natural Log'
}


def validate_frequency(frequency: str) -> str:
    """Validate frequency code."""
    if frequency not in _VALID_FREQUENCIES:
        raise ValueError(f"Invalid frequency: {frequency}. Must be one of {_VALID_FREQUENCIES}")
    return frequency


def validate_transformation(transformation: str) -> str:
    """Validate transformation code."""
    if transformation not in _VALID_TRANSFORMATIONS:
        warnings.warn(f"Unknown transformation code: {transformation}. Will use untransformed data.")
    return transformation


@dataclass
class BlockConfig:
    """Configuration for a single factor block.
    
    Each block represents a group of related time series that share common
    latent factors. Blocks can have their own clock frequency, which must be
    >= the global clock frequency.
    
    Attributes
    ----------
    factors : int
        Number of latent factors in this block (typically 1)
    ar_lag : int
        Autoregressive lag order for the block-level factor (typically 1)
    load_on_global : bool
        Whether this block's factors load on the global factor G_t
    clock : str
        Block-level clock frequency. Must be >= global clock.
        Series in this block must have frequency <= block clock.
    notes : str, optional
        Optional comments/description for the block
    """
    factors: int = 1
    ar_lag: int = 1
    load_on_global: bool = True
    clock: str = 'm'
    notes: Optional[str] = None
    
    def __post_init__(self):
        """Validate block configuration."""
        self.clock = validate_frequency(self.clock)
        if self.factors < 1:
            raise ValueError(f"Block must have at least 1 factor, got {self.factors}")
        if self.ar_lag < 1:
            raise ValueError(f"AR lag must be at least 1, got {self.ar_lag}")


@dataclass
class SeriesConfig:
    """Configuration for a single time series.
    
    This is a generic DFM configuration - no API or database-specific fields.
    For API/database integration, implement adapters in your application layer.
    
    Attributes
    ----------
    frequency : str
        Series frequency: 'm' (monthly), 'q' (quarterly), 'sa' (semi-annual), 'a' (annual)
    transformation : str
        Transformation code: 'lin', 'pch', 'pca', etc.
    blocks : List[str] or List[int]
        Block names (strings) or block indices (ints) this series loads on.
        Must include the global block (first block).
    series_id : str, optional
        Unique identifier (auto-generated if None)
    series_name : str, optional
        Human-readable name (defaults to series_id if None)
    units : str
        Units of measurement
    category : str
        Category/group name
    """
    # Required fields (no defaults)
    frequency: str
    transformation: str
    blocks: Union[List[str], List[int]]  # Can be block names (str) or indices (int)
    # Optional fields (with defaults - must come after required fields)
    series_id: Optional[str] = None  # Auto-generated if None: "series_0", "series_1", etc.
    series_name: Optional[str] = None  # Optional metadata for display
    units: str = ""  # Optional metadata
    category: str = ""  # Optional metadata
    aggregate: Optional[str] = None  # Aggregation method (deprecated: higher frequencies than clock are not supported)
    
    def __post_init__(self):
        """Validate fields after initialization."""
        self.frequency = validate_frequency(self.frequency)
        self.transformation = validate_transformation(self.transformation)
        # Auto-generate series_name if not provided
        if self.series_name is None and self.series_id:
            self.series_name = self.series_id
    
    def to_block_indices(self, block_names: List[str]) -> List[int]:
        """Convert block names to indices.
        
        Parameters
        ----------
        block_names : List[str]
            List of block names in order
            
        Returns
        -------
        List[int]
            Block indices (0 or 1) for each block
        """
        if not self.blocks:
            raise ValueError(f"Series {self.series_id} has no blocks specified")
        
        # If already integers, validate and return
        if isinstance(self.blocks[0], int):
            if len(self.blocks) != len(block_names):
                raise ValueError(
                    f"Series {self.series_id} has {len(self.blocks)} block indices "
                    f"but {len(block_names)} blocks defined"
                )
            return list(self.blocks)
        
        # Convert block names to indices
        # Normalize block names (handle both underscore and hyphen variants)
        block_names_normalized = {name.replace('-', '_'): name for name in block_names}
        blocks_normalized = {name.replace('-', '_'): name for name in self.blocks}
        
        block_indices = [0] * len(block_names)
        for block_name in self.blocks:
            block_name_norm = block_name.replace('-', '_')
            if block_name_norm not in block_names_normalized:
                # Try exact match first
                if block_name in block_names:
                    block_indices[block_names.index(block_name)] = 1
                else:
                    raise ValueError(
                        f"Series {self.series_id} references block '{block_name}' "
                        f"which is not in block_names: {block_names}. "
                        f"Note: Block names are case-sensitive and must match exactly."
                    )
            else:
                # Use normalized name to find index
                actual_block_name = block_names_normalized[block_name_norm]
                block_indices[block_names.index(actual_block_name)] = 1
        
        return block_indices


@dataclass
class DFMConfig:
    """Unified DFM configuration - model structure + estimation parameters.
    
    This is the single configuration class for the DFM module, combining:
    - Model structure (what series, blocks, factors)
    - Estimation parameters (how to run EM algorithm)
    
    The configuration can be built from:
    - Main settings (estimation parameters) from config/default.yaml
    - Series definitions from config/series/default.yaml or CSV
    - Block definitions from config/blocks/default.yaml
    """
    # ========================================================================
    # Model Structure (WHAT - defines the model)
    # ========================================================================
    series: List[SeriesConfig]  # Series specifications
    blocks: Dict[str, BlockConfig]  # Block configurations (block_name -> BlockConfig)
    block_names: List[str] = field(init=False)  # Block names in order (derived from blocks dict)
    factors_per_block: List[int] = field(init=False)  # Number of factors per block (derived from blocks)
    
    # ========================================================================
    # Estimation Parameters (HOW - controls the algorithm)
    # ========================================================================
    ar_lag: int = 1  # Number of lags in AR transition equation (lookback window)
    threshold: float = 1e-5  # EM convergence threshold
    max_iter: int = 5000  # Maximum EM iterations
    nan_method: int = 2  # Missing data handling method (1-5)
    nan_k: int = 3  # Spline parameter for NaN interpolation
    clock: str = 'm'  # Base frequency for nowcasting (global clock): 'd', 'w', 'm', 'q', 'sa', 'a' (defaults to 'm' for monthly)
    
    # ========================================================================
    # Numerical Stability Parameters (transparent and configurable)
    # ========================================================================
    # AR Coefficient Clipping
    clip_ar_coefficients: bool = True  # Enable AR coefficient clipping for stationarity
    ar_clip_min: float = -0.99  # Minimum AR coefficient (must be > -1 for stationarity)
    ar_clip_max: float = 0.99   # Maximum AR coefficient (must be < 1 for stationarity)
    warn_on_ar_clip: bool = True  # Warn when AR coefficients are clipped (indicates near-unit root)
    
    # Data Value Clipping
    clip_data_values: bool = True  # Enable clipping of extreme data values
    data_clip_threshold: float = 100.0  # Clip values beyond this many standard deviations
    warn_on_data_clip: bool = True  # Warn when data values are clipped (indicates outliers)
    
    # Regularization
    use_regularization: bool = True  # Enable regularization for numerical stability
    regularization_scale: float = 1e-6  # Scale factor for ridge regularization (relative to trace)
    min_eigenvalue: float = 1e-8  # Minimum eigenvalue for positive definite matrices
    max_eigenvalue: float = 1e6   # Maximum eigenvalue cap to prevent explosion
    warn_on_regularization: bool = True  # Warn when regularization is applied
    
    # Damped Updates
    use_damped_updates: bool = True  # Enable damped updates when likelihood decreases
    damping_factor: float = 0.8  # Damping factor (0.8 = 80% new, 20% old)
    warn_on_damped_update: bool = True  # Warn when damped updates are used
    
    # ========================================================================
    # Internal cache (not user-configurable)
    # ========================================================================
    _cached_blocks: Optional[np.ndarray] = field(default=None, init=False, repr=False)
    
    def __post_init__(self):
        """Validate blocks structure and consistency.
        
        This method performs comprehensive validation of the DFM configuration:
        - Derives block_names and factors_per_block from blocks dict
        - Ensures at least one series is specified
        - Validates block structure consistency across all series
        - Ensures all series load on the global block
        - Validates block clock constraints (series frequency <= block clock)
        - Validates factor dimensions match block structure
        - Validates clock frequency
        
        Raises
        ------
        ValueError
            If any validation check fails, with a descriptive error message
            indicating what needs to be fixed.
        """
        # Import frequency hierarchy for validation
        from .utils.aggregation import FREQUENCY_HIERARCHY
        
        if not self.series:
            raise ValueError(
                "DFM configuration must contain at least one series. "
                "Please add series definitions to your configuration."
            )
        
        if not self.blocks:
            raise ValueError(
                "DFM configuration must contain at least one block. "
                "Please add block definitions to your configuration."
            )
        
        # Derive block_names and factors_per_block from blocks dict
        # Ensure Block_Global is first
        if 'Block_Global' not in self.blocks:
            raise ValueError(
                "DFM configuration must include 'Block_Global' block. "
                "This is the global/common factor that all series load on."
            )
        
        # Build ordered list: Block_Global first, then others
        # Preserve order from blocks dict, but ensure Block_Global is first
        other_blocks = [name for name in self.blocks.keys() if name != 'Block_Global']
        object.__setattr__(self, 'block_names', ['Block_Global'] + other_blocks)
        object.__setattr__(self, 'factors_per_block', 
                         [self.blocks[name].factors for name in self.block_names])
        
        # Validate global clock
        self.clock = validate_frequency(self.clock)
        global_clock_hierarchy = FREQUENCY_HIERARCHY.get(self.clock, 3)
        
        # Validate block clocks (must be >= global clock)
        for block_name, block_cfg in self.blocks.items():
            block_clock_hierarchy = FREQUENCY_HIERARCHY.get(block_cfg.clock, 3)
            if block_clock_hierarchy < global_clock_hierarchy:
                raise ValueError(
                    f"Block '{block_name}' has clock '{block_cfg.clock}' which is faster than "
                    f"global clock '{self.clock}'. Block clocks must be >= global clock."
                )
        
        # Auto-generate series_id if not provided and convert blocks to indices
        n_blocks = len(self.block_names)
        for i, s in enumerate(self.series):
            if s.series_id is None:
                s.series_id = f"series_{i}"
            if s.series_name is None:
                s.series_name = s.series_id
            
            # Convert block names to indices if needed
            if isinstance(s.blocks, list) and len(s.blocks) > 0:
                if isinstance(s.blocks[0], str):
                    # Convert block names to indices
                    block_indices = s.to_block_indices(self.block_names)
                    object.__setattr__(s, 'blocks', block_indices)
        
        # Validate all series have correct number of blocks
        for i, s in enumerate(self.series):
            if len(s.blocks) != n_blocks:
                raise ValueError(
                    f"Series {i} ('{s.series_id}') has {len(s.blocks)} block loadings, "
                    f"but expected {n_blocks} (from block_names: {self.block_names}). "
                    f"Each series must specify a loading (0 or 1) for each block."
                )
        
        # Check first column (global block) is all 1s
        for i, s in enumerate(self.series):
            if s.blocks[0] != 1:
                raise ValueError(
                    f"Series {i} ('{s.series_id}') must load on the global block "
                    f"(first block '{self.block_names[0]}'). "
                    f"All series must have blocks[0] = 1. "
                    f"Current value: {s.blocks[0]}"
                )
        
        # Validate block clock constraints: series frequency <= block clock
        for i, s in enumerate(self.series):
            series_freq_hierarchy = FREQUENCY_HIERARCHY.get(s.frequency, 3)
            
            # Find which blocks this series loads on
            for block_idx, loads_on_block in enumerate(s.blocks):
                if loads_on_block == 1:
                    block_name = self.block_names[block_idx]
                    block_cfg = self.blocks[block_name]
                    block_clock_hierarchy = FREQUENCY_HIERARCHY.get(block_cfg.clock, 3)
                    
                    # Series frequency must be <= block clock (slower or equal)
                    if series_freq_hierarchy < block_clock_hierarchy:
                        raise ValueError(
                            f"Series '{s.series_id}' has frequency '{s.frequency}' which is faster than "
                            f"block '{block_name}' clock '{block_cfg.clock}'. "
                            f"Series in a block must have frequency <= block clock. "
                            f"Either change the series frequency or move it to a faster block."
                        )
        
        # Validate factors_per_block
        if any(f < 1 for f in self.factors_per_block):
            invalid_blocks = [i for i, f in enumerate(self.factors_per_block) if f < 1]
            raise ValueError(
                f"factors_per_block must contain positive integers (>= 1). "
                f"Invalid values found at block indices {invalid_blocks}: "
                f"{[self.factors_per_block[i] for i in invalid_blocks]}. "
                f"Each block must have at least one factor."
            )
    
    # ========================================================================
    # Helper Methods (snake_case - recommended)
    # ========================================================================
    
    def get_series_ids(self) -> List[str]:
        """Get list of series IDs (snake_case - recommended)."""
        return [s.series_id if s.series_id is not None else f"series_{i}" 
                for i, s in enumerate(self.series)]
    
    def get_series_names(self) -> List[str]:
        """Get list of series names (snake_case - recommended)."""
        return [s.series_name if s.series_name is not None else (s.series_id or f"series_{i}")
                for i, s in enumerate(self.series)]
    
    def get_frequencies(self) -> List[str]:
        """Get list of frequencies (snake_case - recommended)."""
        return [s.frequency for s in self.series]
    
    def get_blocks_array(self) -> np.ndarray:
        """Get blocks as numpy array (snake_case - recommended, cached)."""
        if self._cached_blocks is None:
            blocks_list = [s.blocks for s in self.series]
            self._cached_blocks = np.array(blocks_list, dtype=int)
        return self._cached_blocks
    
    # ========================================================================
    # Legacy Properties (PascalCase - deprecated, use snake_case methods above)
    # ========================================================================
    
    @property
    def SeriesID(self) -> List[str]:
        """DEPRECATED: Use get_series_ids() instead. Backward compatibility only."""
        import warnings
        warnings.warn(
            "SeriesID property is deprecated. Use get_series_ids() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return self.get_series_ids()
    
    @property
    def SeriesName(self) -> List[str]:
        """DEPRECATED: Use get_series_names() instead. Backward compatibility only."""
        import warnings
        warnings.warn(
            "SeriesName property is deprecated. Use get_series_names() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return self.get_series_names()
    
    @property
    def Frequency(self) -> List[str]:
        """DEPRECATED: Use get_frequencies() instead. Backward compatibility only."""
        import warnings
        warnings.warn(
            "Frequency property is deprecated. Use get_frequencies() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return self.get_frequencies()
    
    @property
    def Units(self) -> List[str]:
        """DEPRECATED: Use [s.units for s in config.series] instead. Backward compatibility only."""
        import warnings
        warnings.warn(
            "Units property is deprecated. Access via config.series[i].units instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return [s.units for s in self.series]
    
    @property
    def Transformation(self) -> List[str]:
        """DEPRECATED: Use [s.transformation for s in config.series] instead. Backward compatibility only."""
        import warnings
        warnings.warn(
            "Transformation property is deprecated. Access via config.series[i].transformation instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return [s.transformation for s in self.series]
    
    @property
    def Category(self) -> List[str]:
        """DEPRECATED: Use [s.category for s in config.series] instead. Backward compatibility only."""
        import warnings
        warnings.warn(
            "Category property is deprecated. Access via config.series[i].category instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return [s.category for s in self.series]
    
    @property
    def Aggregate(self) -> List[Optional[str]]:
        """DEPRECATED: Higher frequencies not supported. Always returns None list."""
        import warnings
        warnings.warn(
            "Aggregate property is deprecated. Higher frequencies than clock are not supported.",
            DeprecationWarning,
            stacklevel=2
        )
        return [None for _ in self.series]
    
    @property
    def Blocks(self) -> np.ndarray:
        """DEPRECATED: Use get_blocks_array() instead. Backward compatibility only."""
        import warnings
        warnings.warn(
            "Blocks property is deprecated. Use get_blocks_array() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return self.get_blocks_array()
    
    @property
    def BlockNames(self) -> List[str]:
        """DEPRECATED: Use block_names attribute directly. Backward compatibility only."""
        import warnings
        warnings.warn(
            "BlockNames property is deprecated. Use config.block_names directly.",
            DeprecationWarning,
            stacklevel=2
        )
        return self.block_names
    
    @property
    def UnitsTransformed(self) -> List[str]:
        """DEPRECATED: Use transformation units mapping directly. Backward compatibility only."""
        import warnings
        warnings.warn(
            "UnitsTransformed property is deprecated. Use _TRANSFORM_UNITS_MAP directly.",
            DeprecationWarning,
            stacklevel=2
        )
        return [_TRANSFORM_UNITS_MAP.get(t, t) for t in self.Transformation]
    
    # ========================================================================
    # Factory Methods
    # ========================================================================
    
    @classmethod
    def _extract_estimation_params(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract estimation parameters from dictionary (helper to reduce duplication)."""
        return {
            'ar_lag': data.get('ar_lag', 1),
            'threshold': data.get('threshold', 1e-5),
            'max_iter': data.get('max_iter', 5000),
            'nan_method': data.get('nan_method', 2),
            'nan_k': data.get('nan_k', 3),
            'clock': data.get('clock', 'm'),
            # Numerical stability parameters
            'clip_ar_coefficients': data.get('clip_ar_coefficients', True),
            'ar_clip_min': data.get('ar_clip_min', -0.99),
            'ar_clip_max': data.get('ar_clip_max', 0.99),
            'warn_on_ar_clip': data.get('warn_on_ar_clip', True),
            'clip_data_values': data.get('clip_data_values', True),
            'data_clip_threshold': data.get('data_clip_threshold', 100.0),
            'warn_on_data_clip': data.get('warn_on_data_clip', True),
            'use_regularization': data.get('use_regularization', True),
            'regularization_scale': data.get('regularization_scale', 1e-6),
            'min_eigenvalue': data.get('min_eigenvalue', 1e-8),
            'max_eigenvalue': data.get('max_eigenvalue', 1e6),
            'warn_on_regularization': data.get('warn_on_regularization', True),
            'use_damped_updates': data.get('use_damped_updates', True),
            'damping_factor': data.get('damping_factor', 0.8),
            'warn_on_damped_update': data.get('warn_on_damped_update', True)
        }
    
    @classmethod
    def _from_legacy_dict(cls, data: Dict[str, Any]) -> 'DFMConfig':
        """Convert legacy format (separate lists) to new format (series list)."""
        series_list = []
        n = len(data.get('SeriesID', data.get('series_id', [])))
        
        # Handle Blocks - can be numpy array or list of lists
        blocks_data = data.get('Blocks', data.get('blocks', []))
        if isinstance(blocks_data, np.ndarray):
            blocks_data = blocks_data.tolist()
        elif not isinstance(blocks_data, list):
            blocks_data = []
        
        # Helper to get list value with index fallback
        def get_list_value(key: str, index: int, default=None):
            """Get value from list, handling both camelCase and snake_case keys."""
            val = data.get(key, data.get(key.lower(), default))
            if isinstance(val, list) and index < len(val):
                return val[index]
            return default
        
        for i in range(n):
            # Extract blocks for this series
            if blocks_data and i < len(blocks_data):
                if isinstance(blocks_data[i], (list, np.ndarray)):
                    series_blocks = list(blocks_data[i]) if isinstance(blocks_data[i], np.ndarray) else blocks_data[i]
                else:
                    series_blocks = [blocks_data[i]]
            else:
                series_blocks = []
            
            series_list.append(SeriesConfig(
                frequency=str(get_list_value('Frequency', i, 'm')),
                transformation=str(get_list_value('Transformation', i, 'lin')),
                blocks=series_blocks,
                series_id=get_list_value('SeriesID', i, None),
                series_name=get_list_value('SeriesName', i, None),
                units=str(get_list_value('Units', i, '')),
                category=str(get_list_value('Category', i, '')),
                aggregate=get_list_value('Aggregate', i, None)
            ))
        
        return cls(
            series=series_list,
            block_names=data.get('BlockNames', data.get('block_names', [])),
            factors_per_block=data.get('factors_per_block', None),
            **cls._extract_estimation_params(data)
        )
    
    @classmethod
    def _from_hydra_dict(cls, data: Dict[str, Any]) -> 'DFMConfig':
        """Convert Hydra format (series as dict) to new format."""
        # Get block_names first (required for series processing)
        blocks_dict = data.get('blocks', {})
        if isinstance(blocks_dict, dict) and blocks_dict:
            block_names = list(blocks_dict.keys())
            factors_per_block = [
                blocks_dict[bn].get('factors', 1) if isinstance(blocks_dict[bn], dict) else blocks_dict[bn]
                for bn in block_names
            ]
        else:
            block_names = data.get('block_names', [])
            factors_per_block = data.get('factors_per_block', None)
        
        # If block_names is still empty, try to infer from series blocks
        if not block_names and 'series' in data:
            # Collect all unique block names from series
            all_blocks = set()
            for series_cfg in data['series'].values():
                if isinstance(series_cfg, dict):
                    series_blocks = series_cfg.get('blocks', [])
                    if isinstance(series_blocks, list):
                        all_blocks.update(series_blocks)
            if all_blocks:
                # Ensure Block_Global is first
                block_names = ['Block_Global'] if 'Block_Global' in all_blocks else []
                block_names.extend(sorted([b for b in all_blocks if b != 'Block_Global']))
                factors_per_block = [1] * len(block_names)
        
        # Parse series dict: {series_id: {frequency: ..., blocks: [block_names], ...}}
        series_list = []
        for series_id, series_cfg in data['series'].items():
            if isinstance(series_cfg, dict):
                # Convert block names to binary array (0/1 for each block)
                series_blocks_names = series_cfg.get('blocks', [])
                if isinstance(series_blocks_names, list) and series_blocks_names:
                    # Create binary array: 1 if series loads on block, 0 otherwise
                    # First block (Global) must always be 1
                    series_blocks = [0] * len(block_names)
                    series_blocks[0] = 1  # Global block is always 1
                    for block_name in series_blocks_names:
                        if block_name in block_names:
                            block_idx = block_names.index(block_name)
                            series_blocks[block_idx] = 1
                else:
                    # Default: only global block
                    series_blocks = [1] + [0] * (len(block_names) - 1)
                
                series_list.append(SeriesConfig(
                    series_id=series_id,
                    series_name=series_cfg.get('series_name', series_id),
                    frequency=series_cfg.get('frequency', 'm'),
                    transformation=series_cfg.get('transformation', 'lin'),
                    blocks=series_blocks,
                    units=series_cfg.get('units', ''),
                    category=series_cfg.get('category', ''),
                    aggregate=series_cfg.get('aggregate', None)  # Deprecated
                ))
        
        return cls(
            series=series_list,
            block_names=block_names,
            factors_per_block=factors_per_block if factors_per_block else None,
            **cls._extract_estimation_params(data)
        )
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DFMConfig':
        """Create DFMConfig from dictionary.
        
        Handles multiple formats:
        1. Legacy format: {'SeriesID': [...], 'Frequency': [...], 'Blocks': [[...]], ...}
        2. New format (list): {'series': [{'series_id': ..., ...}], 'block_names': [...]}
        3. New format (Hydra): {'series': {'series_id': {...}}, 'blocks': {'block_name': {'factors': N}}}
        
        Also accepts estimation parameters: ar_lag, threshold, max_iter, nan_method, nan_k
        """
        # Detect legacy format (has SeriesID or series_id as lists)
        if 'SeriesID' in data or ('series_id' in data and isinstance(data.get('series_id'), list)):
            return cls._from_legacy_dict(data)
        
        # New Hydra format: series is a dict
        if 'series' in data and isinstance(data['series'], dict):
            return cls._from_hydra_dict(data)
        
        # New format with series list
        if 'series' in data and isinstance(data['series'], list):
            series_list = [
                SeriesConfig(**s) if isinstance(s, dict) else s 
                for s in data['series']
            ]
            return cls(
                series=series_list,
                block_names=data.get('block_names', []),
                factors_per_block=data.get('factors_per_block', None),
                **cls._extract_estimation_params(data)
            )
        
        # Direct instantiation (shouldn't happen often, but handle it)
        return cls(**data)


# Register with Hydra ConfigStore (optional - only if Hydra is available)
if HYDRA_AVAILABLE and ConfigStore is not None:
    try:
        cs = ConfigStore.instance()
        if cs is not None:
            from dataclasses import dataclass as schema_dataclass
            
            @schema_dataclass
            class SeriesConfigSchema:
                """Schema for SeriesConfig validation in Hydra."""
                series_id: str
                series_name: str
                frequency: str
                units: str
                transformation: str
                category: str
                blocks: List[int]
            
            @schema_dataclass
            class DFMConfigSchema:
                """Schema for unified DFMConfig validation in Hydra."""
                series: List[SeriesConfigSchema]
                block_names: List[str]
                factors_per_block: Optional[List[int]] = None
                ar_lag: int = 1
                threshold: float = 1e-5
                max_iter: int = 5000
                nan_method: int = 2
                nan_k: int = 3
                clock: str = 'm'
            
            # Register schemas
            cs.store(group="dfm", name="base_dfm_config", node=DFMConfigSchema)
            cs.store(group="model", name="base_model_config", node=DFMConfigSchema)
            cs.store(name="dfm_config_schema", node=DFMConfigSchema)
            cs.store(name="model_config_schema", node=DFMConfigSchema)
            
    except Exception as e:
        warnings.warn(f"Could not register Hydra structured config schemas: {e}. "
                     f"Configs will still work via from_dict() but without schema validation.")
