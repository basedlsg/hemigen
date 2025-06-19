from http.server import BaseHTTPRequestHandler
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Test ElevenLabs audio generation only"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        result = {
            "test": "ElevenLabs Audio Generation",
            "steps": []
        }
        
        try:
            # Step 1: Check API key
            api_key = os.environ.get('ELEVENLABS_API_KEY', 'sk_fe6faf571491c9b26bef909dce2e19a8e1d7239bf518027b')
            result["steps"].append({"step": "API Key", "status": "OK", "key_length": len(api_key)})
            
            # Step 2: Import library
            from elevenlabs.client import ElevenLabs
            result["steps"].append({"step": "Import ElevenLabs", "status": "OK"})
            
            # Step 3: Initialize client
            client = ElevenLabs(api_key=api_key)
            result["steps"].append({"step": "Initialize Client", "status": "OK"})
            
            # Step 4: Generate short audio
            test_text = "This is a test of the meditation audio generation system."
            audio_iterator = client.text_to_speech.convert(
                voice_id="7nFoun39JV8WgdJ3vGmC",
                text=test_text,
                model_id="eleven_multilingual_v2",
                voice_settings={
                    "stability": 0.75,
                    "similarity_boost": 0.75,
                    "style": 0.5,
                    "use_speaker_boost": True
                }
            )
            
            audio_data = b"".join(list(audio_iterator))
            result["steps"].append({
                "step": "Generate Audio", 
                "status": "OK", 
                "audio_size": len(audio_data)
            })
            
            # Step 5: Encode audio
            import base64
            audio_b64 = base64.b64encode(audio_data).decode('utf-8')
            result["steps"].append({"step": "Encode Audio", "status": "OK"})
            
            result["success"] = True
            result["audio_data"] = audio_b64[:100] + "..."  # Just show a snippet
            result["audio_size_bytes"] = len(audio_data)
            
        except Exception as e:
            import traceback
            result["error"] = str(e)
            result["traceback"] = traceback.format_exc()
            result["success"] = False
        
        self.wfile.write(json.dumps(result, indent=2).encode())