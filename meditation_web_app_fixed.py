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
session_results = {}  # Store results outside of Flask session

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

ENHANCED_PROMPT_TEMPLATE = """
Create a {duration}-minute Hemi-Sync style meditation script for the following scenario:
"{scenario}"

Follow this EXACT structure based on Monroe Institute methodology and 2024 neuroscience research:

1. **Introduction/Orientation (1-2 min)**: 
   - Welcome and clearly state the specific goal
   - Create immediate engagement with the scenario

2. **Energy Conversion Box (1-2 min)**:
   - Guide to create a mental container
   - Place worries and distractions inside
   - Emphasize security and later retrieval

3. **Resonant Tuning (2-3 min)**:
   - Breathing: inhale energy up to head
   - Exhale with humming vibration
   - Include [PAUSE:10-15] between cycles

4. **Resonant Energy Balloon (2-3 min)**:
   - Energy flows from head, around body, to feet
   - Two functions: retain personal energy, protect from external

5. **Affirmation Phase (1-2 min)**:
   - Standard: "I am more than my physical body..."
   - Scenario-specific affirmations in present tense

6. **Focus 10 Induction (3-4 min)**:
   - Count 1-10 with specific relaxation at each number
   - "Mind awake, body asleep"
   - Include [PAUSE:5] between counts

7. **Main Themed Content ({main_duration} min)**:
   - Multi-sensory visualization of the scenario
   - Present tense - as if already achieved
   - Emotional engagement with the outcome
   - Include [PAUSE:30-60] for deep integration
   - Use neuroscience insights on visualization creating neural pathways

8. **Integration and Anchoring (2-3 min)**:
   - Reinforce new neural pathways
   - Create mental/emotional anchor
   - Suggest daily practice

9. **Return Sequence (2-3 min)**:
   - Count 10-1 to full consciousness
   - Progressive alertness
   - Feeling refreshed and positive

10. **Closing (30 sec-1 min)**:
    - Brief reinforcement
    - Carry energy forward

IMPORTANT:
- Use [PAUSE:X] markers throughout (X = seconds)
- Make it vivid, transformative, and scientifically grounded
- Focus on feelings and sensations of achievement
- Total duration must be approximately {duration} minutes
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
    """Generate meditation script using Gemini."""
    try:
        update_progress(session_id, "Connecting to AI...", 10)
        
        # Calculate main content duration
        fixed_time = 15  # Approximate fixed sections time
        main_duration = max(5, duration - fixed_time)
        
        prompt = ENHANCED_PROMPT_TEMPLATE.format(
            scenario=scenario,
            duration=duration,
            main_duration=main_duration
        )
        
        update_progress(session_id, "Generating meditation script...", 20)
        
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
    """Remove markdown and formatting from script."""
    # Remove markdown headers
    script = re.sub(r'\*\*\d+\.\s*([^*]+)\*\*', r'\1', script)
    script = re.sub(r'\*\*([^*]+)\*\*', r'\1', script)
    script = re.sub(r'\*([^*]+)\*', r'\1', script)
    script = re.sub(r'^#+\s*', '', script, flags=re.MULTILINE)
    script = re.sub(r'^\*\s*', '', script, flags=re.MULTILINE)
    script = re.sub(r'\n\n+', '\n\n', script)
    return script.strip()

def generate_audio(script, session_id):
    """Generate audio from script using ElevenLabs."""
    try:
        update_progress(session_id, "Preparing audio generation...", 40)
        
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
                update_progress(session_id, f"Adding {pause_duration}s pause...", progress)
                voice_track += AudioSegment.silent(duration=pause_duration * 1000)
            else:
                update_progress(session_id, f"Synthesizing segment {current}/{total_segments}...", progress)
                
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
                    print(f"TTS error: {e}")
                    voice_track += AudioSegment.silent(duration=1000)
        
        update_progress(session_id, "Loading background music...", 85)
        
        # Load background
        background = AudioSegment.from_mp3(BACKGROUND_FILE)
        background = background - 12  # Reduce volume
        voice_track = voice_track - 4
        
        # Extend background if needed
        if len(voice_track) > len(background):
            silence_needed = len(voice_track) - len(background)
            background += AudioSegment.silent(duration=silence_needed)
        
        update_progress(session_id, "Mixing audio tracks...", 90)
        
        # Mix
        final_mix = background.overlay(voice_track, position=0)
        
        # Export
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"meditation_{timestamp}.mp3"
        filepath = os.path.join("generated_meditations", filename)
        
        os.makedirs("generated_meditations", exist_ok=True)
        
        update_progress(session_id, "Exporting final audio...", 95)
        final_mix.export(filepath, format="mp3", bitrate="192k")
        
        update_progress(session_id, "Audio generation complete!", 100)
        
        return filename, len(final_mix) / 1000 / 60  # duration in minutes
        
    except Exception as e:
        update_progress(session_id, f"Error generating audio: {str(e)}", None)
        traceback.print_exc()
        return None, None

def process_meditation_request(scenario, duration, generate_audio_flag, session_id):
    """Process the complete meditation generation request."""
    try:
        # Generate script
        script = generate_meditation_script(scenario, duration, session_id)
        if not script:
            return
        
        # Save transcript
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_scenario = re.sub(r'[^a-zA-Z0-9_\- ]', '', scenario)[:50].replace(' ', '_')
        transcript_filename = f"{safe_scenario}_{duration}min_{timestamp}.txt"
        transcript_path = os.path.join("transcripts", transcript_filename)
        
        os.makedirs("transcripts", exist_ok=True)
        
        with open(transcript_path, 'w', encoding='utf-8') as f:
            f.write(f"Meditation Transcript\n")
            f.write(f"Scenario: {scenario}\n")
            f.write(f"Duration: {duration} minutes\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*60}\n\n")
            f.write(script)
        
        # Store result
        result = {
            "status": "success",
            "script": script,
            "transcript_file": transcript_filename
        }
        
        # Generate audio if requested
        if generate_audio_flag:
            audio_filename, audio_duration = generate_audio(script, session_id)
            if audio_filename:
                result["audio_file"] = audio_filename
                result["audio_duration"] = audio_duration
        
        # Store final result in global dictionary
        session_results[session_id] = result
        
    except Exception as e:
        traceback.print_exc()
        update_progress(session_id, f"Error: {str(e)}", None)
        session_results[session_id] = {"status": "error", "error": str(e)}

@app.route('/')
def index():
    return render_template('meditation_generator.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    scenario = data.get('scenario', '').strip()
    duration = int(data.get('duration', 25))
    generate_audio_flag = data.get('generate_audio', False)
    
    if not scenario:
        return jsonify({"error": "Please provide a scenario"}), 400
    
    # Create session ID
    session_id = secrets.token_hex(8)
    progress_queues[session_id] = queue.Queue()
    
    # Start generation in background
    thread = threading.Thread(
        target=process_meditation_request,
        args=(scenario, duration, generate_audio_flag, session_id)
    )
    thread.start()
    
    return jsonify({"session_id": session_id})

@app.route('/progress/<session_id>')
def progress(session_id):
    """Get progress updates for a session."""
    if session_id not in progress_queues:
        return jsonify({"error": "Invalid session"}), 404
    
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
            "message": "Generation complete!",
            "percentage": 100,
            "complete": True,
            "result": session_results[session_id]
        })
        # Clean up
        del session_results[session_id]
        del progress_queues[session_id]
    
    return jsonify({"updates": updates})

@app.route('/download/<file_type>/<filename>')
def download(file_type, filename):
    """Download generated files."""
    if file_type == "transcript":
        directory = "transcripts"
    elif file_type == "audio":
        directory = "generated_meditations"
    else:
        return "Invalid file type", 400
    
    filepath = os.path.join(directory, filename)
    
    if not os.path.exists(filepath):
        return "File not found", 404
    
    return send_file(filepath, as_attachment=True)

if __name__ == '__main__':
    print("="*60)
    print("🧘 AI Meditation Generator Starting... (FIXED VERSION)")
    print("="*60)
    print("🌐 Server will be available at: http://127.0.0.1:5001")
    print("🌐 Or try: http://localhost:5001")
    print("💡 Press Ctrl+C to stop the server")
    print("="*60)
    app.run(debug=True, host='127.0.0.1', port=5001, threaded=True)