from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Simple test endpoint to verify deployments work"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        response = {
            "test": "DEPLOYMENT TEST SUCCESSFUL",
            "timestamp": datetime.now().isoformat(),
            "deployment_marker": "2024-06-19-FORCE-TEST"
        }

        self.wfile.write(json.dumps(response, indent=2).encode())