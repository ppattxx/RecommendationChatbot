"""
API Routes untuk Chat functionality
Endpoint: POST /api/chat
"""
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from flask import Blueprint, request, jsonify
from datetime import datetime
from backend.models.database import db, ChatHistory, UserSession
from services.chatbot_service import ChatbotService
from utils.logger import get_logger

logger = get_logger("chat_routes")

chat_bp = Blueprint('chat', __name__)

# Initialize chatbot service (singleton pattern)
chatbot_service = None

def get_chatbot_service():
    """Get or create chatbot service instance"""
    global chatbot_service
    if chatbot_service is None:
        chatbot_service = ChatbotService()
        logger.info("Chatbot service initialized")
    return chatbot_service


@chat_bp.route('/chat', methods=['POST'])
def chat():
    """
    Handle chat messages from user
    
    Request Body:
    {
        "message": "pizza enak di Kuta",
        "session_id": "optional-session-id",
        "device_token": "optional-device-token"
    }
    
    Response:
    {
        "success": true,
        "data": {
            "bot_response": "...",
            "session_id": "...",
            "timestamp": "..."
        }
    }
    """
    try:
        # Validasi request
        if not request.json:
            return jsonify({
                'success': False,
                'error': 'Request body harus berupa JSON'
            }), 400
        
        user_message = request.json.get('message', '').strip()
        session_id = request.json.get('session_id')
        device_token = request.json.get('device_token')
        
        if not user_message:
            return jsonify({
                'success': False,
                'error': 'Message tidak boleh kosong'
            }), 400
        
        # Get chatbot service
        chatbot = get_chatbot_service()
        
        # Jika tidak ada session_id, buat session baru
        if not session_id:
            session_id, greeting = chatbot.start_conversation(device_token=device_token)
            
            # Simpan session ke database
            new_session = UserSession(
                session_id=session_id,
                device_token=device_token,
                created_at=datetime.utcnow(),
                last_activity=datetime.utcnow(),
                is_active=True
            )
            db.session.add(new_session)
            db.session.commit()
            
            logger.info(f"New session created: {session_id}")
            
            return jsonify({
                'success': True,
                'data': {
                    'bot_response': greeting,
                    'session_id': session_id,
                    'timestamp': datetime.utcnow().isoformat(),
                    'is_new_session': True
                }
            }), 200
        
        # Update last activity
        session = UserSession.query.filter_by(session_id=session_id).first()
        if session:
            session.last_activity = datetime.utcnow()
            db.session.commit()
        
        # Process message dengan chatbot
        bot_response = chatbot.process_message(user_message, session_id)
        
        # Extract entities untuk analisis (optional)
        intent, entities = chatbot._extract_intent_and_entities(user_message)
        
        # Simpan ke database
        chat_record = ChatHistory(
            session_id=session_id,
            device_token=device_token,
            user_message=user_message,
            bot_response=bot_response,
            timestamp=datetime.utcnow(),
            extracted_cuisine=', '.join(entities.get('cuisine', [])) or None,
            extracted_location=', '.join(entities.get('location', [])) or None,
            extracted_mood=', '.join(entities.get('mood', [])) or None,
            extracted_price=', '.join(entities.get('price', [])) or None
        )
        db.session.add(chat_record)
        db.session.commit()
        
        logger.info(f"Chat processed - Session: {session_id}, User: {user_message[:50]}")
        
        return jsonify({
            'success': True,
            'data': {
                'bot_response': bot_response,
                'session_id': session_id,
                'timestamp': datetime.utcnow().isoformat(),
                'is_new_session': False
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing chat: {e}")
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500


@chat_bp.route('/chat/history/<session_id>', methods=['GET'])
def get_chat_history(session_id):
    """
    Get chat history untuk session tertentu
    
    Response:
    {
        "success": true,
        "data": {
            "session_id": "...",
            "messages": [...]
        }
    }
    """
    try:
        history = ChatHistory.query.filter_by(session_id=session_id).order_by(ChatHistory.timestamp).all()
        
        messages = []
        for record in history:
            messages.append({
                'user_message': record.user_message,
                'bot_response': record.bot_response,
                'timestamp': record.timestamp.isoformat()
            })
        
        return jsonify({
            'success': True,
            'data': {
                'session_id': session_id,
                'message_count': len(messages),
                'messages': messages
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
