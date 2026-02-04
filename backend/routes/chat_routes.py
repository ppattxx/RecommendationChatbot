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
        
        # Generate device_token if not provided
        if not device_token:
            import uuid
            device_token = f"web_{uuid.uuid4().hex[:9]}"
            logger.info(f"Generated device_token: {device_token}")
        
        # Handle initialization case (empty message or greeting)
        if not user_message or user_message.lower() in ['halo', 'hai', 'hello', 'hi']:
            # Get chatbot service
            chatbot = get_chatbot_service()
            
            # Start new conversation
            session_id, greeting = chatbot.start_conversation(device_token=device_token)
            
            # Check apakah session sudah ada di database
            existing_session = UserSession.query.filter_by(session_id=session_id).first()
            
            if not existing_session:
                # Simpan session baru ke database
                try:
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
                except Exception as db_error:
                    # Handle jika session sudah ada (race condition)
                    db.session.rollback()
                    logger.warning(f"Session {session_id} already exists in database: {db_error}")
            else:
                logger.info(f"Using existing session: {session_id}")
            
            return jsonify({
                'success': True,
                'data': {
                    'bot_response': greeting,
                    'session_id': session_id,
                    'timestamp': datetime.utcnow().isoformat(),
                    'is_new_session': True
                }
            }), 200
        
        # Get chatbot service for normal message processing
        chatbot = get_chatbot_service()
        
        # If no session_id provided, create a new session first
        if not session_id:
            session_id, _ = chatbot.start_conversation(device_token=device_token)
            logger.info(f"Auto-created session for direct message: {session_id}")
        
        # Update last activity
        session = UserSession.query.filter_by(session_id=session_id).first()
        if session:
            session.last_activity = datetime.utcnow()
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                logger.warning(f"Failed to update session activity: {e}")
        else:
            # Jika session tidak ada di database, buat session baru
            try:
                new_session = UserSession(
                    session_id=session_id,
                    device_token=device_token,
                    created_at=datetime.utcnow(),
                    last_activity=datetime.utcnow(),
                    is_active=True
                )
                db.session.add(new_session)
                db.session.commit()
                logger.info(f"Created missing session: {session_id}")
            except Exception as e:
                db.session.rollback()
                logger.warning(f"Failed to create missing session: {e}")
        
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
    Get chat history untuk session tertentu dengan pagination
    
    Query Parameters:
    - page: optional, page number (default: 1)
    - per_page: optional, items per page (default: 50, max: 100)
    
    Response:
    {
        "success": true,
        "data": {
            "session_id": "...",
            "messages": [...],
            "message_count": 10,
            "page": 1,
            "per_page": 50,
            "total_pages": 1,
            "has_more": false
        }
    }
    """
    try:
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 50)), 100)
        
        # Get total count first
        total_count = ChatHistory.query.filter_by(session_id=session_id).count()
        total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 1
        
        # Validate page
        if page < 1:
            page = 1
        if page > total_pages:
            page = total_pages
        
        # Get paginated history ordered by timestamp (oldest first for chat display)
        history = ChatHistory.query.filter_by(session_id=session_id)\
            .order_by(ChatHistory.timestamp.asc())\
            .offset((page - 1) * per_page)\
            .limit(per_page)\
            .all()
        
        messages = []
        for record in history:
            messages.append({
                'id': record.id,
                'user_message': record.user_message,
                'bot_response': record.bot_response,
                'timestamp': record.timestamp.isoformat(),
                'extracted_entities': {
                    'cuisine': record.extracted_cuisine,
                    'location': record.extracted_location,
                    'mood': record.extracted_mood,
                    'price': record.extracted_price
                }
            })
        
        return jsonify({
            'success': True,
            'data': {
                'session_id': session_id,
                'messages': messages,
                'message_count': len(messages),
                'total_messages': total_count,
                'page': page,
                'per_page': per_page,
                'total_pages': total_pages,
                'has_more': page < total_pages
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@chat_bp.route('/chat/history/device/<device_token>', methods=['GET'])
def get_chat_history_by_device(device_token):
    """
    Get chat history untuk device tertentu (all sessions)
    Berguna untuk restore history saat user kembali
    
    Query Parameters:
    - limit: optional, max messages to return (default: 100)
    
    Response:
    {
        "success": true,
        "data": {
            "device_token": "...",
            "sessions": [...],
            "total_messages": 50
        }
    }
    """
    try:
        limit = min(int(request.args.get('limit', 100)), 500)
        
        # Get all sessions for this device
        sessions = UserSession.query.filter_by(device_token=device_token)\
            .order_by(UserSession.last_activity.desc())\
            .all()
        
        session_data = []
        total_messages = 0
        
        for session in sessions:
            # Get messages for this session
            history = ChatHistory.query.filter_by(session_id=session.session_id)\
                .order_by(ChatHistory.timestamp.asc())\
                .limit(limit)\
                .all()
            
            messages = []
            for record in history:
                messages.append({
                    'user_message': record.user_message,
                    'bot_response': record.bot_response,
                    'timestamp': record.timestamp.isoformat()
                })
            
            session_data.append({
                'session_id': session.session_id,
                'created_at': session.created_at.isoformat(),
                'last_activity': session.last_activity.isoformat(),
                'is_active': session.is_active,
                'messages': messages,
                'message_count': len(messages)
            })
            total_messages += len(messages)
        
        return jsonify({
            'success': True,
            'data': {
                'device_token': device_token,
                'sessions': session_data,
                'session_count': len(session_data),
                'total_messages': total_messages
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting device chat history: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@chat_bp.route('/chat/reset', methods=['DELETE'])
def reset_chat_history():
    """
    Reset chat history untuk user tertentu
    
    Request Body:
    {
        "device_token": "optional",
        "session_id": "optional"
    }
    
    Response:
    {
        "success": true,
        "data": {
            "deleted_count": 21,
            "message": "Chat history berhasil direset"
        }
    }
    """
    try:
        data = request.get_json()
        device_token = data.get('device_token')
        session_id = data.get('session_id')
        
        if not device_token and not session_id:
            return jsonify({
                'success': False,
                'error': 'device_token atau session_id harus disediakan'
            }), 400
        
        # Build query untuk delete
        query = ChatHistory.query
        
        if device_token:
            query = query.filter_by(device_token=device_token)
        elif session_id:
            query = query.filter_by(session_id=session_id)
        
        # Count sebelum delete
        count = query.count()
        
        # Delete chat history
        query.delete()
        
        # Delete user session jika ada
        if session_id:
            UserSession.query.filter_by(session_id=session_id).delete()
        
        db.session.commit()
        
        logger.info(f"Reset chat history: deleted {count} records for device_token={device_token}, session_id={session_id}")
        
        return jsonify({
            'success': True,
            'data': {
                'deleted_count': count,
                'message': f'Berhasil menghapus {count} riwayat chat'
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error resetting chat history: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@chat_bp.route('/chat/reset-all', methods=['DELETE'])
def reset_all_chat_history():
    """
    Reset SEMUA chat history dari database
    HATI-HATI: Ini akan menghapus semua data!
    
    Response:
    {
        "success": true,
        "data": {
            "deleted_chats": 50,
            "deleted_sessions": 10,
            "message": "Semua history berhasil direset"
        }
    }
    """
    try:
        # Count sebelum delete
        chat_count = ChatHistory.query.count()
        session_count = UserSession.query.count()
        
        # Delete SEMUA data
        ChatHistory.query.delete()
        UserSession.query.delete()
        
        db.session.commit()
        
        logger.warning(f"RESET ALL: Deleted {chat_count} chats and {session_count} sessions")
        
        return jsonify({
            'success': True,
            'data': {
                'deleted_chats': chat_count,
                'deleted_sessions': session_count,
                'message': f'Berhasil menghapus semua {chat_count} riwayat chat dan {session_count} sesi'
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error resetting all chat history: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
