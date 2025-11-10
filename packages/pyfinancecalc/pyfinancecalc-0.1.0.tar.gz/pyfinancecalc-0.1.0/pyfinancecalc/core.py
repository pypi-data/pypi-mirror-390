from typing import Iterable, List, Tuple

def rate_from_annual(annual_rate: float, periods_per_year: int) -> float:
    """Convert an annual nominal rate to per-period nominal rate."""
    if periods_per_year <= 0:
        raise ValueError("periods_per_year must be positive")
    return annual_rate / periods_per_year

def rate_to_annual(periodic_rate: float, periods_per_year: int) -> float:
    """Convert a per-period nominal rate to annual nominal rate."""
    if periods_per_year <= 0:
        raise ValueError("periods_per_year must be positive")
    return periodic_rate * periods_per_year

def monthly_rate(annual_rate: float) -> float:
    """Monthly nominal rate from annual nominal rate."""
    return rate_from_annual(annual_rate, 12)

def validate_cashflows(cashflows: Iterable[float]) -> List[float]:
    cf = list(cashflows)
    if len(cf) == 0:
        raise ValueError("cashflows cannot be empty")
    return cf

def npv(rate: float, cashflows: Iterable[float]) -> float:
    """
    Net Present Value.
    cashflows: list where index 0 is CF at t=0, index 1 at t=1, etc.
    """
    cf = validate_cashflows(cashflows)
    total = 0.0
    for t, c in enumerate(cf):
        total += c / ((1 + rate) ** t)
    return total

def irr(cashflows: Iterable[float], guess: float = 0.1, tol: float = 1e-7, max_iter: int = 1000) -> float:
    """
    Internal Rate of Return via Newton-Raphson.
    Returns the rate r such that NPV(r) ~= 0.
    """
    cf = validate_cashflows(cashflows)

    def f(r: float) -> float:
        return npv(r, cf)

    def fprime(r: float) -> float:
        # derivative of NPV wrt r
        s = 0.0
        for t, c in enumerate(cf[1:], start=1):
            s += -t * c / ((1 + r) ** (t + 1 - 1))  # simplify derivative
        # More directly: d/dr [c/(1+r)^t] = -t*c/(1+r)^(t+1)
        # We need the sum over t>=1 because t=0 term's derivative is 0
        s = 0.0
        for t, c in enumerate(cf[1:], start=1):
            s += -t * c / ((1 + r) ** (t + 1))
        return s

    r = guess
    for _ in range(max_iter):
        val = f(r)
        if abs(val) < tol:
            return r
        deriv = fprime(r)
        if deriv == 0:
            break
        r -= val / deriv

    # Fallback: bisection between -0.9999 and very high rate
    low, high = -0.9999, 10.0
    for _ in range(max_iter):
        mid = (low + high) / 2
        val = f(mid)
        if abs(val) < tol:
            return mid
        if val > 0:
            low = mid
        else:
            high = mid
    return mid
