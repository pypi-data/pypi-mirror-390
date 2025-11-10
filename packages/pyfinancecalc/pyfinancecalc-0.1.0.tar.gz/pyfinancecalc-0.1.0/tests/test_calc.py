import math
from pyfinancecalc import (
    sip_future_value, lump_sum_future_value, cagr, xirr,
    emi, amortization_schedule, interest_principal_split,
    goal_sip_needed, goal_lumpsum_needed,
    npv, irr, monthly_rate
)

def test_sip_and_goal_inverse():
    fv = sip_future_value(1000, 0.12, 12)  # simple check
    m = goal_sip_needed(fv, 0.12, 12)
    assert abs(m - 1000) < 1e-4

def test_lumpsum_and_goal_inverse():
    fv = lump_sum_future_value(10000, 0.10, 5)
    req = goal_lumpsum_needed(fv, 0.10, 5)
    assert abs(req - 10000) < 1e-6

def test_emi_schedule_sizes():
    e = emi(100000, 0.12, 12)
    sched = amortization_schedule(100000, 0.12, 12)
    assert len(sched) == 12
    assert abs(sum([row["payment"] for row in sched]) - e*12) < 1e-4

def test_core_npvs():
    cf = [-1000, 400, 400, 400, 400]
    r = 0.1
    v = npv(r, cf)
    assert isinstance(v, float)

def test_irr_reasonable():
    cf = [-1000, 300, 300, 300, 300]
    r = irr(cf)
    assert -0.5 < r < 1.0

def test_xirr_basic():
    cf = [-1000, 300, 300, 300, 300]
    dates = [0, 90, 180, 270, 360]
    r = xirr(cf, dates)
    assert -0.5 < r < 1.0
