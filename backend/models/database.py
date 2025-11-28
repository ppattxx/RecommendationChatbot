"""
Database models untuk Chatbot menggunakan SQLAlchemy
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ChatHistory(db.Model):
    """Model untuk menyimpan history percakapan user"""
    __tablename__ = 'chat_history'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False, index=True)
    device_token = db.Column(db.String(100), nullable=True, index=True)
    user_message = db.Column(db.Text, nullable=False)
    bot_response = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Kolom tambahan untuk analisis
    extracted_cuisine = db.Column(db.String(100), nullable=True)
    extracted_location = db.Column(db.String(100), nullable=True)
    extracted_mood = db.Column(db.String(100), nullable=True)
    extracted_price = db.Column(db.String(50), nullable=True)
    
    def __repr__(self):
        return f'<ChatHistory {self.id}: {self.session_id}>'
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'device_token': self.device_token,
            'user_message': self.user_message,
            'bot_response': self.bot_response,
            'timestamp': self.timestamp.isoformat(),
            'extracted_cuisine': self.extracted_cuisine,
            'extracted_location': self.extracted_location,
            'extracted_mood': self.extracted_mood,
            'extracted_price': self.extracted_price
        }


class UserSession(db.Model):
    """Model untuk tracking user sessions"""
    __tablename__ = 'user_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    device_token = db.Column(db.String(100), nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<UserSession {self.session_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'device_token': self.device_token,
            'created_at': self.created_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'is_active': self.is_active
        }
