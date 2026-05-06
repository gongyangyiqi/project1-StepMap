import os
import tempfile
from pathlib import Path
import importlib

import pytest
from fastapi.testclient import TestClient


def _set_required_env(database_url: str) -> None:
    os.environ.setdefault("APP_ENV", "test")
    os.environ.setdefault("APP_NAME", "StepMap")
    os.environ.setdefault("APP_HOST", "127.0.0.1")
    os.environ.setdefault("APP_PORT", "8000")
    os.environ.setdefault("LOG_LEVEL", "INFO")

    os.environ["DATABASE_URL"] = database_url
    os.environ.setdefault("JWT_SECRET_KEY", "test-secret")
    os.environ.setdefault("JWT_ALGORITHM", "HS256")
    os.environ.setdefault("JWT_EXPIRE_MINUTES", "60")

    os.environ.setdefault("S3_ENDPOINT_URL", "http://localhost:9000")
    os.environ.setdefault("S3_REGION", "us-east-1")
    os.environ.setdefault("S3_BUCKET", "test-bucket")
    os.environ.setdefault("S3_ACCESS_KEY", "test-access-key")
    os.environ.setdefault("S3_SECRET_KEY", "test-secret-key")


@pytest.fixture()
def client() -> TestClient:
    artifacts_root = Path.cwd() / ".test-artifacts"
    artifacts_root.mkdir(parents=True, exist_ok=True)

    temp_dir = Path(tempfile.mkdtemp(prefix="stepmap-tests-", dir=artifacts_root))
    db_path = temp_dir / "test.db"
    database_url = f"sqlite+pysqlite:///{db_path}"

    _set_required_env(database_url)

    from app.db.base import Base
    from app.db import session as db_session
    importlib.reload(db_session)
    from app.models import user as _user_model  # noqa: F401
    from app.main import create_app

    Base.metadata.create_all(bind=db_session.engine)
    app = create_app()
    return TestClient(app)
