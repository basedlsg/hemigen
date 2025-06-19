from http.server import BaseHTTPRequestHandler
import json
import os
from datetime import datetime
import time

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Status endpoint - v4.0 FULL AUDIO"""
        # Force deployment - v4.0 2024-06-17
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        # Direct environment check
        gemini_key = os.environ.get('GEMINI_API_KEY', '')
        elevenlabs_key = os.environ.get('ELEVENLABS_API_KEY', '')
        
        # For internal testing - hardcode if env vars don't work
        if not gemini_key:
            gemini_key = 'AIzaSyAqko3NqGS-GtXhzm8LeiZ3xUEyo_XIqLo'
        if not elevenlabs_key:
            elevenlabs_key = 'sk_fe6faf571491c9b26bef909dce2e19a8e1d7239bf518027b'
        
        status = {
            "status": "API ONLINE v4.0 - FULL AUDIO - ENHANCED DEBUG",
            "timestamp": datetime.now().isoformat(),
            "deployment_timestamp": "2024-06-19-FORCE-REBUILD",
            "environment_check": {
                "gemini_key_set": bool(gemini_key),
                "elevenlabs_key_set": bool(elevenlabs_key),
                "keys_loaded": bool(gemini_key and elevenlabs_key)
            },
            "capabilities": {
                "full_audio_generation": True,
                "meditation_duration": "30-60 minutes",
                "audio_format": "mp3"
            },
            "version": "4.0"
        }

        self.wfile.write(json.dumps(status, indent=2).encode())

    def do_POST(self):
        """Generate full meditation with complete audio"""
        try:
            print("=== API v4.0 FULL AUDIO REQUEST ===")

            # CORS headers
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            # Read request
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                response = {'error': 'No data received'}
                self.wfile.write(json.dumps(response).encode())
                return

            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))

            scenario = data.get('scenario', '').strip()
            duration = int(data.get('duration', 30))

            print(f"Generating {duration}-minute meditation for: {scenario}")

            # Validation
            if not scenario or len(scenario) < 10:
                response = {'error': 'Please provide a detailed meditation intention'}
                self.wfile.write(json.dumps(response).encode())
                return

            # Get API keys with fallback
            gemini_key = os.environ.get('GEMINI_API_KEY', '')
            elevenlabs_key = os.environ.get('ELEVENLABS_API_KEY', '')
            
            # Hardcode for internal testing if env vars fail
            if not gemini_key:
                gemini_key = 'AIzaSyAqko3NqGS-GtXhzm8LeiZ3xUEyo_XIqLo'
            if not elevenlabs_key:
                elevenlabs_key = 'sk_fe6faf571491c9b26bef909dce2e19a8e1d7239bf518027b'

            # Generate meditation script
            script = self.create_meditation_script(scenario, duration, gemini_key)
            print(f"Script created: {len(script)} characters")

            # Generate FULL audio (not just sample)
            audio_data = None
            if elevenlabs_key:
                try:
                    print("🎵 === STARTING FULL MEDITATION AUDIO GENERATION ===")
                    print(f"🔑 ElevenLabs API key present: {bool(elevenlabs_key)}")
                    print(f"📝 Script length: {len(script)} characters")
                    print(f"⏱️ Starting audio generation at: {datetime.now().isoformat()}")
                    
                    start_time = time.time()
                    
                    # Add timeout check - Vercel has 5 minute limit
                    max_audio_time = 240  # 4 minutes max for audio generation
                    
                    audio_data = self.generate_full_audio(script, elevenlabs_key)
                    generation_time = time.time() - start_time
                    
                    if generation_time > max_audio_time:
                        print(f"⚠️ WARNING: Audio generation took {generation_time:.1f}s")
                        print(f"⚠️ This is close to Vercel's 5-minute timeout limit!")
                    
                    if audio_data:
                        print(f"✅ FULL AUDIO GENERATED SUCCESSFULLY!")
                        print(f"📊 Audio size: {len(audio_data)} bytes ({len(audio_data)/1024/1024:.2f} MB)")
                        print(f"⏱️ Generation time: {generation_time:.1f} seconds")
                    else:
                        print(f"❌ Audio generation returned None/empty data")
                        
                except Exception as e:
                    print(f"❌ AUDIO GENERATION FAILED: {e}")
                    print(f"🔍 Error type: {type(e).__name__}")
                    import traceback
                    print("📝 Full error traceback:")
                    traceback.print_exc()
                    # Continue without audio rather than failing completely
                    audio_data = None

            # Success response
            response = {
                'success': True,
                'script': script,
                'scenario': scenario,
                'duration': duration,
                'generated_at': datetime.now().isoformat(),
                'message': f'Full {duration}-minute meditation generated!',
                'audio_available': bool(audio_data),
                'api_version': '4.0',
                'deployment_id': 'ENHANCED-DEBUG-2024-06-19',
                'elevenlabs_version': '2.3.0'
            }

            if audio_data:
                import base64
                response['audio_data'] = base64.b64encode(audio_data).decode('utf-8')
                response['audio_size_mb'] = round(len(audio_data) / (1024 * 1024), 2)

            print(f"Sending response with script and {'full audio' if audio_data else 'no audio'}")
            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            print(f"API v4.0 ERROR: {e}")
            import traceback
            traceback.print_exc()

            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = {
                'error': f'Server Error: {str(e)}',
                'api_version': '4.0'
            }
            self.wfile.write(json.dumps(error_response).encode())

    def do_OPTIONS(self):
        """CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def create_meditation_script(self, scenario, duration, gemini_key):
        """Create full meditation script"""
        
        # Try Gemini first if available
        if gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=gemini_key)
                
                prompt = f"""Create a {duration}-minute Hemi-Sync meditation script for: "{scenario}"

Follow this exact Monroe Institute structure with specific timings:
1. Welcome & Preparation (2 minutes)
2. Energy Conversion Box (2 minutes)  
3. Resonant Tuning (3 minutes)
4. Affirmation (2 minutes)
5. Focus 10 Induction (5 minutes)
6. Main Experience ({duration-16} minutes)
7. Return Sequence (2 minutes)
8. Closing (1 minute)

Requirements:
- Include [PAUSE:X] markers where X is seconds (10-60)
- Write in present tense as if the goal is already achieved
- Include specific visualizations and feelings
- Make the main experience immersive and transformative
- Total duration must be exactly {duration} minutes
- Write out EVERY section completely, no summaries"""
                
                model = genai.GenerativeModel('gemini-1.5-pro-latest')
                response = model.generate_content(prompt)
                print("Gemini script generated successfully")
                return response.text.strip()
                
            except Exception as e:
                print(f"Gemini failed, using enhanced fallback: {e}")
        
        # Enhanced fallback script for full duration
        print("Using enhanced fallback meditation script")
        return self.generate_fallback_script(scenario, duration)

    def generate_fallback_script(self, scenario, duration):
        """Generate a complete fallback script for any duration"""
        main_duration = duration - 16  # Total minus fixed sections
        
        return f"""**Welcome & Preparation (2 minutes)**

Welcome to your personalized Hemi-Sync meditation for {scenario}. Find a comfortable position where you won't be disturbed. Close your eyes and begin to relax.

[PAUSE:15]

Take a deep breath in... and slowly exhale. With each breath, allow yourself to relax more deeply.

[PAUSE:20]

Feel your body becoming heavier, sinking into comfort. You are safe, supported, and ready for this transformative journey.

[PAUSE:25]

**Energy Conversion Box (2 minutes)**

Now, visualize a beautiful, secure container before you. This is your Energy Conversion Box. It can be any shape or material you choose - a treasure chest, a crystal box, or a sphere of light.

[PAUSE:20]

Into this box, place all your worries, concerns, and distractions. Watch as each worry transforms into neutral energy as it enters the box.

[PAUSE:30]

Place any physical discomfort, mental chatter, or emotional tensions into the box. They will be safely stored and transformed while you journey.

[PAUSE:30]

Seal your box now, knowing everything is secure and will be returned to you transformed into positive energy.

[PAUSE:20]

**Resonant Tuning (3 minutes)**

Take a deep breath in, and as you exhale, hum or tone the sound "Ahhhhhh..." Feel the vibration throughout your body.

[PAUSE:25]

Again, breathe in deeply... and "Ahhhhhh..." Let the sound resonate in your chest, spreading warmth and energy.

[PAUSE:25]

One more time, breathe in universal energy... and "Ahhhhhh..." Feel your entire being vibrating in harmony with the universe.

[PAUSE:30]

Continue breathing naturally, feeling the residual vibration aligning every cell in your body with your highest good.

[PAUSE:40]

You are now tuned to the perfect frequency for manifesting {scenario}.

[PAUSE:30]

**Affirmation (2 minutes)**

Repeat after me in your mind: "I am more than my physical body. Because I am more than physical matter, I can perceive that which is greater than the physical world."

[PAUSE:30]

"I am now manifesting {scenario} with perfect ease and divine timing."

[PAUSE:25]

"My consciousness creates my reality. I am aligned with the infinite possibilities of the universe."

[PAUSE:25]

"I trust in the process. What I seek is already mine in the quantum field."

[PAUSE:30]

**Focus 10 Induction (5 minutes)**

Now we'll count from 1 to 10, entering the state of Focus 10 - mind awake, body asleep.

[PAUSE:15]

1... Releasing all tension from your feet and ankles. They are completely relaxed.

[PAUSE:20]

2... Relaxation flowing up through your calves and knees, releasing completely.

[PAUSE:20]

3... Your thighs and hips letting go, sinking into deep relaxation.

[PAUSE:20]

4... Your abdomen and lower back releasing all tension, breathing naturally and easily.

[PAUSE:20]

5... Your chest and upper back relaxing, your heart beating peacefully.

[PAUSE:20]

6... Your shoulders dropping, releasing all burdens and tension.

[PAUSE:20]

7... Your arms and hands becoming heavy and completely relaxed.

[PAUSE:20]

8... Your neck and throat soft and relaxed, no tension remaining.

[PAUSE:20]

9... Your face, jaw, and scalp completely relaxed, your mind clear and alert.

[PAUSE:20]

10... You have reached Focus 10. Your body is completely asleep while your mind remains awake and aware. You are in the perfect state for manifestation.

[PAUSE:30]

**Main Experience ({main_duration} minutes)**

You are now in the quantum field of infinite possibilities, where {scenario} already exists as your reality.

[PAUSE:30]

Visualize yourself living this reality right now. See yourself experiencing {scenario} in vivid detail. What does your environment look like?

[PAUSE:45]

Notice the colors, textures, and light around you. Feel the temperature, the air on your skin. You are fully present in this moment of achievement.

[PAUSE:60]

Who is with you in this reality? See their faces, hear their voices congratulating you, supporting you, celebrating with you.

[PAUSE:45]

Feel the emotions flooding through you - joy, satisfaction, gratitude, peace. Let these feelings fill every cell of your body.

[PAUSE:60]

Your success with {scenario} has ripple effects. See how it positively impacts your life, your loved ones, your community.

[PAUSE:45]

Breathe in this reality. You are not imagining - you are remembering your future that already exists.

[PAUSE:90]

Notice how natural this feels. Of course this is your reality. It was always meant to be this way.

[PAUSE:60]

Your subconscious mind is now reprogramming every neural pathway to align with this reality. Old limiting beliefs dissolve like mist.

[PAUSE:45]

Feel the confidence and certainty flowing through you. You know with absolute certainty that {scenario} is manifesting in perfect timing.

[PAUSE:60]

Take a moment to feel profound gratitude for this reality. Thank the universe, thank yourself, thank all who support you.

[PAUSE:75]

Your energy field is now permanently attuned to {scenario}. You are a magnet for all the resources, opportunities, and synchronicities needed.

[PAUSE:90]

Rest in this knowing. There is nothing more you need to do. The universe is handling all the details.

[PAUSE:120]

Continue to bask in this reality for the next few moments, knowing it is done.

[PAUSE:180]

**Return Sequence (2 minutes)**

In a moment, we'll return to normal waking consciousness, bringing with you all the energy and alignment from this meditation.

[PAUSE:20]

I'll count from 10 back to 1. With each number, you'll return more to normal awareness while maintaining your manifestation.

10... Beginning to return, your manifestation locked into your energy field.
[PAUSE:10]

9... Becoming aware of your physical body, feeling refreshed.
[PAUSE:10]

8... Energy beginning to return to your muscles.
[PAUSE:10]

7... Your breathing deepening naturally.
[PAUSE:10]

6... Beginning to move your fingers and toes gently.
[PAUSE:10]

5... Halfway back, feeling wonderful and aligned.
[PAUSE:10]

4... Your energy increasing, feeling revitalized.
[PAUSE:10]

3... Almost back, preparing to open your eyes.
[PAUSE:10]

2... Taking a deep breath, fully present.
[PAUSE:10]

1... Eyes open when ready, fully awake, alert, and aligned with {scenario}.

[PAUSE:15]

**Closing (1 minute)**

You have successfully completed your Hemi-Sync meditation for {scenario}. The work is done. Your consciousness has been reprogrammed.

Trust that everything is unfolding perfectly. You may notice synchronicities, opportunities, and shifts beginning immediately.

Remember: you are a powerful creator. What you experienced was not imagination - it was a preview of your incoming reality.

Thank you for this sacred time. Go forward knowing that {scenario} is manifesting now.

Namaste."""

    def generate_full_audio(self, script, api_key):
        """Generate complete audio for the entire meditation"""
        try:
            print(f"=== STARTING FULL AUDIO GENERATION ===")
            print(f"Script length: {len(script)} characters")
            print(f"API key provided: {bool(api_key)}")
            print(f"API key length: {len(api_key) if api_key else 0}")
            
            # Test import before attempting client initialization
            print(f"Attempting to import ElevenLabs...")
            try:
                from elevenlabs.client import ElevenLabs
                print("✅ ElevenLabs imported successfully")
            except ImportError as import_error:
                print(f"❌ IMPORT ERROR: {import_error}")
                print("Available packages:")
                import sys
                print([pkg for pkg in sys.modules.keys() if 'eleven' in pkg.lower()])
                raise
            
            print(f"Initializing ElevenLabs client...")
            try:
                client = ElevenLabs(api_key=api_key)
                print("✅ ElevenLabs client initialized successfully")
            except Exception as client_error:
                print(f"❌ CLIENT INITIALIZATION ERROR: {client_error}")
                print(f"API key starts with: {api_key[:10]}..." if api_key else "No API key")
                raise
            
            # Clean the script for TTS
            import re
            
            # Remove markdown formatting
            clean_text = re.sub(r'\*\*([^*]+)\*\*', r'\1', script)
            
            # Replace [PAUSE:X] with actual pauses
            # ElevenLabs supports SSML-like breaks
            clean_text = re.sub(r'\[PAUSE:(\d+)\]', lambda m: '... ' * max(1, int(m.group(1))//5), clean_text)
            
            # Split into manageable chunks (ElevenLabs has a 5000 char limit per request)
            chunks = []
            current_chunk = ""
            
            sentences = clean_text.split('. ')
            for sentence in sentences:
                if len(current_chunk) + len(sentence) < 4500:
                    current_chunk += sentence + ". "
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence + ". "
            
            if current_chunk:
                chunks.append(current_chunk.strip())
            
            print(f"Generating audio in {len(chunks)} chunks...")
            
            # Generate audio for each chunk
            audio_parts = []
            total_bytes = 0
            
            for i, chunk in enumerate(chunks):
                print(f"🎵 Generating chunk {i+1}/{len(chunks)} ({len(chunk)} chars)...")
                chunk_start_time = time.time()
                
                try:
                    print(f"  📤 Sending chunk to ElevenLabs API...")
                    audio_iterator = client.text_to_speech.convert(
                        voice_id="7nFoun39JV8WgdJ3vGmC",  # Calm meditation voice
                        text=chunk,
                        model_id="eleven_multilingual_v2",
                        voice_settings={
                            "stability": 0.75,
                            "similarity_boost": 0.75,
                            "style": 0.5,
                            "use_speaker_boost": True
                        }
                    )
                    print(f"  📥 Received audio iterator from API")
                    
                    print(f"  🔄 Converting audio iterator to bytes...")
                    audio_data = b"".join(list(audio_iterator))
                    audio_parts.append(audio_data)
                    total_bytes += len(audio_data)
                    
                    chunk_time = time.time() - chunk_start_time
                    print(f"  ✅ Chunk {i+1} SUCCESS: {len(audio_data)} bytes in {chunk_time:.1f}s")
                    
                except Exception as chunk_error:
                    print(f"  ❌ ERROR in chunk {i+1}: {chunk_error}")
                    print(f"  📝 Chunk preview: {chunk[:100]}..." if chunk else "Empty chunk")
                    import traceback
                    print(f"  🔍 Full traceback:")
                    traceback.print_exc()
                    raise
                
                # Small delay to avoid rate limiting
                time.sleep(0.5)
            
            # Combine all audio parts
            print(f"🔗 Combining {len(audio_parts)} audio chunks...")
            print(f"📊 Total audio bytes generated: {total_bytes:,}")
            
            full_audio = b"".join(audio_parts)
            final_size = len(full_audio)
            
            print(f"✅ AUDIO GENERATION COMPLETE!")
            print(f"📈 Final audio size: {final_size:,} bytes ({final_size/1024/1024:.2f} MB)")
            print(f"🎯 Audio duration estimate: ~{final_size/32000:.1f} minutes")
            
            return full_audio

        except Exception as e:
            print(f"❌ FULL AUDIO GENERATION FAILED: {e}")
            print(f"🔍 Error type: {type(e).__name__}")
            import traceback
            print("📝 Complete error traceback:")
            traceback.print_exc()
            raise