"""
Chat Controller – handles request validation, calls services, and formats responses.
Uses: DTO validation, @handle_errors decorator, DI via container.
"""
from datetime import datetime
from pathlib import Path
from flask import request, jsonify, current_app

from backend.app.extensions import db
from backend.app.models.database import ChatHistory, UserSession
from backend.app.utils.dto import ChatRequestDTO, ResetRequestDTO, PaginationDTO
from backend.app.utils.error_handlers import handle_errors
from backend.app.utils.logger import get_logger

logger = get_logger("chat_controller")


# ─── Controller functions ────────────────────────────────────────

@handle_errors
def handle_chat():
    """Process a chat message and return bot response."""
    dto = ChatRequestDTO.from_request(request)
    chatbot = current_app.container.chatbot_service

    # Handle initialization (empty or greeting)
    if dto.is_greeting:
        session_id, greeting = chatbot.start_conversation(device_token=dto.device_token)
        _ensure_session_exists(session_id, dto.device_token)
        return jsonify({
            'success': True,
            'data': {
                'bot_response': greeting,
                'session_id': session_id,
                'timestamp': datetime.utcnow().isoformat(),
                'is_new_session': True
            }
        }), 200

    # Auto-create session if needed
    session_id = dto.session_id
    if not session_id:
        session_id, _ = chatbot.start_conversation(device_token=dto.device_token)

    _update_or_create_session(session_id, dto.device_token)

    # Process message
    bot_response = chatbot.process_message(dto.message, session_id)

    # Extract entities for analytics
    intent, entities = chatbot._extract_intent_and_entities(dto.message)

    # Persist to DB
    chat_record = ChatHistory(
        session_id=session_id,
        device_token=dto.device_token,
        user_message=dto.message,
        bot_response=bot_response,
        timestamp=datetime.utcnow(),
        extracted_cuisine=', '.join(entities.get('cuisine', [])) or None,
        extracted_location=', '.join(entities.get('location', [])) or None,
        extracted_mood=', '.join(entities.get('mood', [])) or None,
        extracted_price=', '.join(entities.get('price', [])) or None,
    )
    db.session.add(chat_record)
    db.session.commit()

    logger.log_user_query(session_id=session_id, query=dto.message, device_token=dto.device_token)

    return jsonify({
        'success': True,
        'data': {
            'bot_response': bot_response,
            'session_id': session_id,
            'timestamp': datetime.utcnow().isoformat(),
            'is_new_session': False
        }
    }), 200


@handle_errors
def handle_get_history(session_id):
    """Return paginated chat history for a session."""
    pagination = PaginationDTO.from_request(request, default_per_page=50, max_per_page=100)

    total_count = ChatHistory.query.filter_by(session_id=session_id).count()
    total_pages = max((total_count + pagination.per_page - 1) // pagination.per_page, 1)
    page = max(1, min(pagination.page, total_pages))

    history = (ChatHistory.query
               .filter_by(session_id=session_id)
               .order_by(ChatHistory.timestamp.asc())
               .offset((page - 1) * pagination.per_page)
               .limit(pagination.per_page)
               .all())

    messages = [{
        'id': r.id,
        'user_message': r.user_message,
        'bot_response': r.bot_response,
        'timestamp': r.timestamp.isoformat(),
        'extracted_entities': {
            'cuisine': r.extracted_cuisine,
            'location': r.extracted_location,
            'mood': r.extracted_mood,
            'price': r.extracted_price
        }
    } for r in history]

    return jsonify({
        'success': True,
        'data': {
            'session_id': session_id,
            'messages': messages,
            'message_count': len(messages),
            'total_messages': total_count,
            'page': page,
            'per_page': pagination.per_page,
            'total_pages': total_pages,
            'has_more': page < total_pages
        }
    }), 200


@handle_errors
def handle_get_history_by_device(device_token):
    """Return chat history for all sessions belonging to a device."""
    limit = min(int(request.args.get('limit', 100)), 500)

    sessions = (UserSession.query
                .filter_by(device_token=device_token)
                .order_by(UserSession.last_activity.desc())
                .all())

    session_data = []
    total_messages = 0

    for s in sessions:
        history = (ChatHistory.query
                   .filter_by(session_id=s.session_id)
                   .order_by(ChatHistory.timestamp.asc())
                   .limit(limit)
                   .all())

        msgs = [{
            'user_message': r.user_message,
            'bot_response': r.bot_response,
            'timestamp': r.timestamp.isoformat()
        } for r in history]

        session_data.append({
            'session_id': s.session_id,
            'created_at': s.created_at.isoformat(),
            'last_activity': s.last_activity.isoformat(),
            'is_active': s.is_active,
            'messages': msgs,
            'message_count': len(msgs)
        })
        total_messages += len(msgs)

    return jsonify({
        'success': True,
        'data': {
            'device_token': device_token,
            'sessions': session_data,
            'session_count': len(session_data),
            'total_messages': total_messages
        }
    }), 200


@handle_errors
def handle_reset_history():
    """Delete chat history for a specific user/session."""
    dto = ResetRequestDTO.from_request(request)

    query = ChatHistory.query
    if dto.device_token:
        query = query.filter_by(device_token=dto.device_token)
    elif dto.session_id:
        query = query.filter_by(session_id=dto.session_id)

    count = query.count()
    query.delete()
    if dto.session_id:
        UserSession.query.filter_by(session_id=dto.session_id).delete()
    db.session.commit()

    logger.info(f"Reset history: deleted {count} records")

    return jsonify({
        'success': True,
        'data': {'deleted_count': count, 'message': f'Berhasil menghapus {count} riwayat chat'}
    }), 200


@handle_errors
def handle_reset_all():
    """Delete ALL chat history and sessions."""
    chat_count = ChatHistory.query.count()
    session_count = UserSession.query.count()
    ChatHistory.query.delete()
    UserSession.query.delete()
    db.session.commit()

    # Clear in-memory state held by chatbot/session manager.
    try:
        chatbot = current_app.container.chatbot_service
        if hasattr(chatbot, 'sessions') and isinstance(chatbot.sessions, dict):
            chatbot.sessions.clear()
        if hasattr(chatbot, 'session_manager') and hasattr(chatbot.session_manager, 'memory_sessions'):
            chatbot.session_manager.memory_sessions.clear()
    except Exception:
        # Reset should still succeed even if runtime state is not available.
        pass

    # Clear file-based stores so personalization is truly fresh-start.
    deleted_history_files = 0
    deleted_token_files = 0
    candidate_roots = {
        Path.cwd(),
        Path(current_app.root_path).parent,            # backend/
        Path(current_app.root_path).parent.parent,     # project root
    }

    for root in candidate_roots:
        for rel_dir, counter_name in [('user_histories', 'history'), ('device_tokens', 'token')]:
            target_dir = root / rel_dir
            if not target_dir.exists() or not target_dir.is_dir():
                continue
            for file_path in target_dir.glob('*.json'):
                try:
                    file_path.unlink()
                    if counter_name == 'history':
                        deleted_history_files += 1
                    else:
                        deleted_token_files += 1
                except Exception:
                    continue

    logger.warning(f"RESET ALL: Deleted {chat_count} chats and {session_count} sessions")

    return jsonify({
        'success': True,
        'data': {
            'deleted_chats': chat_count,
            'deleted_sessions': session_count,
            'deleted_history_files': deleted_history_files,
            'deleted_token_files': deleted_token_files,
            'message': (
                f'Berhasil reset total: {chat_count} chat, {session_count} sesi, '
                f'{deleted_history_files} file history, {deleted_token_files} file token'
            )
        }
    }), 200


# ─── Internal helpers ────────────────────────────────────────────

def _ensure_session_exists(session_id, device_token):
    """Create a UserSession row if it doesn't already exist."""
    existing = UserSession.query.filter_by(session_id=session_id).first()
    if not existing:
        try:
            db.session.add(UserSession(
                session_id=session_id,
                device_token=device_token,
                created_at=datetime.utcnow(),
                last_activity=datetime.utcnow(),
                is_active=True
            ))
            db.session.commit()
        except Exception:
            db.session.rollback()


def _update_or_create_session(session_id, device_token):
    """Update last_activity or create session if missing."""
    session = UserSession.query.filter_by(session_id=session_id).first()
    if session:
        session.last_activity = datetime.utcnow()
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
    else:
        _ensure_session_exists(session_id, device_token)
