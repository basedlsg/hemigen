from http.server import BaseHTTPRequestHandler
import json
import os
from datetime import datetime

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Status endpoint - NEW VERSION 3.0"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Check environment variables
        gemini_key = os.environ.get('GEMINI_API_KEY')
        elevenlabs_key = os.environ.get('ELEVENLABS_API_KEY')
        
        status = {
            "status": "API ONLINE v3.0",
            "timestamp": datetime.now().isoformat(),
            "environment_check": {
                "gemini_key_set": bool(gemini_key),
                "gemini_key_preview": gemini_key[:10] + "..." if gemini_key else "NOT SET",
                "elevenlabs_key_set": bool(elevenlabs_key),
                "elevenlabs_key_preview": elevenlabs_key[:10] + "..." if elevenlabs_key else "NOT SET"
            },
            "ready_for_generation": bool(gemini_key),
            "version": "3.0"
        }
        
        self.wfile.write(json.dumps(status, indent=2).encode())

    def do_POST(self):
        """Generate meditation - WORKING VERSION"""
        try:
            print("=== API v3.0 POST REQUEST ===")
            
            # CORS headers
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            # Parse request
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            scenario = data.get('scenario', '').strip()
            duration = int(data.get('duration', 25))
            
            print(f"NEW API v3.0 - Scenario: {scenario[:30]}... Duration: {duration}")
            
            # Basic validation
            if not scenario or len(scenario) < 10:
                print("Validation failed - scenario too short")
                response = {'error': 'Please provide a detailed meditation intention (at least 10 characters)'}
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Generate meditation script (fallback version)
            script = self.create_meditation_script(scenario, duration)
            print(f"Script created: {len(script)} characters")
            
            # Try ElevenLabs if available
            audio_sample = None
            elevenlabs_key = os.environ.get('ELEVENLABS_API_KEY')
            
            if elevenlabs_key:
                try:
                    print("Attempting ElevenLabs generation...")
                    audio_sample = self.generate_elevenlabs_sample(script, elevenlabs_key)
                    print(f"Audio sample: {len(audio_sample) if audio_sample else 0} bytes")
                except Exception as e:
                    print(f"ElevenLabs failed: {e}")
            
            # Success response
            response = {
                'success': True,
                'script': script,
                'scenario': scenario,
                'duration': duration,
                'generated_at': datetime.now().isoformat(),
                'message': 'NEW API v3.0 - Meditation generated successfully!',
                'audio_available': bool(audio_sample),
                'api_version': '3.0'
            }
            
            if audio_sample:
                import base64
                response['audio_data'] = base64.b64encode(audio_sample).decode('utf-8')
                response['message'] = 'NEW API v3.0 - Meditation with audio generated!'
            
            print(f"Sending successful response: {len(json.dumps(response))} chars")
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            print(f"API v3.0 ERROR: {e}")
            import traceback
            traceback.print_exc()
            
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = {
                'error': f'API v3.0 Server Error: {str(e)}',
                'api_version': '3.0'
            }
            self.wfile.write(json.dumps(error_response).encode())

    def do_OPTIONS(self):
        """CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def create_meditation_script(self, scenario, duration):
        """Create meditation script with proper Hemi-Sync structure"""
        
        # Try Gemini first
        gemini_key = os.environ.get('GEMINI_API_KEY')
        if gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=gemini_key)
                
                prompt = f"""Create a {duration}-minute Hemi-Sync meditation script for: "{scenario}"

Follow Monroe Institute structure:
1. Welcome & Preparation (1 min)
2. Energy Conversion Box (1 min)
3. Resonant Tuning (2 min) 
4. Affirmation (1 min)
5. Focus 10 Induction (3 min)
6. Main Experience ({duration-8} min)
7. Return Sequence (2 min)
8. Closing (1 min)

Include [PAUSE:X] markers where X is seconds.
Present tense as if goal achieved.
Total: {duration} minutes."""

                model = genai.GenerativeModel('gemini-1.5-pro-latest')
                response = model.generate_content(prompt)
                print("Gemini script generated successfully")
                return response.text.strip()
                
            except Exception as e:
                print(f"Gemini failed, using fallback: {e}")
        
        # Fallback script
        print("Using fallback meditation script")
        return f"""**Welcome & Preparation (1 min)**

Welcome to your personalized Hemi-Sync meditation for {scenario}. Find a comfortable position, close your eyes, and begin to relax.

[PAUSE:10]

**Energy Conversion Box (1 min)**

Visualize a secure mental container. Place all your worries, fears, and distractions into this box. They will be safe here and available when you return.

[PAUSE:15]

**Resonant Tuning (2 min)**

Take three deep breaths. With each exhale, hum gently: "Ahhhhhh..." Feel the vibration energizing your entire being.

[PAUSE:20]

Breathe in universal energy, breathe out tension and limitation.

[PAUSE:15]

**Affirmation (1 min)**

"I am more than my physical body. Because I am more than physical matter, I can perceive that which is greater than the physical world."

"I am now manifesting {scenario} with perfect ease and divine timing."

[PAUSE:15]

**Focus 10 Induction (3 min)**

Now we'll count from 1 to 10, relaxing deeper with each number...

1... releasing all tension from your feet and legs [PAUSE:8]
2... letting go from your lower torso [PAUSE:8]
3... releasing your chest and shoulders [PAUSE:8]
4... relaxing your arms and hands [PAUSE:8]
5... releasing your neck and throat [PAUSE:8]
6... relaxing your facial muscles [PAUSE:8]
7... releasing your entire head [PAUSE:8]
8... deeper and deeper relaxation [PAUSE:8]
9... mind awake, body completely asleep [PAUSE:8]
10... perfectly relaxed in Focus 10 [PAUSE:15]

**Main Experience ({duration-8} min)**

You are now in the perfect state to experience {scenario} as your current reality.

[PAUSE:30]

See yourself already living this experience. What do you see around you? What feelings arise as you embody this reality?

[PAUSE:45]

Feel the emotions of having achieved {scenario}. Experience the joy, satisfaction, and gratitude flowing through every cell of your being.

[PAUSE:60]

Your subconscious mind is now accepting this as your true reality. Feel it integrating into your energy field.

[PAUSE:45]

Trust that this manifestation is already complete in the quantum field. You are simply allowing it to materialize in physical reality.

[PAUSE:30]

Take a moment to anchor this feeling deep within your heart center.

[PAUSE:30]

**Return Sequence (2 min)**

In a moment, we'll return to normal waking consciousness. You'll feel refreshed, energized, and aligned with your manifestation.

10... beginning to return, carrying this energy with you [PAUSE:8]
9... becoming more aware of your physical body [PAUSE:8]
8... feeling energy returning to your limbs [PAUSE:8]
7... almost back to normal consciousness [PAUSE:8]
6... wiggling your fingers and toes [PAUSE:8]
5... taking deeper breaths [PAUSE:8]
4... feeling alert and energized [PAUSE:8]
3... almost fully back [PAUSE:8]
2... opening your eyes when ready [PAUSE:8]
1... fully awake, alert, and aligned [PAUSE:10]

**Closing (1 min)**

You have successfully programmed your consciousness for {scenario}. This energy now flows through you throughout your day. 

Remember: you are a powerful creator, and your meditation has activated the manifestation process.

Thank you for this sacred time together."""

    def generate_elevenlabs_sample(self, script, api_key):
        """Generate short ElevenLabs audio sample"""
        try:
            from elevenlabs.client import ElevenLabs
            
            client = ElevenLabs(api_key=api_key)
            
            # Extract first clean sentence for sample
            import re
            clean_text = re.sub(r'\[PAUSE:\d+\]', '', script)
            clean_text = re.sub(r'\*\*([^*]+)\*\*', r'\1', clean_text)
            
            sentences = [s.strip() for s in clean_text.split('.') if len(s.strip()) > 30]
            if not sentences:
                return None
            
            sample_text = sentences[0][:200] + '.'
            print(f"Generating audio for: {sample_text[:50]}...")
            
            audio_iterator = client.text_to_speech.convert(
                voice_id="7nFoun39JV8WgdJ3vGmC",
                text=sample_text,
                model_id="eleven_multilingual_v2"
            )
            
            return b"".join(list(audio_iterator))
            
        except Exception as e:
            print(f"ElevenLabs error: {e}")
            return None