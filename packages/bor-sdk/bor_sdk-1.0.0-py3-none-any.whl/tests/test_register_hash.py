"""
Tests for register-hash CLI command.
"""

import json
import os
import platform
import subprocess
import sys


def test_register_hash_command(tmp_path):
    """Test that register-hash CLI command creates correct registry entry."""
    # Create a dummy proof bundle
    bundle_path = tmp_path / "rich_proof_bundle.json"
    with open(bundle_path, "w", encoding="utf-8") as f:
        json.dump({"H_RICH": "dummyhash123"}, f)

    # Run the CLI command
    registry_path = tmp_path / "proof_registry.json"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "bor.cli",
            "register-hash",
            "--bundle",
            str(bundle_path),
            "--registry",
            str(registry_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    # Verify output messages
    assert "[BoR Consensus] Registered proof hash: dummyhash123" in result.stdout
    assert f"[BoR Consensus] Metadata written to {registry_path}" in result.stdout

    # Verify the registry was written correctly
    assert registry_path.exists()
    with open(registry_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["hash"] == "dummyhash123"
    assert "python" in data[0]
    assert "os" in data[0]
    assert "timestamp" in data[0]
    assert "user" in data[0]
    assert "label" in data[0]
    assert data[0]["label"] == "unlabeled"
    assert data[0]["sdk_version"] == "v1.0"


def test_register_hash_with_custom_label(tmp_path):
    """Test register-hash with custom user and label."""
    bundle_path = tmp_path / "rich_proof_bundle.json"
    with open(bundle_path, "w", encoding="utf-8") as f:
        json.dump({"H_RICH": "customhash456"}, f)

    registry_path = tmp_path / "proof_registry.json"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "bor.cli",
            "register-hash",
            "--bundle",
            str(bundle_path),
            "--registry",
            str(registry_path),
            "--user",
            "test-user",
            "--label",
            "demo-v1",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    with open(registry_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data[0]["user"] == "test-user"
    assert data[0]["label"] == "demo-v1"
    assert data[0]["hash"] == "customhash456"


def test_register_hash_appends_to_existing_registry(tmp_path):
    """Test that register-hash appends to existing registry rather than overwriting."""
    bundle_path = tmp_path / "rich_proof_bundle.json"
    registry_path = tmp_path / "proof_registry.json"

    # Create initial registry with one entry
    initial_entry = {
        "user": "user1",
        "timestamp": "2025-01-01T00:00:00Z",
        "os": "TestOS",
        "python": "3.11.0",
        "sdk_version": "v1.0",
        "label": "first",
        "hash": "hash1",
    }
    with open(registry_path, "w", encoding="utf-8") as f:
        json.dump([initial_entry], f)

    # Add second entry
    with open(bundle_path, "w", encoding="utf-8") as f:
        json.dump({"H_RICH": "hash2"}, f)

    subprocess.run(
        [
            sys.executable,
            "-m",
            "bor.cli",
            "register-hash",
            "--bundle",
            str(bundle_path),
            "--registry",
            str(registry_path),
            "--label",
            "second",
        ],
        check=True,
        capture_output=True,
    )

    # Verify both entries exist
    with open(registry_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert len(data) == 2
    assert data[0]["hash"] == "hash1"
    assert data[0]["label"] == "first"
    assert data[1]["hash"] == "hash2"
    assert data[1]["label"] == "second"


def test_register_hash_missing_bundle_fails(tmp_path):
    """Test that register-hash fails gracefully when bundle doesn't exist."""
    registry_path = tmp_path / "proof_registry.json"
    nonexistent_bundle = tmp_path / "nonexistent.json"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "bor.cli",
            "register-hash",
            "--bundle",
            str(nonexistent_bundle),
            "--registry",
            str(registry_path),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "[BoR Consensus] Bundle not found" in result.stderr


def test_register_hash_missing_hrich_fails(tmp_path):
    """Test that register-hash fails when H_RICH is missing from bundle."""
    bundle_path = tmp_path / "bad_bundle.json"
    registry_path = tmp_path / "proof_registry.json"

    # Create bundle without H_RICH
    with open(bundle_path, "w", encoding="utf-8") as f:
        json.dump({"primary": {}, "subproofs": {}}, f)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "bor.cli",
            "register-hash",
            "--bundle",
            str(bundle_path),
            "--registry",
            str(registry_path),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "Missing H_RICH" in result.stderr
