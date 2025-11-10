#!/usr/bin/env python3
"""
DFM Python - Simple API Example

A short example using the new object-oriented API.

Usage:
    import dfm_python as dfm
    dfm.load_config('config/default.yaml')
    dfm.load_data('data/sample_data.csv')
    dfm.train(fast=True)
    factors = dfm.result.Z  # or dfm.get_result().Z
"""

import dfm_python as dfm

# 1) Load config
dfm.load_config('config/default.yaml')
cfg = dfm.get_config()
print(f"✓ Config loaded: {len(cfg.series)} series, {len(cfg.block_names)} blocks")

# 2) Load data
dfm.load_data('data/sample_data.csv')
data = dfm.get_data()
print(f"✓ Data loaded: {data.shape}")

# 3) Train model (fast mode)
dfm.train(fast=True, max_iter=3)
result = dfm.result
print(f"✓ Training complete: converged={result.converged}, iterations={result.num_iter}")

# 4) Inspect results
print(f"✓ Num factors: {result.Z.shape[1]}")
print(f"✓ Log-likelihood: {result.loglik:.2f}")

# 5) Extract factors
common_factor = result.Z[:, 0]
print(f"✓ Common factor shape: {common_factor.shape}")

print("\n✓ All done!")

