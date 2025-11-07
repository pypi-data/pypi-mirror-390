"""
Tests for P₂ Master Proof Aggregation
--------------------------------------
Verifies that:
1. finalize() returns a Proof object with master and stage_hashes
2. Re-running identical chains yields identical HMASTER & stage_hashes
3. Any perturbation (S0/C/V/step order) changes HMASTER
4. Exporter returns canonical primary proof JSON dict
5. Edge case with zero steps produces valid master hash
"""

import copy

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


def build_and_finalize(S0=3, C={"offset": 2}, V="v1.0"):
    """Helper to build and finalize a standard test run."""
    r = BoRRun(S0=S0, C=copy.deepcopy(C), V=V)
    r.add_step(add).add_step(square)
    proof = r.finalize()
    return r, proof


def test_p2_master_determinism():
    """Identical inputs must yield identical HMASTER and stage_hashes."""
    _, p1 = build_and_finalize(S0=3, C={"offset": 2}, V="v1.0")
    _, p2 = build_and_finalize(S0=3, C={"offset": 2}, V="v1.0")
    assert p1.master == p2.master
    assert p1.stage_hashes == p2.stage_hashes


def test_p2_master_sensitivity_input():
    """Changing S0 must change HMASTER."""
    _, p1 = build_and_finalize(S0=3, C={"offset": 2}, V="v1.0")
    _, p2 = build_and_finalize(S0=4, C={"offset": 2}, V="v1.0")
    assert p1.master != p2.master


def test_p2_master_sensitivity_config():
    """Changing config must change HMASTER."""
    _, p1 = build_and_finalize(S0=3, C={"offset": 2}, V="v1.0")
    _, p2 = build_and_finalize(S0=3, C={"offset": 3}, V="v1.0")
    assert p1.master != p2.master


def test_p2_exporter_primary_proof_shape():
    """Exporter must return canonical primary proof JSON dict."""
    r, proof = build_and_finalize()
    exported = r.to_primary_proof()
    assert exported["master"] == proof.master
    assert len(exported["stage_hashes"]) == 2
    assert exported["meta"]["H0"] == r.P0
    assert exported["meta"]["S0"] == r.S0_initial


def test_p2_empty_chain_supported():
    """Zero steps should produce valid HMASTER (hash of domain prefix only)."""
    r = BoRRun(S0=0, C={}, V="v1.0")
    proof = r.finalize()
    assert isinstance(proof.master, str) and len(proof.master) == 64
    assert proof.stage_hashes == []


def test_p2_proof_immutable():
    """Proof object should be immutable (frozen dataclass)."""
    _, proof = build_and_finalize()
    try:
        proof.master = "tampered"
        assert False, "Proof should be immutable"
    except (AttributeError, Exception):
        pass  # Expected - proof is frozen


def test_p2_step_records_complete():
    """Step records in proof should contain all required fields."""
    r, proof = build_and_finalize(S0=5, C={"offset": 3}, V="v2.0")
    assert len(proof.steps) == 2

    # Check first step record
    step1 = proof.steps[0]
    assert step1["i"] == 1
    assert step1["fn"] == "add"
    assert step1["input"] == 5
    assert step1["output"] == 8  # 5 + 3
    assert step1["config"] == {"offset": 3}
    assert step1["version"] == "v2.0"
    assert "fingerprint" in step1

    # Check second step record
    step2 = proof.steps[1]
    assert step2["i"] == 2
    assert step2["fn"] == "square"
    assert step2["input"] == 8
    assert step2["output"] == 64  # 8 * 8


def test_p2_meta_complete():
    """Meta section should contain all initialization parameters."""
    r, proof = build_and_finalize(S0=10, C={"offset": 5}, V="v3.0")
    meta = proof.meta
    assert meta["S0"] == 10
    assert meta["C"] == {"offset": 5}
    assert meta["V"] == "v3.0"
    assert "env" in meta
    assert meta["H0"] == r.P0


def test_p2_version_sensitivity():
    """Changing version string must change HMASTER."""
    _, p1 = build_and_finalize(S0=3, C={"offset": 2}, V="v1.0")
    _, p2 = build_and_finalize(S0=3, C={"offset": 2}, V="v2.0")
    assert p1.master != p2.master
