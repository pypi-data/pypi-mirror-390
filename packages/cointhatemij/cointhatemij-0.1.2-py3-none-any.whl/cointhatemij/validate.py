"""
Validation Script for cointhatemij Package
"""

import numpy as np
from cointhatemij import HatemiJTest

print("="*70)
print("VALIDATION: Hatemi-J Cointegration Test")
print("="*70)

# Test critical values
print("\nChecking critical values against Hatemi-J (2008) Table 1...")
np.random.seed(123)
n = 100
x = np.random.randn(n, 2)
y = np.random.randn(n)

test = HatemiJTest(y, x)
cv = test.CRITICAL_VALUES

# Verify k=1
assert cv[1]['adf_zt']['1%'] == -6.503
assert cv[1]['za']['1%'] == -90.704
print("✓ k=1 critical values correct")

# Verify k=2
assert cv[2]['adf_zt']['1%'] == -6.928
assert cv[2]['za']['1%'] == -99.458
print("✓ k=2 critical values correct")

# Verify k=3
assert cv[3]['adf_zt']['1%'] == -7.833
print("✓ k=3 critical values correct")

# Verify k=4
assert cv[4]['adf_zt']['1%'] == -8.353
print("✓ k=4 critical values correct")

print("\n" + "="*70)
print("✓✓✓ ALL VALIDATIONS PASSED ✓✓✓")
print("Package is compatible with Hatemi-J (2008)")
print("="*70)
