#!/usr/bin/env python3
"""Validate API keys are working"""

import os
import sys

def validate_gemini():
    """Test Gemini API key"""
    api_key = os.environ.get('GEMINI_API_KEY', 'AIzaSyAqko3NqGS-GtXhzm8LeiZ3xUEyo_XIqLo')
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        response = model.generate_content("Say 'API key is valid'")
        
        print(f"✅ Gemini API key is valid")
        print(f"   Response: {response.text.strip()[:50]}...")
        return True
    except Exception as e:
        print(f"❌ Gemini API key error: {e}")
        return False

def validate_elevenlabs():
    """Test ElevenLabs API key"""
    api_key = os.environ.get('ELEVENLABS_API_KEY', 'sk_fe6faf571491c9b26bef909dce2e19a8e1d7239bf518027b')
    
    try:
        from elevenlabs.client import ElevenLabs
        
        client = ElevenLabs(api_key=api_key)
        
        # Try to get user info or generate a tiny audio
        audio = client.text_to_speech.convert(
            voice_id="7nFoun39JV8WgdJ3vGmC",
            text="Test",
            model_id="eleven_multilingual_v2"
        )
        
        audio_data = b"".join(list(audio))
        
        print(f"✅ ElevenLabs API key is valid")
        print(f"   Generated {len(audio_data)} bytes of audio")
        return True
    except Exception as e:
        print(f"❌ ElevenLabs API key error: {e}")
        
        # Check if it's an authentication error
        if "401" in str(e) or "unauthorized" in str(e).lower():
            print("   This appears to be an authentication error - the API key may be invalid or expired")
        elif "403" in str(e) or "forbidden" in str(e).lower():
            print("   This appears to be a permissions error - the API key may not have access to this feature")
        elif "quota" in str(e).lower() or "limit" in str(e).lower():
            print("   This appears to be a quota/limit error - the API key may have exceeded its usage limits")
        
        return False

def main():
    print("Validating API keys...\n")
    
    gemini_valid = validate_gemini()
    print()
    elevenlabs_valid = validate_elevenlabs()
    
    print("\n" + "="*50)
    if gemini_valid and elevenlabs_valid:
        print("✅ All API keys are valid!")
        return 0
    else:
        print("❌ Some API keys have issues")
        return 1

if __name__ == "__main__":
    sys.exit(main())