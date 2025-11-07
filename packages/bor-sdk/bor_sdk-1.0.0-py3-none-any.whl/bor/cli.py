"""
Module: cli
-----------
Command-line interface for BoR-Proof SDK.
"""

import argparse
import json
import sys

from bor.verify import HashMismatchError, verify_primary_file


def main():
    parser = argparse.ArgumentParser(prog="borp", description="BoR-Proof SDK CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser("verify", help="Verify proofs")
    v.add_argument("--primary", required=True, help="Path to primary proof JSON")
    v.add_argument("--initial", required=True, help="JSON for S0")
    v.add_argument("--config", required=True, help="JSON for C")
    v.add_argument("--version", required=True, help="Version string V")
    v.add_argument(
        "--stages",
        nargs="+",
        required=True,
        help="Stage functions as module.fn or module:fn",
    )

    p = sub.add_parser("persist", help="Save proof and compute P₄")
    p.add_argument("--label", required=True, help="Label for storage")
    p.add_argument("--primary", required=True, help="Path to primary proof JSON")
    p.add_argument(
        "--root", default=".bor_store", help="Storage directory (default .bor_store)"
    )
    p.add_argument("--backend", choices=["json", "sqlite", "both"], default="both")

    pr = sub.add_parser("prove", help="Generate proofs")
    pr.add_argument(
        "--all", action="store_true", help="Build primary + subproof bundle"
    )
    pr.add_argument("--initial", help="JSON for S0")
    pr.add_argument("--config", help="JSON for C")
    pr.add_argument("--version", help="Version string V")
    pr.add_argument(
        "--stages", nargs="+", help="Stage functions as module.fn or module:fn"
    )
    pr.add_argument("--outdir", default="out", help="Output directory")

    vb = sub.add_parser("verify-bundle", help="Verify a Rich Proof Bundle")
    vb.add_argument("--bundle", required=True, help="Path to rich_proof_bundle.json")
    vb.add_argument("--initial", help="JSON for S0 (optional)")
    vb.add_argument("--config", help="JSON for C (optional)")
    vb.add_argument("--version", help="Version string V (optional)")
    vb.add_argument(
        "--stages",
        nargs="+",
        help="Stage functions (optional) as module.fn or module:fn",
    )

    sh = sub.add_parser("show", help="Render human-readable views")
    sh.add_argument("--trace", help="Path to primary proof JSON OR bundle JSON")
    sh.add_argument(
        "--from",
        dest="source",
        choices=["primary", "bundle"],
        default="bundle",
        help="Indicate whether --trace points to a primary or a bundle JSON (default bundle)",
    )

    rh = sub.add_parser("register-hash", help="Register proof hash for consensus")
    rh.add_argument(
        "--bundle",
        default="out/rich_proof_bundle.json",
        help="Path to the rich proof bundle",
    )
    rh.add_argument(
        "--registry",
        default="proof_registry.json",
        help="Local JSON file to append consensus entries",
    )
    rh.add_argument(
        "--user", help="Optional user or handle name (auto-detected if not provided)"
    )
    rh.add_argument(
        "--label",
        help="Optional label for this proof record (e.g., 'demo' or 'v1-test')",
    )

    args = parser.parse_args()

    if args.cmd == "verify":
        import json as _json

        try:
            S0 = _json.loads(args.initial)
            C = _json.loads(args.config)
            V = args.version
            report = verify_primary_file(args.primary, S0, C, V, args.stages)
            print("[BoR P₃] VERIFIED")
            print(json.dumps(report, indent=2, sort_keys=True))
            sys.exit(0)
        except HashMismatchError as e:
            print("[BoR P₃] MISMATCH")
            print(e, file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print("[BoR P₃] ERROR", e, file=sys.stderr)
            sys.exit(2)

    elif args.cmd == "persist":
        import json as _json

        from bor.store import load_json_proof, save_json_proof, save_sqlite_proof

        try:
            proof = load_json_proof(args.primary)
            reports = {}
            if args.backend in ("json", "both"):
                rj = save_json_proof(args.label, proof, root=args.root)
                reports["json"] = rj
            if args.backend in ("sqlite", "both"):
                rs = save_sqlite_proof(args.label, proof, root=args.root)
                reports["sqlite"] = rs
            print("[BoR P₄] PERSISTED")
            print(json.dumps(reports, indent=2, sort_keys=True))
            sys.exit(0)
        except Exception as e:
            print("[BoR P₄] ERROR", e, file=sys.stderr)
            sys.exit(2)

    elif args.cmd == "prove" and args.all:
        import json as _json
        import os

        from bor.bundle import build_bundle, build_index
        from bor.verify import _import_stage

        try:
            os.makedirs(args.outdir, exist_ok=True)
            S0 = _json.loads(args.initial)
            C = _json.loads(args.config)
            V = args.version
            stages = [_import_stage(p) for p in args.stages]
            bundle = build_bundle(S0, C, V, stages)
            idx = build_index(bundle)
            with open(
                os.path.join(args.outdir, "rich_proof_bundle.json"),
                "w",
                encoding="utf-8",
            ) as f:
                _json.dump(bundle, f, sort_keys=True)
            with open(
                os.path.join(args.outdir, "rich_proof_index.json"),
                "w",
                encoding="utf-8",
            ) as f:
                _json.dump(idx, f, sort_keys=True)
            print("[BoR RICH] Bundle created")
            print(_json.dumps({"H_RICH": bundle["H_RICH"]}, indent=2, sort_keys=True))
            sys.exit(0)
        except Exception as e:
            print("[BoR RICH] ERROR", e, file=sys.stderr)
            sys.exit(2)

    elif args.cmd == "verify-bundle":
        import json as _json

        from bor.verify import (
            BundleVerificationError,
            _import_stage,
            verify_bundle_file,
        )

        try:
            stages = None
            S0 = C = V = None
            if args.stages and args.initial and args.config and args.version:
                S0 = _json.loads(args.initial)
                C = _json.loads(args.config)
                V = args.version
                stages = [_import_stage(p) for p in args.stages]

            rep = verify_bundle_file(args.bundle, stages=stages, S0=S0, C=C, V=V)
            print("[BoR RICH] VERIFIED")
            print(json.dumps(rep, indent=2, sort_keys=True))
            sys.exit(0)
        except BundleVerificationError as e:
            print("[BoR RICH] MISMATCH")
            print(e, file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print("[BoR RICH] ERROR", e, file=sys.stderr)
            sys.exit(2)

    elif args.cmd == "show":
        import json as _json
        import os

        from bor.verify import render_trace_from_primary

        try:
            path = args.trace
            if not os.path.exists(path):
                print("[BoR SHOW] ERROR: file not found", file=sys.stderr)
                sys.exit(2)
            with open(path, "r", encoding="utf-8") as f:
                obj = _json.load(f)
            if args.source == "primary":
                primary = obj
            else:
                # bundle: extract primary
                if "primary" not in obj:
                    print("[BoR SHOW] ERROR: bundle missing 'primary'", file=sys.stderr)
                    sys.exit(1)
                primary = obj["primary"]
            print(render_trace_from_primary(primary))
            sys.exit(0)
        except Exception as e:
            print("[BoR SHOW] ERROR", e, file=sys.stderr)
            sys.exit(2)

    elif args.cmd == "register-hash":
        import datetime
        import getpass
        import json as _json
        import os
        import platform

        try:
            # Validate bundle existence
            if not os.path.exists(args.bundle):
                print(
                    f"[BoR Consensus] Bundle not found: {args.bundle}", file=sys.stderr
                )
                sys.exit(1)

            # Load proof hash
            try:
                with open(args.bundle, "r", encoding="utf-8") as f:
                    data = _json.load(f)
                H_RICH = data.get("H_RICH")
                if not H_RICH:
                    raise ValueError("Missing H_RICH in bundle")
            except Exception as e:
                print(f"[BoR Consensus] Error reading bundle: {e}", file=sys.stderr)
                sys.exit(1)

            # Collect environment metadata
            entry = {
                "user": args.user or os.getenv("USER", getpass.getuser()),
                "timestamp": datetime.datetime.now(datetime.timezone.utc)
                .isoformat()
                .replace("+00:00", "Z"),
                "os": platform.platform(),
                "python": sys.version.split()[0],
                "sdk_version": "v1.0",
                "label": args.label or "unlabeled",
                "hash": H_RICH,
            }

            # Append to registry
            registry_data = []
            if os.path.exists(args.registry):
                try:
                    with open(args.registry, "r", encoding="utf-8") as f:
                        registry_data = _json.load(f)
                    if not isinstance(registry_data, list):
                        registry_data = [registry_data]
                except Exception:
                    registry_data = []

            registry_data.append(entry)
            with open(args.registry, "w", encoding="utf-8") as f:
                _json.dump(registry_data, f, indent=2)

            print(f"[BoR Consensus] Registered proof hash: {H_RICH}")
            print(f"[BoR Consensus] Metadata written to {args.registry}")
            print(
                f"[BoR Consensus] User: {entry['user']}  |  OS: {entry['os']}  |  Python: {entry['python']}"
            )
            sys.exit(0)
        except Exception as e:
            print(f"[BoR Consensus] ERROR: {e}", file=sys.stderr)
            sys.exit(2)


if __name__ == "__main__":
    main()
