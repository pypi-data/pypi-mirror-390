import json

import pytest

from bor.core import BoRRun
from bor.verify import HashMismatchError, verify_primary_proof_dict


def add(x, C, V):
    return x + C.get("offset", 0)


def square(x, C, V):
    return x * x


def test_verify_recomputes_success(tmp_path):
    run = BoRRun(S0=3, C={"offset": 2}, V="v1.0")
    run.add_step(add).add_step(square)
    proof = run.finalize()
    primary = run.to_primary_proof()

    report = verify_primary_proof_dict(primary, 3, {"offset": 2}, "v1.0", [add, square])
    assert report["verified"] is True


def test_verify_detects_mismatch(tmp_path):
    run = BoRRun(S0=3, C={"offset": 2}, V="v1.0").add_step(add).add_step(square)
    proof = run.finalize()
    primary = run.to_primary_proof()
    altered = primary["master"][:-1] + "x"
    bad_primary = {**primary, "master": altered}

    with pytest.raises(HashMismatchError):
        verify_primary_proof_dict(bad_primary, 3, {"offset": 2}, "v1.0", [add, square])
