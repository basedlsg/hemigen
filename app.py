import os
from flask import Flask, render_template, request, send_from_directory, url_for, jsonify
from quick_generator_elevenlabs_run import generate_complete_meditation, ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID, elevenlabs_client, BACKGROUND_FILE

app = Flask(__name__)
app.secret_key = os.urandom(24) # For session management, flash messages

# Ensure the output directory exists
GENERATED_MEDITATIONS_DIR = "generated_meditations"
os.makedirs(GENERATED_MEDITATIONS_DIR, exist_ok=True)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    user_goal = request.form.get('goal')
    duration_str = request.form.get('duration', '20') # Default to 20 minutes
    
    if not user_goal:
        return jsonify({'status': 'error', 'message': "Please enter a meditation goal."}), 400

    try:
        duration_minutes = int(duration_str)
        if not 5 <= duration_minutes <= 60: # Basic validation for duration
            return jsonify({'status': 'error', 'message': "Duration must be between 5 and 60 minutes."}), 400
    except ValueError:
        return jsonify({'status': 'error', 'message': "Invalid duration. Please enter a number."}), 400

    # Check if ElevenLabs client is initialized (moved here for earlier feedback)
    if not ELEVENLABS_API_KEY or not ELEVENLABS_VOICE_ID:
        return jsonify({'status': 'error', 'message': "ElevenLabs API Key or Voice ID not configured in the backend."}), 500
    if elevenlabs_client is None:
         return jsonify({'status': 'error', 'message': "ElevenLabs client failed to initialize in the backend."}), 500
    if not os.path.exists(BACKGROUND_FILE):
        return jsonify({'status': 'error', 'message': f"Background audio file not found: {BACKGROUND_FILE}"}), 500


    print(f"Web app received goal: '{user_goal}', duration: {duration_minutes} min")
    
    # Call the refactored generation function
    # The function now handles its own print statements for progress
    output_filepath = generate_complete_meditation(user_goal, duration_minutes)
    
    if output_filepath:
        # output_filepath from generate_complete_meditation is the full path
        # We only need the filename part for the URL
        base_filename = os.path.basename(output_filepath)
        download_url = url_for('download_file', filename=base_filename, _external=False)
        return jsonify({
            'status': 'success',
            'goal': user_goal,
            'filename': base_filename,
            'download_url': download_url
        })
    else:
        return jsonify({
            'status': 'error',
            'goal': user_goal,
            'message': "Failed to generate meditation. Check server logs for details."
        }), 500

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(GENERATED_MEDITATIONS_DIR, filename, as_attachment=True)

if __name__ == '__main__':
    # Make sure to run with debug=False in a production environment
    app.run(debug=True, port=5002) 