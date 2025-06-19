#!/usr/bin/env python3
"""Test the full API flow locally"""

import json
import os
import time
import re

def test_script_generation():
    """Test script generation with fallback"""
    scenario = "Manifesting $90,000 for financial freedom"
    duration = 30
    
    print("=== Testing Script Generation ===")
    
    # Try Gemini first
    gemini_key = os.environ.get('GEMINI_API_KEY', 'AIzaSyAqko3NqGS-GtXhzm8LeiZ3xUEyo_XIqLo')
    
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
        script = response.text.strip()
        print("✅ Gemini script generated successfully")
        print(f"Script length: {len(script)} characters")
        return script
        
    except Exception as e:
        print(f"❌ Gemini failed: {e}")
        print("Using fallback script generation")
        # Return a simple fallback
        return f"Fallback meditation script for {scenario}"

def test_audio_generation(script):
    """Test audio generation"""
    print("\n=== Testing Audio Generation ===")
    
    elevenlabs_key = os.environ.get('ELEVENLABS_API_KEY', 'sk_fe6faf571491c9b26bef909dce2e19a8e1d7239bf518027b')
    
    try:
        from elevenlabs.client import ElevenLabs
        
        client = ElevenLabs(api_key=elevenlabs_key)
        
        # Clean the script for TTS
        clean_text = re.sub(r'\*\*([^*]+)\*\*', r'\1', script)
        clean_text = re.sub(r'\[PAUSE:(\d+)\]', lambda m: '... ' * max(1, int(m.group(1))//5), clean_text)
        
        # Take only first 1000 chars for testing
        test_chunk = clean_text[:1000]
        
        print(f"Generating audio for {len(test_chunk)} characters...")
        
        audio_iterator = client.text_to_speech.convert(
            voice_id="7nFoun39JV8WgdJ3vGmC",
            text=test_chunk,
            model_id="eleven_multilingual_v2",
            voice_settings={
                "stability": 0.75,
                "similarity_boost": 0.75,
                "style": 0.5,
                "use_speaker_boost": True
            }
        )
        
        audio_data = b"".join(list(audio_iterator))
        print(f"✅ Audio generated: {len(audio_data)} bytes")
        return audio_data
        
    except Exception as e:
        print(f"❌ Audio generation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Test the full flow"""
    print("Testing full API flow...\n")
    
    # Test script generation
    script = test_script_generation()
    
    # Test audio generation
    audio_data = test_audio_generation(script)
    
    # Create response like API would
    response = {
        'success': True,
        'script': script[:500] + "...",  # Truncated for display
        'scenario': "Manifesting $90,000 for financial freedom",
        'duration': 30,
        'audio_available': bool(audio_data),
        'api_version': '4.0'
    }
    
    if audio_data:
        response['audio_size_mb'] = round(len(audio_data) / (1024 * 1024), 2)
    
    print("\n=== Final Response ===")
    print(json.dumps(response, indent=2))
    
    return audio_data is not None

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)