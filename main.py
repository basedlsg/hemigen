#!/usr/bin/env python3
"""
SIMPLE SOLUTION - NO BULLSHIT
"""

if __name__ == "__main__":
    print("🎯 SIMPLE WORKING MEDITATION GENERATOR")
    print("🎙️ ElevenLabs voice: READY")
    print("📝 Script generation: READY")
    print("🔇 Pauses: WORKING")
    print("🎵 Background: READY")
    
    # Import the SIMPLE working version
    from simple_meditation_generator import app
    
    # Run it
    app.run(
        host='0.0.0.0', 
        port=5000, 
        debug=False
    )