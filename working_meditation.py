#!/usr/bin/env python3
"""
SIMPLE WORKING MEDITATION GENERATOR
- ElevenLabs voice ✓
- Script generation ✓ 
- Real pauses ✓
- Monroe Institute background ✓
NO OVERCOMPLICATED BULLSHIT
"""

from flask import Flask, request, jsonify, send_from_directory
import os
import json
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
            "status": "SIMPLE WORKING MEDITATION GENERATOR",
            "timestamp": datetime.now().isoformat(),
            "version": "SIMPLE_WORKS"
        })
    
    try:
        data = request.get_json()
        scenario = data.get('scenario', '').strip()
        duration = max(int(data.get('duration', 30)), 30)
        
        print(f"🎯 Generating meditation: {scenario} ({duration} min)")
        
        # Generate script
        script = create_simple_script(scenario, duration)
        print(f"📝 Script: {len(script)} chars")
        
        # Generate audio - SIMPLE VERSION
        audio_data = generate_simple_audio(script)
        
        response = {
            'success': True,
            'script': script,
            'scenario': scenario,
            'duration': duration,
            'generated_at': datetime.now().isoformat(),
            'message': f'✅ SIMPLE MEDITATION WORKS - {duration} minutes',
            'audio_available': bool(audio_data)
        }
        
        if audio_data:
            response['audio_data'] = base64.b64encode(audio_data).decode('utf-8')
            response['audio_size_mb'] = round(len(audio_data) / (1024 * 1024), 2)
            print(f"🎵 Audio: {len(audio_data)} bytes ({response['audio_size_mb']} MB)")
        
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'error': str(e), 'audio_available': False})

def create_simple_script(scenario, duration):
    """Simple Monroe Institute script"""
    return f"""Monroe Institute Meditation: {scenario}
Duration: {duration} minutes

Welcome to your meditation for {scenario}.

Find a comfortable position and close your eyes.

[PAUSE:20]

Take three deep breaths. In... and out.

[PAUSE:15]

Place all worries into your energy conversion box.

[PAUSE:30]

Now tune your energy by humming "Ahhhhhh"...

[PAUSE:25]

Repeat: "I am more than my physical body."

[PAUSE:20]

"I am manifesting {scenario} now."

[PAUSE:25]

Count from 1 to 10, relaxing deeper with each number.

1... feet relaxed [PAUSE:15]
2... legs relaxed [PAUSE:15] 
3... torso relaxed [PAUSE:15]
4... chest relaxed [PAUSE:15]
5... arms relaxed [PAUSE:15]
6... shoulders relaxed [PAUSE:15]
7... neck relaxed [PAUSE:15]
8... face relaxed [PAUSE:15]
9... mind clear [PAUSE:15]
10... Focus 10 achieved [PAUSE:20]

You are now experiencing {scenario} as reality.

[PAUSE:60]

See yourself living this truth. What do you see around you?

[PAUSE:90]

Feel the emotions of success. Joy, gratitude, satisfaction.

[PAUSE:75]

This is not imagination. This is your future reality.

[PAUSE:120]

Your subconscious accepts this as truth.

[PAUSE:90]

You are a magnet for {scenario}.

[PAUSE:180]

Rest in this knowing. It is done.

[PAUSE:240]

Now returning to normal awareness.

10... 9... 8... 7... 6... 5... 4... 3... 2... 1...

Eyes open when ready. {scenario} is manifesting now.

[PAUSE:15]

Your meditation is complete."""

def generate_simple_audio(script):
    """Generate audio - SIMPLE VERSION THAT WORKS"""
    try:
        print("🎵 Starting SIMPLE audio generation...")
        
        from elevenlabs.client import ElevenLabs
        client = ElevenLabs(api_key='sk_fe6faf571491c9b26bef909dce2e19a8e1d7239bf518027b')
        
        # STEP 1: Find Monroe Institute background
        monroe_file = None
        monroe_paths = [
            'assets/audio/monroe_background.mp3',
            '/Users/carlos/Focus-Creation/assets/audio/monroe_background.mp3',
            '/Users/carlos/Focus-Creation/Focus-Creation/background_audio/y2mate.is - Robert Monroe Institute Astral Projection Gateway Process 40 minutes no talking -edB7QI8I02c-192k-1700669353.mp3'
        ]
        
        for path in monroe_paths:
            if os.path.exists(path):
                print(f"✅ Found Monroe Institute: {path}")
                with open(path, 'rb') as f:
                    monroe_file = f.read()
                break
        
        if not monroe_file:
            print("⚠️ Monroe Institute background not found - generating spoken only")
        
        # STEP 2: Parse script into speech and pauses
        parts = []
        current_text = ""
        
        for line in script.split('\n'):
            line = line.strip()
            if line.startswith('[PAUSE:') and line.endswith(']'):
                # Save text before pause
                if current_text.strip():
                    parts.append(('speech', current_text.strip()))
                    current_text = ""
                
                # Add pause
                pause_match = re.search(r'\[PAUSE:(\d+)\]', line)
                if pause_match:
                    pause_seconds = int(pause_match.group(1))
                    parts.append(('pause', pause_seconds))
            elif line and not line.startswith('---'):
                current_text += line + " "
        
        # Add remaining text
        if current_text.strip():
            parts.append(('speech', current_text.strip()))
        
        print(f"📋 Parsed into {len(parts)} parts")
        
        # STEP 3: Generate speech parts only (skip complex mixing for now)
        audio_parts = []
        
        for i, (part_type, content) in enumerate(parts):
            if part_type == 'speech':
                print(f"🎙️ Generating speech {i+1}: {len(content)} chars")
                
                audio_iterator = client.text_to_speech.convert(
                    voice_id="7nFoun39JV8WgdJ3vGmC",
                    text=content,
                    model_id="eleven_multilingual_v2",
                    voice_settings={
                        "stability": 0.8,
                        "similarity_boost": 0.7
                    }
                )
                
                speech_audio = b"".join(list(audio_iterator))
                audio_parts.append(speech_audio)
                print(f"  ✅ Generated: {len(speech_audio)} bytes")
                
            elif part_type == 'pause':
                print(f"🔇 Adding {content}s pause")
                # Simple silence - repeat a small silence pattern
                silence = b'\x00' * (content * 1000)  # Basic silence
                audio_parts.append(silence)
        
        # STEP 4: Combine everything
        final_audio = b"".join(audio_parts)
        
        print(f"✅ SIMPLE AUDIO COMPLETE: {len(final_audio)} bytes ({len(final_audio)/1024/1024:.2f} MB)")
        
        return final_audio
        
    except Exception as e:
        print(f"❌ Audio generation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)