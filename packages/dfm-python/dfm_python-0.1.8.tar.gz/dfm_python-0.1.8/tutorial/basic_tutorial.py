#!/usr/bin/env python3
"""
DFM Python - Basic Tutorial

This script demonstrates the basic usage of the Dynamic Factor Model (DFM) package.

Outline:
1. Data Loading
2. Model Training
3. Inference and Forecasting
"""

# Import required libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import pickle
import warnings
warnings.filterwarnings('ignore')

# DFM package import
# Method 1: High-level API (recommended - simple and intuitive)
import dfm_python as dfm
from dfm_python import DFMResult  # For type hints

# Method 2: Low-level API (for advanced users)
# from dfm_python import (
#     load_config_from_spec, load_config, load_data, dfm as dfm_func, 
#     DFMResult, calculate_rmse
# )

print("✓ All libraries loaded")

# ============================================================================
# 1. Data Loading
# ============================================================================

print("\n" + "="*70)
print("1. Data Loading")
print("="*70)

# 1.1 Load configuration
# You can load configuration in multiple ways:
# - Hydra-style YAML: load_config('config/default.yaml') - recommended
# - Spec file: load_config_from_spec('data/sample_spec.csv')
# - Single YAML: load_config('config/sample_config.yaml')

# Method 1: High-level API (recommended)
dfm.load_config('config/default.yaml')
config = dfm.get_config()

print(f"\n✓ Config loaded")
print(f"  - series: {len(config.series)}")
print(f"  - blocks: {len(config.block_names)}")
print(f"  - block names: {', '.join(config.block_names)}")
print(f"  - clock: {config.clock}")

# Method 2: Load from spec file
# dfm.load_config_from_spec('data/sample_spec.csv')
# config = dfm.get_config()

# Method 3: Low-level API
# from dfm_python import load_config
# config = load_config('config/default.yaml')

# 설정 정보 확인
print("\nSeries sample (first 5):")
for i, series in enumerate(config.series[:5]):
    print(f"  {i+1}. {series.series_id}: {series.series_name[:50]}...")
    print(f"     frequency: {series.frequency}, transformation: {series.transformation}, blocks: {series.blocks}")

# 1.2 Load and transform data
# Load data file and transform according to configuration.

# High-level API use (quick test with recent data only)
dfm.load_data('data/sample_data.csv', sample_start='2022-01-01')
X = dfm.get_data()
Time = dfm.get_time()
Z = dfm.get_original_data()  # Original (untransformed) data

# Low-level API (alternative)
# from dfm_python import load_data as load_data_func
# X, Time, Z = load_data_func('data/sample_data.csv', config)

print(f"\n✓ Data loaded")
print(f"  - shape: {X.shape} (time x series)")
print(f"  - time range: {Time[0]} ~ {Time[-1]}")
print(f"  - periods: {len(Time)}")
print(f"  - num series: {X.shape[1]}")
print(f"  - missing ratio: {np.isnan(X).sum() / X.size * 100:.2f}%")

# Data visualization (first 5 series)
try:
    fig, axes = plt.subplots(5, 1, figsize=(12, 10))
    for i in range(min(5, X.shape[1])):
        axes[i].plot(Time, X[:, i], linewidth=1.5)
        axes[i].set_title(f"{config.series[i].series_id}: {config.series[i].series_name[:50]}...")
        axes[i].set_ylabel("Value")
        axes[i].grid(True, alpha=0.3)
    axes[-1].set_xlabel("Date")
    plt.tight_layout()
    plt.savefig('outputs/data_visualization.png', dpi=150, bbox_inches='tight')
    print("\n✓ Saved data visualization: outputs/data_visualization.png")
    plt.close()
except Exception as e:
    print(f"\n⚠ Plot error (continuing): {e}")

# ============================================================================
# 2. Model Training
# ============================================================================

print("\n" + "="*70)
print("2. Model Training")
print("="*70)

# Train model
# threshold: convergence tolerance (smaller = more precise, slower)
# max_iter: maximum iterations (use small for tests)

# High-level API use (fast test mode)
dfm.train(
    fast=True,       # Fast test mode (default: threshold=1e-2, max_iter=5)
    max_iter=1       # Minimal execution with 1 iteration for quick verification
)
result = dfm.result

# Low-level API (alternative - quick settings)
# from dfm_python import dfm as dfm_func
# result = dfm_func(X, config, threshold=1e-2, max_iter=3)

print(f"\n✓ Model training complete!")
print(f"  - converged: {result.converged}")
print(f"  - iterations: {result.num_iter}")
print(f"  - final log-likelihood: {result.loglik:.2f}")
print(f"  - num factors: {result.Z.shape[1]}")
print(f"  - loading matrix shape: {result.C.shape}")
print(f"  - transition matrix shape: {result.A.shape}")

# Model fit
if result.rmse is not None:
    print(f"\nModel fit:")
    print(f"  - overall RMSE: {result.rmse:.4f}")
    print(f"  - RMSE per series (top 5):")
    rmse_per_series = result.rmse_per_series
    top_5_idx = np.argsort(rmse_per_series)[:5]
    for idx in top_5_idx:
        print(f"    {config.series[idx].series_id}: {rmse_per_series[idx]:.4f}")

# Common factor visualization skipped for quick test
# Uncomment to enable:
# try:
#     common_factor = result.Z[:, 0]
#     plt.figure(figsize=(12, 4))
#     plt.plot(Time, common_factor, linewidth=2, label='Common Factor')
#     plt.title('Common Factor', fontsize=14)
#     plt.xlabel('Date')
#     plt.ylabel('Factor value')
#     plt.grid(True, alpha=0.3)
#     plt.legend()
#     plt.tight_layout()
#     plt.savefig('outputs/common_factor.png', dpi=150, bbox_inches='tight')
#     print("\n✓ Saved common factor plot: outputs/common_factor.png")
#     plt.close()
# except Exception as e:
#     print(f"\n⚠ Plot error (continuing): {e}")

# Save trained model
output_dir = Path('outputs')
output_dir.mkdir(exist_ok=True)

model_path = output_dir / 'trained_model.pkl'
with open(model_path, 'wb') as f:
    pickle.dump({
        'result': result,
        'config': config,
        'Time': Time,
        'X_original': Z,  # Original data
        'X_transformed': X,  # Transformed data
    }, f)

print(f"\n✓ Model saved: {model_path}")

# ============================================================================
# 3. Inference and Forecasting
# ============================================================================

print("\n" + "="*70)
print("3. Inference and Forecasting")
print("="*70)

def forecast_factors(result: DFMResult, horizon: int):
    """Forecast factors for a given horizon."""
    A = result.A
    Z_last = result.Z[-1, :]  # Last observed factor value
    
    # Forecast factors forward
    Z_forecast = np.zeros((horizon, Z_last.shape[0]))
    Z_forecast[0, :] = A @ Z_last
    
    for h in range(1, horizon):
        Z_forecast[h, :] = A @ Z_forecast[h-1, :]
    
    return Z_forecast

def forecast_series(result: DFMResult, horizon: int):
    """Forecast observed series using factor forecasts."""
    Z_forecast = forecast_factors(result, horizon)
    
    # Project factors to series space
    X_forecast = Z_forecast @ result.C.T
    
    # Unstandardize (restore to original scale)
    X_forecast_unstd = X_forecast * result.Wx + result.Mx
    
    return X_forecast_unstd, Z_forecast

# Perform forecasting
forecast_horizon = 12  # 12 months ahead

X_forecast, Z_forecast = forecast_series(result, forecast_horizon)

print(f"\n✓ Forecast complete")
print(f"  - horizon: {forecast_horizon}")
print(f"  - forecasted series shape: {X_forecast.shape}")
print(f"  - forecasted factors shape: {Z_forecast.shape}")

# Visualize factor forecast
try:
    plt.figure(figsize=(14, 5))
    
    # Past factor
    plt.plot(Time, result.Z[:, 0], 'b-', linewidth=2, label='Past factor')
    
    # Forecast factor
    forecast_dates = pd.date_range(start=Time[-1] + pd.Timedelta(days=30), periods=forecast_horizon, freq='M')
    plt.plot(forecast_dates, Z_forecast[:, 0], 'r--', linewidth=2, label='Forecast factor')
    
    plt.axvline(x=Time[-1], color='gray', linestyle=':', linewidth=1, label='Forecast start')
    plt.title('Common Factor: Past and Forecast', fontsize=14)
    plt.xlabel('Date')
    plt.ylabel('Factor value')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('outputs/factor_forecast.png', dpi=150, bbox_inches='tight')
    print("\n✓ Saved factor forecast plot: outputs/factor_forecast.png")
    plt.close()
except Exception as e:
    print(f"\n⚠ Plot error (continuing): {e}")

# Series forecast visualization skipped for quick test
# Uncomment to enable:
# try:
#     series_idx = 0
#     series_id = config.series[series_idx].series_id
#     series_name = config.series[series_idx].series_name
#     plt.figure(figsize=(14, 5))
#     plt.plot(Time, Z[:, series_idx], 'b-', linewidth=2, label='Observed', alpha=0.7)
#     plt.plot(Time, result.X_sm[:, series_idx], 'g-', linewidth=1.5, label='Smoothed', alpha=0.7)
#     forecast_dates = pd.date_range(start=Time[-1] + pd.Timedelta(days=30), periods=forecast_horizon, freq='M')
#     plt.plot(forecast_dates, X_forecast[:, series_idx], 'r--', linewidth=2, label='Forecast')
#     plt.axvline(x=Time[-1], color='gray', linestyle=':', linewidth=1, label='Forecast start')
#     plt.title(f'{series_id}: {series_name[:50]}...', fontsize=14)
#     plt.xlabel('Date')
#     plt.ylabel('Value')
#     plt.legend()
#     plt.grid(True, alpha=0.3)
#     plt.tight_layout()
#     plt.savefig('outputs/series_forecast.png', dpi=150, bbox_inches='tight')
#     print("\n✓ Saved series forecast plot: outputs/series_forecast.png")
#     plt.close()
# except Exception as e:
#     print(f"\n⚠ Plot error (continuing): {e}")

# Save forecasts to CSV
forecast_dates = pd.date_range(start=Time[-1] + pd.Timedelta(days=30), periods=forecast_horizon, freq='M')
# Use new API: get_series_ids() method
series_ids = config.get_series_ids()
forecast_df = pd.DataFrame(
    X_forecast,
    index=forecast_dates,
    columns=series_ids
)

forecast_path = output_dir / 'forecasts.csv'
forecast_df.to_csv(forecast_path)
print(f"\n✓ Saved forecast CSV: {forecast_path}")
print(f"\nForecast sample (first 5 series, first 3 periods):")
print(forecast_df.iloc[:3, :5])

# ============================================================================
# 4. Load Saved Model and Reuse
# ============================================================================

print("\n" + "="*70)
print("4. Load saved model and reuse")
print("="*70)

# Load saved model
with open(model_path, 'rb') as f:
    model_data = pickle.load(f)

loaded_result = model_data['result']
loaded_config = model_data['config']
loaded_time = model_data['Time']

print(f"\n✓ Model loaded")
print(f"  - Training span: {loaded_time[0]} ~ {loaded_time[-1]}")
print(f"  - Number of factors: {loaded_result.Z.shape[1]}")
print(f"  - Number of series: {loaded_result.C.shape[0]}")

# Use loaded model for forecasting
X_forecast_loaded, Z_forecast_loaded = forecast_series(loaded_result, forecast_horizon)
print(f"\n✓ Forecast with loaded model complete")
print(f"  - forecasted series shape: {X_forecast_loaded.shape}")

# ============================================================================
# Summary
# ============================================================================

print("\n" + "="*70)
print("Summary")
print("="*70)

print("""
In this tutorial, we covered:

1. Data Loading: load config (Hydra) and read data CSV
2. Model Training: estimate factors and parameters using the DFM
3. Forecasting: forecast factors and series into the future
4. Save/Load: persist and reuse trained results

Next steps:
- News Decomposition: analyze forecast updates when new data arrives
- Hyperparameter Tuning: adjust `threshold`, `max_iter`, etc.
- Block Structure Experiments: try different block configurations
- Visualization: extend factor and series plots
""")

print("\n✓ Tutorial complete!")

