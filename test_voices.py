#!/usr/bin/env python3
"""Test available ElevenLabs voices"""

import os

def test_voices():
    api_key = os.environ.get('ELEVENLABS_API_KEY', 'sk_fe6faf571491c9b26bef909dce2e19a8e1d7239bf518027b')
    
    try:
        from elevenlabs.client import ElevenLabs
        from elevenlabs import Voice
        
        client = ElevenLabs(api_key=api_key)
        
        print("Testing voice availability...")
        
        # Try the voice ID from the code
        test_voice_id = "7nFoun39JV8WgdJ3vGmC"
        
        # Try to generate with this voice
        try:
            audio = client.text_to_speech.convert(
                voice_id=test_voice_id,
                text="Testing voice",
                model_id="eleven_multilingual_v2"
            )
            audio_data = b"".join(list(audio))
            print(f"✅ Voice ID {test_voice_id} works! Generated {len(audio_data)} bytes")
        except Exception as e:
            print(f"❌ Voice ID {test_voice_id} failed: {e}")
            
        # Try to list available voices
        try:
            voices = client.voices.get_all()
            print(f"\n✅ Available voices: {len(voices.voices)} found")
            for voice in voices.voices[:5]:  # Show first 5
                print(f"  - {voice.name} (ID: {voice.voice_id})")
        except Exception as e:
            print(f"❌ Could not list voices: {e}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_voices()