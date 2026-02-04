"""
Flask Backend untuk Chatbot Rekomendasi Restoran
Entry Point utama aplikasi
"""
import sys
import os
from pathlib import Path

# Tambahkan parent directory ke sys.path untuk import modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from flask import Flask, jsonify
from flask_cors import CORS
from backend.models.database import db
from backend.routes.chat_routes import chat_bp
from backend.routes.preferences_routes import preferences_bp
from config.settings import DATABASE_CONFIG

def create_app():
    """Factory function untuk membuat Flask app"""
    app = Flask(__name__)
    
    # Konfigurasi database
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DATABASE_CONFIG['sqlite']['path']}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Konfigurasi JSON output untuk format yang lebih rapi
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    app.json.sort_keys = False  # Maintain order of keys
    
    # Initialize extensions
    db.init_app(app)
    
    # Setup CORS - izinkan frontend untuk akses backend
    CORS(app, resources={
        r"/api/*": {
            "origins": [
                "http://localhost:3000", "http://127.0.0.1:3000",
                "http://localhost:3001", "http://127.0.0.1:3001",
                "http://localhost:5173", "http://127.0.0.1:5173"
            ],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })
    
    # Register blueprints
    app.register_blueprint(chat_bp, url_prefix='/api')
    app.register_blueprint(preferences_bp, url_prefix='/api')
    
    # Import recommendations routes
    from backend.routes.recommendations_routes import recommendations_bp
    app.register_blueprint(recommendations_bp, url_prefix='/api')
    
    # Buat database tables
    with app.app_context():
        db.create_all()
        print("[OK] Database tables created successfully")
    
    # Root endpoint
    @app.route('/')
    def index():
        return jsonify({
            'message': 'Chatbot Rekomendasi Restoran API',
            'version': '1.0.0',
            'endpoints': {
                'chat': '/api/chat',
                'preferences': '/api/user-preferences',
                'recommendations': '/api/recommendations',
                'health': '/api/health'
            }
        })
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'message': 'Backend is running'
        }), 200
    
    return app


if __name__ == '__main__':
    app = create_app()
    print("=" * 60)
    print("Starting Chatbot Recommendation Backend")
    print("=" * 60)
    print("Backend URL: http://localhost:5500")
    print("API Endpoints:")
    print("   - POST /api/chat")
    print("   - GET  /api/user-preferences")
    print("   - GET  /api/health")
    print("=" * 60)
    
    try:
        app.run(
            host='0.0.0.0',
            port=5500,
            debug=False,
            use_reloader=False,
            threaded=True
        )
    except OSError as e:
        if "Address already in use" in str(e) or "access permissions" in str(e):
            print("Port 5500 is busy, trying port 5501...")
            app.run(
                host='0.0.0.0',
                port=5501,
                debug=True,
                use_reloader=False
            )
        else:
            raise e
