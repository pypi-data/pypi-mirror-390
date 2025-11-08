"""
Basic Example: Simple Cointegration Test
"""

import numpy as np
from cointhatemij import coint_hatemi_j

# Set random seed
np.random.seed(123)

# Generate sample data
print("Generating synthetic data...")
n = 100
x = np.random.randn(n, 2)
y = 0.5 + 0.3 * x[:, 0] + 0.2 * x[:, 1] + np.random.randn(n)

print(f"\nDataset: {n} observations, {x.shape[1]} independent variables")

# Run test
print("\nRunning Hatemi-J Cointegration Test...")
results = coint_hatemi_j(y, x, verbose=True)

# Access results
print("\n" + "="*65)
print("Results Summary")
print("="*65)
print(f"ADF statistic: {results['ADF_min']:.4f}")
print(f"Break dates: {results['TB1_adf']}, {results['TB2_adf']}")
print("="*65)
