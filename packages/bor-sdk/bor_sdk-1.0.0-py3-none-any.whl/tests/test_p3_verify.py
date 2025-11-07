"""
Tests for P₃ Verification Surface
----------------------------------
Verifies that:
1. verify_primary_proof_dict() returns verified=True for matching runs
2. It raises HashMismatchError when any of (S0/C/V/steps) differ
3. replay_master() produces identical HMASTER as finalize()
4. Verification API works with both dict and file inputs
"""

import json
from pathlib import Path

from bor.core import BoRRun
from bor.decorators import step
from bor.verify import HashMismatchError, replay_master, verify_primary_proof_dict


@step
def add(x, C, V):
    """Add offset from config to state."""
    return x + C["offset"]


@step
def square(x, C, V):
    """Square the state."""
    return x * x


def _build_primary_json(tmp_path: Path, S0=3, C={"offset": 2}, V="v1.0"):
    """Helper to build a primary proof and save to file."""
    r = BoRRun(S0=S0, C=C, V=V)
    r.add_step(add).add_step(square)
    proof = r.finalize()
    primary = r.to_primary_proof()
    p = tmp_path / "primary.json"
    p.write_text(
        json.dumps(primary, separators=(",", ":"), sort_keys=True), encoding="utf-8"
    )
    return primary, p


def test_p3_verify_success(tmp_path):
    """Verification should succeed when inputs match."""
    primary, _ = _build_primary_json(tmp_path)
    report = verify_primary_proof_dict(
        primary, S0=3, C={"offset": 2}, V="v1.0", stages=[add, square]
    )
    assert report["verified"] is True
    assert report["stored_master"] == report["recomputed_master"]


def test_p3_verify_mismatch(tmp_path):
    """Verification should fail when S0 differs."""
    primary, _ = _build_primary_json(tmp_path)
    try:
        verify_primary_proof_dict(
            primary, S0=4, C={"offset": 2}, V="v1.0", stages=[add, square]
        )
        assert False, "Expected mismatch"
    except HashMismatchError as e:
        assert '"verified": false' in str(e) or '"verified":false' in str(e)


def test_p3_replay_master_matches_finalize(tmp_path):
    """replay_master should produce same HMASTER as finalize()."""
    primary, _ = _build_primary_json(tmp_path)
    rm = replay_master(S0=3, C={"offset": 2}, V="v1.0", stage_fns=[add, square])
    assert rm == primary["master"]


def test_p3_verify_config_sensitivity(tmp_path):
    """Verification should fail when config differs."""
    primary, _ = _build_primary_json(tmp_path, S0=5, C={"offset": 3}, V="v1.0")
    try:
        verify_primary_proof_dict(
            primary, S0=5, C={"offset": 999}, V="v1.0", stages=[add, square]
        )
        assert False, "Expected mismatch"
    except HashMismatchError as e:
        assert '"verified": false' in str(e) or '"verified":false' in str(e)


def test_p3_verify_version_sensitivity(tmp_path):
    """Verification should fail when version differs."""
    primary, _ = _build_primary_json(tmp_path, S0=5, C={"offset": 2}, V="v1.0")
    try:
        verify_primary_proof_dict(
            primary, S0=5, C={"offset": 2}, V="v2.0", stages=[add, square]
        )
        assert False, "Expected mismatch"
    except HashMismatchError as e:
        assert '"verified": false' in str(e) or '"verified":false' in str(e)


def test_p3_verify_step_order_matters(tmp_path):
    """Verification should fail when step order differs."""
    primary, _ = _build_primary_json(tmp_path)
    try:
        # Reverse the order of steps
        verify_primary_proof_dict(
            primary, S0=3, C={"offset": 2}, V="v1.0", stages=[square, add]
        )
        assert False, "Expected mismatch"
    except HashMismatchError as e:
        assert '"verified": false' in str(e) or '"verified":false' in str(e)


def test_p3_verify_deterministic_replay(tmp_path):
    """Multiple replays should produce identical results."""
    primary, _ = _build_primary_json(tmp_path, S0=10, C={"offset": 5}, V="v2.0")

    rm1 = replay_master(S0=10, C={"offset": 5}, V="v2.0", stage_fns=[add, square])
    rm2 = replay_master(S0=10, C={"offset": 5}, V="v2.0", stage_fns=[add, square])
    rm3 = replay_master(S0=10, C={"offset": 5}, V="v2.0", stage_fns=[add, square])

    assert rm1 == rm2 == rm3 == primary["master"]
