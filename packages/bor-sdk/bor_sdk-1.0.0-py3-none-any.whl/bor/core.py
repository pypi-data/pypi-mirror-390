"""
Module: core
------------
Implements BoRRun, BoRStep, and Proof structures.
Each step in reasoning emits a fingerprint hi,
and all fingerprints concatenate into HMASTER.
"""

import inspect
from dataclasses import asdict, dataclass
from typing import Any, Callable, Dict, List

from bor.exceptions import DeterminismError, HashMismatchError
from bor.hash_utils import canonical_bytes, content_hash, env_fingerprint


@dataclass
class BoRStep:
    """Represents a single deterministic reasoning step."""

    fn_name: str
    input_state: Any
    output_state: Any
    config: Dict
    code_version: str
    fingerprint: str = None

    def compute_fingerprint(self):
        """Compute and store fingerprint for this step."""
        payload = {
            "fn": self.fn_name,
            "input": self.input_state,
            "config": self.config,
            "version": self.code_version,
        }
        self.fingerprint = content_hash(payload)
        return self.fingerprint


@dataclass(frozen=True)
class Proof:
    """Holds complete proof chain: meta, steps, stage_hashes, and HMASTER."""

    meta: Dict[str, Any]
    steps: List[Dict[str, Any]]
    stage_hashes: List[str]
    master: str


class BoRRun:
    """
    Controller for executing deterministic reasoning chains.
    Usage:
        run = BoRRun(S0, C, V)
        run.add_step(fn1).add_step(fn2)
        proof = run.finalize()
        run.verify()
    """

    def __init__(self, S0: Any, C: Dict, V: str):
        self.S0 = S0
        self.S0_initial = S0  # Keep original S0 for meta
        self.C = C
        self.V = V
        self.initial_state = S0  # Backward compatibility
        self.config = C  # Backward compatibility
        self.code_version = V  # Backward compatibility
        self.env = env_fingerprint()
        # Compute initialization proof hash P₀
        self.P0 = content_hash(
            {"S0": self.S0, "C": self.C, "V": self.V, "env": self.env}
        )
        # Optional console confirmation
        print(f"[BoR P₀] Initialization Proof Hash = {self.P0}")

        self.steps: List[BoRStep] = []
        self._final_state = None
        self.proof: Proof | None = None

    # --- Step execution ---
    def add_step(self, fn: Callable):
        """Apply a deterministic function and record its fingerprint."""
        if not callable(fn):
            raise DeterminismError("Step must be a callable.")
        prev_state = self.initial_state if not self.steps else self._final_state

        try:
            output_state = fn(prev_state, self.config, self.code_version)
        except Exception as e:
            raise DeterminismError(
                f"Function {fn.__name__} failed deterministically: {e}"
            )

        # Prefer decorator-provided name if present
        fn_name = getattr(fn, "__bor_step_name__", fn.__name__)
        step = BoRStep(
            fn_name, prev_state, output_state, self.config, self.code_version
        )
        step.compute_fingerprint()
        self.steps.append(step)
        self._final_state = output_state

        # Emit P₁ step-level proof hash
        step_num = len(self.steps)
        print(f"[BoR P₁] Step #{step_num} '{fn_name}' → hᵢ = {step.fingerprint}")

        return self

    def _stage_hashes(self) -> List[str]:
        """Return ordered list of step fingerprints (hᵢ)."""
        return [s.fingerprint for s in self.steps]

    # --- Final proof computation ---
    def finalize(self) -> Proof:
        """
        Aggregate step fingerprints into HMASTER and construct primary proof.
        HMASTER = H(h1 || h2 || ... || hn)
        """
        stage_hashes = self._stage_hashes()

        # Domain-separate the aggregation string (defensive)
        concat = "P2|" + "|".join(stage_hashes)
        HMASTER = content_hash(concat)

        # Build canonical primary proof object (P0–P2)
        step_records = [
            {
                "i": i + 1,
                "fn": s.fn_name,
                "input": s.input_state,
                "output": s.output_state,
                "config": s.config,
                "version": s.code_version,
                "fingerprint": s.fingerprint,
            }
            for i, s in enumerate(self.steps)
        ]

        meta = {
            "S0": self.S0_initial,
            "C": self.C,
            "V": self.V,
            "env": self.env,
            "H0": self.P0,
        }

        self.proof = Proof(
            meta=meta, steps=step_records, stage_hashes=stage_hashes, master=HMASTER
        )
        print(f"[BoR P₂] HMASTER = {HMASTER}")
        return self.proof

    def to_primary_proof(self) -> Dict[str, Any]:
        """
        Return the canonical primary proof JSON-ready dict.
        Requires finalize() to have been called.
        """
        if self.proof is None:
            raise RuntimeError("Call finalize() before exporting the primary proof.")
        return {
            "meta": self.proof.meta,
            "steps": self.proof.steps,
            "stage_hashes": self.proof.stage_hashes,
            "master": self.proof.master,
        }

    def run_steps(self, stage_fns):
        """
        Convenience wrapper: execute a sequence of functions as steps.
        """
        for fn in stage_fns:
            self.add_step(fn)
        return self

    # --- Verification ---
    def verify(self) -> bool:
        """Recompute proof deterministically and check master equality."""
        if not self.proof:
            raise DeterminismError("Run must be finalized before verification.")
        old_master = self.proof.master
        recomputed = self.finalize()
        if recomputed.master != old_master:
            raise HashMismatchError("Master proof mismatch: reasoning diverged.")
        return True

    def summary(self) -> Dict:
        """Return dictionary summary of current run."""
        return {
            "initial_state": self.initial_state,
            "num_steps": len(self.steps),
            "fingerprints": [s.fingerprint for s in self.steps],
            "HMASTER": self.proof.master if self.proof else None,
        }
