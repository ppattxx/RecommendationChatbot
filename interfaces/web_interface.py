import sys
from pathlib import Path
from flask import Flask, render_template, request, jsonify, session, Response
from flask_cors import CORS
import uuid
from datetime import datetime
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
from services.chatbot_service import ChatbotService
from services.device_token_service import DeviceTokenService
from utils.logger import get_logger
from config.settings import API_CONFIG, RESTAURANTS_ENTITAS_CSV
logger = get_logger("web_interface")
TEMPLATES_DIR = Path(__file__).parent / "templates"
app = Flask(__name__, template_folder=str(TEMPLATES_DIR))
app.secret_key = "chatbot_recommendation_secret_key_2024"
CORS(app)
chatbot_service = None
device_token_service = None
def initialize_chatbot():
    global chatbot_service, device_token_service
    try:
        logger.info("Initializing chatbot service for web interface...")
        chatbot_service = ChatbotService(str(RESTAURANTS_ENTITAS_CSV))
        device_token_service = DeviceTokenService()
        logger.info("Chatbot service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize chatbot service: {e}")
        raise
@app.route('/')
def index():
    from flask import redirect, url_for
    logger.info("Redirecting root URL to /chat")
    return redirect(url_for('chat_page'))

@app.route('/index')
def index_page():
    try:
        logger.info("Rendering index.html template")
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering index template: {e}")
        return f"Error rendering template: {e}", 500
@app.route('/chat')
def chat_page():
    try:
        logger.info("Rendering chat.html template")
        return render_template('chat.html')
    except Exception as e:
        logger.error(f"Error rendering chat template: {e}")
        return f"Error rendering template: {e}", 500
@app.route('/test')
def test_page():
    try:
        with open('simple_chat_test.html', 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error loading test page: {e}", 500
@app.route('/api/health')
def health_check():
    try:
        stats = chatbot_service.get_statistics() if chatbot_service else {}
        session_stats = chatbot_service.session_manager.get_session_stats() if chatbot_service else {}
        
        return jsonify({
            'status': 'healthy',
            'version': '1.0.0',
            'service': 'chatbot_recommendation',
            'timestamp': datetime.now().isoformat(),
            'statistics': stats,
            'session_stats': session_stats
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/session_info')
def get_session_info():
    try:
        session_id = session.get('session_id')
        device_token = session.get('device_token')
        
        if not session_id or not device_token:
            return jsonify({
                'success': False,
                'error': 'No active session'
            }), 400
        
        # Get session data
        session_data = chatbot_service.session_manager.get_session(session_id)
        
        if not session_data:
            return jsonify({
                'success': False,
                'error': 'Session not found or expired'
            }), 404
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'device_token': device_token,
            'created_at': session_data['created_at'],
            'last_activity': session_data['last_activity'],
            'message_count': len(session_data['messages']),
            'is_active': session_data.get('is_active', False)
        })
        
    except Exception as e:
        logger.error(f"Error getting session info: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get session info'
        }), 500

@app.route('/api/generate_device_token', methods=['POST'])
def generate_device_token():
    try:
        data = request.get_json() or {}
        user_agent = request.headers.get('User-Agent', '')
        ip_address = request.remote_addr
        
        screen_info = data.get('screen_info', {})
        timezone_info = data.get('timezone_info', {})
        language_info = data.get('language_info', {})
        
        additional_info = {
            'screen_resolution': screen_info.get('resolution'),
            'screen_color_depth': screen_info.get('color_depth'),
            'timezone': timezone_info.get('timezone'),
            'timezone_offset': timezone_info.get('offset'),
            'languages': language_info.get('languages', []),
            'platform_info': data.get('platform_info', {})
        }
        
        device_token = device_token_service.generate_device_token(
            user_agent=user_agent,
            ip_address=ip_address, 
            additional_info=additional_info
        )
        
        session['device_token'] = device_token
        
        logger.info(f"Generated device token: {device_token}")
        
        return jsonify({
            'success': True,
            'device_token': device_token,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error generating device token: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate device token'
        }), 500

@app.route('/api/start_conversation', methods=['POST'])
def start_conversation():
    try:
        device_token = session.get('device_token')
        if not device_token:
            user_agent = request.headers.get('User-Agent', '')
            ip_address = request.remote_addr or 'unknown'
            
            device_token = device_token_service.generate_device_token(
                user_agent=user_agent,
                ip_address=ip_address
            )
            session['device_token'] = device_token
            logger.info(f"Generated new device token: {device_token}")
        else:
            device_token_service.update_token_activity(device_token)
        
        user_history = device_token_service.get_or_create_user_history(device_token)
        user_preferences = device_token_service.get_user_preferences(device_token)
        
        session_id, greeting = chatbot_service.start_conversation(device_token, device_token)
        session['session_id'] = session_id
        
        if user_history.get('interaction_stats', {}).get('total_sessions', 0) > 0:
            total_sessions = user_history['interaction_stats']['total_sessions']
            
            if "Selamat datang kembali! Mari lanjutkan percakapan kita." in greeting:
                greeting = f"Sesi dilanjutkan! Ini adalah sesi ke-{total_sessions + 1} Anda.\n\n{greeting}"
            else:
                greeting = f"Selamat datang kembali! Ini adalah sesi ke-{total_sessions + 1} Anda.\n\n{greeting}"
            
            if user_preferences.get('preferred_cuisines'):
                cuisines = ', '.join(user_preferences['preferred_cuisines'][:3])
                greeting += f"\n\nSaya ingat Anda suka: {cuisines}"
        
        logger.info(f"Started/continued conversation for device {device_token}, session {session_id}")
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'device_token': device_token,
            'greeting': greeting
        })
    except Exception as e:
        logger.error(f"Error starting conversation: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to start conversation'
        }), 500
@app.route('/api/send_message', methods=['POST'])
def send_message():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        if not user_message:
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400
            
        device_token = session.get('device_token')
        session_id = session.get('session_id')
        
        if not session_id or not device_token:
            if not device_token:
                device_token = f"dev_{str(uuid.uuid4().hex[:16])}"
                session['device_token'] = device_token
            
            session_id, greeting = chatbot_service.start_conversation(device_token)
            session['session_id'] = session_id
            
        bot_response = chatbot_service.process_message(user_message, session_id)
        
        try:
            current_session = chatbot_service.sessions.get(session_id, {})
            messages = current_session.get('messages', [])
            
            device_token_service.add_chat_session(device_token, {
                'session_id': session_id,
                'messages': messages[-10:],  
                'recommendations': [],  
                'feedback': {}
            })
        except Exception as e:
            logger.error(f"Error saving to device history: {e}")
        
        logger.info(f"Device {device_token} sent: {user_message}")
        
        return jsonify({
            'success': True,
            'response': bot_response,
            'device_token': device_token,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to process message'
        }), 500

@app.route('/api/send_message_stream', methods=['POST'])
def send_message_stream():
    """Stream bot response word by word for typing effect"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        if not user_message:
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400
            
        device_token = session.get('device_token')
        session_id = session.get('session_id')
        
        if not session_id or not device_token:
            if not device_token:
                device_token = f"dev_{str(uuid.uuid4().hex[:16])}"
                session['device_token'] = device_token
            
            session_id, greeting = chatbot_service.start_conversation(device_token)
            session['session_id'] = session_id
        
        def generate():
            import time
            import json
            
            bot_response = chatbot_service.process_message(user_message, session_id)
            
            try:
                current_session = chatbot_service.sessions.get(session_id, {})
                messages = current_session.get('messages', [])
                
                device_token_service.add_chat_session(device_token, {
                    'session_id': session_id,
                    'messages': messages[-10:],  
                    'recommendations': bot_response,  
                    'feedback': {}
                })
            except Exception as e:
                logger.error(f"Error saving to device history: {e}")
            
            words = bot_response.split(' ')
            accumulated_text = ""
            
            for i, word in enumerate(words):
                accumulated_text += word
                if i < len(words) - 1:
                    accumulated_text += " "
                
                data_chunk = {
                    'text': accumulated_text,
                    'word': word,
                    'is_complete': i == len(words) - 1,
                    'session_id': session_id,
                    'device_token': device_token
                }
                
                yield f"data: {json.dumps(data_chunk)}\n\n"
                time.sleep(0.05)  
        
        return Response(
            generate(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Cache-Control'
            }
        )
        
    except Exception as e:
        logger.error(f"Error in send_message_stream: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to process streaming message'
        }), 500

@app.route('/api/user_preferences')
def get_user_preferences():
    try:
        device_token = session.get('device_token')
        if not device_token:
            return jsonify({
                'success': False,
                'error': 'No device token found'
            }), 400
        
        preferences = device_token_service.get_user_preferences(device_token)
        stats = device_token_service.get_user_stats(device_token)
        history = device_token_service.get_or_create_user_history(device_token)
        
        return jsonify({
            'success': True,
            'preferences': preferences,
            'stats': stats,
            'total_sessions': len(history.get('chat_sessions', [])),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting user preferences: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get user preferences'
        }), 500

@app.route('/api/user_history')
def get_user_history():
    try:
        device_token = session.get('device_token')
        if not device_token:
            return jsonify({
                'success': False,
                'error': 'No device token found'
            }), 400
        
        history = device_token_service.get_or_create_user_history(device_token)
        
        limited_history = {
            'device_token': history.get('device_token'),
            'total_sessions': len(history.get('chat_sessions', [])),
            'preferences': history.get('preferences', {}),
            'stats': history.get('interaction_stats', {}),
            'recent_sessions': history.get('chat_sessions', [])[-5:] 
        }
        
        return jsonify({
            'success': True,
            'history': limited_history,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting user history: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get user history'
        }), 500

@app.route('/api/cleanup_old_tokens', methods=['POST'])
def cleanup_old_tokens():
    try:
        data = request.get_json() or {}
        admin_key = data.get('admin_key')
        
        if admin_key != "cleanup_admin_2024":
            return jsonify({
                'success': False,
                'error': 'Unauthorized'
            }), 403
        
        days_threshold = data.get('days_threshold', 90)
        device_token_service.cleanup_old_tokens(days_threshold)
        
        return jsonify({
            'success': True,
            'message': f'Cleaned up tokens older than {days_threshold} days',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error cleaning up tokens: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to cleanup tokens'
        }), 500

@app.route('/api/analyze_preferences', methods=['POST'])
def analyze_preferences():
    """Analyze and return user preferences based on chat history"""
    try:
        device_token = session.get('device_token')
        if not device_token:
            return jsonify({
                'success': False,
                'error': 'Device token not found'
            }), 400
        
        # Analyze preferences from history
        preferences = device_token_service.analyze_user_preferences(device_token)
        
        # Get user history stats
        user_history = device_token_service.get_or_create_user_history(device_token)
        stats = user_history.get('interaction_stats', {})
        
        return jsonify({
            'success': True,
            'preferences': preferences,
            'stats': {
                'total_sessions': stats.get('total_sessions', 0),
                'total_messages': stats.get('total_messages', 0),
                'favorite_restaurants': stats.get('favorite_restaurants', [])
            },
            'analyzed_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error analyzing preferences: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to analyze preferences'
        }), 500

@app.route('/api/reset_device_token', methods=['POST'])
def reset_device_token():
    try:
        if 'device_token' in session:
            old_token = session['device_token']
            del session['device_token']
            logger.info(f"Reset device token: {old_token}")
        
        return jsonify({
            'success': True,
            'message': 'Device token reset. New token will be generated on next request.',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error resetting device token: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to reset device token'
        }), 500

def run_web_interface():
    try:
        initialize_chatbot()
        config = API_CONFIG
        chat_url = f"http://{config['host']}:{config['port']}/chat"
        
        app.run(
            host=config['host'],
            port=config['port'],
            debug=config['debug']
        )
    except Exception as e:
        logger.error(f"Failed to run web interface: {e}")
        print(f"Error starting web interface: {e}")
        sys.exit(1)
if __name__ == '__main__':
    run_web_interface()