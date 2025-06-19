from http.server import BaseHTTPRequestHandler
import json
import os
from datetime import datetime
import time
import base64

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Status endpoint - v5.0 with robust error handling"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        status = {
            "status": "API ONLINE v5.0 - ROBUST",
            "timestamp": datetime.now().isoformat(),
            "environment": {
                "python_version": str(sys.version) if 'sys' in globals() else "unknown",
                "platform": os.name,
                "keys_present": {
                    "gemini": bool(os.environ.get('GEMINI_API_KEY')),
                    "elevenlabs": bool(os.environ.get('ELEVENLABS_API_KEY'))
                }
            },
            "version": "5.0"
        }
        
        self.wfile.write(json.dumps(status, indent=2).encode())

    def do_POST(self):
        """Generate meditation with robust error handling"""
        response_sent = False
        
        try:
            # Read request first
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            
            scenario = data.get('scenario', '').strip()
            duration = int(data.get('duration', 30))
            
            # Send headers immediately
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response_sent = True
            
            # Validate input
            if not scenario or len(scenario) < 10:
                response = {'error': 'Please provide a detailed meditation intention'}
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Get API keys
            gemini_key = os.environ.get('GEMINI_API_KEY', 'AIzaSyAqko3NqGS-GtXhzm8LeiZ3xUEyo_XIqLo')
            elevenlabs_key = os.environ.get('ELEVENLABS_API_KEY', 'sk_fe6faf571491c9b26bef909dce2e19a8e1d7239bf518027b')
            
            # Generate script
            script = self._generate_script(scenario, duration, gemini_key)
            
            # Try audio generation
            audio_data = None
            audio_error = None
            
            if elevenlabs_key:
                audio_data, audio_error = self._generate_audio_safe(script[:2000], elevenlabs_key)  # Limit script length for testing
            
            # Prepare response
            response = {
                'success': True,
                'script': script,
                'scenario': scenario,
                'duration': duration,
                'generated_at': datetime.now().isoformat(),
                'audio_available': bool(audio_data),
                'api_version': '5.0'
            }
            
            if audio_data:
                response['audio_data'] = base64.b64encode(audio_data).decode('utf-8')
                response['audio_size_mb'] = round(len(audio_data) / (1024 * 1024), 2)
            
            if audio_error:
                response['audio_debug'] = audio_error
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            if not response_sent:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
            
            error_response = {
                'error': f'Server Error: {str(e)}',
                'api_version': '5.0'
            }
            self.wfile.write(json.dumps(error_response).encode())

    def do_OPTIONS(self):
        """CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def _generate_script(self, scenario, duration, gemini_key):
        """Generate script with fallback"""
        try:
            if gemini_key:
                import google.generativeai as genai
                genai.configure(api_key=gemini_key)
                
                prompt = f"Create a {duration}-minute meditation script for: {scenario}. Include relaxation, visualization, and affirmations."
                
                model = genai.GenerativeModel('gemini-1.5-pro-latest')
                response = model.generate_content(prompt)
                return response.text.strip()
        except:
            pass
        
        # Fallback script
        return f"""**{duration}-Minute Meditation: {scenario}**

Welcome. Find a comfortable position and close your eyes.

[PAUSE:30]

Take three deep breaths. In... and out...

[PAUSE:45]

As you relax, focus on your intention: {scenario}

[PAUSE:60]

Visualize this reality manifesting in your life right now.

[PAUSE:90]

Feel the emotions of already having achieved this goal.

[PAUSE:120]

You are worthy. You are capable. This is your reality.

[PAUSE:90]

When you're ready, slowly return to awareness and open your eyes.

Namaste."""

    def _generate_audio_safe(self, text, api_key):
        """Generate audio with comprehensive error handling"""
        try:
            # Try to import ElevenLabs
            try:
                from elevenlabs.client import ElevenLabs
            except ImportError as e:
                return None, f"Import error: {str(e)}"
            
            # Initialize client
            try:
                client = ElevenLabs(api_key=api_key)
            except Exception as e:
                return None, f"Client init error: {str(e)}"
            
            # Clean text
            import re
            clean_text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
            clean_text = re.sub(r'\[PAUSE:\d+\]', '... ', clean_text)
            
            # Limit text length
            clean_text = clean_text[:1000]
            
            # Generate audio
            try:
                audio_iterator = client.text_to_speech.convert(
                    voice_id="7nFoun39JV8WgdJ3vGmC",
                    text=clean_text,
                    model_id="eleven_multilingual_v2"
                )
                
                audio_data = b"".join(list(audio_iterator))
                return audio_data, None
                
            except Exception as e:
                return None, f"Audio generation error: {str(e)}"
                
        except Exception as e:
            return None, f"Unexpected error: {str(e)}"

# Add sys import
import sys