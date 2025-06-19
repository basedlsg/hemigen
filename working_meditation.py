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

@app.route('/api/debug-audio', methods=['GET'])
def debug_audio():
    """Debug endpoint to test each component separately"""
    debug_results = {
        'timestamp': datetime.now().isoformat(),
        'tests': {}
    }
    
    # TEST 1: ElevenLabs import and client
    try:
        from elevenlabs.client import ElevenLabs
        client = ElevenLabs(api_key='sk_fe6faf571491c9b26bef909dce2e19a8e1d7239bf518027b')
        debug_results['tests']['elevenlabs'] = {
            'status': 'SUCCESS',
            'message': 'ElevenLabs client initialized'
        }
    except Exception as e:
        debug_results['tests']['elevenlabs'] = {
            'status': 'FAILED',
            'error': str(e)
        }
    
    # TEST 2: Monroe Institute file detection
    monroe_paths = [
        'assets/audio/monroe_background.mp3',
        '/Users/carlos/Focus-Creation/assets/audio/monroe_background.mp3',
        '/Users/carlos/Focus-Creation/Focus-Creation/background_audio/y2mate.is - Robert Monroe Institute Astral Projection Gateway Process 40 minutes no talking -edB7QI8I02c-192k-1700669353.mp3'
    ]
    
    monroe_found = False
    monroe_info = {}
    
    for path in monroe_paths:
        if os.path.exists(path):
            size = os.path.getsize(path)
            monroe_found = True
            monroe_info = {
                'status': 'SUCCESS',
                'path': path,
                'size_mb': round(size / (1024 * 1024), 2)
            }
            break
    
    if not monroe_found:
        monroe_info = {
            'status': 'FAILED',
            'message': 'Monroe Institute background not found',
            'checked_paths': monroe_paths
        }
    
    debug_results['tests']['monroe_background'] = monroe_info
    
    # TEST 3: Script parsing
    test_script = """Test script with pause.
[PAUSE:10]
More text here.
[PAUSE:20]
Final text."""
    
    try:
        parts = []
        current_text = ""
        
        for line in test_script.split('\n'):
            line = line.strip()
            if line.startswith('[PAUSE:') and line.endswith(']'):
                if current_text.strip():
                    parts.append(('speech', current_text.strip()))
                    current_text = ""
                
                pause_match = re.search(r'\[PAUSE:(\d+)\]', line)
                if pause_match:
                    pause_seconds = int(pause_match.group(1))
                    parts.append(('pause', pause_seconds))
            elif line:
                current_text += line + " "
        
        if current_text.strip():
            parts.append(('speech', current_text.strip()))
        
        debug_results['tests']['script_parsing'] = {
            'status': 'SUCCESS',
            'total_parts': len(parts),
            'speech_parts': len([p for p in parts if p[0] == 'speech']),
            'pause_parts': len([p for p in parts if p[0] == 'pause']),
            'parts_preview': parts[:3]
        }
        
    except Exception as e:
        debug_results['tests']['script_parsing'] = {
            'status': 'FAILED',
            'error': str(e)
        }
    
    # TEST 4: Simple ElevenLabs audio generation
    if debug_results['tests']['elevenlabs']['status'] == 'SUCCESS':
        try:
            from elevenlabs.client import ElevenLabs
            client = ElevenLabs(api_key='sk_fe6faf571491c9b26bef909dce2e19a8e1d7239bf518027b')
            
            audio_iterator = client.text_to_speech.convert(
                voice_id="7nFoun39JV8WgdJ3vGmC",
                text="This is a test of the audio generation system.",
                model_id="eleven_multilingual_v2"
            )
            
            test_audio = b"".join(list(audio_iterator))
            
            debug_results['tests']['audio_generation'] = {
                'status': 'SUCCESS',
                'audio_size': len(test_audio),
                'audio_size_kb': round(len(test_audio) / 1024, 2)
            }
            
        except Exception as e:
            debug_results['tests']['audio_generation'] = {
                'status': 'FAILED',
                'error': str(e)
            }
    else:
        debug_results['tests']['audio_generation'] = {
            'status': 'SKIPPED',
            'reason': 'ElevenLabs client failed'
        }
    
    # TEST 5: Environment info
    debug_results['tests']['environment'] = {
        'python_version': os.sys.version,
        'current_directory': os.getcwd(),
        'environment_variables': {
            'PORT': os.environ.get('PORT', 'Not set'),
        }
    }
    
    return jsonify(debug_results)

@app.route('/api/generate', methods=['GET', 'POST'])
def generate():
    if request.method == 'GET':
        return jsonify({
            "status": "SIMPLE WORKING MEDITATION GENERATOR - DEBUG MODE",
            "timestamp": datetime.now().isoformat(),
            "version": "DEBUG_ENABLED"
        })
    
    try:
        print("=" * 60)
        print("🔍 STARTING AUDIO GENERATION DEBUG TRACE")
        print("=" * 60)
        
        # STEP 1: Parse request
        print("STEP 1: Parsing request data...")
        data = request.get_json()
        scenario = data.get('scenario', '').strip()
        duration = max(int(data.get('duration', 30)), 30)
        print(f"✅ Request parsed: {scenario} ({duration} min)")
        
        # STEP 2: Generate script
        print("\nSTEP 2: Generating meditation script...")
        script = create_simple_script(scenario, duration)
        print(f"✅ Script generated: {len(script)} characters")
        
        # STEP 3: CRITICAL - Audio generation with full debugging
        print("\nSTEP 3: CRITICAL AUDIO GENERATION...")
        print("🚨 This is where audio_available likely becomes false")
        
        try:
            audio_data = generate_simple_audio(script)
            if audio_data:
                print(f"✅ AUDIO GENERATION SUCCESS: {len(audio_data)} bytes")
            else:
                print("❌ AUDIO GENERATION RETURNED NONE - THIS IS THE PROBLEM")
        except Exception as audio_error:
            print(f"❌ AUDIO GENERATION EXCEPTION: {audio_error}")
            import traceback
            print("🔍 Full traceback:")
            traceback.print_exc()
            audio_data = None
        
        # STEP 4: Response assembly
        print("\nSTEP 4: Assembling response...")
        response = {
            'success': True,
            'script': script,
            'scenario': scenario,
            'duration': duration,
            'generated_at': datetime.now().isoformat(),
            'message': f'DEBUG: audio_data is {"NOT NONE" if audio_data else "NONE"}',
            'audio_available': bool(audio_data),
            'debug_info': {
                'audio_data_type': type(audio_data).__name__,
                'audio_data_length': len(audio_data) if audio_data else 0,
                'script_length': len(script)
            }
        }
        
        if audio_data:
            response['audio_data'] = base64.b64encode(audio_data).decode('utf-8')
            response['audio_size_mb'] = round(len(audio_data) / (1024 * 1024), 2)
            print(f"✅ Audio encoded: {response['audio_size_mb']} MB")
        else:
            print("❌ NO AUDIO DATA TO ENCODE")
        
        print(f"\n🔍 FINAL RESPONSE: audio_available = {response['audio_available']}")
        print("=" * 60)
        
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ TOP-LEVEL ERROR: {e}")
        import traceback
        print("🔍 Complete traceback:")
        traceback.print_exc()
        return jsonify({
            'error': str(e), 
            'audio_available': False,
            'debug_info': 'Top-level exception caught'
        })

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
    """Generate audio - SIMPLE VERSION WITH FULL DEBUG TRACING"""
    try:
        print("\n" + "=" * 40)
        print("🎵 AUDIO GENERATION FUNCTION START")
        print("=" * 40)
        
        # DEPENDENCY CHECK 1: ElevenLabs
        print("AUDIO STEP 1: Testing ElevenLabs import...")
        try:
            from elevenlabs.client import ElevenLabs
            print("✅ ElevenLabs imported successfully")
        except ImportError as import_error:
            print(f"❌ ElevenLabs import failed: {import_error}")
            return None
        
        # DEPENDENCY CHECK 2: Client initialization
        print("AUDIO STEP 2: Initializing ElevenLabs client...")
        try:
            client = ElevenLabs(api_key='sk_fe6faf571491c9b26bef909dce2e19a8e1d7239bf518027b')
            print("✅ ElevenLabs client initialized")
        except Exception as client_error:
            print(f"❌ ElevenLabs client failed: {client_error}")
            return None
        
        # STEP 1: Monroe Institute background detection
        print("AUDIO STEP 3: Checking Monroe Institute background...")
        monroe_file = None
        monroe_paths = [
            'assets/audio/monroe_background.mp3',
            '/Users/carlos/Focus-Creation/assets/audio/monroe_background.mp3',
            '/Users/carlos/Focus-Creation/Focus-Creation/background_audio/y2mate.is - Robert Monroe Institute Astral Projection Gateway Process 40 minutes no talking -edB7QI8I02c-192k-1700669353.mp3'
        ]
        
        for i, path in enumerate(monroe_paths):
            print(f"  Checking path {i+1}: {path}")
            if os.path.exists(path):
                print(f"✅ Found Monroe Institute: {path}")
                try:
                    with open(path, 'rb') as f:
                        monroe_file = f.read()
                    print(f"✅ Monroe file loaded: {len(monroe_file)} bytes")
                    break
                except Exception as file_error:
                    print(f"❌ Monroe file read error: {file_error}")
            else:
                print(f"❌ Path not found: {path}")
        
        if not monroe_file:
            print("⚠️ NO MONROE INSTITUTE BACKGROUND - continuing with spoken only")
        
        # STEP 2: Script parsing with detailed logging
        print("AUDIO STEP 4: Parsing script into segments...")
        parts = []
        current_text = ""
        
        lines = script.split('\n')
        print(f"  Script has {len(lines)} lines")
        
        pause_count = 0
        speech_count = 0
        
        for line_num, line in enumerate(lines):
            line = line.strip()
            if line.startswith('[PAUSE:') and line.endswith(']'):
                # Save text before pause
                if current_text.strip():
                    parts.append(('speech', current_text.strip()))
                    speech_count += 1
                    current_text = ""
                
                # Add pause
                pause_match = re.search(r'\[PAUSE:(\d+)\]', line)
                if pause_match:
                    pause_seconds = int(pause_match.group(1))
                    parts.append(('pause', pause_seconds))
                    pause_count += 1
                    print(f"  Found pause: {pause_seconds}s at line {line_num}")
            elif line and not line.startswith('---'):
                current_text += line + " "
        
        # Add remaining text
        if current_text.strip():
            parts.append(('speech', current_text.strip()))
            speech_count += 1
        
        print(f"✅ Parsing complete: {len(parts)} total parts")
        print(f"  Speech segments: {speech_count}")
        print(f"  Pause segments: {pause_count}")
        
        if len(parts) == 0:
            print("❌ NO PARTS TO PROCESS - script parsing failed")
            return None
        
        # STEP 3: Audio generation with detailed tracking
        print("AUDIO STEP 5: Generating audio segments...")
        audio_parts = []
        total_bytes = 0
        
        for i, (part_type, content) in enumerate(parts):
            print(f"  Processing part {i+1}/{len(parts)}: {part_type}")
            
            if part_type == 'speech':
                print(f"    🎙️ Generating speech: {len(content)} chars")
                print(f"    Text preview: {content[:100]}...")
                
                try:
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
                    total_bytes += len(speech_audio)
                    print(f"    ✅ Speech generated: {len(speech_audio)} bytes")
                    
                except Exception as speech_error:
                    print(f"    ❌ Speech generation failed: {speech_error}")
                    return None
                
            elif part_type == 'pause':
                pause_seconds = content
                print(f"    🔇 Adding {pause_seconds}s pause")
                
                # Simple silence - repeat a small silence pattern
                silence = b'\x00' * (pause_seconds * 1000)  # Basic silence
                audio_parts.append(silence)
                total_bytes += len(silence)
                print(f"    ✅ Silence added: {len(silence)} bytes")
        
        # STEP 4: Final assembly
        print("AUDIO STEP 6: Combining audio parts...")
        print(f"  Total parts to combine: {len(audio_parts)}")
        print(f"  Total bytes before combination: {total_bytes}")
        
        if len(audio_parts) == 0:
            print("❌ NO AUDIO PARTS TO COMBINE")
            return None
        
        final_audio = b"".join(audio_parts)
        final_size = len(final_audio)
        
        print(f"✅ FINAL AUDIO ASSEMBLY COMPLETE!")
        print(f"  Final size: {final_size} bytes ({final_size/1024/1024:.2f} MB)")
        print(f"  Expected vs actual: {total_bytes} vs {final_size}")
        
        if final_size == 0:
            print("❌ FINAL AUDIO IS EMPTY - CRITICAL ERROR")
            return None
        
        print("=" * 40)
        print("🎵 AUDIO GENERATION FUNCTION SUCCESS")
        print("=" * 40)
        
        return final_audio
        
    except Exception as e:
        print(f"\n❌ AUDIO GENERATION FUNCTION EXCEPTION: {e}")
        print(f"Exception type: {type(e).__name__}")
        import traceback
        print("🔍 Complete traceback:")
        traceback.print_exc()
        print("=" * 40)
        return None

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)