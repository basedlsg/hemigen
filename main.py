#!/usr/bin/env python3
"""
REPLIT DEPLOYMENT MAIN FILE
Simple entry point for meditation generator
"""

if __name__ == "__main__":
    # Import our working Flask app
    from flask_app import app
    
    print("🚀 Starting Meditation Generator on Replit...")
    print("📝 Script generation: READY")
    print("🎵 Audio generation: READY") 
    print("🔗 ElevenLabs integration: ACTIVE")
    
    # Run on Replit's default configuration
    app.run(
        host='0.0.0.0', 
        port=5000, 
        debug=False,
        threaded=True
    )