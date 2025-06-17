import json
import os
from datetime import datetime
from http.server import BaseHTTPRequestHandler

# Try imports safely
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

# Initialize APIs
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

MEDITATION_PROMPT = """
Create a {duration}-minute Hemi-Sync meditation script for: "{scenario}"

STRUCTURE (Monroe Institute methodology):

1. **Welcome & Orientation (1-2 min)**
   - Warm, personal welcome acknowledging their intention
   - Brief overview of the meditation journey

2. **Energy Conversion Box (1-2 min)**
   - Guide placement of worries/distractions into mental container
   - Include [PAUSE:15] for placement

3. **Resonant Tuning (2-3 min)**
   - Breathing exercises with energy visualization
   - Include [PAUSE:10] between breathing cycles
   - 3-4 complete breathing cycles

4. **Affirmation (1-2 min)**
   - "I am more than my physical body..."
   - Specific affirmations for their intention
   - Include [PAUSE:10] between affirmations

5. **Focus 10 Induction (3-4 min)**
   - Count 1-10 with progressive relaxation
   - Include [PAUSE:5] between counts

6. **Main Experience ({main_duration} min)**
   - Multi-sensory visualization as if goal is achieved
   - Present tense throughout
   - Include [PAUSE:30-60] for deep integration periods
   - Specific scenarios related to intention

7. **Return Sequence (2-3 min)**
   - Count 10-1 back to normal awareness
   - Include [PAUSE:5] between counts

8. **Closing (1 min)**
   - Reinforce intention

REQUIREMENTS:
- Use [PAUSE:X] markers (X = seconds)
- Present tense for main content
- Total duration: {duration} minutes
"""

def generate_script_only(scenario, duration):
    """Generate just the meditation script."""
    if not GEMINI_API_KEY or not GEMINI_AVAILABLE:
        return f"Sample meditation script for {scenario} ({duration} minutes):\n\nWelcome to your meditation journey...\n[PAUSE:10]\nClose your eyes and begin to relax...\n[PAUSE:15]\nThis is a sample script as Gemini API is not configured."
    
    try:
        main_duration = max(5, duration - 15)
        prompt = MEDITATION_PROMPT.format(
            scenario=scenario,
            duration=duration,
            main_duration=main_duration
        )
        
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        response = model.generate_content(prompt)
        return response.text.strip()
        
    except Exception as e:
        print(f"Gemini error: {e}")
        return f"Error generating script: {str(e)}"

def synthesize_audio_only(text):
    """Generate just a single audio segment."""
    if not elevenlabs_client:
        return None
    
    try:
        # Clean text for TTS
        clean_text = text.replace('[PAUSE:', '').replace(']', '').replace('**', '')
        if len(clean_text.strip()) < 10:
            return None
            
        audio_iterator = elevenlabs_client.text_to_speech.convert(
            voice_id="7nFoun39JV8WgdJ3vGmC",
            text=clean_text[:1000],  # Limit length for testing
            model_id="eleven_multilingual_v2"
        )
        
        full_audio_bytes = b"".join(list(audio_iterator))
        return full_audio_bytes
        
    except Exception as e:
        print(f"TTS error: {e}")
        return None

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # CORS headers
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            # Parse request
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            scenario = data.get('scenario', '').strip()
            duration = int(data.get('duration', 25))
            
            # Validate
            if not scenario or len(scenario) < 10:
                response = {'error': 'Please provide a detailed meditation intention'}
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Generate script
            print(f"Generating script for: {scenario}")
            script = generate_script_only(scenario, duration)
            
            # Try to generate a short audio sample
            audio_sample = None
            if elevenlabs_client:
                print("Attempting audio generation...")
                # Just generate audio for the first sentence
                first_sentence = script.split('.')[0] + '.'
                audio_sample = synthesize_audio_only(first_sentence)
            
            response = {
                'success': True,
                'script': script,
                'scenario': scenario,
                'duration': duration,
                'generated_at': datetime.now().isoformat(),
                'debug': {
                    'gemini_available': GEMINI_AVAILABLE,
                    'elevenlabs_available': ELEVENLABS_AVAILABLE,
                    'elevenlabs_client': elevenlabs_client is not None,
                    'audio_sample_generated': audio_sample is not None,
                    'audio_sample_size': len(audio_sample) if audio_sample else 0
                }
            }
            
            if audio_sample:
                import base64
                response['audio_sample'] = base64.b64encode(audio_sample).decode('utf-8')
                response['message'] = 'Script and audio sample generated!'
            else:
                response['message'] = 'Script generated (audio not available)'
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            
            self.send_response(500)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = {
                'error': str(e),
                'type': type(e).__name__
            }
            self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()