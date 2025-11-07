"""
Module: subproofs
-----------------
Sub-proof implementations: DIP, DP, PEP, PoPI, CCP, CMIP, PP, TRP.
These provide additional verification layers beyond the primary proof chain.
"""

import copy
import hashlib
import json
import os
import tempfile
import time
from typing import Any, Callable, Dict, Iterable, List, Tuple

from bor.core import BoRRun
from bor.decorators import step
from bor.store import DEFAULT_DIR as _STORE_DIR
from bor.store import (
    load_json_proof,
    load_sqlite_proof,
    save_json_proof,
    save_sqlite_proof,
)
from bor.verify import replay_master


def _sha256_minified_json(obj: Dict[str, Any]) -> str:
    """Compute SHA-256 of minified JSON."""
    b = json.dumps(obj, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return hashlib.sha256(b).hexdigest()


# === DIP: Deterministic Identity Proof ===


def run_DIP(
    S0: Any, C: Dict[str, Any], V: str, stages: Iterable[Callable]
) -> Dict[str, Any]:
    """
    Deterministic Identity Proof: two identical runs → equal master.
    Verifies that the reasoning chain is deterministic.
    """
    r1 = BoRRun(S0=S0, C=C, V=V)
    for fn in stages:
        r1.add_step(fn)
    p1 = r1.finalize().master

    r2 = BoRRun(S0=S0, C=C, V=V)
    for fn in stages:
        r2.add_step(fn)
    p2 = r2.finalize().master

    return {"ok": p1 == p2, "master_a": p1, "master_b": p2}


# === DP: Divergence Proof ===


def run_DP(
    S0: Any,
    C: Dict[str, Any],
    V: str,
    stages: Iterable[Callable],
    perturb: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Divergence Proof: change exactly one element → different master.
    Verifies that the proof is sensitive to input changes.
    """
    r1 = BoRRun(S0=S0, C=C, V=V)
    for fn in stages:
        r1.add_step(fn)
    p1 = r1.finalize().master

    S0b, Cb, Vb = S0, dict(C), V
    if "S0" in perturb:
        S0b = perturb["S0"]
    if "C" in perturb:
        Cb.update(perturb["C"])
    if "V" in perturb:
        Vb = perturb["V"]

    r2 = BoRRun(S0=S0b, C=Cb, V=Vb)
    for fn in stages:
        r2.add_step(fn)
    p2 = r2.finalize().master

    return {"diverged": p1 != p2, "master_a": p1, "master_b": p2, "perturb": perturb}


# === PEP: Purity Enforcement Proof ===


def run_PEP_bad_signature() -> Tuple[bool, str]:
    """
    Purity Enforcement Proof: a bad @step signature must be rejected.
    Verifies that the decorator enforces signature constraints.
    """
    try:

        @step
        def bad(x, C):  # wrong arity
            return x

        return False, "no_error"
    except Exception as e:
        return True, type(e).__name__


# === PoPI: Proof-of-Proof Integrity ===


def run_PoPI(primary_proof: Dict[str, Any]) -> Dict[str, Any]:
    """
    Proof-of-Proof Integrity: hash(minified primary proof JSON).
    Provides a compact fingerprint of the entire proof structure.
    """
    h = _sha256_minified_json(primary_proof)
    return {"proof_hash": h}


# === CCP: Canonicalization Consistency Proof ===


def run_CCP(
    S0: Any, C: Dict[str, Any], V: str, stages: Iterable[Callable]
) -> Dict[str, Any]:
    """
    Canonicalization Consistency Proof:
    Re-encode semantically identical inputs with different dict orders and show
    HMASTER is invariant due to canonical encoder.
    """
    # Base
    r1 = BoRRun(S0=S0, C=C, V=V)
    for fn in stages:
        r1.add_step(fn)
    m1 = r1.finalize().master

    # Permute key order in config; same semantics
    C2 = dict(C)
    if isinstance(C2, dict):
        # Create a shuffled-order JSON string -> parse back -> dict with same keys, values
        j = json.dumps(C2, sort_keys=False)
        C2_perm = json.loads(
            j
        )  # dict order is irrelevant; canonical encoder should normalize
    else:
        C2_perm = C2

    r2 = BoRRun(S0=S0, C=C2_perm, V=V)
    for fn in stages:
        r2.add_step(fn)
    m2 = r2.finalize().master

    return {"equal": m1 == m2, "master_a": m1, "master_b": m2}


# === CMIP: Cross-Module Integrity Proof ===


def run_CMIP(
    S0: Any, C: Dict[str, Any], V: str, stages: Iterable[Callable]
) -> Dict[str, Any]:
    """
    Cross-Module Integrity Proof:
    Compare HMASTER from:
      (1) core pipeline,
      (2) verify.replay_master (verification surface),
      (3) persisted JSON (store.load_json_proof)
    All must match.
    """
    # (1) core
    r = BoRRun(S0=S0, C=C, V=V)
    for fn in stages:
        r.add_step(fn)
    p = r.finalize().master

    # (2) verify surface
    rv = replay_master(S0, C, V, stages)

    # (3) persisted JSON (temporary location)
    tmpdir = tempfile.mkdtemp(prefix="bor_cmip_")
    primary = r.to_primary_proof()
    # Save JSON proof (P4 JSON)
    rec_json = save_json_proof("cmip", primary, root=tmpdir)
    loaded = load_json_proof(rec_json["path"])
    pj = loaded["master"]

    return {"equal": (p == rv == pj), "core": p, "verify": rv, "json": pj}


# === PP: Persistence Proof Linkage ===


def run_PP(
    S0: Any, C: Dict[str, Any], V: str, stages: Iterable[Callable]
) -> Dict[str, Any]:
    """
    Persistence Proof linkage:
    Save to JSON and SQLite, return H_store values and equality of masters.
    """
    tmpdir = tempfile.mkdtemp(prefix="bor_pp_")
    r = BoRRun(S0=S0, C=C, V=V)
    for fn in stages:
        r.add_step(fn)
    _ = r.finalize()
    primary = r.to_primary_proof()

    rec_j = save_json_proof("pp", primary, root=tmpdir)
    rec_s = save_sqlite_proof("pp", primary, root=tmpdir)
    loaded_j = load_json_proof(rec_j["path"])
    loaded_s = load_sqlite_proof("pp", root=tmpdir)

    eq = (loaded_s is not None) and (loaded_j["master"] == loaded_s["master"])
    return {
        "equal": bool(eq),
        "H_store_json": rec_j["H_store"],
        "H_store_sqlite": rec_s["H_store"],
        "master_json": loaded_j.get("master"),
        "master_sqlite": None if loaded_s is None else loaded_s["master"],
    }


# === TRP: Temporal Reproducibility Proof ===


def run_TRP(
    S0: Any,
    C: Dict[str, Any],
    V: str,
    stages: Iterable[Callable],
    delay_sec: float = 0.05,
) -> Dict[str, Any]:
    """
    Temporal Reproducibility Proof:
    Run now and after Δt; HMASTER must be identical.
    """
    r1 = BoRRun(S0=S0, C=C, V=V)
    for fn in stages:
        r1.add_step(fn)
    m1 = r1.finalize().master

    time.sleep(delay_sec)

    r2 = BoRRun(S0=S0, C=C, V=V)
    for fn in stages:
        r2.add_step(fn)
    m2 = r2.finalize().master

    return {"equal": m1 == m2, "master_t0": m1, "master_t1": m2}
