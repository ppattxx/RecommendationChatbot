import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from backend.app.utils.logger import get_logger

logger = get_logger("session_manager")

class SessionManager:
    
    def __init__(self, histories_dir: str = "user_histories", device_token_service=None):
        self.histories_dir = Path(histories_dir)
        self.histories_dir.mkdir(exist_ok=True)
        self.session_timeout = timedelta(hours=24) 
        self.memory_sessions = {}
        self.device_token_service = device_token_service  
        
    def create_session(self, device_token: str, user_id: str = None) -> tuple[str, str]:
        import uuid
        
        session_id = f"session_{uuid.uuid4().hex[:8]}"
        
        history_data = self._get_or_create_user_history(device_token)
        
        new_session = {
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'messages': [],
            'recommendations_given': '',
            'user_feedback': {}
        }
        
        history_data['chat_sessions'].append(new_session)
        history_data['last_updated'] = datetime.now().isoformat()
        
        if 'interaction_stats' not in history_data:
            history_data['interaction_stats'] = {
                'total_messages': 0,
                'total_sessions': 0,
                'favorite_restaurants': [],
                'search_patterns': {}
            }
        
        history_data['interaction_stats']['total_sessions'] += 1
        
        self._save_user_history(device_token, history_data)
        
        self.memory_sessions[session_id] = {
            'device_token': device_token,
            'session_data': new_session,
            'history_data': history_data
        }
        
        greeting = (
            "Halo! Saya siap membantu Anda mencari restoran yang pas!\n\n"
            "Ceritakan apa yang Anda inginkan, misalnya:\n"
            "• Cari pizza enak di Kuta\n"
            "• Restoran seafood murah\n"
            "• Tempat romantis untuk dinner"
        )
        
        return session_id, greeting
    
    def _build_session_from_database(self, session_id: str) -> Optional[Dict]:
        try:
            from backend.app.models.database import ChatHistory, UserSession

            session_row = UserSession.query.filter_by(session_id=session_id).first()
            if not session_row:
                return None

            last_activity = session_row.last_activity or session_row.created_at
            if last_activity:
                now = datetime.now(last_activity.tzinfo) if last_activity.tzinfo else datetime.now()
                if now - last_activity > self.session_timeout:
                    return None

            history_data = self._get_user_history(session_row.device_token)
            if not history_data:
                history_data = self._get_or_create_user_history(session_row.device_token)

            rows = (ChatHistory.query
                    .filter_by(session_id=session_id)
                    .order_by(ChatHistory.timestamp.asc())
                    .all())

            messages = []
            recommendations_given = ''
            for row in rows:
                messages.append({
                    'user': row.user_message,
                    'timestamp': row.timestamp.isoformat() if row.timestamp else datetime.now().isoformat(),
                })
                recommendations_given = row.bot_response or recommendations_given

            session_data = {
                'session_id': session_id,
                'timestamp': (last_activity or datetime.now()).isoformat(),
                'messages': messages,
                'recommendations_given': recommendations_given,
                'user_feedback': {},
            }

            existing_sessions = history_data.setdefault('chat_sessions', [])
            found = False
            for idx, chat_session in enumerate(existing_sessions):
                if chat_session.get('session_id') == session_id:
                    existing_sessions[idx] = session_data
                    found = True
                    break
            if not found:
                existing_sessions.append(session_data)

            if 'interaction_stats' not in history_data:
                history_data['interaction_stats'] = {
                    'total_messages': 0,
                    'total_sessions': len(existing_sessions),
                    'favorite_restaurants': [],
                    'search_patterns': {},
                }
            history_data['interaction_stats']['total_messages'] = max(
                history_data['interaction_stats'].get('total_messages', 0),
                len(messages),
            )
            history_data['interaction_stats']['total_sessions'] = max(
                history_data['interaction_stats'].get('total_sessions', 0),
                len(existing_sessions),
            )
            history_data['last_updated'] = datetime.now().isoformat()

            session_info = {
                'device_token': session_row.device_token,
                'session_data': session_data,
                'history_data': history_data,
            }
            self.memory_sessions[session_id] = session_info
            return session_info

        except Exception as e:
            logger.error(f"Error rebuilding session {session_id} from database: {e}")
            return None


    def get_session(self, session_id: str) -> Optional[Dict]:
        if session_id in self.memory_sessions:
            return self.memory_sessions[session_id]
        
        # Try fast database lookup first. This is required for production
        # deployments where another worker may not have local JSON cache files.
        db_session = self._build_session_from_database(session_id)
        if db_session:
            return db_session
        
        
        # Fallback to scanning all history files
        for history_file in self.histories_dir.glob("*_history.json"):
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    history_data = json.load(f)
                
                for session in history_data.get('chat_sessions', []):
                    if session.get('session_id') == session_id:
                        session_time = datetime.fromisoformat(session['timestamp'])
                        if datetime.now() - session_time > self.session_timeout:
                            return None
                        
                        device_token = history_data['device_token']
                        self.memory_sessions[session_id] = {
                            'device_token': device_token,
                            'session_data': session,
                            'history_data': history_data
                        }
                        return self.memory_sessions[session_id]
                        
            except Exception as e:
                logger.error(f"Error loading history file {history_file}: {e}")
                continue
        
        return None
    
    def update_session(self, session_id: str, user_message: str, bot_response: str):
        session_info = self.get_session(session_id)
        if not session_info:
            logger.error(f"Session {session_id} not found")
            return False
        
        device_token = session_info['device_token']
        session_data = session_info['session_data']
        
        history_data = self.device_token_service.get_or_create_user_history(device_token)
        
        new_message = {
            'user': user_message,
            'timestamp': datetime.now().isoformat()
        }
        
        session_data['messages'].append(new_message)
        session_data['recommendations_given'] = bot_response
        
        history_data['interaction_stats']['total_messages'] += 1
        history_data['last_updated'] = datetime.now().isoformat()
        
        found_session = False
        for chat_session in history_data.get('chat_sessions', []):
            if chat_session.get('session_id') == session_id:
                chat_session['messages'] = session_data['messages']
                chat_session['recommendations_given'] = bot_response
                chat_session['timestamp'] = datetime.now().isoformat()
                found_session = True
                break
        
        if not found_session:

            if 'chat_sessions' not in history_data:
                history_data['chat_sessions'] = []
            history_data['chat_sessions'].append({
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'messages': session_data['messages'],
                'recommendations_given': bot_response,
                'user_feedback': {}
            })
        
        self._save_user_history(device_token, history_data)
        
        session_info['history_data'] = history_data
        self.memory_sessions[session_id] = session_info
        
        return True
    
    def get_active_session_for_device(self, device_token: str) -> Optional[str]:
        for session_id, session_info in self.memory_sessions.items():
            if session_info['device_token'] == device_token:
                session_time = datetime.fromisoformat(session_info['session_data']['timestamp'])
                if datetime.now() - session_time <= self.session_timeout:
                    return session_id
        
        history_data = self._get_user_history(device_token)
        if history_data and 'chat_sessions' in history_data:
            recent_sessions = sorted(
                history_data['chat_sessions'],
                key=lambda x: x['timestamp'],
                reverse=True
            )
            
            if recent_sessions:
                latest_session = recent_sessions[0]
                session_time = datetime.fromisoformat(latest_session['timestamp'])
                if datetime.now() - session_time <= self.session_timeout:
                    session_id = latest_session['session_id']
                    self.memory_sessions[session_id] = {
                        'device_token': device_token,
                        'session_data': latest_session,
                        'history_data': history_data
                    }
                    return session_id
        
        return None
    
    def _get_or_create_user_history(self, device_token: str) -> Dict:
        history_data = self._get_user_history(device_token)
        if history_data:
            return history_data
        
        new_history = {
            'device_token': device_token,
            'created_at': datetime.now().isoformat(),
            'chat_sessions': [],
            'preferences': {
                'preferred_cuisines': [],
                'preferred_locations': [],
                'price_preference': None,
                'mood_preferences': [],
                'dietary_restrictions': []
            },
            'interaction_stats': {
                'total_messages': 0,
                'total_sessions': 0,
                'favorite_restaurants': [],
                'search_patterns': {}
            },
            'last_updated': datetime.now().isoformat()
        }
        
        return new_history
    
    def _get_user_history(self, device_token: str) -> Optional[Dict]:
        history_file = self.histories_dir / f"{device_token}_history.json"
        if history_file.exists():
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading user history {device_token}: {e}")
        return None
    
    def _save_user_history(self, device_token: str, history_data: Dict):
        try:
            history_file = self.histories_dir / f"{device_token}_history.json"
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving user history {device_token}: {e}")
    
    def cleanup_expired_sessions(self):
        cutoff_time = datetime.now() - timedelta(days=30)
        
        for history_file in self.histories_dir.glob("*_history.json"):
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    history_data = json.load(f)
                
                original_count = len(history_data.get('chat_sessions', []))
                history_data['chat_sessions'] = [
                    session for session in history_data.get('chat_sessions', [])
                    if datetime.fromisoformat(session['timestamp']) > cutoff_time
                ]
                
                cleaned_count = original_count - len(history_data['chat_sessions'])
                if cleaned_count > 0:
                    history_data['last_updated'] = datetime.now().isoformat()
                    with open(history_file, 'w', encoding='utf-8') as f:
                        json.dump(history_data, f, indent=2, ensure_ascii=False)
                    
            except Exception as e:
                logger.error(f"Error cleaning up history file {history_file}: {e}")
    
    def get_session_stats(self) -> Dict[str, Any]:
        total_sessions = 0
        total_histories = 0
        
        for history_file in self.histories_dir.glob("*_history.json"):
            total_histories += 1
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    history_data = json.load(f)
                    total_sessions += len(history_data.get('chat_sessions', []))
            except Exception as e:
                logger.error(f"Error reading history file {history_file}: {e}")
        
        return {
            'total_user_histories': total_histories,
            'total_sessions': total_sessions,
            'active_memory_sessions': len(self.memory_sessions),
            'session_timeout_hours': self.session_timeout.total_seconds() / 3600
        }
