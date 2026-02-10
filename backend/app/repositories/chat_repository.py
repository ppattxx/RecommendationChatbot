"""
Repository for ChatHistory CRUD operations.
Separates database access from business logic.
"""
from datetime import datetime
from backend.app.extensions import db
from backend.app.models.database import ChatHistory
from backend.app.utils.logger import get_logger

logger = get_logger("chat_repository")


class ChatRepository:
    """Data access layer for chat history records"""

    @staticmethod
    def create(session_id, device_token, user_message, bot_response,
               extracted_cuisine=None, extracted_location=None,
               extracted_mood=None, extracted_price=None):
        """Create a new chat history record"""
        chat = ChatHistory(
            session_id=session_id,
            device_token=device_token,
            user_message=user_message,
            bot_response=bot_response,
            extracted_cuisine=extracted_cuisine,
            extracted_location=extracted_location,
            extracted_mood=extracted_mood,
            extracted_price=extracted_price
        )
        db.session.add(chat)
        db.session.commit()
        return chat

    @staticmethod
    def find_by_session(session_id, limit=50):
        """Get chat history for a session"""
        return ChatHistory.query.filter_by(
            session_id=session_id
        ).order_by(
            ChatHistory.timestamp.asc()
        ).limit(limit).all()

    @staticmethod
    def find_by_device_token(device_token, limit=100):
        """Get chat history for a device token"""
        return ChatHistory.query.filter_by(
            device_token=device_token
        ).order_by(
            ChatHistory.timestamp.asc()
        ).limit(limit).all()

    @staticmethod
    def find_by_filters(session_id=None, device_token=None, limit=100):
        """Get chat history with optional filters"""
        query = ChatHistory.query
        if device_token:
            query = query.filter_by(device_token=device_token)
        if session_id:
            query = query.filter_by(session_id=session_id)
        return query.order_by(ChatHistory.timestamp.asc()).limit(limit).all()

    @staticmethod
    def count_all():
        """Count total chat history records"""
        from sqlalchemy import func
        return db.session.query(func.count(ChatHistory.id)).scalar()

    @staticmethod
    def count_distinct_sessions():
        """Count distinct sessions"""
        from sqlalchemy import func
        return db.session.query(
            func.count(func.distinct(ChatHistory.session_id))
        ).scalar()

    @staticmethod
    def get_top_entity(column_name):
        """Get most common value for an extracted entity column"""
        from sqlalchemy import func
        column = getattr(ChatHistory, column_name, None)
        if column is None:
            return None
        result = db.session.query(
            column, func.count(column)
        ).filter(
            column.isnot(None)
        ).group_by(column).order_by(
            func.count(column).desc()
        ).first()
        return result[0] if result else None
