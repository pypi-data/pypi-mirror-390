"""
Hatemi-J Cointegration Test with Two Unknown Regime Shifts

This package implements the cointegration test developed by Hatemi-J (2008)
that allows for two structural breaks with unknown timing.

Author: Dr. Merwan Roudane
Email: merwanroudane920@gmail.com
GitHub: https://github.com/merwanroudane/cointhatemij

Reference:
    Hatemi-J, A. (2008). Tests for cointegration with two unknown regime shifts
    with an application to financial market integration.
    Empirical Economics, 35, 497-505.
    DOI: 10.1007/s00181-007-0175-9
"""

from .hatemi_j_test import HatemiJTest, coint_hatemi_j

__version__ = "0.1.4"
__author__ = "Dr. Merwan Roudane"
__email__ = "merwanroudane920@gmail.com"

__all__ = ['HatemiJTest', 'coint_hatemi_j']
