from http.server import BaseHTTPRequestHandler
import json
import os
import sys

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Debug endpoint to check environment"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Check environment
        debug_info = {
            "python_version": sys.version,
            "platform": sys.platform,
            "env_vars": {
                "GEMINI_API_KEY": bool(os.environ.get('GEMINI_API_KEY')),
                "ELEVENLABS_API_KEY": bool(os.environ.get('ELEVENLABS_API_KEY')),
            },
            "packages": {}
        }
        
        # Check if packages are importable
        try:
            import google.generativeai
            debug_info["packages"]["google-generativeai"] = google.generativeai.__version__
        except Exception as e:
            debug_info["packages"]["google-generativeai"] = f"Error: {str(e)}"
        
        try:
            import elevenlabs
            debug_info["packages"]["elevenlabs"] = elevenlabs.__version__
        except Exception as e:
            debug_info["packages"]["elevenlabs"] = f"Error: {str(e)}"
        
        try:
            import requests
            debug_info["packages"]["requests"] = requests.__version__
        except Exception as e:
            debug_info["packages"]["requests"] = f"Error: {str(e)}"
        
        # Test ElevenLabs client initialization
        try:
            from elevenlabs.client import ElevenLabs
            api_key = os.environ.get('ELEVENLABS_API_KEY', 'sk_fe6faf571491c9b26bef909dce2e19a8e1d7239bf518027b')
            client = ElevenLabs(api_key=api_key)
            debug_info["elevenlabs_client"] = "Initialized successfully"
        except Exception as e:
            debug_info["elevenlabs_client"] = f"Error: {str(e)}"
        
        self.wfile.write(json.dumps(debug_info, indent=2).encode())