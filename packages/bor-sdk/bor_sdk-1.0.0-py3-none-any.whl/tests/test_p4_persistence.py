"""
Tests for P₄ Persistence Proof
-------------------------------
Verifies that:
1. Saving to JSON returns a sidecar with H_store and timestamp
2. Saving to SQLite returns H_store and rowid; load_* reproduces the proof
3. JSON vs SQLite master equality can be checked programmatically
4. Round-trip integrity for both backends
5. H_store computation is deterministic and includes timestamp
"""

import json
import os
from pathlib import Path

from bor.core import BoRRun
from bor.decorators import step
from bor.store import (
    load_json_proof,
    load_sqlite_proof,
    save_json_proof,
    save_sqlite_proof,
)
from bor.verify import persistence_equivalence


@step
def add(x, C, V):
    """Add offset from config to state."""
    return x + C["offset"]


@step
def square(x, C, V):
    """Square the state."""
    return x * x


def _make_primary(tmp: Path):
    """Helper to create a primary proof."""
    r = BoRRun(S0=3, C={"offset": 2}, V="v1.0")
    r.add_step(add).add_step(square)
    p = r.finalize()
    primary = r.to_primary_proof()
    path = tmp / "primary.json"
    path.write_text(
        json.dumps(primary, separators=(",", ":"), sort_keys=True), encoding="utf-8"
    )
    return primary, path


def test_p4_json_store_roundtrip(tmp_path):
    """JSON storage should preserve HMASTER and emit H_store."""
    primary, p = _make_primary(tmp_path)
    rec = save_json_proof("demo", primary, root=str(tmp_path))
    assert os.path.exists(rec["path"])
    loaded = load_json_proof(rec["path"])
    assert loaded["master"] == primary["master"]
    assert isinstance(rec["H_store"], str) and len(rec["H_store"]) == 64


def test_p4_sqlite_store_roundtrip(tmp_path):
    """SQLite storage should preserve HMASTER and emit H_store."""
    primary, p = _make_primary(tmp_path)
    rec = save_sqlite_proof("demo", primary, root=str(tmp_path))
    loaded = load_sqlite_proof("demo", root=str(tmp_path))
    assert loaded is not None
    assert loaded["master"] == primary["master"]
    assert isinstance(rec["H_store"], str) and len(rec["H_store"]) == 64


def test_p4_equivalence_json_vs_sqlite(tmp_path):
    """JSON and SQLite should store identical HMASTER."""
    primary, p = _make_primary(tmp_path)
    save_json_proof("demo", primary, root=str(tmp_path))
    save_sqlite_proof("demo", primary, root=str(tmp_path))
    report = persistence_equivalence(
        str(tmp_path / "demo.json"), "demo", root=str(tmp_path)
    )
    assert report["equal"] is True
    assert report["master_json"] == report["master_sqlite"]


def test_p4_json_sidecar_created(tmp_path):
    """JSON storage should create a P4 sidecar file."""
    primary, p = _make_primary(tmp_path)
    rec = save_json_proof("test_sidecar", primary, root=str(tmp_path))
    sidecar_path = rec["path"] + ".p4.json"
    assert os.path.exists(sidecar_path)
    with open(sidecar_path, "r") as f:
        sidecar = json.load(f)
    assert sidecar["label"] == "test_sidecar"
    assert sidecar["H_store"] == rec["H_store"]
    assert sidecar["timestamp"] == rec["timestamp"]


def test_p4_sqlite_rowid_returned(tmp_path):
    """SQLite storage should return rowid."""
    primary, p = _make_primary(tmp_path)
    rec = save_sqlite_proof("test_row", primary, root=str(tmp_path))
    assert "rowid" in rec
    assert isinstance(rec["rowid"], int)
    assert rec["rowid"] > 0


def test_p4_timestamp_included(tmp_path):
    """Both backends should include timestamp."""
    primary, p = _make_primary(tmp_path)

    rec_json = save_json_proof("t1", primary, root=str(tmp_path))
    assert "timestamp" in rec_json
    assert isinstance(rec_json["timestamp"], int)

    rec_sqlite = save_sqlite_proof("t2", primary, root=str(tmp_path))
    assert "timestamp" in rec_sqlite
    assert isinstance(rec_sqlite["timestamp"], int)


def test_p4_hstore_differs_across_saves(tmp_path):
    """H_store should differ due to timestamp even for same proof."""
    primary, p = _make_primary(tmp_path)

    import time

    rec1 = save_json_proof("demo1", primary, root=str(tmp_path))
    time.sleep(1.1)  # Ensure different timestamp (int(time.time()) is in seconds)
    rec2 = save_json_proof("demo2", primary, root=str(tmp_path))

    # Different H_store due to different timestamps
    assert rec1["H_store"] != rec2["H_store"]


def test_p4_complete_proof_preservation(tmp_path):
    """All proof components should be preserved through storage."""
    primary, p = _make_primary(tmp_path)

    # JSON round-trip
    save_json_proof("complete", primary, root=str(tmp_path))
    loaded_json = load_json_proof(str(tmp_path / "complete.json"))
    assert loaded_json["meta"] == primary["meta"]
    assert loaded_json["steps"] == primary["steps"]
    assert loaded_json["stage_hashes"] == primary["stage_hashes"]
    assert loaded_json["master"] == primary["master"]

    # SQLite round-trip
    save_sqlite_proof("complete", primary, root=str(tmp_path))
    loaded_sqlite = load_sqlite_proof("complete", root=str(tmp_path))
    assert loaded_sqlite["meta"] == primary["meta"]
    assert loaded_sqlite["steps"] == primary["steps"]
    assert loaded_sqlite["stage_hashes"] == primary["stage_hashes"]
    assert loaded_sqlite["master"] == primary["master"]


def test_p4_sqlite_missing_label(tmp_path):
    """persistence_equivalence should handle missing SQLite proof."""
    primary, p = _make_primary(tmp_path)
    save_json_proof("only_json", primary, root=str(tmp_path))

    # Don't save to SQLite
    report = persistence_equivalence(
        str(tmp_path / "only_json.json"), "only_json", root=str(tmp_path)
    )
    assert report["equal"] is False
    assert report["reason"] == "sqlite_missing"
