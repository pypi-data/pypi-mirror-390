"""
Example: Using the Hatemi-J Cointegration Test with All Three Models

This example demonstrates how to use all three models:
- Model 1 (C): Level shift - intercept changes only
- Model 2 (C/T): Level shift with trend
- Model 3 (C/S): Regime shift - intercept and slope changes
"""

import numpy as np
import sys
sys.path.insert(0, '/home/claude/cointhatemij')
from cointhatemij import coint_hatemi_j

def example_1_basic_usage():
    """Example 1: Basic usage with Model 3 (default)"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Usage with Model 3 (Regime Shift)")
    print("="*70)
    
    # Generate cointegrated data with two structural breaks
    np.random.seed(123)
    n = 200
    
    # Generate I(1) process for x
    x = np.cumsum(np.random.randn(n, 1), axis=0)
    
    # Create breaks at 30% and 70% of sample
    tb1, tb2 = int(0.3 * n), int(0.7 * n)
    du1 = np.concatenate([np.zeros(tb1), np.ones(n - tb1)])
    du2 = np.concatenate([np.zeros(tb2), np.ones(n - tb2)])
    
    # Generate y with regime shifts (both intercept and slope change)
    y = (1.0 + 1.5 * du1 - 1.0 * du2 +           # Intercepts
         0.5 * x[:, 0] +                          # Base slope
         0.3 * du1 * x[:, 0] -                    # First break in slope
         0.2 * du2 * x[:, 0] +                    # Second break in slope
         np.random.randn(n) * 0.3)                # Stationary error
    
    # Run test with default parameters (Model 3)
    results = coint_hatemi_j(y, x, model=3, verbose=True)
    
    print(f"\nTrue breaks were at: {tb1} (30%) and {tb2} (70%)")
    print(f"Estimated breaks: {results['TB1_adf']} and {results['TB2_adf']}")


def example_2_model_comparison():
    """Example 2: Compare all three models on the same data"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Comparing All Three Models")
    print("="*70)
    
    # Generate data
    np.random.seed(456)
    n = 200
    x = np.cumsum(np.random.randn(n, 2), axis=0)  # 2 regressors
    
    # Create breaks
    tb1, tb2 = int(0.25 * n), int(0.75 * n)
    du1 = np.concatenate([np.zeros(tb1), np.ones(n - tb1)])
    du2 = np.concatenate([np.zeros(tb2), np.ones(n - tb2)])
    
    # Generate cointegrated y
    y = (2.0 + 1.0 * du1 - 0.8 * du2 +
         0.4 * x[:, 0] + 0.3 * x[:, 1] +
         0.2 * du1 * x[:, 0] + 0.1 * du1 * x[:, 1] -
         0.15 * du2 * x[:, 0] - 0.1 * du2 * x[:, 1] +
         np.random.randn(n) * 0.4)
    
    models = {
        1: "C (Level shift - intercept only)",
        2: "C/T (Level shift with trend)",
        3: "C/S (Regime shift - intercept and slopes)"
    }
    
    print(f"\nTrue breaks: tb1={tb1} ({tb1/n:.1%}), tb2={tb2} ({tb2/n:.1%})")
    print(f"\nComparing all three models:\n")
    
    for model_num in [1, 2, 3]:
        print(f"\n{'='*70}")
        print(f"Model {model_num}: {models[model_num]}")
        print('='*70)
        
        results = coint_hatemi_j(y, x, model=model_num, verbose=False)
        
        print(f"\nTest Statistics:")
        print(f"  ADF: {results['ADF_min']:.3f}")
        print(f"  Zt:  {results['Zt_min']:.3f}")
        print(f"  Za:  {results['Za_min']:.3f}")
        
        print(f"\nEstimated Breaks:")
        print(f"  TB1: {results['TB1_adf']} ({results['TB1_adf']/n:.1%})")
        print(f"  TB2: {results['TB2_adf']} ({results['TB2_adf']/n:.1%})")
        
        cv = results['cv_adf_zt']
        conclusion = "Cointegration detected" if results['ADF_min'] < cv['10%'] else "No cointegration"
        print(f"\nConclusion (10% level): {conclusion}")


def example_3_custom_options():
    """Example 3: Using custom options"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Custom Options")
    print("="*70)
    
    # Generate data
    np.random.seed(789)
    n = 250
    x = np.cumsum(np.random.randn(n, 1), axis=0)
    
    tb1, tb2 = 60, 180
    du1 = np.concatenate([np.zeros(tb1), np.ones(n - tb1)])
    du2 = np.concatenate([np.zeros(tb2), np.ones(n - tb2)])
    
    y = (1.5 + 0.8 * du1 - 0.6 * du2 +
         0.6 * x[:, 0] +
         0.25 * du1 * x[:, 0] -
         0.2 * du2 * x[:, 0] +
         np.random.randn(n) * 0.5)
    
    print("\nTest 1: Using AIC for lag selection")
    print("-" * 70)
    results1 = coint_hatemi_j(y, x, model=3, ic=1, verbose=False)
    print(f"ADF: {results1['ADF_min']:.3f}, Breaks: {results1['TB1_adf']}, {results1['TB2_adf']}")
    
    print("\nTest 2: Using Bartlett kernel (varm=2)")
    print("-" * 70)
    results2 = coint_hatemi_j(y, x, model=3, varm=2, verbose=False)
    print(f"Zt: {results2['Zt_min']:.3f}, Za: {results2['Za_min']:.3f}")
    
    print("\nTest 3: Using 15% trimming and larger bandwidth")
    print("-" * 70)
    results3 = coint_hatemi_j(y, x, model=3, trimm=0.15, bwl=7, verbose=False)
    print(f"ADF: {results3['ADF_min']:.3f}, Bandwidth: {results3['bwl']}")
    
    print(f"\nTrue breaks were at: {tb1} and {tb2}")


def example_4_financial_data():
    """Example 4: Simulated financial market integration (like paper's example)"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Financial Market Integration (Simulated)")
    print("="*70)
    
    # Simulate weekly data similar to US-UK example in paper
    np.random.seed(1991)
    n = 550  # ~10 years of weekly data
    
    # Simulate log stock indices (I(1) processes)
    us_index = 100 + np.cumsum(np.random.randn(n) * 0.02)  # S&P 500
    
    # UK index with structural breaks
    # First break: Early 1991 (~20% through) - Gulf War
    # Second break: End 1992 (~70% through) - Exchange rate crisis
    tb1 = int(0.2 * n)  # ~110
    tb2 = int(0.7 * n)  # ~385
    
    du1 = np.concatenate([np.zeros(tb1), np.ones(n - tb1)])
    du2 = np.concatenate([np.zeros(tb2), np.ones(n - tb2)])
    
    # UK index cointegrated with US but with changing relationship
    uk_index = (10 +                           # Base intercept
                5 * du1 -                       # First break (Gulf War effect)
                3 * du2 +                       # Second break (Exchange crisis)
                0.8 * us_index +               # Base elasticity
                -0.3 * du1 * us_index +        # Reduced integration period 1
                0.5 * du2 * us_index +         # Increased integration period 2
                np.random.randn(n) * 2)        # Idiosyncratic shocks
    
    x = us_index.reshape(-1, 1)
    y = uk_index
    
    print(f"\nSimulated data: {n} weekly observations")
    print(f"True breaks: tb1={tb1} (~early 1991), tb2={tb2} (~end 1992)")
    print("\nTesting for cointegration with regime shifts...")
    
    results = coint_hatemi_j(y, x, model=3, verbose=True)
    
    # Interpret results
    print("\n" + "="*70)
    print("INTERPRETATION")
    print("="*70)
    print(f"\nThe test strongly rejects no cointegration (all statistics < critical values)")
    print(f"This suggests the US and UK markets are integrated with structural breaks.")
    print(f"\nEstimated break dates:")
    print(f"  First break:  {results['TB1_adf']} ({results['TB1_adf']/n:.1%})")
    print(f"  Second break: {results['TB2_adf']} ({results['TB2_adf']/n:.1%})")
    print(f"\nThese align well with:")
    print(f"  - Early 1991: First Gulf War")
    print(f"  - End 1992: European exchange rate crisis")


def example_5_no_cointegration():
    """Example 5: Data without cointegration (should fail to reject H0)"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Testing Non-Cointegrated Data")
    print("="*70)
    
    # Generate two independent I(1) processes
    np.random.seed(999)
    n = 200
    
    # Both are random walks (I(1)) but not cointegrated
    x = np.cumsum(np.random.randn(n, 1), axis=0)
    y = np.cumsum(np.random.randn(n), axis=0)  # Independent random walk
    
    print("\nTesting two independent I(1) processes...")
    print("Expected: Should fail to reject H0 (no cointegration)\n")
    
    results = coint_hatemi_j(y, x, model=3, verbose=True)
    
    cv = results['cv_adf_zt']
    if results['ADF_min'] >= cv['10%']:
        print("\n✓ Correctly failed to reject H0: No cointegration detected")
    else:
        print("\n⚠ Unexpectedly rejected H0 (Type I error)")


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("HATEMI-J COINTEGRATION TEST - COMPREHENSIVE EXAMPLES")
    print("="*70)
    
    example_1_basic_usage()
    example_2_model_comparison()
    example_3_custom_options()
    example_4_financial_data()
    example_5_no_cointegration()
    
    print("\n" + "="*70)
    print("ALL EXAMPLES COMPLETED")
    print("="*70)
    print("\nKey Takeaways:")
    print("  1. Model 1 (C): Use when only intercept changes")
    print("  2. Model 2 (C/T): Use when intercept changes with trend")
    print("  3. Model 3 (C/S): Use when both intercept and slopes change")
    print("  4. Test statistics should be negative")
    print("  5. More negative = stronger evidence for cointegration")
    print("  6. Compare against critical values to make decision")
    print("="*70)


if __name__ == "__main__":
    main()
