#!/usr/bin/env python3
"""Test ElevenLabs API integration"""

import os
import sys

def test_elevenlabs():
    # Get API key
    api_key = os.environ.get('ELEVENLABS_API_KEY', '')
    if not api_key:
        # Fallback to hardcoded key from generate.py
        api_key = 'sk_fe6faf571491c9b26bef909dce2e19a8e1d7239bf518027b'
    
    print(f"Testing ElevenLabs API...")
    print(f"API Key present: {bool(api_key)}")
    print(f"API Key length: {len(api_key)}")
    
    try:
        from elevenlabs.client import ElevenLabs
        from elevenlabs import Voice, VoiceSettings
        
        print("\n✅ ElevenLabs library imported successfully")
        
        # Initialize client
        client = ElevenLabs(api_key=api_key)
        print("✅ Client initialized")
        
        # Test text
        test_text = "Testing ElevenLabs API integration. This is a short test."
        
        # Try to generate audio
        print("\nAttempting to generate audio...")
        audio_iterator = client.text_to_speech.convert(
            voice_id="7nFoun39JV8WgdJ3vGmC",  # Same voice ID from generate.py
            text=test_text,
            model_id="eleven_multilingual_v2",
            voice_settings={
                "stability": 0.75,
                "similarity_boost": 0.75,
                "style": 0.5,
                "use_speaker_boost": True
            }
        )
        
        # Collect audio data
        audio_data = b"".join(list(audio_iterator))
        print(f"✅ Audio generated successfully! Size: {len(audio_data)} bytes")
        
        # Save test audio
        with open("test_audio.mp3", "wb") as f:
            f.write(audio_data)
        print("✅ Test audio saved as test_audio.mp3")
        
        return True
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("Make sure to install: pip install elevenlabs")
        return False
        
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_elevenlabs()
    sys.exit(0 if success else 1)