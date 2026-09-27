import asyncio
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from edge_persistence import EdgePersistence, _database_url, get_database_url


class EdgePersistenceTests(unittest.TestCase):
    def test_railway_postgresql_urls_use_asyncpg_driver(self):
        self.assertEqual(
            _database_url("postgresql://user:pass@host/db"),
            "postgresql+asyncpg://user:pass@host/db",
        )
        self.assertEqual(
            _database_url("postgres://user:pass@host/db"),
            "postgresql+asyncpg://user:pass@host/db",
        )

    def test_railway_requires_database_url(self):
        for railway_marker in ("RAILWAY_ENVIRONMENT", "RAILWAY_ENVIRONMENT_NAME"):
            with self.subTest(railway_marker=railway_marker):
                with patch.dict(os.environ, {railway_marker: "production"}, clear=True):
                    with self.assertRaisesRegex(RuntimeError, "DATABASE_URL is required"):
                        get_database_url()

    def test_sqlite_session_and_transcript_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            database_path = Path(directory) / "sync.sqlite3"
            store = EdgePersistence(f"sqlite+aiosqlite:///{database_path}")

            async def exercise():
                try:
                    await store.initialize()
                    session_id = await store.start_session(
                        clinic_id="clinic-oromia-01", language_code="om-ET"
                    )
                    await store.record_transcript(
                        session_id=session_id,
                        clinic_id="clinic-oromia-01",
                        transcript="Dhukkuba garaacha qaba.",
                        event_type="final",
                    )
                finally:
                    await store.close()

            asyncio.run(exercise())
            self.assertEqual(store.backend, "sqlite")
            self.assertTrue(database_path.exists())


if __name__ == "__main__":
    unittest.main()
