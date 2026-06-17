"""Experiment-focused tests for noisy user query variants.

These scenarios mirror the six query examples used in the experiment table.
"""

import sys
from pathlib import Path

import pytest


project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.app import create_app


@pytest.fixture(scope="module")
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


@pytest.mark.parametrize(
    "query",
    [
        "rekomen dong yg enak di kuta",
        "mau mkn yg murce seafood senggigi",
        "piza di kta",
        "seafood murrah di sengigi",
        "looking for cheap seafood near senggigi",
        "pizza??? di kuta!!!",
    ],
)
def test_experiment_query_variants_are_handled(client, query):
    token = "web_experiment_query_variants"

    init_resp = client.post("/api/chat", json={"message": "halo", "device_token": token})
    assert init_resp.status_code == 200
    init_payload = init_resp.get_json()
    assert init_payload.get("success") is True

    session_id = init_payload.get("data", {}).get("session_id")
    assert session_id

    resp = client.post(
        "/api/chat",
        json={"message": query, "session_id": session_id, "device_token": token},
    )
    assert resp.status_code == 200

    payload = resp.get_json()
    assert payload.get("success") is True

    response_text = payload.get("data", {}).get("bot_response", "")
    assert isinstance(response_text, str)
    assert len(response_text.strip()) > 0

    lowered = response_text.lower()
    assert "traceback" not in lowered
    assert "internal server error" not in lowered