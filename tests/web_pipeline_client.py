"""Web pipeline client for experiment scripts.

Provides a single access path to the same backend endpoint used by the frontend:
GET /api/recommendations/all-ranked

Modes:
- live: always call running backend API via HTTP
- local: always call Flask test_client (in-process)
- auto: try live first, fallback to local if live is unavailable

Environment variables:
- WEB_API_MODE: auto|live|local (default: auto)
- WEB_API_BASE_URL: backend base URL (default: http://localhost:5500)
"""

import json
import os
from pathlib import Path
from typing import Dict, Any
from urllib.parse import urlencode
from urllib.request import urlopen

import sys

project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class WebPipelineClient:
    def __init__(self):
        self.mode = (os.getenv("WEB_API_MODE") or "auto").strip().lower()
        self.base_url = (os.getenv("WEB_API_BASE_URL") or "http://localhost:5500").rstrip("/")
        self._local_client = None

        if self.mode not in {"auto", "live", "local"}:
            self.mode = "auto"

    def get_all_ranked(self, query: str, device_token: str, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        params = {
            "device_token": device_token,
            "query": query,
            "page": page,
            "limit": limit,
        }

        if self.mode == "live":
            return self._get_live(params)

        if self.mode == "local":
            return self._get_local(params)

        # auto mode
        try:
            return self._get_live(params)
        except Exception:
            return self._get_local(params)

    def _get_live(self, params: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/api/recommendations/all-ranked?{urlencode(params)}"
        with urlopen(url, timeout=15) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw)

    def _get_local(self, params: Dict[str, Any]) -> Dict[str, Any]:
        if self._local_client is None:
            from backend.app import create_app

            app = create_app()
            self._local_client = app.test_client()

        response = self._local_client.get("/api/recommendations/all-ranked", query_string=params)
        return response.get_json() or {}
