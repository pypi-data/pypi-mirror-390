from .investment import sip_future_value, lump_sum_future_value
from .loan import emi

def goal_sip_needed(target: float, annual_rate: float, months: int) -> float:
    """
    Monthly SIP required to reach a target corpus in given months.
    Inverse of SIP FV formula.
    """
    if target <= 0 or months <= 0:
        raise ValueError("target and months must be positive")
    r = annual_rate / 12.0
    if r == 0:
        return target / months
    return target / ( ((1 + r) ** months - 1) / r * (1 + r) )

def goal_lumpsum_needed(target: float, annual_rate: float, years: float) -> float:
    """
    Lump sum required today to reach the target in given years.
    """
    if target <= 0 or years <= 0:
        raise ValueError("target and years must be positive")
    return target / ((1 + annual_rate) ** years)
