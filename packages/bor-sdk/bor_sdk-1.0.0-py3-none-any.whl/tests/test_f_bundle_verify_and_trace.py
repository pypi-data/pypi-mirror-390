"""
Tests for Phase F: Bundle Verification & Trace Rendering
---------------------------------------------------------
Verifies that:
1. verify_bundle_dict() validates structure, sub-proofs, and H_RICH
2. Bundle tampering is detected
3. Optional primary replay check works
4. render_trace_from_primary() produces deterministic text output
5. CLI commands work correctly
"""

import json
from pathlib import Path

import pytest

from bor.bundle import build_bundle
from bor.decorators import step
from bor.verify import (
    BundleVerificationError,
    render_trace_from_primary,
    verify_bundle_dict,
)


@step
def add(x, C, V):
    """Add offset from config to state."""
    return x + C.get("offset", 0)


@step
def square(x, C, V):
    """Square the state."""
    return x * x


def _bundle(S0=3, C={"offset": 2}, V="v1.0"):
    """Helper to create a test bundle."""
    return build_bundle(S0, C, V, [add, square])


def test_verify_bundle_success():
    """verify_bundle_dict should pass for valid bundle."""
    b = _bundle()
    rep = verify_bundle_dict(b)
    assert rep["ok"] is True
    assert rep["checks"]["H_RICH_match"] is True
    assert rep["checks"]["subproof_hashes_match"] is True


def test_verify_bundle_with_optional_replay():
    """verify_bundle_dict should include primary replay check when stages provided."""
    b = _bundle()
    rep = verify_bundle_dict(b, stages=[add, square], S0=3, C={"offset": 2}, V="v1.0")
    assert rep["ok"] is True
    assert rep["checks"]["H_RICH_match"] is True
    assert rep["checks"]["subproof_hashes_match"] is True
    assert rep["checks"]["primary_master_replay_match"] is True


def test_verify_bundle_detects_tamper_subproof():
    """verify_bundle_dict should detect tampering with sub-proof data."""
    b = _bundle()
    b["subproofs"]["DIP"]["ok"] = False  # tamper
    try:
        verify_bundle_dict(b)
        assert False, "Expected bundle verification failure on tamper"
    except BundleVerificationError:
        assert True


def test_verify_bundle_detects_tamper_h_rich():
    """verify_bundle_dict should detect tampering with H_RICH."""
    b = _bundle()
    b["H_RICH"] = "0" * 64  # tamper
    try:
        verify_bundle_dict(b)
        assert False, "Expected bundle verification failure on H_RICH tamper"
    except BundleVerificationError:
        assert True


def test_verify_bundle_detects_missing_keys():
    """verify_bundle_dict should detect missing required keys."""
    b = _bundle()
    del b["H_RICH"]
    try:
        verify_bundle_dict(b)
        assert False, "Expected bundle verification failure on missing key"
    except BundleVerificationError as e:
        assert "missing" in str(e).lower()


def test_verify_bundle_detects_mismatched_subproof_hashes():
    """verify_bundle_dict should detect mismatched subproof hashes."""
    b = _bundle()
    # Tamper with a subproof but not update its hash
    b["subproofs"]["CCP"]["equal"] = False
    # Don't update subproof_hashes - this should fail
    try:
        verify_bundle_dict(b)
        assert False, "Expected bundle verification failure on hash mismatch"
    except BundleVerificationError:
        assert True


def test_trace_renderer_shape(tmp_path):
    """render_trace_from_primary should produce expected structure."""
    b = _bundle()
    txt = render_trace_from_primary(b["primary"])
    assert "BoR Primary Proof Trace" in txt
    assert "Aggregation:" in txt
    assert "HMASTER" in txt
    assert "S0:" in txt
    assert "Step" in txt
    # Write file for manual inspection if needed
    (tmp_path / "trace.txt").write_text(txt, encoding="utf-8")


def test_trace_renderer_includes_meta():
    """Trace should include meta information."""
    b = _bundle(S0=5, C={"offset": 3}, V="v2.0")
    txt = render_trace_from_primary(b["primary"])
    assert "S0: 5" in txt
    assert "offset" in txt
    assert "v2.0" in txt


def test_trace_renderer_includes_steps():
    """Trace should include step information."""
    b = _bundle()
    txt = render_trace_from_primary(b["primary"])
    assert "add" in txt
    assert "square" in txt
    # Should show step transformations
    assert "->" in txt


def test_trace_renderer_includes_hashes():
    """Trace should include step hashes."""
    b = _bundle()
    txt = render_trace_from_primary(b["primary"])
    # Should contain hash values (64 char hex strings)
    assert len([line for line in txt.split("\n") if len(line) > 64]) > 0


def test_trace_renderer_deterministic():
    """Trace should be deterministic for same input."""
    b1 = _bundle()
    b2 = _bundle()
    txt1 = render_trace_from_primary(b1["primary"])
    txt2 = render_trace_from_primary(b2["primary"])
    assert txt1 == txt2


def test_verify_bundle_file(tmp_path):
    """verify_bundle_file should load and verify bundle from file."""
    from bor.verify import verify_bundle_file

    b = _bundle()
    path = tmp_path / "bundle.json"
    path.write_text(json.dumps(b, sort_keys=True), encoding="utf-8")

    rep = verify_bundle_file(str(path))
    assert rep["ok"] is True


def test_verify_bundle_file_with_replay(tmp_path):
    """verify_bundle_file should support optional replay check."""
    from bor.verify import verify_bundle_file

    b = _bundle()
    path = tmp_path / "bundle.json"
    path.write_text(json.dumps(b, sort_keys=True), encoding="utf-8")

    rep = verify_bundle_file(
        str(path), stages=[add, square], S0=3, C={"offset": 2}, V="v1.0"
    )
    assert rep["ok"] is True
    assert rep["checks"]["primary_master_replay_match"] is True


def test_bundle_verification_report_structure():
    """Verification report should have expected structure."""
    b = _bundle()
    rep = verify_bundle_dict(b)
    assert "ok" in rep
    assert "checks" in rep
    assert isinstance(rep["checks"], dict)
    assert "H_RICH_match" in rep["checks"]
    assert "subproof_hashes_match" in rep["checks"]
