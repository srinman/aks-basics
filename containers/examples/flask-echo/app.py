"""
Flask Echo Application
A simple REST API that echoes back messages with metadata.
Demonstrates containerizing a Flask application with dependencies.
"""

from flask import Flask, request, jsonify
import os
import socket
import datetime

app = Flask(__name__)

# Configuration from environment variables
PORT = int(os.getenv('PORT', 8080))
APP_VERSION = os.getenv('APP_VERSION', '1.0.0')


@app.route('/')
def home():
    """Home endpoint with API information."""
    return jsonify({
        'service': 'Flask Echo API',
        'version': APP_VERSION,
        'framework': 'Flask',
        'endpoints': {
            '/': 'API information',
            '/echo': 'POST - Echo message with metadata',
            '/health': 'Health check endpoint',
            '/info': 'Container information'
        }
    })


@app.route('/echo', methods=['POST'])
def echo():
    """
    Echo endpoint that returns the message with metadata.
    
    Request body:
    {
        "message": "Your message here"
    }
    
    Response:
    {
        "echo": "Your message here",
        "timestamp": "2026-01-01T12:00:00",
        "hostname": "container-id",
        "client_ip": "192.168.1.1"
    }
    """
    data = request.get_json()
    
    if not data or 'message' not in data:
        return jsonify({
            'error': 'Missing "message" field in request body'
        }), 400
    
    response = {
        'echo': data['message'],
        'timestamp': datetime.datetime.now().isoformat(),
        'hostname': socket.gethostname(),
        'client_ip': request.remote_addr,
        'metadata': {
            'framework': 'Flask',
            'version': APP_VERSION,
            'python_version': os.sys.version.split()[0]
        }
    }
    
    return jsonify(response)


@app.route('/health')
def health():
    """Health check endpoint for container orchestration."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.datetime.now().isoformat(),
        'hostname': socket.gethostname()
    })


@app.route('/info')
def info():
    """Container and environment information."""
    return jsonify({
        'container': {
            'hostname': socket.gethostname(),
            'python_version': os.sys.version.split()[0]
        },
        'application': {
            'framework': 'Flask',
            'version': APP_VERSION,
            'port': PORT
        },
        'environment': {
            key: value for key, value in os.environ.items()
            if key.startswith('APP_') or key in ['PORT', 'HOSTNAME']
        }
    })


if __name__ == '__main__':
    print(f"Starting Flask Echo API v{APP_VERSION} on port {PORT}")
    print(f"Hostname: {socket.gethostname()}")
    print(f"Python version: {os.sys.version.split()[0]}")
    
    # Run the application
    # Use 0.0.0.0 to accept connections from outside the container
    app.run(host='0.0.0.0', port=PORT, debug=False)
