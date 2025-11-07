"""
Tests for P₀ Initialization Proof
----------------------------------
Verifies that:
1. Identical inputs produce identical P₀ hashes (determinism)
2. Different inputs produce different P₀ hashes (sensitivity)
"""

from bor.core import BoRRun


def test_p0_determinism():
    """Identical inputs must yield identical P₀"""
    r1 = BoRRun(S0=3, C={"offset": 2}, V="v1.0")
    r2 = BoRRun(S0=3, C={"offset": 2}, V="v1.0")
    assert r1.P0 == r2.P0, "Identical inputs must yield identical P₀"


def test_p0_variation():
    """Different inputs must yield different P₀"""
    r1 = BoRRun(S0=3, C={"offset": 2}, V="v1.0")
    r2 = BoRRun(S0=4, C={"offset": 2}, V="v1.0")
    assert r1.P0 != r2.P0, "Different inputs must yield different P₀"
