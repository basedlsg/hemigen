from http.server import BaseHTTPRequestHandler
import json
import os
import traceback
from datetime import datetime

# Import dependencies safely
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    from elevenlabs.client import ElevenLabs
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False

# Configure APIs
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
ELEVENLABS_API_KEY = os.environ.get('ELEVENLABS_API_KEY', 'sk_fe6faf571491c9b26bef909dce2e19a8e1d7239bf518027b')

if GEMINI_API_KEY and GEMINI_AVAILABLE:
    genai.configure(api_key=GEMINI_API_KEY)

elevenlabs_client = None
if ELEVENLABS_API_KEY and ELEVENLABS_AVAILABLE:
    try:
        elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    except Exception as e:
        print(f"ElevenLabs init failed: {e}")

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Status endpoint"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        status = {
            "status": "API Online",
            "timestamp": datetime.now().isoformat(),
            "capabilities": {
                "gemini": GEMINI_AVAILABLE and bool(GEMINI_API_KEY),
                "elevenlabs": ELEVENLABS_AVAILABLE and bool(elevenlabs_client),
                "script_generation": True,
                "audio_generation": bool(elevenlabs_client)
            },
            "version": "2.0"
        }
        
        self.wfile.write(json.dumps(status, indent=2).encode())

    def do_POST(self):
        """Generate meditation"""
        try:
            print("=== NEW API REQUEST ===")
            
            # CORS
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
            
            print(f"Request: {scenario[:50]}... ({duration} min)")
            
            # Validate
            if not scenario or len(scenario) < 10:
                response = {'error': 'Please provide a detailed meditation intention (at least 10 characters)'}
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Generate script
            script = self.generate_script(scenario, duration)
            if not script:
                response = {'error': 'Failed to generate script'}
                self.wfile.write(json.dumps(response).encode())
                return
            
            print(f"Script generated: {len(script)} characters")
            
            # Try audio generation
            audio_data = None
            if elevenlabs_client:
                try:
                    print("Attempting audio generation...")
                    audio_data = self.generate_audio_sample(script)
                    print(f"Audio generated: {len(audio_data) if audio_data else 0} bytes")
                except Exception as e:
                    print(f"Audio failed: {e}")
            
            # Response
            response = {
                'success': True,
                'script': script,
                'scenario': scenario,
                'duration': duration,
                'generated_at': datetime.now().isoformat(),
                'audio_available': bool(audio_data),
                'message': 'Meditation generated successfully!'
            }
            
            if audio_data:
                import base64
                response['audio_data'] = base64.b64encode(audio_data).decode('utf-8')
                response['message'] = 'Meditation with audio generated!'
            
            print(f"Sending response: {len(json.dumps(response))} bytes")
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            print(f"ERROR: {e}")
            traceback.print_exc()
            
            try:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                error_response = {
                    'error': f'Server error: {str(e)}',
                    'debug': str(e)[:200]
                }
                self.wfile.write(json.dumps(error_response).encode())
            except:
                pass

    def do_OPTIONS(self):
        """CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def generate_script(self, scenario, duration):
        """Generate meditation script"""
        if not GEMINI_AVAILABLE or not GEMINI_API_KEY:
            # Fallback script with proper structure
            return f"""**Welcome & Preparation (1 min)**

Welcome to your personalized meditation for {scenario}. Find a comfortable position and close your eyes.

[PAUSE:10]

**Energy Conversion Box (1 min)**

Imagine placing all your worries and distractions into a mental box. They will be there when you return.

[PAUSE:15]

**Resonant Tuning (2 min)**

Take three deep breaths. With each exhale, hum gently to energize your being.

[PAUSE:20]

**Affirmation (1 min)**

I am more than my physical body. Because I am more than physical matter, I can perceive that which is greater than the physical world.

I am manifesting {scenario} with ease and grace.

[PAUSE:15]

**Focus 10 Induction (3 min)**

Count with me from 1 to 10, relaxing deeper with each number...

1... releasing tension from your feet [PAUSE:5]
2... letting go from your legs [PAUSE:5]
3... releasing your abdomen [PAUSE:5]
4... relaxing your chest [PAUSE:5]
5... releasing your arms [PAUSE:5]
6... relaxing your shoulders [PAUSE:5]
7... releasing your neck [PAUSE:5]
8... relaxing your face [PAUSE:5]
9... releasing your entire head [PAUSE:5]
10... completely relaxed, mind awake, body asleep [PAUSE:10]

**Main Experience ({duration-8} min)**

Now you are in the perfect state to manifest {scenario}. Feel yourself having already achieved this goal.

[PAUSE:30]

See yourself living this reality. What does it look like? What does it feel like?

[PAUSE:45]

Experience the emotions of having achieved {scenario}. Feel the gratitude, joy, and satisfaction.

[PAUSE:60]

Your subconscious mind is now programming this reality. Trust the process.

[PAUSE:30]

**Return (2 min)**

When you're ready, we'll return to normal consciousness...

10... beginning to return [PAUSE:5]
9... becoming more aware [PAUSE:5]
8... feeling energy returning [PAUSE:5]
7... almost back [PAUSE:5]
6... wiggling fingers and toes [PAUSE:5]
5... taking deeper breaths [PAUSE:5]
4... feeling more alert [PAUSE:5]
3... almost fully back [PAUSE:5]
2... opening your eyes when ready [PAUSE:5]
1... fully awake and energized [PAUSE:5]

**Closing**

You have successfully programmed your subconscious for {scenario}. Carry this energy with you throughout your day."""

        try:
            # Use Gemini if available
            prompt = f"""Create a {duration}-minute Hemi-Sync meditation script for: "{scenario}"

Use this exact structure with [PAUSE:X] markers:
1. Welcome & Preparation (1 min)
2. Energy Conversion Box (1 min) 
3. Resonant Tuning (2 min)
4. Affirmation (1 min)
5. Focus 10 Induction (3 min)
6. Main Experience ({duration-8} min)
7. Return Sequence (2 min)
8. Closing (1 min)

Include [PAUSE:X] markers throughout where X is seconds (5-60). 
Present tense as if the goal is already achieved.
Total duration: {duration} minutes."""

            model = genai.GenerativeModel('gemini-1.5-pro-latest')
            response = model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            print(f"Gemini error: {e}")
            return None

    def generate_audio_sample(self, script):
        """Generate audio for first 200 characters of script"""
        if not elevenlabs_client:
            return None
            
        try:
            # Clean text for TTS (remove markdown and pause markers)
            import re
            clean_text = re.sub(r'\[PAUSE:\d+\]', '', script)
            clean_text = re.sub(r'\*\*([^*]+)\*\*', r'\1', clean_text)
            clean_text = re.sub(r'\*([^*]+)\*', r'\1', clean_text)
            
            # Take first meaningful sentence
            sentences = [s.strip() for s in clean_text.split('.') if len(s.strip()) > 20]
            if not sentences:
                return None
            
            sample_text = sentences[0][:200] + '.'
            print(f"Generating audio for: {sample_text[:50]}...")
            
            audio_iterator = elevenlabs_client.text_to_speech.convert(
                voice_id="7nFoun39JV8WgdJ3vGmC",
                text=sample_text,
                model_id="eleven_multilingual_v2"
            )
            
            return b"".join(list(audio_iterator))
            
        except Exception as e:
            print(f"Audio generation error: {e}")
            return None