
import os
import subprocess
import sys

from sqlalchemy import create_engine, inspect


def test_fresh_database_migration_creates_items_table(tmp_path):
    database_path = tmp_path / "fresh.db"
    database_url = f"sqlite:///{database_path.as_posix()}"

    env = os.environ.copy()
    env["SECUREAPP_DATABASE_URL"] = database_url

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "alembic",
            "upgrade",
            "head",
        ],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr

    engine = create_engine(database_url)
    try:
        tables = inspect(engine).get_table_names()
        assert "items" in tables
        assert "alembic_version" in tables
    finally:
        engine.dispose()
