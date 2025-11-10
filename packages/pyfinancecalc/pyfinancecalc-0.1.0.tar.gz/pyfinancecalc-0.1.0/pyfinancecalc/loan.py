from typing import List, Dict, Tuple

def emi(principal: float, annual_rate: float, months: int) -> float:
    """
    Equated Monthly Installment.
    """
    if months <= 0:
        raise ValueError("months must be positive")
    r = annual_rate / 12.0
    if r == 0:
        return principal / months
    return principal * r * (1 + r) ** months / ((1 + r) ** months - 1)

def interest_principal_split(principal: float, annual_rate: float, months: int) -> List[Tuple[float, float]]:
    """
    Returns list of (interest, principal_component) for each month.
    """
    r = annual_rate / 12.0
    e = emi(principal, annual_rate, months)
    out = []
    bal = principal
    for _ in range(months):
        interest = bal * r
        principal_comp = e - interest
        bal -= principal_comp
        out.append((round(interest, 10), round(principal_comp, 10)))
    return out

def amortization_schedule(principal: float, annual_rate: float, months: int) -> List[dict]:
    """
    Detailed amortization schedule per month.
    """
    r = annual_rate / 12.0
    e = emi(principal, annual_rate, months)
    schedule = []
    bal = principal
    for i in range(1, months + 1):
        interest = bal * r
        principal_comp = e - interest
        bal = max(0.0, bal - principal_comp)
        schedule.append({
            "month": i,
            "payment": e,
            "interest": interest,
            "principal": principal_comp,
            "balance": bal
        })
    return schedule
