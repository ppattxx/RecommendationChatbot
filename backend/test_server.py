"""Simple test server to verify Flask works"""
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/test')
def test():
    return jsonify({'status': 'ok', 'message': 'Test server working'})

@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy', 'message': 'Backend is running'})

if __name__ == '__main__':
    print("Starting test server on port 8080...")
    app.run(host='127.0.0.1', port=8080, debug=False, use_reloader=False)
