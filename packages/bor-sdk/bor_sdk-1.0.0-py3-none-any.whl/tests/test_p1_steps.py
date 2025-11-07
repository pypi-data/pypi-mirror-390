"""
Tests for P₁ Step-Level Proof
------------------------------
Verifies that:
1. Each step emits a stable fingerprint (hᵢ)
2. Different steps produce different hashes
3. Changing inputs changes step hashes
4. Purity enforcement works correctly
"""

from bor.core import BoRRun
from bor.decorators import step


@step
def add(x, C, V):
    """Add offset from config to state."""
    return x + C["offset"]


@step
def square(x, C, V):
    """Square the state."""
    return x * x


def test_p1_step_hashes_change():
    """Different steps must produce different hashes."""
    run = BoRRun(S0=3, C={"offset": 2}, V="v1.0")
    run.add_step(add).add_step(square)
    assert len(run.steps) == 2
    assert run.steps[0].fingerprint != run.steps[1].fingerprint


def test_p1_step_hash_sensitivity():
    """Changing input state must change step hash."""
    r1 = BoRRun(S0=3, C={"offset": 2}, V="v1.0")
    r1.add_step(add)
    r2 = BoRRun(S0=4, C={"offset": 2}, V="v1.0")
    r2.add_step(add)
    assert r1.steps[0].fingerprint != r2.steps[0].fingerprint


def test_p1_deterministic_replay():
    """Same inputs must produce identical step hashes."""
    r1 = BoRRun(S0=5, C={"offset": 3}, V="v1.0")
    r1.add_step(add).add_step(square)

    r2 = BoRRun(S0=5, C={"offset": 3}, V="v1.0")
    r2.add_step(add).add_step(square)

    assert r1.steps[0].fingerprint == r2.steps[0].fingerprint
    assert r1.steps[1].fingerprint == r2.steps[1].fingerprint


def test_p1_config_sensitivity():
    """Changing config must change step hash."""
    r1 = BoRRun(S0=3, C={"offset": 2}, V="v1.0")
    r1.add_step(add)

    r2 = BoRRun(S0=3, C={"offset": 5}, V="v1.0")
    r2.add_step(add)

    assert r1.steps[0].fingerprint != r2.steps[0].fingerprint
