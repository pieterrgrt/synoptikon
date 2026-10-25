import os
import sys
from pathlib import Path

import pytest

# Testdatabase in een tijdelijke map, vóór de app wordt geïmporteerd.
_TMP = Path(os.environ.get("PYTEST_TMPDIR", "/tmp")) / f"synoptikon-test-{os.getpid()}"
_TMP.mkdir(parents=True, exist_ok=True)
os.environ["SYNOPTIKON_DATA_DIR"] = str(_TMP)
os.environ["SYNOPTIKON_AUTH_MODE"] = "password"
os.environ["SYNOPTIKON_COOKIE_SECURE"] = "0"
os.environ["SYNOPTIKON_SECRET_KEY"] = "test-sleutel"

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from synoptikon.auth import hash_password  # noqa: E402
from synoptikon.config import settings  # noqa: E402

settings.password_hash = hash_password("geheim")

from synoptikon import db as database  # noqa: E402
from synoptikon.seed import seed  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def gevulde_db():
    database.init_db()
    with database.session() as s:
        seed(s)
    yield
    import shutil

    shutil.rmtree(_TMP, ignore_errors=True)


@pytest.fixture
def client():
    from fastapi.testclient import TestClient

    from synoptikon.main import app

    with TestClient(app) as c:
        c.post("/login", data={"wachtwoord": "geheim", "volgende": "/"})
        yield c


@pytest.fixture
def anoniem():
    from fastapi.testclient import TestClient

    from synoptikon.main import app

    with TestClient(app) as c:
        yield c
