"""CLI utilities for backing up and restoring memory data."""

import argparse
import json
import time
from datetime import datetime
from pathlib import Path

from classes.memory import MemoryManager, MemoryType


def _parse_memory_type(value: str):
    if not value:
        return None
    normalized = value.strip().lower()
    return MemoryType(normalized)


def _parse_tags(raw_tags: str):
    if not raw_tags:
        return None
    tags = [tag.strip() for tag in raw_tags.split(",") if tag.strip()]
    return tags or None


def _print_result(result: dict):
    print(json.dumps(result, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="memory_cli",
        description="Export, import, and back up NOVA-AI memories.",
    )
    parser.add_argument(
        "--db-path",
        default="memories.db",
        help="Path to memories SQLite database (default: memories.db)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    export_parser = subparsers.add_parser("export", help="Export memories to JSON")
    export_parser.add_argument("output", help="Output JSON file path")
    export_parser.add_argument(
        "--type",
        choices=[m.value for m in MemoryType],
        help="Optional memory type filter",
    )
    export_parser.add_argument(
        "--tags",
        help="Optional comma-separated tags filter (memories must contain all tags)",
    )
    export_parser.add_argument(
        "--query",
        help="Optional content/tag text filter for exported memories",
    )

    import_parser = subparsers.add_parser("import", help="Import memories from JSON")
    import_parser.add_argument("input", help="Input JSON file path")
    import_parser.add_argument(
        "--no-deduplicate",
        action="store_true",
        help="Allow duplicate entries during import",
    )

    subparsers.add_parser("migrate", help="Run additive schema migration checks")

    backup_parser = subparsers.add_parser(
        "backup-schedule", help="Run scheduled JSON backups"
    )
    backup_parser.add_argument(
        "--output-dir",
        default="memory_backups",
        help="Directory where timestamped backups are written",
    )
    backup_parser.add_argument(
        "--interval-minutes",
        type=float,
        default=60.0,
        help="Backup interval in minutes (default: 60)",
    )
    backup_parser.add_argument(
        "--run-count",
        type=int,
        default=0,
        help="Number of backups to run before exit (0 = run forever, stop with Ctrl+C)",
    )

    args = parser.parse_args()
    manager = MemoryManager(db_path=args.db_path)

    if args.command == "export":
        result = manager.export_memories(
            export_path=args.output,
            memory_type=_parse_memory_type(args.type) if args.type else None,
            tags=_parse_tags(args.tags),
            query=args.query,
        )
        _print_result(result)
        return

    if args.command == "import":
        result = manager.import_memories(
            import_path=args.input, deduplicate=not args.no_deduplicate
        )
        _print_result(result)
        return

    if args.command == "migrate":
        result = manager.migrate_schema()
        _print_result(result)
        return

    if args.command == "backup-schedule":
        interval_seconds = max(1, round(args.interval_minutes * 60))
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        completed = 0
        while True:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            target = output_dir / f"memories-backup-{timestamp}.json"
            result = manager.export_memories(str(target))
            _print_result(result)
            completed += 1

            if args.run_count > 0 and completed >= args.run_count:
                break
            time.sleep(interval_seconds)


if __name__ == "__main__":
    main()
