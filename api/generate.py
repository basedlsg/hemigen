import json
import os
import time
import hashlib
from datetime import datetime, timedelta
import google.generativeai as genai
from http.server import BaseHTTPRequestHandler
import traceback
import re
import io
import base64

# Try to import optional dependencies
try:
    import redis
except ImportError:
    redis = None

try:
    from elevenlabs.client import ElevenLabs
    from pydub import AudioSegment
    AUDIO_AVAILABLE = True
except ImportError:
    ElevenLabs = None
    AudioSegment = None
    AUDIO_AVAILABLE = False
    print("Audio dependencies not available - text-only mode")

# Initialize APIs
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
ELEVENLABS_API_KEY = os.environ.get('ELEVENLABS_API_KEY', 'sk_fe6faf571491c9b26bef909dce2e19a8e1d7239bf518027b')
ELEVENLABS_VOICE_ID = os.environ.get('ELEVENLABS_VOICE_ID', '7nFoun39JV8WgdJ3vGmC')

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Initialize ElevenLabs
elevenlabs_client = None
if ELEVENLABS_API_KEY and AUDIO_AVAILABLE:
    try:
        elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        print("ElevenLabs client initialized successfully")
    except Exception as e:
        print(f"ElevenLabs initialization failed: {e}")

# Redis for rate limiting (Upstash free tier)
REDIS_URL = os.environ.get('REDIS_URL')
redis_client = None
if REDIS_URL and redis:
    try:
        redis_client = redis.from_url(REDIS_URL)
        print("Redis client initialized successfully")
    except Exception as e:
        print(f"Redis initialization failed: {e}")

# Enhanced meditation prompt optimized for production
MEDITATION_PROMPT = """
Create a {duration}-minute Hemi-Sync meditation script for: "{scenario}"

STRUCTURE (Monroe Institute methodology):

1. **Welcome & Orientation (1-2 min)**
   - Warm, personal welcome acknowledging their intention
   - Brief overview of the meditation journey
   - Create emotional connection to their goal

2. **Energy Conversion Box (1-2 min)**
   - Guide placement of worries/distractions into mental container
   - Emphasize security and later retrieval
   - Present tense language

3. **Resonant Tuning (2-3 min)**
   - Breathing exercises with energy visualization
   - Humming vibrations on exhale
   - Include [PAUSE:15] between cycles
   - 3-4 complete breathing cycles

4. **Energy Balloon Protection (2-3 min)**
   - Protective energy sphere visualization
   - Energy flows from head, around body, enters through feet
   - Include [PAUSE:20] for feeling the protection

5. **Affirmation (1-2 min)**
   - "I am more than my physical body..."
   - Specific affirmations for their intention (present tense)
   - [PAUSE:10] between affirmations

6. **Focus 10 Induction (3-4 min)**
   - Count 1-10 with progressive relaxation
   - "Mind awake, body asleep" emphasis
   - [PAUSE:5] between counts

7. **Main Experience ({main_duration} min)**
   - Multi-sensory visualization as if goal is achieved
   - Present tense throughout
   - Include FEELING states of success
   - [PAUSE:30-60] for deep integration
   - Specific scenarios related to intention
   - Emotional anchoring techniques

8. **Integration (2-3 min)**
   - Reinforce new neural pathways
   - Create mental anchor for daily recall
   - [PAUSE:20] for integration

9. **Return Sequence (2-3 min)**
   - Count 10-1 back to normal awareness
   - Progressive physical awareness return
   - Energized, positive suggestions
   - [PAUSE:5] between counts

10. **Closing (1 min)**
    - Reinforce intention
    - Daily practice encouragement

REQUIREMENTS:
- Use [PAUSE:X] markers (X = seconds)
- Suggestive language ("you may notice", "allow yourself")
- Focus on achievement feelings
- Present tense for main content
- Scientifically grounded approach
- Total duration: {duration} minutes
"""

def get_client_ip(request):
    """Extract client IP from request headers."""
    forwarded = request.headers.get('x-forwarded-for')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.headers.get('x-real-ip', 'unknown')

def check_rate_limit(ip_address, max_requests=3, window_hours=24):
    """Check if IP is within rate limits."""
    if not redis_client:
        return True  # Allow if no Redis
    
    key = f"rate_limit:{ip_address}"
    try:
        current_count = redis_client.get(key)
        if current_count is None:
            redis_client.setex(key, window_hours * 3600, 1)
            return True
        elif int(current_count) < max_requests:
            redis_client.incr(key)
            return True
        else:
            return False
    except:
        return True  # Allow on Redis error

def validate_input(scenario, duration):
    """Validate user input."""
    if not scenario or len(scenario.strip()) < 10:
        return "Please provide a detailed meditation intention (at least 10 characters)"
    
    if len(scenario) > 500:
        return "Meditation intention too long (max 500 characters)"
    
    if not isinstance(duration, int) or duration < 10 or duration > 60:
        return "Duration must be between 10 and 60 minutes"
    
    # Check for inappropriate content
    banned_words = ['hack', 'illegal', 'drug', 'violence', 'harm']
    scenario_lower = scenario.lower()
    if any(word in scenario_lower for word in banned_words):
        return "Please use appropriate content for meditation intentions"
    
    return None

def generate_meditation_script(scenario, duration):
    """Generate meditation script using Gemini API."""
    try:
        if not GEMINI_API_KEY:
            raise Exception("API configuration error")
        
        main_duration = max(5, duration - 15)  # Reserve 15 min for structure
        
        prompt = MEDITATION_PROMPT.format(
            scenario=scenario,
            duration=duration,
            main_duration=main_duration
        )
        
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        
        generation_config = {
            "temperature": 0.8,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }
        
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]
        
        response = model.generate_content(
            prompt,
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        return response.text.strip()
        
    except Exception as e:
        print(f"Gemini API error: {str(e)}")
        traceback.print_exc()
        return None

def synthesize_text_elevenlabs(text):
    """Synthesize text using ElevenLabs API."""
    if not elevenlabs_client or not AUDIO_AVAILABLE:
        print("ElevenLabs client not available")
        return None
    
    try:
        audio_data_iterator = elevenlabs_client.text_to_speech.convert(
            voice_id=ELEVENLABS_VOICE_ID,
            text=text,
            model_id="eleven_multilingual_v2"
        )
        # Consume the iterator and join byte chunks
        full_audio_bytes = b"".join(list(audio_data_iterator))
        return full_audio_bytes
    except Exception as e:
        print(f"Error during ElevenLabs synthesis: {e}")
        traceback.print_exc()
        return None

def create_meditation_audio(script_text):
    """Create complete meditation audio with pauses."""
    if not AUDIO_AVAILABLE:
        print("Audio generation not available - missing dependencies")
        return None
        
    try:
        if not script_text:
            return None
        
        # Split script by pause markers
        segments_raw = re.split(r'(\[PAUSE:\d+\])', script_text)
        voice_track = AudioSegment.empty()
        
        for segment_text in segments_raw:
            segment_text = segment_text.strip()
            if not segment_text:
                continue
            
            # Check if it's a pause marker
            pause_match = re.match(r'\[PAUSE:(\d+)\]', segment_text)
            if pause_match:
                try:
                    pause_duration_seconds = int(pause_match.group(1))
                    print(f"Adding pause: {pause_duration_seconds}s")
                    if pause_duration_seconds > 0:
                        voice_track += AudioSegment.silent(duration=pause_duration_seconds * 1000)
                except ValueError:
                    print(f"Warning: Could not parse pause duration: {segment_text}")
            elif segment_text:  # Text segment
                print(f"Synthesizing: '{segment_text[:50]}...'")
                audio_bytes = synthesize_text_elevenlabs(segment_text)
                if audio_bytes:
                    try:
                        audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")
                        voice_track += audio_segment
                    except Exception as e:
                        print(f"Error creating audio segment: {e}")
                        voice_track += AudioSegment.silent(duration=1000)  # 1 second silence as fallback
                else:
                    print(f"TTS failed for segment: '{segment_text[:50]}...'")
                    voice_track += AudioSegment.silent(duration=1000)
        
        if len(voice_track) == 0:
            print("Voice track is empty")
            return None
        
        # Export to bytes
        output_buffer = io.BytesIO()
        voice_track.export(output_buffer, format="mp3")
        output_buffer.seek(0)
        
        return output_buffer.getvalue()
        
    except Exception as e:
        print(f"Error creating meditation audio: {e}")
        traceback.print_exc()
        return None

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests for testing."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        response = {
            'status': 'API is running',
            'method': 'GET',
            'endpoints': {
                'POST /api/generate': 'Generate meditation with audio',
                'GET /api/generate': 'This status endpoint'
            },
            'environment': {
                'gemini_available': bool(GEMINI_API_KEY),
                'audio_available': AUDIO_AVAILABLE,
                'elevenlabs_client': elevenlabs_client is not None
            }
        }
        self.wfile.write(json.dumps(response, indent=2).encode())

    def do_POST(self):
        try:
            print(f"=== API CALL RECEIVED ===")
            print(f"Time: {datetime.now().isoformat()}")
            print(f"Headers: {dict(self.headers)}")
            
            # CORS headers
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            # Rate limiting
            client_ip = get_client_ip(self)
            print(f"Client IP: {client_ip}")
            
            if not check_rate_limit(client_ip):
                print("Rate limit exceeded")
                response = {
                    'error': 'Rate limit exceeded. Please try again in 24 hours.',
                    'code': 'RATE_LIMIT_EXCEEDED'
                }
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Parse request
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            print(f"Request data: {data}")
            
            scenario = data.get('scenario', '').strip()
            duration = int(data.get('duration', 25))
            
            print(f"Parsed - Scenario: '{scenario}', Duration: {duration}")
            
            # Validate input
            validation_error = validate_input(scenario, duration)
            if validation_error:
                response = {'error': validation_error}
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Generate meditation script
            print("Starting script generation...")
            script = generate_meditation_script(scenario, duration)
            print(f"Script generated. Length: {len(script) if script else 0} characters")
            
            if not script:
                print("Script generation failed")
                response = {
                    'error': 'Unable to generate meditation. Please try again.',
                    'code': 'GENERATION_FAILED'
                }
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Try to generate audio (with timeout protection)
            audio_data = None
            audio_error = None
            
            print(f"Starting audio generation. AUDIO_AVAILABLE: {AUDIO_AVAILABLE}, elevenlabs_client: {elevenlabs_client is not None}")
            
            # Skip audio for now to test script generation
            if False:  # Temporarily disable audio generation
                try:
                    start_time = time.time()
                    audio_data = create_meditation_audio(script)
                    generation_time = time.time() - start_time
                    print(f"Audio generation took {generation_time:.2f} seconds")
                except Exception as e:
                    audio_error = str(e)
                    print(f"Audio generation failed: {e}")
                    traceback.print_exc()
            else:
                print("Audio generation skipped for testing")
                audio_error = "Audio generation temporarily disabled for testing"
            
            if not audio_data:
                # Fallback to text-only if audio generation fails
                message = 'Meditation script generated!'
                if audio_error:
                    message += f' (Audio unavailable: {audio_error})'
                elif not AUDIO_AVAILABLE:
                    message += ' (Audio generation not supported in this environment)'
                else:
                    message += ' (Audio generation temporarily unavailable)'
                    
                response = {
                    'success': True,
                    'script': script,
                    'scenario': scenario,
                    'duration': duration,
                    'generated_at': datetime.now().isoformat(),
                    'message': message,
                    'audio_available': False
                }
            else:
                # Convert audio to base64 for transmission
                try:
                    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                    
                    response = {
                        'success': True,
                        'script': script,
                        'audio_data': audio_base64,
                        'scenario': scenario,
                        'duration': duration,
                        'generated_at': datetime.now().isoformat(),
                        'message': 'Your personalized Hemi-Sync meditation with audio is ready!',
                        'audio_available': True
                    }
                except Exception as e:
                    print(f"Error encoding audio data: {e}")
                    response = {
                        'success': True,
                        'script': script,
                        'scenario': scenario,
                        'duration': duration,
                        'generated_at': datetime.now().isoformat(),
                        'message': 'Meditation script generated! (Audio encoding failed)',
                        'audio_available': False
                    }
            
            print(f"Sending response. Audio available: {response.get('audio_available', False)}")
            print(f"Response message: {response.get('message', 'No message')}")
            
            response_json = json.dumps(response)
            print(f"Response size: {len(response_json)} characters")
            
            self.wfile.write(response_json.encode())
            print("Response sent successfully")
            
        except Exception as e:
            error_msg = str(e)
            print(f"Handler error: {error_msg}")
            traceback.print_exc()
            
            try:
                self.send_response(500)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                
                response = {
                    'error': 'Internal server error. Please try again.',
                    'code': 'INTERNAL_ERROR',
                    'debug': error_msg if len(error_msg) < 100 else error_msg[:100] + '...'
                }
                self.wfile.write(json.dumps(response).encode())
            except Exception as write_error:
                print(f"Error writing error response: {write_error}")
    
    def do_OPTIONS(self):
        # Handle CORS preflight
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()