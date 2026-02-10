"""
DTO (Data Transfer Objects) for request validation.
Uses Python dataclasses — zero external dependencies.
Each DTO validates and sanitizes incoming request data.
"""
from dataclasses import dataclass, field
from typing import Optional
import uuid


class DTOValidationError(Exception):
    """Raised when DTO validation fails."""
    def __init__(self, message: str, field_name: str = None):
        self.message = message
        self.field_name = field_name
        super().__init__(self.message)


# ─── Chat DTOs ───────────────────────────────────────────────────

@dataclass
class ChatRequestDTO:
    """Validated chat request payload."""
    message: str
    session_id: Optional[str] = None
    device_token: str = ""

    @classmethod
    def from_request(cls, request):
        """Parse and validate a Flask request into a ChatRequestDTO."""
        json_data = request.get_json(silent=True)
        if not json_data:
            raise DTOValidationError("Request body harus berupa JSON")

        message = str(json_data.get('message', '')).strip()
        session_id = json_data.get('session_id')
        device_token = json_data.get('device_token')

        # Auto-generate device_token if missing
        if not device_token:
            device_token = f"web_{uuid.uuid4().hex[:9]}"

        if session_id is not None and not isinstance(session_id, str):
            raise DTOValidationError("session_id harus berupa string", "session_id")

        return cls(message=message, session_id=session_id, device_token=device_token)

    @property
    def is_greeting(self) -> bool:
        return not self.message or self.message.lower() in ['halo', 'hai', 'hello', 'hi']


@dataclass
class ResetRequestDTO:
    """Validated reset request payload."""
    device_token: Optional[str] = None
    session_id: Optional[str] = None

    @classmethod
    def from_request(cls, request):
        json_data = request.get_json(silent=True)
        if not json_data:
            raise DTOValidationError("Request body harus berupa JSON")
        
        device_token = json_data.get('device_token')
        session_id = json_data.get('session_id')

        if not device_token and not session_id:
            raise DTOValidationError(
                "device_token atau session_id harus disediakan"
            )

        return cls(device_token=device_token, session_id=session_id)


# ─── Pagination DTOs ─────────────────────────────────────────────

@dataclass
class PaginationDTO:
    """Validated pagination parameters."""
    page: int = 1
    per_page: int = 20

    @classmethod
    def from_request(cls, request, per_page_key='per_page', default_per_page=20, max_per_page=100):
        """Parse and clamp pagination params from query string."""
        try:
            page = int(request.args.get('page', 1))
        except (ValueError, TypeError):
            raise DTOValidationError("'page' harus berupa angka", "page")

        try:
            per_page = int(request.args.get(per_page_key, default_per_page))
        except (ValueError, TypeError):
            raise DTOValidationError(f"'{per_page_key}' harus berupa angka", per_page_key)

        page = max(1, page)
        per_page = max(1, min(per_page, max_per_page))

        return cls(page=page, per_page=per_page)


@dataclass
class RecommendationQueryDTO:
    """Validated recommendation query parameters."""
    session_id: Optional[str] = None
    device_token: Optional[str] = None
    query: str = ""
    category: Optional[str] = None
    page: int = 1
    per_page: int = 20

    @classmethod
    def from_request(cls, request, per_page_key='per_page', default_per_page=20, max_per_page=100):
        session_id = request.args.get('session_id')
        device_token = request.args.get('device_token')
        query = request.args.get('query', '')
        category = request.args.get('category')

        try:
            page = int(request.args.get('page', 1))
        except (ValueError, TypeError):
            raise DTOValidationError("'page' harus berupa angka", "page")

        try:
            per_page = int(request.args.get(per_page_key, default_per_page))
        except (ValueError, TypeError):
            raise DTOValidationError(f"'{per_page_key}' harus berupa angka", per_page_key)

        page = max(1, page)
        per_page = max(1, min(per_page, max_per_page))

        return cls(
            session_id=session_id,
            device_token=device_token,
            query=query,
            category=category,
            page=page,
            per_page=per_page,
        )


@dataclass
class PreferenceQueryDTO:
    """Validated preference query parameters."""
    device_token: Optional[str] = None
    session_id: Optional[str] = None
    limit: int = 100

    @classmethod
    def from_request(cls, request):
        device_token = request.args.get('device_token')
        session_id = request.args.get('session_id')

        try:
            limit = int(request.args.get('limit', 100))
        except (ValueError, TypeError):
            raise DTOValidationError("'limit' harus berupa angka", "limit")

        limit = max(1, min(limit, 500))

        return cls(device_token=device_token, session_id=session_id, limit=limit)
