"""
pyfinancecalc
A lightweight, dependency-free finance calculations library.
"""

from .investment import sip_future_value, lump_sum_future_value, cagr, xirr
from .loan import emi, amortization_schedule, interest_principal_split
from .planning import goal_sip_needed, goal_lumpsum_needed
from .core import npv, irr, rate_from_annual, rate_to_annual, monthly_rate, validate_cashflows

__all__ = [
    "sip_future_value", "lump_sum_future_value", "cagr", "xirr",
    "emi", "amortization_schedule", "interest_principal_split",
    "goal_sip_needed", "goal_lumpsum_needed",
    "npv", "irr", "rate_from_annual", "rate_to_annual", "monthly_rate", "validate_cashflows"
]

__version__ = "0.1.0"
