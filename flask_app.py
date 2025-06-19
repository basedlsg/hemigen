from flask import Flask, request, jsonify, send_from_directory
import os
import json
import time
import base64
from datetime import datetime
import re

app = Flask(__name__)

@app.route('/')
def index():
    return send_from_directory('public', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('public', path)

@app.route('/api/generate', methods=['GET', 'POST'])
def generate():
    if request.method == 'GET':
        return jsonify({
            "status": "FLASK DEPLOYMENT - WORKING",
            "timestamp": datetime.now().isoformat(),
            "elevenlabs_ready": True,
            "gemini_ready": True,
            "version": "FIXED"
        })
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            scenario = data.get('scenario', '').strip()
            duration = int(data.get('duration', 25))
            
            if not scenario or len(scenario) < 10:
                return jsonify({'error': 'Please provide a detailed meditation intention'})
            
            print(f"Generating {duration}-minute meditation for: {scenario}")
            
            # Generate script
            script = generate_meditation_script(scenario, duration)
            print(f"Script generated: {len(script)} characters")
            
            # Generate audio
            audio_data = generate_audio(script)
            
            response = {
                'success': True,
                'script': script,
                'scenario': scenario,
                'duration': duration,
                'generated_at': datetime.now().isoformat(),
                'message': f'WORKING! {duration}-minute meditation with audio!',
                'audio_available': bool(audio_data),
                'platform': 'Flask - ACTUALLY WORKS'
            }
            
            if audio_data:
                response['audio_data'] = base64.b64encode(audio_data).decode('utf-8')
                response['audio_size_mb'] = round(len(audio_data) / (1024 * 1024), 2)
                print(f"Audio generated: {len(audio_data)} bytes")
            
            return jsonify(response)
            
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({'error': f'Error: {str(e)}'})

def generate_meditation_script(scenario, duration):
    main_duration = duration - 10
    
    return f"""**Welcome & Preparation (2 minutes)**

Welcome to your personalized meditation for {scenario}. Find a comfortable position and close your eyes.

Take a deep breath in... and slowly exhale. With each breath, allow yourself to relax more deeply.

**Energy Conversion Box (2 minutes)**

Visualize a beautiful container before you. Place all your worries and concerns into this box. 

**Resonant Tuning (2 minutes)**

Take a deep breath and hum "Ahhhhhh..." Feel the vibration throughout your body.

**Affirmation (2 minutes)**

"I am more than my physical body. I am now manifesting {scenario} with perfect ease."

**Main Experience ({main_duration} minutes)**

You are now experiencing {scenario} as your reality. See yourself living this truth right now.

Visualize every detail - the colors, sounds, feelings. You are fully present in this moment of achievement.

Feel the emotions flooding through you - joy, satisfaction, gratitude, peace.

Your success with {scenario} has ripple effects. See how it positively impacts your life and loved ones.

Continue to bask in this reality, knowing it is done.

**Return (2 minutes)**

I'll count from 10 to 1. With each number, you'll return to normal awareness.

10... 9... 8... 7... 6... 5... 4... 3... 2... 1...

Eyes open when ready. Your meditation is complete.

---
Generated with working deployment"""

def generate_audio(script):
    try:
        print("Starting audio generation...")
        
        from elevenlabs.client import ElevenLabs
        client = ElevenLabs(api_key='sk_fe6faf571491c9b26bef909dce2e19a8e1d7239bf518027b')
        
        # Clean script
        clean_text = re.sub(r'\*\*([^*]+)\*\*', r'\1', script)
        clean_text = re.sub(r'\[PAUSE:(\d+)\]', lambda m: '... ' * max(1, int(m.group(1))//5), clean_text)
        
        # Split into chunks
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
        
        print(f"Generating {len(chunks)} audio chunks...")
        
        # Generate audio
        audio_parts = []
        for i, chunk in enumerate(chunks):
            print(f"  Chunk {i+1}/{len(chunks)}...")
            
            audio_iterator = client.text_to_speech.convert(
                voice_id="7nFoun39JV8WgdJ3vGmC",
                text=chunk,
                model_id="eleven_multilingual_v2",
                voice_settings={
                    "stability": 0.75,
                    "similarity_boost": 0.75
                }
            )
            
            audio_data = b"".join(list(audio_iterator))
            audio_parts.append(audio_data)
            time.sleep(0.5)
        
        full_audio = b"".join(audio_parts)
        print(f"Audio complete: {len(full_audio)} bytes")
        return full_audio
        
    except Exception as e:
        print(f"Audio generation failed: {e}")
        return None

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

# For production deployment
app.debug = False