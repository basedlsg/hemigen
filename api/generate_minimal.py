from http.server import BaseHTTPRequestHandler
import json
import os
from datetime import datetime
import time

# Try importing at module level
try:
    from elevenlabs.client import ElevenLabs
    import google.generativeai as genai
    IMPORTS_OK = True
except Exception as e:
    IMPORTS_OK = False
    IMPORT_ERROR = str(e)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Status endpoint"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        status = {
            "status": "API ONLINE - MINIMAL",
            "imports_ok": IMPORTS_OK,
            "timestamp": datetime.now().isoformat()
        }
        
        if not IMPORTS_OK:
            status["import_error"] = IMPORT_ERROR
            
        self.wfile.write(json.dumps(status, indent=2).encode())

    def do_POST(self):
        """Generate meditation"""
        try:
            # CORS headers FIRST
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            # Read request
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))

            scenario = data.get('scenario', '').strip()
            duration = int(data.get('duration', 30))

            # Simple fallback script
            script = f"""Meditation for: {scenario}
            
Welcome to your {duration}-minute meditation.

[PAUSE:30]

Take a deep breath and relax...

[PAUSE:60]

Focus on your intention: {scenario}

[PAUSE:120]

You are manifesting this reality now.

[PAUSE:60]

When you're ready, slowly open your eyes."""

            # Try audio generation with minimal approach
            audio_data = None
            audio_error = None
            
            if IMPORTS_OK:
                try:
                    api_key = os.environ.get('ELEVENLABS_API_KEY', 'sk_fe6faf571491c9b26bef909dce2e19a8e1d7239bf518027b')
                    
                    # Initialize client
                    client = ElevenLabs(api_key=api_key)
                    
                    # Generate audio for short text
                    test_text = script[:500]  # Limit to 500 chars
                    
                    audio_iterator = client.text_to_speech.convert(
                        voice_id="7nFoun39JV8WgdJ3vGmC",
                        text=test_text,
                        model_id="eleven_multilingual_v2"
                    )
                    
                    audio_data = b"".join(list(audio_iterator))
                    
                except Exception as e:
                    audio_error = str(e)

            # Response
            response = {
                'success': True,
                'script': script,
                'scenario': scenario,
                'duration': duration,
                'audio_available': bool(audio_data),
                'api_version': 'minimal'
            }
            
            if audio_error:
                response['audio_error'] = audio_error
                
            if audio_data:
                import base64
                response['audio_data'] = base64.b64encode(audio_data).decode('utf-8')

            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            error_response = {'error': str(e)}
            self.wfile.write(json.dumps(error_response).encode())

    def do_OPTIONS(self):
        """CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()