import pytest

from app import create_app
from app.config import Settings


@pytest.fixture()
def settings() -> Settings:
    return Settings.from_env()


@pytest.fixture()
def client(settings):
    app = create_app(settings)
    app.config["TESTING"] = True
    return app.test_client()
