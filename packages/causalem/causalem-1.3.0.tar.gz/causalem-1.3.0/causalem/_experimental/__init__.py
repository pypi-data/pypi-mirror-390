"""
Experimental features for CausalEM.

This module contains experimental functionality that is under active development.
APIs in this module may change without notice and should be considered unstable.

Current experimental features:
- CATE (Conditional Average Treatment Effect) estimation
"""

from .cate import MatchingCATEEstimator

__all__ = ["MatchingCATEEstimator"]
