# cointhatemij

**Hatemi-J Cointegration Test with Two Unknown Regime Shifts**

A Python implementation of the Hatemi-J (2008) cointegration test that allows for two structural breaks with unknown timing.

## Reference

**Hatemi-J, A. (2008)**. Tests for cointegration with two unknown regime shifts with an application to financial market integration. *Empirical Economics*, 35, 497-505. DOI: [10.1007/s00181-007-0175-9](https://doi.org/10.1007/s00181-007-0175-9)

## Features

- ✅ Three test statistics (ADF, Zt, Za)
- ✅ Endogenous detection of two structural breaks
- ✅ Multiple lag selection criteria (AIC, BIC, t-stat)
- ✅ Various variance estimation methods
- ✅ Critical values for k ≤ 4 independent variables
- ✅ Fully validated against original paper

## Installation

```bash
pip install cointhatemij
```

## Quick Start

```python
import numpy as np
from cointhatemij import coint_hatemi_j

# Your data
y = np.array([...])  # Dependent variable
x = np.array([...])  # Independent variable(s)

# Run test
results = coint_hatemi_j(y, x)

# Check results
print(f"ADF statistic: {results['ADF_min']:.3f}")
print(f"Break dates: {results['TB1_adf']}, {results['TB2_adf']}")
```

## Usage Example

```python
import numpy as np
from cointhatemij import HatemiJTest

# Generate sample data
np.random.seed(123)
n = 100
x = np.random.randn(n, 2)
y = 0.5 + 0.3 * x[:, 0] + 0.2 * x[:, 1] + np.random.randn(n)

# Create test instance
test = HatemiJTest(y, x, 
                   model=3,      # Only model 3 available
                   ic=3,         # t-stat lag selection
                   pmax=8,       # Maximum 8 lags
                   varm=1,       # iid variance
                   trimm=0.10)   # 10% trimming

# Run test
results = test.fit()

# Display results
test.summary()
```

## Parameters

- **y**: Dependent variable (n × 1)
- **x**: Independent variables (n × k), where k ≤ 4
- **model**: Model specification (only 3 available)
- **ic**: Information criterion (1=AIC, 2=BIC, 3=t-stat)
- **pmax**: Maximum lags for ADF test (default: 8)
- **varm**: Variance method (1=iid, 2=Bartlett, 3=QS)
- **trimm**: Trimming rate (default: 0.10)

## Output

Returns dictionary with:
- **ADF_min**, **Zt_min**, **Za_min**: Test statistics
- **TB1_adf**, **TB2_adf**: Break dates (ADF)
- **TB1_zt**, **TB2_zt**: Break dates (Zt)
- **TB1_za**, **TB2_za**: Break dates (Za)
- **cv_adf_zt**, **cv_za**: Critical values

## Critical Values

From Hatemi-J (2008), Table 1:

| k | Test    | 1%       | 5%       | 10%      |
|---|---------|----------|----------|----------|
| 1 | ADF/Zt  | -6.503   | -6.015   | -5.653   |
| 2 | ADF/Zt  | -6.928   | -6.458   | -6.224   |
| 3 | ADF/Zt  | -7.833   | -7.352   | -7.118   |
| 4 | ADF/Zt  | -8.353   | -7.903   | -7.705   |

## Methodology

The test is based on the model:

```
y_t = α_0 + α_1*D1_t + α_2*D2_t + β_0'*x_t + β_1'*D1_t*x_t + β_2'*D2_t*x_t + u_t
```

Where D1_t and D2_t are dummy variables for two structural breaks. Break dates are estimated endogenously, and three test statistics are computed as the minimum values across all possible break combinations.

**Null hypothesis**: No cointegration

## Testing

```bash
# Run tests
pytest tests/ -v

# Run validation
python validate.py
```

## Citation

```bibtex
@article{hatemi2008tests,
  title={Tests for cointegration with two unknown regime shifts},
  author={Hatemi-J, Abdulnasser},
  journal={Empirical Economics},
  volume={35},
  pages={497--505},
  year={2008}
}

@software{roudane2024cointhatemij,
  author = {Roudane, Merwan},
  title = {cointhatemij: Python implementation of Hatemi-J test},
  year = {2024},
  url = {https://github.com/merwanroudane/cointhatemij}
}
```

## License

MIT License - see LICENSE file for details.

## Author

**Dr. Merwan Roudane**
- Email: merwanroudane920@gmail.com
- GitHub: [@merwanroudane](https://github.com/merwanroudane)

## Support

- Issues: https://github.com/merwanroudane/cointhatemij/issues
- Documentation: https://github.com/merwanroudane/cointhatemij#readme
