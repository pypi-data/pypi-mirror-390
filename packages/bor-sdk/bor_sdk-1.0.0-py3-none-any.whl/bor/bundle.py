"""
Module: bundle
--------------
Rich Proof Bundle builder: combines primary proof with sub-proofs.
Produces a comprehensive verification package with H_RICH commitment.
"""

import hashlib
import json
import time
from typing import Any, Callable, Dict, Iterable

from bor.core import BoRRun
from bor.subproofs import (
    run_CCP,
    run_CMIP,
    run_DIP,
    run_DP,
    run_PEP_bad_signature,
    run_PoPI,
    run_PP,
    run_TRP,
)


def build_primary(
    S0: Any, C: Dict[str, Any], V: str, stages: Iterable[Callable]
) -> Dict[str, Any]:
    """
    Build a primary proof by executing the reasoning chain.
    Returns the primary proof JSON dictionary.
    """
    r = BoRRun(S0=S0, C=C, V=V)
    for fn in stages:
        r.add_step(fn)
    _ = r.finalize()
    return r.to_primary_proof()


def build_bundle(
    S0: Any, C: Dict[str, Any], V: str, stages: Iterable[Callable]
) -> Dict[str, Any]:
    """
    Build a Rich Proof Bundle containing:
    - Primary proof (P0-P2)
    - Sub-proofs (DIP, DP, PEP, PoPI, CCP, CMIP, PP, TRP)
    - Sub-proof hashes
    - H_RICH: master commitment over all sub-proofs
    """
    primary = build_primary(S0, C, V, stages)

    # Run sub-proofs
    dip = run_DIP(S0, C, V, stages)
    dp = run_DP(
        S0, C, V, stages, perturb={"C": {"__bor_delta__": 1}}
    )  # harmless C perturbation key
    pep_ok, pep_exc = run_PEP_bad_signature()
    popi = run_PoPI(primary)
    ccp = run_CCP(S0, C, V, stages)
    cmip = run_CMIP(S0, C, V, stages)
    pp = run_PP(S0, C, V, stages)
    trp = run_TRP(S0, C, V, stages)

    subproofs = {
        "DIP": dip,
        "DP": dp,
        "PEP": {"ok": pep_ok, "exception": pep_exc},
        "PoPI": popi,
        "CCP": ccp,
        "CMIP": cmip,
        "PP": pp,
        "TRP": trp,
    }

    # Compute hash for each subproof
    def h_sub(obj):
        return hashlib.sha256(
            json.dumps(obj, separators=(",", ":"), sort_keys=True).encode("utf-8")
        ).hexdigest()

    sub_hashes = {k: h_sub(v) for k, v in subproofs.items()}

    # H_RICH = commitment over all subproof hashes
    H_RICH = hashlib.sha256(
        "|".join([sub_hashes[k] for k in sorted(sub_hashes.keys())]).encode("utf-8")
    ).hexdigest()

    bundle = {
        "primary": primary,
        "subproofs": subproofs,
        "subproof_hashes": sub_hashes,
        "H_RICH": H_RICH,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    return bundle


def build_index(bundle: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build a compact index from a bundle.
    Contains H_RICH and subproof hashes for quick verification.
    """
    idx = {"H_RICH": bundle["H_RICH"], "subproof_hashes": bundle["subproof_hashes"]}
    return idx
