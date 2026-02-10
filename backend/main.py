"""
Entry point for the RecommendationChatbot backend server

Usage:
    python backend/main.py
"""
import sys
from pathlib import Path

# Add project root to sys.path (the ONLY place this is done)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.app import create_app
from backend.config.settings import API_CONFIG

app = create_app()


if __name__ == '__main__':
    print("=" * 50)
    print("  Chatbot Rekomendasi Restoran - Backend")
    print("=" * 50)
    print(f"  Running on http://{API_CONFIG['host']}:{API_CONFIG['port']}")
    print("=" * 50)
    app.run(
        host=API_CONFIG['host'],
        port=API_CONFIG['port'],
        debug=API_CONFIG['debug']
    )
