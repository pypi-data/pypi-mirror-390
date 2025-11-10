from typing import Iterable, List
from .core import npv, irr, monthly_rate, validate_cashflows

def sip_future_value(monthly_investment: float, annual_rate: float, months: int) -> float:
    """
    Future value of a monthly SIP (end of period).
    """
    if months < 0:
        raise ValueError("months must be non-negative")
    r = monthly_rate(annual_rate)
    if r == 0:
        return monthly_investment * months
    return monthly_investment * (((1 + r) ** months - 1) / r) * (1 + r)

def lump_sum_future_value(principal: float, annual_rate: float, years: float) -> float:
    """
    Future value of a lump sum compounded annually.
    """
    if years < 0:
        raise ValueError("years must be non-negative")
    return principal * ((1 + annual_rate) ** years)

def cagr(begin_value: float, end_value: float, years: float) -> float:
    """
    Compound Annual Growth Rate.
    """
    if begin_value <= 0 or years <= 0:
        raise ValueError("begin_value and years must be positive")
    return (end_value / begin_value) ** (1 / years) - 1

def xirr(cashflows: Iterable[float], dates: Iterable[int], guess: float = 0.1) -> float:
    """
    Approximate XIRR using day-count as integer offsets (days from t0).
    No external dependencies. dates are integers (days from start).
    """
    cf = list(cashflows)
    ds = list(dates)
    if len(cf) != len(ds) or len(cf) == 0:
        raise ValueError("cashflows and dates must be same non-zero length")
    t0 = ds[0]

    def npv_cont(rate: float) -> float:
        total = 0.0
        for c, d in zip(cf, ds):
            years = (d - t0) / 365.0
            total += c / ((1 + rate) ** years)
        return total

    # Newton with bisection fallback
    r = guess
    for _ in range(200):
        # numerical derivative
        f0 = npv_cont(r)
        if abs(f0) < 1e-7:
            return r
        h = 1e-5
        f1 = npv_cont(r + h)
        deriv = (f1 - f0) / h
        if deriv == 0:
            break
        r -= f0 / deriv
        if r <= -0.9999:
            r = -0.9999

    low, high = -0.9999, 10.0
    for _ in range(200):
        mid = (low + high) / 2
        val = npv_cont(mid)
        if abs(val) < 1e-7:
            return mid
        if val > 0:
            low = mid
        else:
            high = mid
    return mid
