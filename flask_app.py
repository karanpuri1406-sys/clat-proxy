#!/usr/bin/env python3
"""
Multi-AI API Proxy Server for CLAT Mock Test Generator
Proxies requests to Google Gemini and OpenAI APIs
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

# API Keys - Hardcoded for simplicity
GEMINI_API_KEY = 'AIzaSyCWSDV-DUmNeQJPw4chBUBDW3t8avPRhJc'
GEMINI_BASE_URL = 'https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent'

# OpenAI API Key - Hardcoded
OPENAI_API_KEY = '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'
OPENAI_BASE_URL = 'https://api.openai.com/v1/chat/completions'

@app.route('/generate', methods=['POST', 'OPTIONS'])
def generate():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    try:
        data = request.get_json()
        gemini_response = requests.post(
            f'{GEMINI_BASE_URL}?key={GEMINI_API_KEY}',
            headers={'Content-Type': 'application/json'},
            json=data,
            timeout=120
        )
        
        response_json = gemini_response.json()
        
        if 'candidates' in response_json and len(response_json['candidates']) > 0:
            try:
                text_content = response_json['candidates'][0]['content']['parts'][0]['text']
                text_content = text_content.strip().strip('\ufeff')
                response_json['candidates'][0]['content']['parts'][0]['text'] = text_content
            except (KeyError, IndexError):
                pass
        
        return jsonify(response_json), gemini_response.status_code
        
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Request timeout'}), 504
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Network error: {str(e)}'}), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/openai', methods=['POST', 'OPTIONS'])
def openai_proxy():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    try:
        if not OPENAI_API_KEY:
            return jsonify({'error': 'OpenAI API key not configured'}), 400
        
        data = request.get_json()
        openai_response = requests.post(
            OPENAI_BASE_URL,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {OPENAI_API_KEY}'
            },
            json=data,
            timeout=90
        )
        
        return jsonify(openai_response.json()), openai_response.status_code
        
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Request timeout'}), 504
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Network error: {str(e)}'}), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy', 
        'service': 'Multi-AI Proxy',
        'endpoints': {
            '/generate': 'Gemini API proxy',
            '/openai': 'OpenAI API proxy',
            '/health': 'Health check'
        },
        'openai_configured': bool(OPENAI_API_KEY)
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
