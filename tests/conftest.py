from threading import Thread

import pytest
from werkzeug.serving import make_server

from app import create_app


@pytest.fixture
def app(tmp_path):
    return create_app({"TESTING": True, "DATABASE": str(tmp_path / "test.sqlite")})


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def live_server(app):
    """Use a bound ephemeral localhost port, a temp DB path and guaranteed cleanup."""
    server = make_server("127.0.0.1", 0, app, threaded=True)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
        if thread.is_alive():
            raise RuntimeError("Test server did not stop")
