import google.generativeai as genai
import os
# MODIFIED ElevenLabs imports
from elevenlabs.client import ElevenLabs
from elevenlabs import Voice as ElevenVoiceObject, VoiceSettings as ElevenVoiceSettings 
from pydub import AudioSegment
import re
import io

# --- Gemini API Key Configuration ---
GEMINI_API_KEY = "AIzaSyAqko3NqGS-GtXhzm8LeiZ3xUEyo_XIqLo" # As provided by user
genai.configure(api_key=GEMINI_API_KEY)

generation_config = {
    "temperature": 0.7,
    "top_p": 1.0,
    "top_k": 1,
    "max_output_tokens": 2048,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

# --- ElevenLabs API Key Configuration ---
ELEVENLABS_API_KEY = "sk_fe6faf571491c9b26bef909dce2e19a8e1d7239bf518027b" # As provided by user
# elevenlabs_set_api_key(ELEVENLABS_API_KEY) # No longer needed if passed to client
ELEVENLABS_VOICE_ID = "7nFoun39JV8WgdJ3vGmC" # As provided by user

# MODIFIED: Instantiate ElevenLabs client
elevenlabs_client = None
if ELEVENLABS_API_KEY:
    try:
        elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    except Exception as e:
        print(f"Failed to initialize ElevenLabs client: {e}")
else:
    print("ElevenLabs API Key not found. TTS will be skipped.")

def generate_meditation_script_gemini_v1(user_goal, main_content_duration_minutes=15):
    # This function remains the same as in the Google version, generating the script text
    script = f"""
Welcome. You are more than your physical body. Today, our journey is to explore {user_goal}, moving into a state of expanded awareness.
[PAUSE:3]
Please, find a comfortable position, loosen any tight clothing, and gently close your eyes.
[PAUSE:3]
Take a long, deep breath... hold it for a moment... and now, exhale slowly, completely.
[PAUSE:5]
As you exhale, let all tensions, all concerns, just flow out of you, carried away with your breath. Feel your body becoming calm and relaxed.
[PAUSE:5]
Now, in your mind\'s eye, create your Energy Conversion Box. This is your mental container to hold any concerns, distractions, or interferences. See it, feel it, imagine it.
[PAUSE:3]
Place any thoughts, any worries, any distractions gently inside this box. You can use concrete symbols if you wish.
[PAUSE:3]
And now, close the lid. Know that these things are safely stored and will be there if you need them when you return. For now, they are set aside, allowing you to focus.
[PAUSE:5]
Let\'s begin our Resonant Tuning. This helps vitalize and charge your entire system. Breathe only slightly deeper than you normally would.
[PAUSE:3]
As you inhale, imagine pulling sparkling, vibrant energy into all parts of your body.
[PAUSE:2]
And as you exhale, create a gentle humming sound... hmmmmmmmm. Feel the vibrations. Do this at your own pace.
[PAUSE:10]
Once more. Breathe in that sparkling energy... and hum as you exhale... hmmmmmmm.
[PAUSE:7]
Now, repeat this Affirmation mentally, after me: I am more than my physical body.
[PAUSE:3]
Because I am more than physical matter, I can perceive that which is greater than the physical world. I am open to this experience.
[PAUSE:5]
We will now move into Focus 10, the state of mind awake, body asleep. I will count from one to ten. As I count, allow yourself to drift deeper into relaxation.
[PAUSE:2]
One... you are beginning to relax more and more.
[PAUSE:2]
Two... letting go of all physical tension. Your body knows how to do this.
[PAUSE:2]
Three... drifting deeper, calmly and comfortably.
[PAUSE:2]
Four... mind awake, body relaxed.
[PAUSE:2]
Five... your body is calm, comfortable, and at ease.
[PAUSE:2]
Six... deeper and deeper into profound relaxation.
[PAUSE:2]
Seven... just letting go completely.
[PAUSE:2]
Eight... mind remains awake and alert, body deeply asleep.
[PAUSE:2]
Nine... drifting into total relaxation, secure and comfortable.
[PAUSE:2]
Ten. You are now in Focus 10. A state of heightened awareness, mind fully awake, body profoundly asleep.
[PAUSE:7]
"""
    main_prompt = f"""
Write approximately {main_content_duration_minutes} minutes of guided meditation content for the main section of a Hemi-Sync style Focus 10 meditation.
The specific theme for this main section is: \'{user_goal}\'.
The style should be present tense, using gentle, suggestive language like \'you may now perceive...\', \'allow yourself to explore...\', \'notice any sensations or images...\'.
The tone should be calm, reassuring, exploratory, and positive, consistent with the Gateway Experience.
Intersperse [PAUSE:10] or [PAUSE:15] or [PAUSE:20] markers every few sentences to allow time for the listener to experience and reflect.
Do not include an introduction (we\'ve already done that) or a return sequence (that will be added later). Focus only on the main guidance for the specified theme and duration.
Maintain a consistent, flowing narrative.
"""
    gemini_response_text = ""
    try:
        model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest",
                                      generation_config=generation_config,
                                      safety_settings=safety_settings)
        response_obj = model.generate_content(main_prompt)
        gemini_response_text = response_obj.text
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        gemini_response_text = f"[AI GENERATION FAILED: {e}]"
        if 'response_obj' in locals() and hasattr(response_obj, 'prompt_feedback') and response_obj.prompt_feedback:
             print(f"Prompt Feedback: {response_obj.prompt_feedback}")

    script += gemini_response_text
    script += """
[PAUSE:10]
It is now time to return to full, waking physical consciousness, which we call C-1.
[PAUSE:3]
Remember this experience and know that you can return to this state of awareness when you choose.
[PAUSE:3]
I will count from ten down to one. At the count of one, you will be fully alert, refreshed, feeling fine, and in perfect health, ready for your normal activities.
[PAUSE:3]
Ten... nine... beginning to return now, feeling energy and awareness returning to your physical body...
[PAUSE:2]
Eight... seven... becoming more aware of your physical surroundings...
[PAUSE:2]
Six... five... feeling energy returning to your arms and legs, your hands and feet...
[PAUSE:2]
Four... three... almost back now, feeling wonderful and refreshed, calm and centered...
[PAUSE:2]
Two... and one. Eyes open, fully awake. Wide awake, feeling fine and in perfect health, better than before. Take a moment to stretch if you wish.
"""
    return script.strip()

# MODIFIED: synthesize_text_elevenlabs function
def synthesize_text_elevenlabs(text, voice_id, stability=0.7, similarity_boost=0.75, style=0.2):
    """Synthesizes text using ElevenLabs API via the client."""
    if not elevenlabs_client:
        print("ElevenLabs client not initialized or API key missing. Skipping synthesis.")
        return None
    try:
        audio_data_iterator = elevenlabs_client.text_to_speech.convert(
            voice_id=voice_id,
            text=text,
            model_id="eleven_multilingual_v2" 
        )
        # Consume the iterator and join byte chunks
        full_audio_bytes = b"".join(list(audio_data_iterator))
        return full_audio_bytes
    except Exception as e:
        print(f"Error during ElevenLabs synthesis for text \'{text[:50]}...': {e}")
        return None

def create_meditation_mp3_elevenlabs(script_text, background_audio_path, output_filename="custom_meditation_elevenlabs.mp3"):
    print(f"Generating voice for script using ElevenLabs (Voice ID: {ELEVENLABS_VOICE_ID})...")
    segments_raw = re.split(r'''\[PAUSE:(\d+)\]''', script_text)
    voice_track = AudioSegment.empty()

    for i, segment_text in enumerate(segments_raw):
        segment_text = segment_text.strip()
        if not segment_text:
            continue
        if i % 2 == 0: # Text segment
            if segment_text:
                print(f"Synthesizing (ElevenLabs): \'{segment_text[:50]}...\'")
                audio_bytes = synthesize_text_elevenlabs(segment_text, ELEVENLABS_VOICE_ID)
                if audio_bytes: # Should now always be bytes or None
                    audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")
                    voice_track += audio_segment
                else: # TTS failed
                    voice_track += AudioSegment.silent(duration=1000) # Add 1s silence
        else: # Pause duration
            try:
                pause_duration_seconds = int(segment_text)
                print(f"Adding pause: {pause_duration_seconds}s")
                voice_track += AudioSegment.silent(duration=pause_duration_seconds * 1000)
            except ValueError:
                print(f"Warning: Could not parse pause duration: {segment_text}")

    print("Voice track generation complete.")
    print(f"Loading background audio: {background_audio_path}")
    try:
        background = AudioSegment.from_mp3(background_audio_path)
    except Exception as e:
        print(f"Error loading background audio \'{background_audio_path}\': {e}")
        return None

    # Adjust volumes
    background = background - 12 # Keep background quieter
    voice_track = voice_track - 4  # Reduce cloned voice volume by 4dB initially (can be adjusted)
    
    if len(voice_track) > len(background):
        print(f"Voice track ({len(voice_track)/1000}s) is longer than background ({len(background)/1000}s). Padding background.")
        silence_needed = len(voice_track) - len(background)
        background += AudioSegment.silent(duration=silence_needed)
    
    print("Mixing voice and background...")
    output_dir = "generated_meditations"
    os.makedirs(output_dir, exist_ok=True)
    full_output_path = os.path.join(output_dir, output_filename)

    final_mix = background.overlay(voice_track, position=0)
    print(f"Exporting final MP3 to: {full_output_path}")
    try:
        final_mix.export(full_output_path, format="mp3")
        print("Meditation MP3 created successfully!")
        return full_output_path
    except Exception as e:
        print(f"Error exporting MP3 \'{full_output_path}\': {e}")
        return None

if __name__ == "__main__":
    user_input_goal = "experience profound mental clarity" # New goal for testing
    total_duration_minutes = 25 # Different duration
    
    print(f"Autonomous run for goal: \'{user_input_goal}\', duration: {total_duration_minutes} min (using ElevenLabs)")

    estimated_fixed_parts_duration = 5 
    main_content_gen_duration = total_duration_minutes - estimated_fixed_parts_duration
    if main_content_gen_duration < 1:
         main_content_gen_duration = 1
    
    BACKGROUND_FILE = "Focus-Creation/background_audio/y2mate.is - Robert Monroe Institute Astral Projection Gateway Process 40 minutes no talking -edB7QI8I02c-192k-1700669353.mp3"
    
    run_generation = False
    if not ELEVENLABS_API_KEY or not ELEVENLABS_VOICE_ID:
        print("ERROR: ElevenLabs API Key or Voice ID not configured in the script.")
    elif elevenlabs_client is None: # Check if client initialized
        print("ERROR: ElevenLabs client failed to initialize. Cannot proceed.")
    elif not os.path.exists(BACKGROUND_FILE):
        print(f"ERROR: Background audio file not found at \'{BACKGROUND_FILE}\'. Please check the path.")
    elif not BACKGROUND_FILE.lower().endswith(".mp3"):
        print(f"ERROR: Background audio file \'{BACKGROUND_FILE}\' does not seem to be an MP3. Please check the file format.")
    else:
        run_generation = True

    if run_generation:
        print(f"Generating script for \'{user_input_goal}\' (main content approx. {main_content_gen_duration} min)...")
        script = generate_meditation_script_gemini_v1(user_input_goal, main_content_gen_duration)
        output_mp3_filename = f"custom_elevenlabs_{user_input_goal.replace(' ', '_')[:20]}_{total_duration_minutes}min.mp3"
        create_meditation_mp3_elevenlabs(script, BACKGROUND_FILE, output_mp3_filename)
    else:
        print("Pre-run checks failed. Meditation generation aborted.") 