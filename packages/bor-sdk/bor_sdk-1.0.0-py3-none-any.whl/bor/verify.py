"""
Module: verify
--------------
P₃ Verification Surface: Deterministic replay and HMASTER comparison.
P₄ Persistence checks: JSON vs SQLite equivalence.
Phase F: Rich Proof Bundle verification and trace rendering.
"""

import hashlib
import importlib
import json
from typing import Any, Callable, Dict, Iterable, List, Optional

from bor.core import BoRRun
from bor.store import load_json_proof, load_sqlite_proof


class HashMismatchError(Exception):
    """Raised when stored and recomputed HMASTER do not match."""

    pass


class BundleVerificationError(Exception):
    """Raised when Rich Proof Bundle verification fails."""

    pass


def _import_stage(path: str) -> Callable:
    """
    Import a function from 'module.submodule:function' OR 'module.submodule.function'.
    """
    if ":" in path:
        module_path, fn_name = path.split(":")
    else:
        module_path, fn_name = path.rsplit(".", 1)
    mod = importlib.import_module(module_path)
    fn = getattr(mod, fn_name)
    return fn


def replay_master(
    S0: Any, C: Dict[str, Any], V: str, stage_fns: Iterable[Callable]
) -> str:
    """
    Build a BoRRun, execute steps, and return recomputed HMASTER.
    """
    r = BoRRun(S0=S0, C=C, V=V)
    for fn in stage_fns:
        r.add_step(fn)
    proof = r.finalize()
    return proof.master


def verify_primary_proof_dict(
    proof_obj: Dict[str, Any],
    S0: Any,
    C: Dict[str, Any],
    V: str,
    stages: Iterable[Callable],
) -> Dict[str, Any]:
    """
    P₃ Verification: recompute HMASTER from supplied code and inputs,
    then compare against stored proof.master.
    Returns a structured report.
    Raises HashMismatchError on mismatch.
    """
    stored_master = proof_obj["master"]
    recomputed_master = replay_master(S0, C, V, stages)
    ok = stored_master == recomputed_master
    report = {
        "verified": ok,
        "stored_master": stored_master,
        "recomputed_master": recomputed_master,
    }
    if not ok:
        raise HashMismatchError(json.dumps(report, sort_keys=True))
    return report


def verify_primary_file(
    proof_path: str, S0: Any, C: Dict[str, Any], V: str, stage_paths: List[str]
) -> Dict[str, Any]:
    """
    Convenience wrapper: load proof JSON from disk and import stages by path.
    """
    with open(proof_path, "r", encoding="utf-8") as f:
        proof_obj = json.load(f)
    stages = [_import_stage(p) for p in stage_paths]
    return verify_primary_proof_dict(proof_obj, S0, C, V, stages)


# === P₄ Persistence Verification ===


def persistence_equivalence(
    json_path: str, label: str, root: str = ".bor_store"
) -> Dict[str, Any]:
    """
    Load proof from JSON file and from SQLite (latest by label) and assert same HMASTER.
    Returns a report dict: {equal: bool, master_json: str, master_sqlite: str}
    """
    pj = load_json_proof(json_path)
    ps = load_sqlite_proof(label, root=root)
    if ps is None:
        return {"equal": False, "reason": "sqlite_missing"}
    equal = pj["master"] == ps["master"]
    return {"equal": equal, "master_json": pj["master"], "master_sqlite": ps["master"]}


# === Phase F: Bundle Verification ===


def _sha256_minified(obj: Dict[str, Any]) -> str:
    """Compute SHA-256 of minified JSON."""
    return hashlib.sha256(
        json.dumps(obj, separators=(",", ":"), sort_keys=True).encode("utf-8")
    ).hexdigest()


def verify_bundle_dict(
    bundle: Dict[str, Any],
    stages: Optional[Iterable[Callable]] = None,
    S0: Any = None,
    C: Dict[str, Any] = None,
    V: str = None,
) -> Dict[str, Any]:
    """
    Verify a Rich Proof Bundle:
      1) Check structure of 'primary', 'subproofs', 'subproof_hashes', 'H_RICH'
      2) Recompute each sub-proof hash and compare with 'subproof_hashes'
      3) Recompute H_RICH over sorted sub-proof digests and compare with bundle.H_RICH
      4) Optionally, if stages & (S0,C,V) provided, replay primary and compare 'primary.master'
    Returns a report dict; raises BundleVerificationError on failure.
    """
    report = {"ok": True, "checks": {}}

    # Basic keys
    for k in ("primary", "subproofs", "subproof_hashes", "H_RICH"):
        if k not in bundle:
            report["ok"] = False
            report["checks"][k] = "missing"
    if not report["ok"]:
        raise BundleVerificationError(json.dumps(report, sort_keys=True))

    primary = bundle["primary"]
    subproofs = bundle["subproofs"]
    sub_hashes = bundle["subproof_hashes"]
    H_RICH = bundle["H_RICH"]

    # 2) Recompute each sub-proof digest
    recomputed_hashes = {k: _sha256_minified(v) for k, v in subproofs.items()}
    report["checks"]["subproof_hashes_match"] = recomputed_hashes == sub_hashes

    # 3) Recompute H_RICH deterministically (sorted keys)
    h_concat = "|".join(
        [recomputed_hashes[k] for k in sorted(recomputed_hashes.keys())]
    )
    H_RICH_re = hashlib.sha256(h_concat.encode("utf-8")).hexdigest()
    report["checks"]["H_RICH_match"] = H_RICH == H_RICH_re

    # 4) Optional primary replay check (if user supplies stages + S0,C,V)
    primary_ok = None
    if stages is not None and S0 is not None and C is not None and V is not None:
        # Re-run to recompute HMASTER and match primary.master
        try:
            master_re = replay_master(S0, C, V, stages)
            primary_ok = primary.get("master") == master_re
        except Exception as e:
            primary_ok = False
        report["checks"]["primary_master_replay_match"] = bool(primary_ok)

    # Overall
    ok = report["checks"]["subproof_hashes_match"] and report["checks"]["H_RICH_match"]
    if primary_ok is not None:
        ok = ok and primary_ok
    report["ok"] = bool(ok)

    if not report["ok"]:
        raise BundleVerificationError(json.dumps(report, sort_keys=True))
    return report


def verify_bundle_file(
    path: str,
    stages: Optional[Iterable[Callable]] = None,
    S0: Any = None,
    C: Dict[str, Any] = None,
    V: str = None,
) -> Dict[str, Any]:
    """Load bundle from file and verify it."""
    with open(path, "r", encoding="utf-8") as f:
        bundle = json.load(f)
    return verify_bundle_dict(bundle, stages=stages, S0=S0, C=C, V=V)


# === Phase F: Trace Renderer ===


def render_trace_from_primary(primary: Dict[str, Any]) -> str:
    """
    Produce a deterministic, plain-text trace:
      - Header with meta
      - Table: idx | fn | input | output | hᵢ
      - Aggregation line: h1||...||hn -> HMASTER
    """
    lines = []
    meta = primary.get("meta", {})
    lines.append("=== BoR Primary Proof Trace ===")
    lines.append(f"S0: {meta.get('S0')}")
    lines.append(f"C: {meta.get('C')}")
    lines.append(f"V: {meta.get('V')}")
    lines.append(f"H0: {meta.get('H0')}")
    lines.append("")
    lines.append("Step | Function | Input -> Output | h_i")
    lines.append(
        "-----+----------+-----------------+----------------------------------------------------------------"
    )
    steps = primary.get("steps", [])
    stage_hashes = primary.get("stage_hashes", [])
    for i, s in enumerate(steps, start=1):
        lines.append(
            f"{i:>4} | {s['fn']:8} | {s['input']} -> {s['output']:6} | {s['fingerprint']}"
        )
    lines.append("")
    if stage_hashes:
        concat_preview = "||".join([h[:8] for h in stage_hashes])
        lines.append(f"Aggregation: {concat_preview}... -> HMASTER")
    else:
        lines.append("Aggregation: (no steps)")
    lines.append(f"HMASTER = {primary.get('master')}")
    return "\n".join(lines)
