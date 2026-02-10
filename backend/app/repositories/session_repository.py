"""
Repository for UserSession CRUD operations.
"""
from datetime import datetime
from backend.app.extensions import db
from backend.app.models.database import UserSession
from backend.app.utils.logger import get_logger

logger = get_logger("session_repository")


class SessionRepository:
    """Data access layer for user sessions"""

    @staticmethod
    def create(session_id, device_token=None):
        """Create a new user session"""
        session = UserSession(
            session_id=session_id,
            device_token=device_token,
            is_active=True
        )
        db.session.add(session)
        db.session.commit()
        return session

    @staticmethod
    def find_by_session_id(session_id):
        """Find session by session_id"""
        return UserSession.query.filter_by(session_id=session_id).first()

    @staticmethod
    def find_active_by_device_token(device_token):
        """Find active sessions for a device token"""
        return UserSession.query.filter_by(
            device_token=device_token,
            is_active=True
        ).order_by(UserSession.last_activity.desc()).first()

    @staticmethod
    def update_activity(session_id):
        """Update last_activity timestamp"""
        session = UserSession.query.filter_by(session_id=session_id).first()
        if session:
            session.last_activity = datetime.utcnow()
            db.session.commit()
        return session

    @staticmethod
    def deactivate(session_id):
        """Deactivate a session"""
        session = UserSession.query.filter_by(session_id=session_id).first()
        if session:
            session.is_active = False
            db.session.commit()
        return session
