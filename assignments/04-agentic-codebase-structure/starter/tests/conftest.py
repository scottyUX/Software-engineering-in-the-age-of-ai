import pytest

import main


@pytest.fixture(autouse=True)
def fresh_db(tmp_path, monkeypatch):
    """Point the app at an empty, per-test SQLite file."""
    monkeypatch.setattr(main, "DB_PATH", tmp_path / "links.db")
    main.init_db()
