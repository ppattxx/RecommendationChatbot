import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from utils.logger import get_logger

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
        
        greeting = "Halo! Saya siap membantu Anda mencari restoran yang pas!\\n\\nCeritakan apa yang Anda inginkan, misalnya:\\n- 'Cari pizza enak di Kuta'\\n- 'Restoran seafood murah'\\n- 'Tempat romantis untuk dinner'"
        
        logger.info(f"Created new session {session_id} for device {device_token}")
        return session_id, greeting
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        if session_id in self.memory_sessions:
            return self.memory_sessions[session_id]
        
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
        
        # Get fresh history data to avoid overwriting recent updates (like preferences)
        history_data = self.device_token_service.get_or_create_user_history(device_token)
        
        new_message = {
            'user': user_message,
            'timestamp': datetime.now().isoformat()
        }
        
        session_data['messages'].append(new_message)
        session_data['recommendations_given'] = bot_response
        
        history_data['interaction_stats']['total_messages'] += 1
        history_data['last_updated'] = datetime.now().isoformat()
        
        # Update the session data in history
        found_session = False
        for chat_session in history_data.get('chat_sessions', []):
            if chat_session.get('session_id') == session_id:
                chat_session['messages'] = session_data['messages']
                chat_session['recommendations_given'] = bot_response
                chat_session['timestamp'] = datetime.now().isoformat()
                found_session = True
                break
        
        if not found_session:
            # Add new session if not found
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
        
        # Update memory session with fresh data
        session_info['history_data'] = history_data
        self.memory_sessions[session_id] = session_info
        
        logger.debug(f"Updated session {session_id} with new message")
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
                    logger.info(f"Cleaned up {cleaned_count} old sessions from {history_file}")
                    
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
