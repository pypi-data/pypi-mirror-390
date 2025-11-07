"""
Module: store
-------------
P₄ Persistence Proof: Local persistence layer with integrity verification.
Two modes: JSON (default) and SQLite (optional).
"""

import hashlib
import json
import os
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from bor.core import Proof

DEFAULT_DIR = ".bor_store"
DEFAULT_DB = "proofs.db"


def _ensure_dir(root: str = DEFAULT_DIR):
    """Ensure storage directory exists."""
    os.makedirs(root, exist_ok=True)


def _sha256_bytes(b: bytes) -> str:
    """Compute SHA-256 hash of bytes."""
    return hashlib.sha256(b).hexdigest()


# === P₄ JSON Storage ===


def save_json_proof(
    label: str, proof: Dict[str, Any], root: str = DEFAULT_DIR
) -> Dict[str, Any]:
    """
    Save primary proof JSON (already canonical dict) and compute P₄.
    Returns a record with path and H_store.
    """
    _ensure_dir(root)
    path = os.path.join(root, f"{label}.json")
    # minified, sorted JSON for stable bytes
    data = json.dumps(proof, separators=(",", ":"), sort_keys=True).encode("utf-8")
    with open(path, "wb") as f:
        f.write(data)
    ts = int(time.time())
    h_store = _sha256_bytes(data + str(ts).encode("utf-8"))
    record = {"label": label, "path": path, "timestamp": ts, "H_store": h_store}
    # write sidecar for audit
    with open(path + ".p4.json", "w", encoding="utf-8") as f:
        json.dump(record, f, sort_keys=True)
    return record


def load_json_proof(path: str) -> Dict[str, Any]:
    """Load proof from JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# === P₄ SQLite Storage ===


def init_sqlite(root: str = DEFAULT_DIR) -> str:
    """Initialize SQLite database with schema."""
    _ensure_dir(root)
    db_path = os.path.join(root, DEFAULT_DB)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
        CREATE TABLE IF NOT EXISTS proofs(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          label TEXT,
          meta TEXT NOT NULL,
          steps TEXT NOT NULL,
          stage_hashes TEXT NOT NULL,
          master TEXT NOT NULL,
          timestamp INTEGER NOT NULL
        )"""
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_label ON proofs(label)")
    return db_path


def save_sqlite_proof(
    label: str, proof: Dict[str, Any], root: str = DEFAULT_DIR
) -> Dict[str, Any]:
    """
    Persist proof into SQLite and compute P₄ over a canonical row blob.
    """
    db_path = init_sqlite(root)
    ts = int(time.time())
    meta = json.dumps(proof["meta"], separators=(",", ":"), sort_keys=True)
    steps = json.dumps(proof["steps"], separators=(",", ":"), sort_keys=True)
    stage_hashes = json.dumps(
        proof["stage_hashes"], separators=(",", ":"), sort_keys=True
    )
    master = proof["master"]
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO proofs(label, meta, steps, stage_hashes, master, timestamp) VALUES (?,?,?,?,?,?)",
            (label, meta, steps, stage_hashes, master, ts),
        )
        rowid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        # Canonical row object for H_store
        row_obj = {
            "label": label,
            "meta": json.loads(meta),
            "steps": json.loads(steps),
            "stage_hashes": json.loads(stage_hashes),
            "master": master,
        }
        row_blob = json.dumps(row_obj, separators=(",", ":"), sort_keys=True).encode(
            "utf-8"
        )
        h_store = _sha256_bytes(row_blob + str(ts).encode("utf-8"))
    return {
        "label": label,
        "db_path": db_path,
        "rowid": rowid,
        "timestamp": ts,
        "H_store": h_store,
    }


def load_sqlite_proof(label: str, root: str = DEFAULT_DIR) -> Optional[Dict[str, Any]]:
    """Load latest proof by label from SQLite."""
    db_path = init_sqlite(root)
    with sqlite3.connect(db_path) as conn:
        cur = conn.execute(
            "SELECT meta, steps, stage_hashes, master, timestamp FROM proofs WHERE label=? ORDER BY id DESC LIMIT 1",
            (label,),
        )
        row = cur.fetchone()
        if not row:
            return None
        meta = json.loads(row[0])
        steps = json.loads(row[1])
        stage_hashes = json.loads(row[2])
        master = row[3]
        ts = row[4]
    return {
        "meta": meta,
        "steps": steps,
        "stage_hashes": stage_hashes,
        "master": master,
        "timestamp": ts,
    }


# === Legacy ProofStore Class (backward compatibility) ===


class ProofStore:
    """Legacy class-based interface for backward compatibility."""

    def __init__(self, root: str = ".bor_store", use_sqlite: bool = False):
        self.root = Path(root)
        self.use_sqlite = use_sqlite
        self.root.mkdir(exist_ok=True)
        if use_sqlite:
            self.db_path = self.root / "proofs.db"
            self._init_db()

    def _init_db(self):
        init_sqlite(str(self.root))

    def save(self, label: str, proof: Proof) -> Path:
        """Save proof using legacy interface."""
        proof_dict = {
            "label": label,
            "master": proof.master,
            "stage_hashes": proof.stage_hashes,
            "meta": proof.meta,
            "steps": proof.steps,
        }
        if self.use_sqlite:
            save_sqlite_proof(label, proof_dict, root=str(self.root))
            return self.db_path
        else:
            save_json_proof(label, proof_dict, root=str(self.root))
            return self.root / f"{label}.json"

    def load(self, label: str) -> Proof:
        """Load proof using legacy interface."""
        if self.use_sqlite:
            data = load_sqlite_proof(label, root=str(self.root))
            if data is None:
                raise FileNotFoundError(f"No proof named {label}")
            return Proof(
                meta=data["meta"],
                steps=data["steps"],
                stage_hashes=data["stage_hashes"],
                master=data["master"],
            )
        else:
            path = self.root / f"{label}.json"
            if not path.exists():
                raise FileNotFoundError(f"No proof named {label}")
            data = load_json_proof(str(path))
            return Proof(
                meta=data.get("meta", {}),
                steps=data.get("steps", []),
                stage_hashes=data["stage_hashes"],
                master=data["master"],
            )

    def list_proofs(self) -> List[str]:
        """List all stored proof labels."""
        if self.use_sqlite:
            db_path = init_sqlite(str(self.root))
            with sqlite3.connect(db_path) as conn:
                cur = conn.execute("SELECT DISTINCT label FROM proofs ORDER BY id DESC")
                labels = [r[0] for r in cur.fetchall()]
            return labels
        return [p.stem for p in self.root.glob("*.json")]
