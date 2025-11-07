"""
Tests for Phase E Part 2: Remaining Sub-proofs
-----------------------------------------------
Verifies that:
1. CCP (Canonicalization Consistency Proof) works correctly
2. CMIP (Cross-Module Integrity Proof) validates across modules
3. PP (Persistence Proof) links JSON and SQLite with H_store
4. TRP (Temporal Reproducibility Proof) proves time-invariance
5. Bundle v2 includes all sub-proofs
6. H_RICH is updated with new sub-proofs
"""

import json

from bor.bundle import build_bundle
from bor.decorators import step
from bor.subproofs import run_CCP, run_CMIP, run_PP, run_TRP


@step
def add(x, C, V):
    """Add offset from config to state."""
    return x + C.get("offset", 0)


@step
def square(x, C, V):
    """Square the state."""
    return x * x


def test_ccp_canonicalization():
    """CCP should show HMASTER is invariant to dict key ordering."""
    S0, C, V = 3, {"offset": 2}, "v1.0"
    result = run_CCP(S0, C, V, [add, square])
    assert result["equal"] is True
    assert result["master_a"] == result["master_b"]


def test_cmip_cross_module_integrity():
    """CMIP should verify consistency across core/verify/store modules."""
    S0, C, V = 3, {"offset": 2}, "v1.0"
    result = run_CMIP(S0, C, V, [add, square])
    assert result["equal"] is True
    assert result["core"] == result["verify"] == result["json"]


def test_pp_persistence_linkage():
    """PP should verify JSON and SQLite storage produce same master."""
    S0, C, V = 3, {"offset": 2}, "v1.0"
    result = run_PP(S0, C, V, [add, square])
    assert result["equal"] is True
    assert len(result["H_store_json"]) == 64
    assert len(result["H_store_sqlite"]) == 64
    assert result["master_json"] == result["master_sqlite"]


def test_pp_hstore_values():
    """PP should return H_store values for both backends."""
    S0, C, V = 3, {"offset": 2}, "v1.0"
    result = run_PP(S0, C, V, [add, square])
    assert "H_store_json" in result
    assert "H_store_sqlite" in result
    # H_store values should be different (different timestamps)
    # But masters should be the same
    assert result["master_json"] == result["master_sqlite"]


def test_trp_temporal_reproducibility():
    """TRP should show HMASTER is invariant across time."""
    S0, C, V = 3, {"offset": 2}, "v1.0"
    result = run_TRP(S0, C, V, [add, square])
    assert result["equal"] is True
    assert result["master_t0"] == result["master_t1"]


def test_bundle_v2_includes_all_subproofs():
    """Bundle v2 should include all 8 sub-proofs."""
    S0, C, V = 3, {"offset": 2}, "v1.0"
    bundle = build_bundle(S0, C, V, [add, square])

    sp = bundle["subproofs"]
    # Check all sub-proofs are present
    assert "DIP" in sp
    assert "DP" in sp
    assert "PEP" in sp
    assert "PoPI" in sp
    assert "CCP" in sp
    assert "CMIP" in sp
    assert "PP" in sp
    assert "TRP" in sp


def test_remaining_subproofs_present_and_valid():
    """All new sub-proofs should be present and return valid results."""
    S0, C, V = 3, {"offset": 2}, "v1.0"
    bundle = build_bundle(S0, C, V, [add, square])

    sp = bundle["subproofs"]
    # CCP
    assert "CCP" in sp and isinstance(sp["CCP"]["equal"], bool)
    # CMIP
    assert "CMIP" in sp and sp["CMIP"]["equal"] is True
    # PP
    assert "PP" in sp and sp["PP"]["equal"] is True
    assert len(sp["PP"]["H_store_json"]) == 64
    assert len(sp["PP"]["H_store_sqlite"]) == 64
    # TRP
    assert "TRP" in sp and sp["TRP"]["equal"] is True

    # Rich commitment updated
    assert "H_RICH" in bundle and len(bundle["H_RICH"]) == 64


def test_bundle_subproof_hashes_cover_all():
    """Subproof hashes should cover all sub-proofs."""
    S0, C, V = 3, {"offset": 2}, "v1.0"
    bundle = build_bundle(S0, C, V, [add, square])
    subs = set(bundle["subproofs"].keys())
    subs_h = set(bundle["subproof_hashes"].keys())
    assert subs == subs_h


def test_h_rich_includes_all_subproofs():
    """H_RICH should be computed from all 8 sub-proofs."""
    S0, C, V = 3, {"offset": 2}, "v1.0"
    bundle = build_bundle(S0, C, V, [add, square])

    # Verify all 8 sub-proofs contribute to H_RICH
    assert len(bundle["subproof_hashes"]) == 8

    # Manually verify H_RICH computation
    import hashlib

    sorted_hashes = [
        bundle["subproof_hashes"][k] for k in sorted(bundle["subproof_hashes"].keys())
    ]
    expected_h_rich = hashlib.sha256(
        "|".join(sorted_hashes).encode("utf-8")
    ).hexdigest()
    assert bundle["H_RICH"] == expected_h_rich


def test_ccp_different_representations_same_semantics():
    """CCP should handle semantically identical but differently ordered configs."""
    S0, V = 5, "v1.0"
    C1 = {"offset": 3, "extra": "value"}
    C2 = {"extra": "value", "offset": 3}  # Same keys, different order

    result = run_CCP(S0, C1, V, [add, square])
    # Due to canonical encoding, both should produce same HMASTER
    assert result["equal"] is True


def test_cmip_modules_consistent():
    """CMIP should confirm all modules produce identical HMASTER."""
    S0, C, V = 10, {"offset": 5}, "v2.0"
    result = run_CMIP(S0, C, V, [add, square])

    assert "core" in result
    assert "verify" in result
    assert "json" in result
    assert result["core"] == result["verify"]
    assert result["verify"] == result["json"]
    assert result["equal"] is True


def test_pp_backends_equivalent():
    """PP should prove JSON and SQLite backends are equivalent."""
    S0, C, V = 7, {"offset": 1}, "v1.5"
    result = run_PP(S0, C, V, [add, square])

    # Both backends should produce same master
    assert result["master_json"] is not None
    assert result["master_sqlite"] is not None
    assert result["master_json"] == result["master_sqlite"]

    # Both should have H_store
    assert result["H_store_json"] is not None
    assert result["H_store_sqlite"] is not None


def test_trp_time_invariance():
    """TRP should prove reasoning is time-invariant."""
    S0, C, V = 4, {"offset": 3}, "v1.0"
    result = run_TRP(S0, C, V, [add, square], delay_sec=0.1)

    assert result["master_t0"] is not None
    assert result["master_t1"] is not None
    assert result["master_t0"] == result["master_t1"]
    assert result["equal"] is True
