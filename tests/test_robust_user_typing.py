"""Robustness tests for real-world user typing styles.

Coverage:
- Slang and abbreviations
- Typos and noisy punctuation
- Ambiguous/no-entity prompts
- Mixed language (ID + EN)
- Personalization signal after mixed interactions
"""

import pytest
import sys
from pathlib import Path

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
        # Slang/abbreviation
        "rekomen dong yg enak di kuta",
        "mau mkn yg murce seafood senggigi",
        "nyari tmpt makan santuy buat kluarga",

        # Typo-heavy variants
        "piza di kta",
        "seafoood murrah di sengigi",
        "romntis dinner di sengigi",

        # Ambiguous/no-entity
        "laper nih",
        "mau makan",
        "bingung mau kemana",

        # Mixed language
        "looking for cheap seafood near senggigi",
        "rekomend cafe for date night di kuta",

        # Noisy punctuation/symbols
        "pizza??? di kuta!!!",
        "restoran @#$% murah yg enak",
    ],
)
def test_chat_handles_robust_typing(client, query):
    token = "web_robust_typing_suite"

    # Ensure a session exists first.
    init_resp = client.post("/api/chat", json={"message": "halo", "device_token": token})
    assert init_resp.status_code == 200
    init_data = init_resp.get_json()
    assert init_data.get("success") is True
    session_id = init_data.get("data", {}).get("session_id")
    assert session_id

    resp = client.post(
        "/api/chat",
        json={"message": query, "session_id": session_id, "device_token": token},
    )
    assert resp.status_code == 200

    data = resp.get_json()
    assert data.get("success") is True

    bot_response = data.get("data", {}).get("bot_response", "")
    assert isinstance(bot_response, str)
    assert len(bot_response.strip()) > 0

    # Safety check: avoid hard crashes hidden in text output.
    lowered = bot_response.lower()
    assert "traceback" not in lowered
    assert "internal server error" not in lowered


def test_personalization_signal_after_mixed_typing(client):
    token = "web_robust_personal_profile"

    seed_queries = [
        "piza di kta",
        "seafood murce senggigi",
        "tempat romantis di sengigi",
        "rekomen dong seafood murah",
        "yang santuy buat keluarga",
    ]

    session_id = None
    for idx, q in enumerate(seed_queries):
        payload = {"message": q, "device_token": token}
        if session_id:
            payload["session_id"] = session_id

        resp = client.post("/api/chat", json=payload)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data.get("success") is True

        if idx == 0:
            session_id = data.get("data", {}).get("session_id")
            assert session_id

    ranked = client.get(
        "/api/recommendations/all-ranked",
        query_string={
            "session_id": session_id,
            "device_token": token,
            "limit": 10,
        },
    )
    assert ranked.status_code == 200
    ranked_data = ranked.get_json()
    assert ranked_data.get("success") is True

    payload = ranked_data.get("data", {})
    restaurants = payload.get("restaurants", [])
    assert isinstance(restaurants, list)
    assert len(restaurants) > 0

    insights = payload.get("personalization_insights", {})
    assert isinstance(insights, dict)

    # We expect at least one preference signal after multi-turn mixed typing.
    top_pref = insights.get("top_preferences", {})
    pref_count = sum(len(top_pref.get(k, [])) for k in ["cuisines", "locations", "moods", "prices"])
    assert pref_count >= 1
