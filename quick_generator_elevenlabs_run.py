import os
# MODIFIED ElevenLabs imports
from elevenlabs.client import ElevenLabs
from elevenlabs import Voice as ElevenVoiceObject, VoiceSettings as ElevenVoiceSettings 
from pydub import AudioSegment
import re
import io
import json # For potential future communication with MCP server

# --- ElevenLabs API Key Configuration ---
ELEVENLABS_API_KEY = "sk_fe6faf571491c9b26bef909dce2e19a8e1d7239bf518027b" # User provided
ELEVENLABS_VOICE_ID = "7nFoun39JV8WgdJ3vGmC" # User provided

# MODIFIED: Instantiate ElevenLabs client
elevenlabs_client = None
if ELEVENLABS_API_KEY:
    try:
        elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    except Exception as e:
        print(f"Failed to initialize ElevenLabs client: {e}")
else:
    print("ElevenLabs API Key not found. TTS will be skipped for actual audio generation if attempted later.")

# Using the precise absolute path found by file search
BACKGROUND_FILE = "/Users/carlos/Focus-Creation/Focus-Creation/background_audio/y2mate.is - Robert Monroe Institute Astral Projection Gateway Process 40 minutes no talking -edB7QI8I02c-192k-1700669353.mp3"

# --- MONROE-STYLE STRUCTURE SUMMARY (Derived from 1.pl analysis) ---
# This summary will guide the AI in structuring the meditation.
MONROE_STRUCTURE_SUMMARY = """
A Hemi-Sync/Monroe-style meditation script typically follows this flow:
1.  **Introduction/Preparation**: Brief welcome, orienting the listener, stating the session's aim (related to the user_goal). (~1-2 minutes of speech)
2.  **Energy Conversion Box**: Guide the listener to place worries/distractions into a mental box. (~1-2 minutes of speech)
3.  **Resonant Tuning**: Guide breathing and humming to energize. (~2-3 minutes, including pauses for practice)
4.  **Affirmation**: Standard "I am more than my physical body..." and a goal-specific affirmation. (~1 minute of speech)
5.  **Focus Level Induction (Focus 10)**: Count 1-10, guiding relaxation into mind awake/body asleep state. (~2-3 minutes, including pauses between counts)
6.  **Themed Content (Focus 10 or higher, based on goal)**: This is the main section.
    *   Address the `user_goal` (e.g., manifesting, healing, exploration).
    *   Use evocative, suggestive language.
    *   Incorporate periods of silence/minimal guidance for listener experience ([PAUSE:X] markers are crucial). The AI should determine appropriate pause lengths (e.g., 5 to 60 seconds or more for deep experiences).
    *   If a higher Focus level (e.g., Focus 12 for problem-solving/non-physical senses, Focus 15 for no-time/creation, Focus 21 for other realities) is appropriate for the `user_goal`, include a guided induction to that level from Focus 10.
    *   The duration of this section (speech + pauses) should be the primary variable to meet `main_content_duration_minutes` (which is `total_duration_minutes` - approx fixed parts time).
7.  **Return to C-1 (Waking Consciousness)**: Count down (e.g., 10-1 or from the current Focus level), guiding the listener back to full alertness, feeling refreshed and positive. (~2-3 minutes, including pauses)
8.  **Closing**: Brief positive reinforcement and integration suggestion related to the `user_goal`. (~0.5-1 minute of speech)

Instructions for AI (Gemini via zen-mcp-server):
*   Adhere to this structure and the spirit of the Monroe Institute's Gateway Experience.
*   The total script length (speech + pauses) should be crafted to fit the `total_duration_minutes` passed by the user (the placeholder will use a simplified `main_content_duration_minutes`).
*   Integrate the specific `user_goal` naturally and creatively into sections 1 (aim), 4 (affirmation), 6 (core themed content), and 8 (closing/integration).
*   Use clear, calm, reassuring, and evocative language. Employ present tense and suggestive phrasing (e.g., "you may perceive...", "allow yourself to experience...").
*   Intersperse `[PAUSE:X]` (where X is seconds) markers thoughtfully throughout the script, especially in section 6 and during Focus level inductions/returns. Typical pauses might range from 5 to 60 seconds. Longer pauses can be used for deeper reflection or experiential segments.
*   The dialogue must be original and insightful, drawing inspiration from the Monroe style but tailored to the user's goal. Do not simply copy existing scripts.
*   Output *only* the script text, including the `[PAUSE:X]` markers, ready for TTS.
*   Ensure the script is coherent, flows well, and is of high quality, suitable for a guided meditation.
"""

# --- PLACEHOLDER FOR MCP SERVER INTERACTION ---
def call_mcp_server_for_script_generation(user_goal, total_duration_minutes, structure_summary):
    """
    Placeholder for calling the zen-mcp-server to get AI-generated script.
    This function simulates the AI's response for now.
    YOU WILL NEED TO REPLACE THE BODY OF THIS FUNCTION with actual code to:
    1. Construct a detailed prompt for Gemini, including the user_goal, total_duration_minutes,
       and the MONROE_STRUCTURE_SUMMARY.
    2. Make an HTTP POST request to your local zen-mcp-server endpoint
       (e.g., http://localhost:YOUR_MCP_PORT/generate-script or similar).
    3. The zen-mcp-server should be configured with your GEMINI_API_KEY in its .env file.
    4. Receive and return the AI-generated script text from the server response.
    """
    print(f"\n=== SIMULATING AI SCRIPT GENERATION (via MCP placeholder) ===")
    print(f"  User Goal: {user_goal}")
    print(f"  Requested Total Duration: {total_duration_minutes} minutes")

    # Simplified calculation for themed content in this placeholder
    # A real AI would manage total time more dynamically based on content generation.
    approx_fixed_parts_speech_time = 7 # Rough estimate for intro, box, tuning, F10 induction, return, closing (speech only)
    # Pauses for fixed parts might add another 3-5 minutes. Let's say total fixed parts duration is ~10-12 mins with pauses.
    # For a 10-minute total duration, main content will be very short or mostly integrated.
    main_content_target_speech_minutes = max(1, total_duration_minutes - 8) # Ensure at least 1 min speech for theme
    
    # Simulated script structure (very basic for the placeholder)
    script = f"""[INFO: This is a SIMULATED AI-generated script. Implement actual MCP call to Gemini.]

Welcome. Today, our journey is to explore {user_goal}, moving into a state of expanded awareness.
[PAUSE:10]
Find a comfortable position. Loosen any tight clothing. Gently close your eyes.
[PAUSE:10]
Now, in your mind's eye, create your Energy Conversion Box. This is your mental container to hold any concerns or distractions. Place them inside, close the lid, and set them aside.
[PAUSE:20]
Let's begin our Resonant Tuning. Breathe slightly deeper than normal. As you inhale, pull sparkling, vibrant energy into all parts of your body. As you exhale, create a gentle humming sound... hmmmmmmm. Feel the vibrations. Do this a few times.
[PAUSE:30]
Repeat this Affirmation mentally, after me: I am more than my physical body. Because I am more than physical matter, I can perceive that which is greater than the physical world. I am open to this experience, and I deeply desire to achieve {user_goal}.
[PAUSE:15]
We will now move into Focus 10, the state of mind awake, body asleep. I will count from one to ten.
One... you are beginning to relax more and more.
[PAUSE:5]
Two... letting go of all physical tension.
[PAUSE:5]
Three... drifting deeper, calmly and comfortably.
[PAUSE:5]
Four... mind awake, body relaxed.
[PAUSE:5]
Five... your body is calm, comfortable, and at ease.
[PAUSE:5]
Six... deeper and deeper into profound relaxation.
[PAUSE:5]
Seven... just letting go completely.
[PAUSE:5]
Eight... mind remains awake and alert, body deeply asleep.
[PAUSE:5]
Nine... drifting into total relaxation, secure and comfortable.
[PAUSE:5]
Ten. You are now in Focus 10. A state of heightened awareness, mind fully awake, body profoundly asleep.
[PAUSE:30]

Now, in this state of heightened awareness, let us fully explore the pathway to {user_goal}.
(AI would generate detailed guided imagery, affirmations, and instructions for approximately {main_content_target_speech_minutes} minutes of speech here, specifically tailored to '{user_goal}'. This section would integrate appropriate [PAUSE:X] markers, for example, [PAUSE:30] or [PAUSE:60] for reflection and experience. If the goal is manifestation, it might guide towards Focus 12 or 15 concepts.)
Imagine {user_goal} as a present reality. Feel the emotions associated with this achievement. What does it look like? What does it feel like? Immerse yourself in this reality now.
[PAUSE:60]
(Further detailed guidance for '{user_goal}' based on its nature, e.g., steps for clean eating, sensations of clean skin, feelings of abundance for $90k, the experience of being at the university, or preparing for a transformative psychedelic journey by setting intentions and a safe space.)
[PAUSE:60]

It is now time to return to full, waking physical consciousness, which we call C-1. Bring with you the new understandings and the positive energy focused on {user_goal}.
I will count from ten down to one. At the count of one, you will be fully alert, refreshed, and ready to integrate this experience into your daily life.
Ten... nine... beginning to return now, feeling energy and awareness returning to your physical body.
[PAUSE:5]
Eight... seven... becoming more aware of your physical surroundings.
[PAUSE:5]
Six... five... feeling energy returning to your arms and legs, your hands and feet.
[PAUSE:5]
Four... three... almost back now, feeling wonderful and refreshed, calm and centered.
[PAUSE:5]
Two... and one. Eyes open, fully awake. Wide awake, feeling fine and in perfect health, better than before. Carry the energy of {user_goal} with you.
"""
    return script.strip()

# --- NEW AI-POWERED SCRIPT GENERATION FUNCTION ---
def generate_meditation_script_with_ai(user_goal, total_duration_minutes):
    """
    Generates a meditation script using an AI (via MCP server placeholder).
    """
    print(f"\n--- Preparing to generate AI script for: '{user_goal}' ({total_duration_minutes} min) ---")
    
    ai_generated_script = call_mcp_server_for_script_generation(
        user_goal, 
        total_duration_minutes, 
        MONROE_STRUCTURE_SUMMARY
    )

    if not ai_generated_script:
        print(f"ERROR: AI (MCP Server placeholder) failed to generate script for goal '{user_goal}'.")
        return None
    
    # Print the AI-generated script (transcript) for review during this phase
    print(f"\n--- AI-Generated Transcript for '{user_goal}' (Simulated) ---")
    print(ai_generated_script)
    print(f"--- End of Transcript for '{user_goal}' ---")
    
    return ai_generated_script

# MODIFIED: synthesize_text_elevenlabs function
def synthesize_text_elevenlabs(text, voice_id, stability=0.7, similarity_boost=0.75, style=0.2):
    """Synthesizes text using ElevenLabs API via the client."""
    if not elevenlabs_client:
        print("ElevenLabs client not initialized or API key missing. Skipping synthesis.")
        return None
    
    # Log the text being sent to TTS
    print(f"TTS_INPUT: {text}")
    
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
    if not script_text or script_text.startswith("[INFO:") or script_text.startswith("[ERROR:") or script_text.startswith("[WARNING:"):
        print(f"Skipping MP3 generation due to script content: {script_text}")
        return None

    print(f"Generating voice for script using ElevenLabs (Voice ID: {ELEVENLABS_VOICE_ID})...")
    segments_raw = re.split(r'(\[PAUSE:\d+\])', script_text) # Keep delimiters
    voice_track = AudioSegment.empty()

    for segment_text in segments_raw:
        segment_text = segment_text.strip()
        if not segment_text:
            continue

        pause_match = re.match(r'\[PAUSE:(\d+)\]', segment_text)
        if pause_match:
            try:
                pause_duration_seconds = int(pause_match.group(1))
                print(f"Adding pause: {pause_duration_seconds}s")
                if pause_duration_seconds > 0:
                    voice_track += AudioSegment.silent(duration=pause_duration_seconds * 1000)
            except ValueError:
                print(f"Warning: Could not parse pause duration: {segment_text}")
        elif segment_text: # Text segment
            print(f"Synthesizing (ElevenLabs): '{segment_text[:50]}...'")
            audio_bytes = synthesize_text_elevenlabs(segment_text, ELEVENLABS_VOICE_ID)
            if audio_bytes:
                try:
                    audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")
                    voice_track += audio_segment
                except Exception as e:
                    print(f"Error creating audio segment from TTS bytes: {e}. Adding 1s silence.")
                    voice_track += AudioSegment.silent(duration=1000)
            else: # TTS failed
                print(f"TTS failed for segment: '{segment_text[:50]}...'. Adding 1s silence.")
                voice_track += AudioSegment.silent(duration=1000) 

    if len(voice_track) == 0:
        print("Voice track is empty. Aborting MP3 creation.")
        return None

    print("Voice track generation complete.")
    print(f"Loading background audio: {background_audio_path}")
    if not os.path.exists(background_audio_path):
        print(f"ERROR: Background audio file '{background_audio_path}' not found. Cannot create MP3.")
        return None
    try:
        background = AudioSegment.from_mp3(background_audio_path)
    except Exception as e:
        print(f"Error loading background audio '{background_audio_path}': {e}")
        return None

    background = background - 12 
    voice_track = voice_track - 4  
    
    if len(voice_track) > len(background):
        print(f"Voice track ({len(voice_track)/1000}s) is longer than background ({len(background)/1000}s). Padding background.")
        silence_needed = len(voice_track) - len(background)
        background += AudioSegment.silent(duration=silence_needed)
    
    target_dir_for_output = os.path.dirname(output_filename)
    if target_dir_for_output:
        os.makedirs(target_dir_for_output, exist_ok=True)
    
    print("Mixing voice and background...")
    final_mix = background.overlay(voice_track, position=0)
    
    print(f"Exporting final MP3 to: {output_filename}")
    try:
        final_mix.export(output_filename, format="mp3")
        print("Meditation MP3 created successfully!")
        return output_filename
    except Exception as e:
        print(f"Error exporting MP3 '{output_filename}': {e}")
        return None

# --- MAIN ORCHESTRATION (modified to use AI and optionally generate MP3) ---
def generate_complete_meditation(user_goal, total_duration_minutes, create_audio_file=False):
    """
    Generates a meditation script using AI. 
    If create_audio_file is True, also synthesizes TTS and creates MP3.
    Returns the AI-generated script (transcript) or path to MP3 if created.
    """
    script_text = generate_meditation_script_with_ai(user_goal, total_duration_minutes)

    if not script_text or script_text.startswith("[ERROR:"):
        # Allow warnings to proceed to audio if desired, but errors should stop.
        print(f"Script generation resulted in an error or was empty: {script_text}")
        return script_text 

    # If it's just an INFO (like the simulation marker) or WARNING, and we want audio, we can proceed
    # But if it's an error, we should have returned above.
    if "[INFO: This is a SIMULATED AI-generated script." in script_text and not create_audio_file:
         print("Returning simulated script text for review. Audio generation skipped by default for simulated scripts.")
         return script_text

    if create_audio_file:
        if script_text.startswith("[WARNING:"):
            print(f"Proceeding with audio generation despite warning: {script_text}")
        elif script_text.startswith("[INFO:") and "SIMULATED" not in script_text: # Real INFO from AI
             print(f"Proceeding with audio generation for informational script: {script_text}")

        print(f"\n--- Proceeding to audio generation for: '{user_goal}' ---")
        safe_goal_name = re.sub(r'[^a-zA-Z0-9_\-]+', '_', user_goal) if user_goal else "ai_meditation"
        output_filename_base = f"{safe_goal_name}_{total_duration_minutes}min_elevenlabs_AI.mp3"
        
        generated_dir = "generated_meditations"
        os.makedirs(generated_dir, exist_ok=True)
        output_filepath = os.path.join(generated_dir, output_filename_base)

        print(f"Attempting to save generated meditation to: {output_filepath}")

        if not os.path.exists(BACKGROUND_FILE):
            error_msg = f"ERROR: Background audio file '{BACKGROUND_FILE}' not found. Cannot proceed."
            print(error_msg)
            return error_msg

        final_mp3_path = create_meditation_mp3_elevenlabs(script_text, BACKGROUND_FILE, output_filepath)

        if final_mp3_path:
            print(f"Meditation MP3 generated successfully: {final_mp3_path}")
            return final_mp3_path
        else:
            print(f"Failed to create meditation MP3 for goal '{user_goal}'.")
            return f"[ERROR: Failed to create MP3 for '{user_goal}']"
    else:
        # If not creating audio, just return the AI-generated script for review
        return script_text


# --- MAIN EXECUTION FOR DEBUGGING AI TRANSCRIPTS ---
if __name__ == "__main__":
    goals = [
        "Manifesting $90k",
        "Manifesting entrance into University of Washington Summer Semester",
        "Manifesting extremely clean skin and a healthy body",
        "Manifesting clean eating habits",
        "Manifesting a transformative psychedelic experience"
    ]
    
    # For review, a shorter duration is fine. The placeholder AI will adapt its themed content part.
    duration_for_review = 10 

    print("===== GENERATING AI MEDITATION TRANSCRIPTS FOR REVIEW =====")
    print("IMPORTANT: The following transcripts are SIMULATED via a placeholder function. ")
    print("You will need to implement the actual calls to your zen-mcp-server ")
    print("in the 'call_mcp_server_for_script_generation' function to use Gemini with your API key.\n")

    all_generated_content = {}

    for goal in goals:
        # create_audio_file is False, so this will only generate and print the simulated transcript
        content = generate_complete_meditation(goal, duration_for_review, create_audio_file=False)
        all_generated_content[goal] = content
        if goal != goals[-1]:
            print("\n" + "="*80 + "\n") 

    print("\n\n===== SUMMARY OF SIMULATED AI-GENERATED TRANSCRIPTS (FIRST/LAST 5 LINES) =====")
    for goal, transcript_text in all_generated_content.items():
        print(f"\n--- Goal: {goal} ---")
        if transcript_text and not transcript_text.startswith("[ERROR:"):
            lines = transcript_text.split('\n')
            if len(lines) > 10:
                print("\n".join(lines[:5]))
                print("[...] (Full transcript was printed above during its generation)")
                print("\n".join(lines[-5:]))
            else:
                print(transcript_text)
        elif transcript_text:
             print(f"  Content: {transcript_text}") # Print error/info message
        else:
            print("  [No transcript or unexpected error during generation]")
        print("-"*(len(goal) + 12) + "\n")

    print("\nReview the full console output above for the complete simulated transcripts.")
    print("Next steps:")
    print("1. Implement the actual HTTP request to your zen-mcp-server in the 'call_mcp_server_for_script_generation' function.")
    print("2. Ensure your zen-mcp-server is running and correctly configured with your Gemini API key.")
    print("3. Once the MCP call is implemented, run this script again to get REAL AI-generated transcripts.")
    print("4. Evaluate the quality of the real AI transcripts. If good, you can set create_audio_file=True to generate MP3s.")
