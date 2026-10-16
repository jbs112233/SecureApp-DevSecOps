
import os
import subprocess
import sys

from sqlalchemy import create_engine, inspect, text


def run_alembic(database_url, *arguments):
    env = os.environ.copy()
    env["SECUREAPP_DATABASE_URL"] = database_url

    return subprocess.run(
        [
            sys.executable,
            "-m",
            "alembic",
            *arguments,
        ],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_fresh_database_migration_creates_items_table(tmp_path):
    database_path = tmp_path / "fresh.db"
    database_url = f"sqlite:///{database_path.as_posix()}"

    result = run_alembic(database_url, "upgrade", "head")

    assert result.returncode == 0, result.stdout + result.stderr

    engine = create_engine(database_url)
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        assert "items" in tables
        assert "users" in tables
        assert "alembic_version" in tables

        item_columns = {
            column["name"]
            for column in inspector.get_columns("items")
        }
        assert "owner_id" in item_columns

        owner_foreign_keys = [
            fk for fk in inspector.get_foreign_keys("items")
            if fk.get("constrained_columns") == ["owner_id"]
        ]
        assert any(
            fk.get("referred_table") == "users"
            and fk.get("referred_columns") == ["id"]
            for fk in owner_foreign_keys
        )
    finally:
        engine.dispose()


def test_item_ownership_migration_can_downgrade_and_upgrade(tmp_path):
    database_path = tmp_path / "migration_cycle.db"
    database_url = f"sqlite:///{database_path.as_posix()}"

    result = run_alembic(
        database_url,
        "upgrade",
        "ab148143cd93",
    )

    assert result.returncode == 0, result.stdout + result.stderr

    engine = create_engine(database_url)
    try:
        with engine.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO items (name, description, price)
                    VALUES (:name, :description, :price)
                    """
                ),
                {
                    "name": "Migration preservation test",
                    "description": "Existing item data",
                    "price": 19.99,
                },
            )
    finally:
        engine.dispose()

    result = run_alembic(
        database_url,
        "upgrade",
        "e770598fc08d",
    )

    assert result.returncode == 0, result.stdout + result.stderr


    engine = create_engine(database_url)
    try:
        columns = {
            column["name"]
            for column in inspect(engine).get_columns("items")
        }
        assert "owner_id" in columns

        with engine.connect() as connection:
            item = connection.execute(
                text(
                    """
                    SELECT name, description, price
                    FROM items
                    WHERE name = :name
                    """
                ),
                {"name": "Migration preservation test"},
            ).one_or_none()

        assert item is not None
        assert item.name == "Migration preservation test"
        assert item.description == "Existing item data"
        assert item.price == 19.99
    finally:
        engine.dispose()


    result = run_alembic(
        database_url,
        "downgrade",
        "ab148143cd93",
    )
    assert result.returncode == 0, result.stdout + result.stderr

    engine = create_engine(database_url)
    try:
        columns = {
            column["name"]
            for column in inspect(engine).get_columns("items")
        }
        assert "owner_id" not in columns
    finally:
        engine.dispose()

    result = run_alembic(
        database_url,
        "upgrade",
        "head",
    )
    assert result.returncode == 0, result.stdout + result.stderr

    engine = create_engine(database_url)
    try:
        columns = {
            column["name"]
            for column in inspect(engine).get_columns("items")
        }
        assert "owner_id" in columns
    finally:
        engine.dispose()
