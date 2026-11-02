from pathlib import Path

from flask import Flask

from app import create_app


def test_factory_defaults():
    application = create_app()
    assert isinstance(application, Flask)
    assert application.config["DEBUG"] is False
    assert application.config["TESTING"] is False
    assert application.config["DATABASE"] == str(Path(application.instance_path) / "lab.sqlite")
    assert Path(application.instance_path).is_dir()
    assert set(application.blueprints) == {"main", "reflected", "stored", "dom"}


def test_test_config_overrides_defaults(app, tmp_path):
    assert app.testing is True
    assert app.config["DATABASE"] == str(tmp_path / "test.sqlite")
    assert not Path(app.config["DATABASE"]).exists()


def test_creates_instance_directory(tmp_path, monkeypatch):
    instance_path = tmp_path / "new-instance"
    monkeypatch.setattr(Flask, "auto_find_instance_path", lambda self: str(instance_path))
    application = create_app()
    assert instance_path.is_dir()
    assert application.config["DATABASE"] == str(instance_path / "lab.sqlite")
    assert not (instance_path / "lab.sqlite").exists()


def test_get_pages_never_create_database(app, client):
    database = Path(app.config["DATABASE"])
    for path in (
        "/", "/guide", "/documents", "/documents?category=Web", "/documents/1",
        "/vulnerable/search", "/fixed/search", "/vulnerable/comments",
        "/fixed/comments", "/vulnerable/preview", "/fixed/preview", "/missing",
    ):
        client.get(path)
    assert not database.exists()


def test_default_database_is_not_touched():
    application = create_app()
    database = Path(application.config["DATABASE"])
    before = database.read_bytes() if database.exists() else None
    for path in ("/", "/documents", "/documents/1", "/vulnerable/comments"):
        assert application.test_client().get(path).status_code == 200
    after = database.read_bytes() if database.exists() else None
    assert after == before
