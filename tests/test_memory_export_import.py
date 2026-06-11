import json
import tempfile
import unittest
from pathlib import Path

from classes.memory import MemoryManager, MemoryType


class MemoryExportImportTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        self.db_path = Path(self.tmpdir.name) / "memories.db"
        self.manager = MemoryManager(db_path=str(self.db_path))

    def test_export_includes_metadata_and_filters(self):
        self.manager.store_memory(
            "remember coffee", MemoryType.SHORT_TERM, tags=["drink", "daily"]
        )
        self.manager.store_memory("walk dog", MemoryType.QUICK_NOTE, tags=["pets"])

        export_path = Path(self.tmpdir.name) / "export.json"
        result = self.manager.export_memories(
            str(export_path), tags=["drink"], query="coffee"
        )

        self.assertEqual(result["count"], 1)
        payload = json.loads(export_path.read_text(encoding="utf-8"))
        self.assertIn("exported_at", payload)
        self.assertEqual(len(payload["memories"]), 1)
        memory = payload["memories"][0]
        self.assertIn("created_at", memory)
        self.assertIn("updated_at", memory)
        self.assertEqual(memory["tags"], ["drink", "daily"])

    def test_import_deduplicates_entries(self):
        self.manager.store_memory("same memory", MemoryType.LONG_TERM, tags=["tag"])
        import_payload = {
            "schema_version": 1,
            "memories": [
                {
                    "type": "long_term",
                    "content": "same memory",
                    "tags": ["tag"],
                    "created_at": "2025-01-01T00:00:00",
                    "updated_at": "2025-01-01T00:00:00",
                    "importance": 1,
                },
                {
                    "type": "quick_note",
                    "content": "new memory",
                    "tags": ["tag2"],
                    "created_at": "2025-01-02T00:00:00",
                    "updated_at": "2025-01-02T00:00:00",
                    "importance": 1,
                },
            ],
        }
        import_path = Path(self.tmpdir.name) / "import.json"
        import_path.write_text(json.dumps(import_payload), encoding="utf-8")

        result = self.manager.import_memories(str(import_path), deduplicate=True)
        self.assertEqual(result["imported"], 1)
        self.assertEqual(result["skipped_duplicates"], 1)

    def test_migrate_schema_reports_result(self):
        result = self.manager.migrate_schema()
        self.assertIn("timestamp", result)
        self.assertIn("applied_changes", result)


if __name__ == "__main__":
    unittest.main()
