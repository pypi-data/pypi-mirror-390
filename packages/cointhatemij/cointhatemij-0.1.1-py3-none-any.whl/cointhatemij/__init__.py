"""
Hatemi-J Cointegration Test with Two Unknown Regime Shifts.

Reference:
  Hatemi-J (2008) Empirical Economics, 35, 497–505.
"""

from .hatemi_j_test import HatemiJTest, coint_hatemi_j

__all__ = ["HatemiJTest", "coint_hatemi_j"]
__version__ = "0.1.1"
__author__ = "Dr. Merwan Roudane"
__email__ = "merwanroudane920@gmail.com"
