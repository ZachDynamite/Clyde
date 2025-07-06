# Save as ctf-backend.py
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import subprocess
import json
import os
import sys

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/')
def index():
    """Serve the main HTML file"""
    try:
        return send_from_directory('.', 'ctf-ai-helper.html')
    except Exception as e:
        return f"Error loading HTML file: {str(e)}", 500

@app.route('/api/generate', methods=['POST'])
def generate():
    """Generate code using Ollama"""
    try:
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({
                'success': False, 
                'error': 'No prompt provided'
            }), 400
        
        prompt = data['prompt']
        
        # Check if it's a test request
        if prompt.lower().strip() == 'test':
            return jsonify({
                'success': True,
                'output': 'Backend connection successful!'
            })
        
        print(f"Received prompt: {prompt}")
        
        # Execute ollama command
        try:
            result = subprocess.run(
                ['ollama', 'run', 'deepseek-coder-v2:latest', prompt],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                return jsonify({
                    'success': True,
                    'output': result.stdout
                })
            else:
                error_msg = result.stderr or 'Unknown error occurred'
                print(f"Ollama error: {error_msg}")
                return jsonify({
                    'success': False,
                    'error': f'Ollama error: {error_msg}'
                }), 500
                
        except subprocess.TimeoutExpired:
            return jsonify({
                'success': False,
                'error': 'Request timed out (5 minutes)'
            }), 500
        except FileNotFoundError:
            return jsonify({
                'success': False,
                'error': 'Ollama not found. Please make sure Ollama is installed and in your PATH.'
            }), 500
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Subprocess error: {str(e)}'
            }), 500
            
    except Exception as e:
        print(f"General error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test if ollama is available
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return jsonify({
                'status': 'healthy',
                'ollama': 'available',
                'models': result.stdout
            })
        else:
            return jsonify({
                'status': 'unhealthy',
                'ollama': 'error',
                'error': result.stderr
            }), 500
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'ollama': 'unavailable',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Check if HTML file exists
    if not os.path.exists('ctf-ai-helper.html'):
        print("ERROR: ctf-ai-helper.html not found in current directory!")
        print("Please make sure both files are in the same directory.")
        sys.exit(1)
    
    # Check if ollama is available
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            print("WARNING: Ollama may not be properly installed or configured.")
            print("Error:", result.stderr)
    except FileNotFoundError:
        print("ERROR: Ollama not found in PATH!")
        print("Please install Ollama from https://ollama.ai/")
        sys.exit(1)
    except Exception as e:
        print(f"WARNING: Could not check Ollama status: {e}")
    
    print("Starting CTF AI Helper backend...")
    print("Make sure deepseek-coder-v2:latest is installed: ollama pull deepseek-coder-v2:latest")
    print("Access the application at: http://localhost:5000")
    
    app.run(debug=True, host='localhost', port=5000)