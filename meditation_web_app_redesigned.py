from flask import Flask, render_template, request, jsonify, send_file
import google.generativeai as genai
from elevenlabs.client import ElevenLabs
from pydub import AudioSegment
import os
import re
import io
import json
from datetime import datetime
import secrets
import threading
import queue
import time
import traceback

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# API Configuration
GEMINI_API_KEY = "AIzaSyAqko3NqGS-GtXhzm8LeiZ3xUEyo_XIqLo"
ELEVENLABS_API_KEY = "sk_fe6faf571491c9b26bef909dce2e19a8e1d7239bf518027b"
ELEVENLABS_VOICE_ID = "7nFoun39JV8WgdJ3vGmC"
BACKGROUND_FILE = "/Users/carlos/Focus-Creation/Focus-Creation/background_audio/y2mate.is - Robert Monroe Institute Astral Projection Gateway Process 40 minutes no talking -edB7QI8I02c-192k-1700669353.mp3"

# Initialize APIs
genai.configure(api_key=GEMINI_API_KEY)
elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

# Global progress tracking and results storage
progress_queues = {}
session_results = {}

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

# Enhanced prompt template with 2024-2025 neuroscience insights
ENHANCED_PROMPT_TEMPLATE = """
Create a {duration}-minute Hemi-Sync style meditation script for the following intention:
"{scenario}"

Based on the latest 2024-2025 neuroscience research on meditation and manifestation:

STRUCTURE (Follow Monroe Institute methodology exactly):

1. **Introduction/Orientation (1-2 min)**: 
   - Warm welcome acknowledging their specific intention
   - Brief explanation of the journey ahead
   - Create immediate emotional connection to the goal

2. **Energy Conversion Box (1-2 min)**:
   - Guide creation of mental container for worries/distractions
   - Emphasize complete security and later retrieval
   - Use present tense: "You are now placing..." not "You will place..."

3. **Resonant Tuning (2-3 min)**:
   - Breathing exercises: inhale energy up through body to head
   - Exhale with humming vibration (mention the physical sensation)
   - Include [PAUSE:10-15] between breathing cycles
   - 3-4 complete cycles minimum

4. **Resonant Energy Balloon (2-3 min)**:
   - Energy flows from head, around body, enters through feet
   - Two key functions: retain personal energy, protect from external
   - Visualize as shimmering, protective sphere
   - Include [PAUSE:15-20] for feeling the protection

5. **Affirmation Phase (1-2 min)**:
   - Standard: "I am more than my physical body. Because I am more than physical matter, I can perceive that which is greater than the physical world."
   - Specific affirmations related to the intention (present tense)
   - Include [PAUSE:10] between affirmations

6. **Focus 10 Induction (3-4 min)**:
   - Count 1-10 with specific relaxation suggestions at each number
   - Emphasize "mind awake, body asleep" concept
   - Include [PAUSE:5] between each count
   - Progressive deepening with each number

7. **Main Themed Content ({main_duration} min)**:
   Based on 2024 neuroscience research on visualization and neural plasticity:
   - Use multi-sensory visualization (visual, auditory, kinesthetic, emotional)
   - Present tense as if the intention is already achieved
   - Include the FEELING states of having achieved the goal
   - Incorporate quantum field concepts where appropriate
   - Use [PAUSE:30-60] for deep integration periods
   - Guide through specific scenarios related to the intention
   - Emphasize emotional states and body sensations
   - Include anchoring techniques for future recall

8. **Integration and Anchoring (2-3 min)**:
   - Reinforce new neural pathways created during visualization
   - Create mental/emotional anchor for daily recall
   - Suggest daily practice for neuroplasticity enhancement
   - Include [PAUSE:15-20] for integration

9. **Return Sequence (2-3 min)**:
   - Count 10-1 to return to normal consciousness (C-1)
   - Progressive return of physical awareness
   - Suggestions of feeling refreshed, energized, positive
   - Carry the energy and certainty forward
   - Include [PAUSE:3-5] between counts

10. **Closing (30 sec-1 min)**:
    - Brief reinforcement of the intention
    - Encouragement to carry the energy throughout the day
    - Reminder of daily practice benefits

CRITICAL REQUIREMENTS:
- Use [PAUSE:X] markers throughout (X = seconds)
- Language should be suggestive, not commanding ("you may notice", "allow yourself")
- Focus intensely on the FEELING states of achievement
- Include sensory details specific to the intention
- Maintain Monroe Institute's exploratory, non-dogmatic approach
- Total estimated duration should match {duration} minutes
- Make it profoundly transformative and scientifically grounded
- Use present tense throughout main content as if goal is already achieved
"""

def update_progress(session_id, message, percentage=None):
    """Update progress for a specific session."""
    if session_id in progress_queues:
        progress_queues[session_id].put({
            "message": message,
            "percentage": percentage,
            "timestamp": datetime.now().isoformat()
        })

def generate_meditation_script(scenario, duration, session_id):
    """Generate meditation script using Gemini with enhanced prompting."""
    try:
        update_progress(session_id, "Connecting to AI consciousness stream...", 10)
        
        # Calculate main content duration
        fixed_time = 15  # Approximate fixed sections time
        main_duration = max(5, duration - fixed_time)
        
        prompt = ENHANCED_PROMPT_TEMPLATE.format(
            scenario=scenario,
            duration=duration,
            main_duration=main_duration
        )
        
        update_progress(session_id, "Generating personalized meditation script...", 20)
        
        model = genai.GenerativeModel(
            model_name="gemini-1.5-pro-latest",
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        response = model.generate_content(prompt)
        script = response.text.strip()
        
        update_progress(session_id, "Script generated successfully!", 30)
        return script
        
    except Exception as e:
        update_progress(session_id, f"Error generating script: {str(e)}", None)
        return None

def clean_script_for_tts(script):
    """Remove markdown and formatting from script for TTS."""
    # Remove markdown headers and formatting
    script = re.sub(r'\*\*\d+\.\s*([^*]+)\*\*', r'\1', script)
    script = re.sub(r'\*\*([^*]+)\*\*', r'\1', script)
    script = re.sub(r'\*([^*]+)\*', r'\1', script)
    script = re.sub(r'^#+\s*', '', script, flags=re.MULTILINE)
    script = re.sub(r'^\*\s*', '', script, flags=re.MULTILINE)
    script = re.sub(r'\n\n+', '\n\n', script)
    return script.strip()

def generate_audio(script, session_id):
    """Generate audio from script using ElevenLabs with error handling."""
    try:
        update_progress(session_id, "Initializing neural voice synthesis...", 40)
        
        # Clean script
        clean_script = clean_script_for_tts(script)
        
        # Split into segments
        segments = re.split(r'(\[PAUSE:\d+\])', clean_script)
        voice_track = AudioSegment.empty()
        
        total_segments = len([s for s in segments if s.strip()])
        current = 0
        
        for segment in segments:
            segment = segment.strip()
            if not segment:
                continue
                
            current += 1
            progress = 40 + (current / total_segments * 40)  # 40-80%
            
            pause_match = re.match(r'\[PAUSE:(\d+)\]', segment)
            if pause_match:
                pause_duration = int(pause_match.group(1))
                update_progress(session_id, f"Adding {pause_duration}s meditative pause...", progress)
                voice_track += AudioSegment.silent(duration=pause_duration * 1000)
            else:
                update_progress(session_id, f"Synthesizing meditation segment {current}/{total_segments}...", progress)
                
                try:
                    audio_data = elevenlabs_client.text_to_speech.convert(
                        voice_id=ELEVENLABS_VOICE_ID,
                        text=segment,
                        model_id="eleven_multilingual_v2"
                    )
                    audio_bytes = b"".join(list(audio_data))
                    audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")
                    voice_track += audio_segment
                except Exception as e:
                    print(f"TTS error for segment: {e}")
                    update_progress(session_id, f"TTS service temporarily unavailable, adding silence...", progress)
                    # Add proportional silence based on text length
                    estimated_duration = len(segment) * 50  # ~50ms per character
                    voice_track += AudioSegment.silent(duration=estimated_duration)
        
        update_progress(session_id, "Loading Hemi-Sync background frequencies...", 85)
        
        # Load background audio
        if not os.path.exists(BACKGROUND_FILE):
            update_progress(session_id, "Background audio not found, creating voice-only version...", 90)
            # Export voice-only version
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"meditation_voice_only_{timestamp}.mp3"
            filepath = os.path.join("generated_meditations", filename)
            os.makedirs("generated_meditations", exist_ok=True)
            voice_track.export(filepath, format="mp3", bitrate="192k")
            update_progress(session_id, "Voice-only meditation created successfully!", 100)
            return filename, len(voice_track) / 1000 / 60
        
        background = AudioSegment.from_mp3(BACKGROUND_FILE)
        background = background - 12  # Reduce volume
        voice_track = voice_track - 4   # Slightly reduce voice
        
        # Extend background if needed
        if len(voice_track) > len(background):
            silence_needed = len(voice_track) - len(background)
            background += AudioSegment.silent(duration=silence_needed)
        
        update_progress(session_id, "Mixing voice with Hemi-Sync frequencies...", 90)
        
        # Mix tracks
        final_mix = background.overlay(voice_track, position=0)
        
        # Export with high quality
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"meditation_hemi_sync_{timestamp}.mp3"
        filepath = os.path.join("generated_meditations", filename)
        
        os.makedirs("generated_meditations", exist_ok=True)
        
        update_progress(session_id, "Finalizing your meditation audio...", 95)
        final_mix.export(filepath, format="mp3", bitrate="192k")
        
        update_progress(session_id, "Meditation creation complete!", 100)
        
        return filename, len(final_mix) / 1000 / 60
        
    except Exception as e:
        update_progress(session_id, f"Audio generation error: {str(e)}", None)
        traceback.print_exc()
        return None, None

def process_meditation_request(scenario, duration, generate_audio_flag, session_id):
    """Process the complete meditation generation request."""
    try:
        # Generate script
        script = generate_meditation_script(scenario, duration, session_id)
        if not script:
            return
        
        # Save transcript with enhanced metadata
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_scenario = re.sub(r'[^a-zA-Z0-9_\- ]', '', scenario)[:50].replace(' ', '_')
        transcript_filename = f"{safe_scenario}_{duration}min_{timestamp}.txt"
        transcript_path = os.path.join("transcripts", transcript_filename)
        
        os.makedirs("transcripts", exist_ok=True)
        
        with open(transcript_path, 'w', encoding='utf-8') as f:
            f.write(f"Zenith Flow Meditation Transcript\n")
            f.write(f"{'='*50}\n")
            f.write(f"Intention: {scenario}\n")
            f.write(f"Duration: {duration} minutes\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Technology: Hemi-Sync + AI-Generated Script\n")
            f.write(f"Neuroscience: 2024-2025 Research Based\n")
            f.write(f"{'='*50}\n\n")
            f.write(script)
        
        # Store result
        result = {
            "status": "success",
            "script": script,
            "transcript_file": transcript_filename,
            "intention": scenario,
            "duration": duration
        }
        
        # Generate audio if requested
        if generate_audio_flag:
            audio_filename, audio_duration = generate_audio(script, session_id)
            if audio_filename:
                result["audio_file"] = audio_filename
                result["audio_duration"] = audio_duration
        
        # Store final result
        session_results[session_id] = result
        
    except Exception as e:
        traceback.print_exc()
        update_progress(session_id, f"Error: {str(e)}", None)
        session_results[session_id] = {"status": "error", "error": str(e)}

@app.route('/')
def index():
    """Serve the full-screen Hemi-gen interface."""
    return render_template('hemi_gen_fullscreen.html')

@app.route('/generate', methods=['POST'])
def generate():
    """Handle meditation generation requests."""
    data = request.json
    scenario = data.get('scenario', '').strip()
    duration = int(data.get('duration', 25))
    generate_audio_flag = data.get('generate_audio', False)
    
    # Enhanced validation
    if not scenario:
        return jsonify({"error": "Please describe your meditation intention"}), 400
    
    if len(scenario) < 10:
        return jsonify({"error": "Please provide a more detailed description of your intention (at least 10 characters)"}), 400
    
    if duration < 10 or duration > 60:
        return jsonify({"error": "Duration must be between 10 and 60 minutes"}), 400
    
    # Create session ID
    session_id = secrets.token_hex(8)
    progress_queues[session_id] = queue.Queue()
    
    # Start generation in background thread
    thread = threading.Thread(
        target=process_meditation_request,
        args=(scenario, duration, generate_audio_flag, session_id),
        daemon=True
    )
    thread.start()
    
    return jsonify({"session_id": session_id})

@app.route('/progress/<session_id>')
def progress(session_id):
    """Get progress updates for a session."""
    if session_id not in progress_queues:
        return jsonify({"error": "Invalid session ID"}), 404
    
    updates = []
    q = progress_queues[session_id]
    
    # Get all available updates
    while not q.empty():
        try:
            updates.append(q.get_nowait())
        except:
            break
    
    # Check if generation is complete
    if session_id in session_results:
        updates.append({
            "message": "Your meditation is ready!",
            "percentage": 100,
            "complete": True,
            "result": session_results[session_id]
        })
        # Clean up
        del session_results[session_id]
        if session_id in progress_queues:
            del progress_queues[session_id]
    
    return jsonify({"updates": updates})

@app.route('/download/<file_type>/<filename>')
def download(file_type, filename):
    """Download generated files with security checks."""
    # Validate file type
    if file_type not in ["transcript", "audio"]:
        return "Invalid file type", 400
    
    # Set directory based on file type
    directory = "transcripts" if file_type == "transcript" else "generated_meditations"
    filepath = os.path.join(directory, filename)
    
    # Security: Ensure the path is within our expected directories
    if not os.path.abspath(filepath).startswith(os.path.abspath(directory)):
        return "Invalid file path", 400
    
    if not os.path.exists(filepath):
        return "File not found", 404
    
    # Set appropriate content type
    mimetype = 'text/plain' if file_type == "transcript" else 'audio/mpeg'
    
    return send_file(filepath, as_attachment=True, mimetype=mimetype)

@app.errorhandler(404)
def not_found(error):
    """Custom 404 handler."""
    return render_template('hemi_gen_fullscreen.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Custom 500 handler."""
    return jsonify({"error": "Internal server error. Please try again."}), 500

if __name__ == '__main__':
    print("="*60)
    print("🧘 Hemi-gen - AI Meditation Generator")
    print("🎨 Full-Screen 2024-2025 Interface")
    print("="*60)
    print("🌐 Server: http://127.0.0.1:5001")
    print("💫 Features: Full-screen layout, Glassmorphism, Breathing Animations")
    print("🧠 AI: Enhanced Gemini Pro with latest neuroscience research")
    print("🎵 Audio: Neural voice synthesis + Hemi-Sync frequencies")
    print("💡 Press Ctrl+C to stop")
    print("="*60)
    
    # Ensure directories exist
    os.makedirs("transcripts", exist_ok=True)
    os.makedirs("generated_meditations", exist_ok=True)
    
    app.run(debug=True, host='127.0.0.1', port=5001, threaded=True)