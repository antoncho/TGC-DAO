#!/usr/bin/env python3
"""
Quantum Kernel CLI - operational harness for the Anton Fabrica environment.

This lightweight implementation keeps all core interactions self-contained so
the shell can manage scroll processing, registry inspection, and braid queries
without the optional kernel package.
"""

import argparse
import ast
import csv
import hashlib
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ensure the repository root is on sys.path for local imports
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("QuantumKernelCLI")


class QuantumKernelCLI:
    """Self-contained command interface for Fabrica kernel operations."""

    def __init__(self) -> None:
        self.root_dir = ROOT_DIR
        self.vault_dir = self.root_dir / "bundles/ΣΩΩ.current/vault"
        self.documents_dir = self.vault_dir / "documents"
        self.braids_dir = self.vault_dir / "braids"
        self.registry_path = self.vault_dir / "execution_registry.json"
        self.braidmap_path = self.vault_dir / "braidmap.json"
        self.scrollchain_path = self.root_dir / "scrollchain/ledger_sync.json"

        self._bootstrap_paths()

    def _bootstrap_paths(self) -> None:
        """Ensure all expected directories and seed files exist."""
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        self.documents_dir.mkdir(parents=True, exist_ok=True)
        self.braids_dir.mkdir(parents=True, exist_ok=True)
        self.scrollchain_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.registry_path.exists():
            logger.info("Creating empty execution registry at %s", self.registry_path)
            self._write_json(
                self.registry_path,
                {
                    "epoch": "ΣΩΩ.3.2",
                    "executions": [],
                    "last_updated": datetime.utcnow().isoformat()
                }
            )

        if not self.braidmap_path.exists():
            self._write_json(
                self.braidmap_path,
                {
                    "braidmap": {
                        "version": "1.0",
                        "epoch": "ΣΩΩ.3.2",
                        "documents": [],
                        "relationships": [],
                        "semantic_links": {}
                    },
                    "last_updated": datetime.utcnow().isoformat()
                }
            )

    def _read_json(self, path: Path) -> Dict[str, Any]:
        """Read JSON data from path; return {} on error."""
        if not path.exists():
            return {}
        try:
            with path.open("r", encoding="utf-8") as handle:
                return json.load(handle)
        except json.JSONDecodeError as exc:
            logger.error("Malformed JSON detected in %s: %s", path, exc)
            return {}

    def _write_json(self, path: Path, data: Any) -> None:
        """Persist JSON data to disk."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)

    def _load_registry(self) -> Dict[str, Any]:
        """Load the execution registry structure."""
        data = self._read_json(self.registry_path)
        executions = data.get("executions")
        if not isinstance(executions, list):
            executions = []
        data["executions"] = executions
        return data

    def _save_registry(self, data: Dict[str, Any]) -> None:
        """Persist the registry with updated timestamp."""
        data["last_updated"] = datetime.utcnow().isoformat()
        self._write_json(self.registry_path, data)

    def _build_execution_entry(
        self,
        kernel_name: str,
        doc_path: Path,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Construct a registry entry for a processed document."""
        timestamp = datetime.utcnow().isoformat()
        file_bytes = doc_path.read_bytes()
        content_hash = hashlib.sha256(file_bytes).hexdigest()
        execution_id = f"ex-{int(time.time() * 1000):x}"

        return {
            "execution_id": execution_id,
            "kernel": kernel_name,
            "document": str(doc_path),
            "status": "completed",
            "timestamp": timestamp,
            "metrics": {
                "size_bytes": len(file_bytes)
            },
            "quantum_seal": content_hash,
            "context": context
        }

    def process_document(
        self,
        doc_path: str,
        context: Optional[Dict[str, Any]] = None,
        enable_enrichment: bool = True,
        enable_scrollchain: bool = True
    ) -> Dict[str, Any]:
        """Process a document by hashing and recording it in the registry."""
        target = Path(doc_path).expanduser()
        if not target.is_file():
            return {"success": False, "error": f"Document not found: {doc_path}"}

        registry = self._load_registry()
        safe_context = dict(context or {})
        safe_context.setdefault("enable_enrichment", enable_enrichment)
        safe_context.setdefault("enable_scrollchain", enable_scrollchain)

        entry = self._build_execution_entry(
            "quantum_document_processor",
            target,
            safe_context
        )
        registry["executions"].append(entry)
        self._save_registry(registry)

        return {"success": True, "execution": entry}

    def list_kernels(self) -> List[str]:
        """List available kernel modules with their docstring summaries."""
        kernels: List[str] = []
        for module_path in sorted(self.root_dir.glob("*_kernel.py")):
            try:
                module_ast = ast.parse(module_path.read_text(encoding="utf-8"))
                doc = ast.get_docstring(module_ast) or ""
                summary = doc.strip().splitlines()[0] if doc.strip() else "No description"
            except Exception:
                summary = "No description"
            kernels.append(f"{module_path.stem}: {summary}")
        return kernels

    def view_registry(self, execution_id: Optional[str] = None, limit: int = 20) -> Dict[str, Any]:
        """Return registry entries or a specific execution."""
        registry = self._load_registry()
        executions = registry["executions"]

        if execution_id:
            match = next(
                (e for e in executions if e.get("execution_id") == execution_id),
                None
            )
            if match:
                return {"execution": match, "found": True}
            return {"execution": None, "found": False, "execution_id": execution_id}

        executions_sorted = sorted(
            executions,
            key=lambda item: item.get("timestamp", ""),
            reverse=True
        )
        return {
            "count": len(executions_sorted),
            "executions": executions_sorted[:max(limit, 0)],
            "last_updated": registry.get("last_updated")
        }

    def view_braidmap(self, doc_id: Optional[str] = None) -> Dict[str, Any]:
        """Inspect braid map data for semantic relationships."""
        braid_data = self._read_json(self.braidmap_path)
        braidmap = braid_data.get("braidmap", {})
        documents = braidmap.get("documents", [])
        relationships = braidmap.get("relationships", [])

        if doc_id:
            doc = next(
                (d for d in documents if d.get("id") == doc_id or d.get("doc_id") == doc_id),
                None
            )
            related = [
                r for r in relationships if doc_id in (r.get("source"), r.get("target"))
            ]
            if doc:
                return {"document": doc, "relationships": related}
            return {"error": f"Document '{doc_id}' not found in braidmap"}

        return {
            "documents": documents,
            "relationships": relationships,
            "semantic_links": braidmap.get("semantic_links", {}),
            "last_updated": braid_data.get("last_updated")
        }

    def watch_executions(self, interval: int = 5) -> None:
        """Tail the registry for new entries."""
        seen = 0
        try:
            while True:
                registry = self._load_registry()
                executions = registry["executions"]
                if len(executions) > seen:
                    for execution in executions[seen:]:
                        print(
                            f"[{execution.get('timestamp')}] "
                            f"{execution.get('kernel')} -> {execution.get('document')} "
                            f"({execution.get('status')})"
                        )
                    seen = len(executions)
                time.sleep(max(interval, 1))
        except KeyboardInterrupt:
            print("\nStopped monitoring executions.")

    def verify_scrollchain(self) -> Dict[str, Any]:
        """Verify scrollchain sync using the bundled netsync module, if available."""
        try:
            from netsync_scrollchain import get_scrollchain_sync
        except Exception as exc:  # pylint: disable=broad-except
            return {"status": "unavailable", "error": str(exc)}

        sync = get_scrollchain_sync(
            registry_path=str(self.registry_path),
            scrollchain_path=str(self.scrollchain_path)
        )
        verified = sync.verify_sync()
        latest = sync.get_latest_sync()
        return {
            "status": "synchronized" if verified else "out_of_sync",
            "last_sync": latest.get("timestamp") if latest else None,
            "registry_hash": latest.get("registry_hash") if latest else None,
            "timestamp": datetime.utcnow().isoformat()
        }

    def export_registry(self, output_file: str, format: str = "json") -> bool:
        """Export registry executions to JSON or CSV."""
        registry = self._load_registry()
        executions = registry["executions"]
        output_path = Path(output_file).expanduser()

        if format.lower() == "json":
            self._write_json(output_path, executions)
            return True

        if format.lower() == "csv":
            fieldnames = set()
            for entry in executions:
                fieldnames.update(entry.keys())
            with output_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=sorted(fieldnames))
                writer.writeheader()
                for row in executions:
                    writer.writerow(row)
            return True

        logger.error("Unsupported export format: %s", format)
        return False

    def visualize_graph(self, output_file: Optional[str] = None, show: bool = True) -> bool:
        """Placeholder for graph visualization."""
        logger.warning(
            "Graph visualization is not available in the lightweight CLI (requested output=%s, show=%s).",
            output_file,
            show
        )
        return False

    def status(self) -> Dict[str, Any]:
        """Return a concise status report for the CLI environment."""
        return {
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat(),
            "vault": str(self.vault_dir),
            "registry_entries": len(self._load_registry()["executions"]),
            "scrollchain": self.verify_scrollchain()["status"]
        }


def _parse_json_context(raw: Optional[str]) -> Dict[str, Any]:
    """Parse an optional JSON context argument."""
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise argparse.ArgumentTypeError(f"Invalid JSON context: {exc}") from exc


def main() -> int:
    """Run the CLI with argparse dispatch."""
    cli = QuantumKernelCLI()

    parser = argparse.ArgumentParser(
        description="Quantum Kernel CLI (Fabrica Edition)"
    )
    subparsers = parser.add_subparsers(dest="command")

    process_parser = subparsers.add_parser("process", help="Process a document")
    process_parser.add_argument("document", help="Path to the document to process")
    process_parser.add_argument("--context", type=_parse_json_context, help="Optional JSON context")
    process_parser.add_argument("--no-enrichment", action="store_true", help="Disable enrichment step")
    process_parser.add_argument("--no-scrollchain", action="store_true", help="Disable scrollchain sync")

    subparsers.add_parser("kernels", help="List available kernels")

    registry_parser = subparsers.add_parser("registry", help="View execution registry")
    registry_parser.add_argument("--id", help="Execution ID to view")
    registry_parser.add_argument("--limit", type=int, default=20, help="Number of recent executions to show")

    braid_parser = subparsers.add_parser("braid", help="View braid map")
    braid_parser.add_argument("--doc", help="Document ID to view")

    watch_parser = subparsers.add_parser("watch", help="Monitor executions in real-time")
    watch_parser.add_argument("--interval", type=int, default=5, help="Polling interval in seconds")

    export_parser = subparsers.add_parser("export", help="Export registry")
    export_parser.add_argument("output_file", help="Output file path")
    export_parser.add_argument("--format", choices=["json", "csv"], default="json")

    subparsers.add_parser("verify", help="Verify ScrollChain sync")
    subparsers.add_parser("status", help="Show system status")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    if args.command == "process":
        result = cli.process_document(
            args.document,
            context=args.context,
            enable_enrichment=not args.no_enrichment,
            enable_scrollchain=not args.no_scrollchain
        )
        print(json.dumps(result, indent=2))
        return 0 if result.get("success") else 1

    if args.command == "kernels":
        kernels = cli.list_kernels()
        print(json.dumps({"kernels": kernels}, indent=2))
        return 0

    if args.command == "registry":
        result = cli.view_registry(args.id, limit=args.limit)
        print(json.dumps(result, indent=2))
        return 0

    if args.command == "braid":
        result = cli.view_braidmap(args.doc)
        print(json.dumps(result, indent=2))
        return 0

    if args.command == "watch":
        print("Starting execution monitor (Ctrl+C to stop)...")
        cli.watch_executions(interval=args.interval)
        return 0

    if args.command == "export":
        success = cli.export_registry(args.output_file, format=args.format)
        print(json.dumps({"success": success, "output": args.output_file}, indent=2))
        return 0 if success else 1

    if args.command == "verify":
        result = cli.verify_scrollchain()
        print(json.dumps(result, indent=2))
        return 0 if result.get("status") != "error" else 1

    if args.command == "status":
        print(json.dumps(cli.status(), indent=2))
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
