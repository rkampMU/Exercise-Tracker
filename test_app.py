"""Smoke tests: app starts and main pages load. No database access."""
import importlib
import os
import sys
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.dirname(__file__))


@pytest.fixture(scope="module")
def app_module():
    env = {
        "SUPABASE_URL": "http://localhost:54321",
        "SUPABASE_KEY": "dummy-key",
        "SECRET_KEY": "test-secret",
    }
    with patch.dict(os.environ, env), \
            patch("supabase.create_client", return_value=MagicMock()):
        sys.modules.pop("app", None)
        module = importlib.import_module("app")
        module.app.config["TESTING"] = True
        yield module
        sys.modules.pop("app", None)


@pytest.fixture
def client(app_module):
    return app_module.app.test_client()


def test_app_starts(app_module):
    assert app_module.app is not None
    assert app_module.app.config["TESTING"] is True


def test_index_page_loads(client):
    assert client.get("/").status_code == 200


def test_login_page_loads(client):
    assert client.get("/admin/login").status_code == 200


def test_admin_redirects_to_login_when_unauthenticated(client):
    resp = client.get("/admin")
    assert resp.status_code == 302
    assert "/admin/login" in resp.headers["Location"]


def test_api_classes_requires_auth(client):
    assert client.get("/api/classes").status_code == 401


def test_logout_works_without_session(client):
    resp = client.post("/api/logout")
    assert resp.status_code == 200
    assert resp.get_json() == {"success": True}
