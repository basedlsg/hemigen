import os
# MODIFIED ElevenLabs imports
from elevenlabs.client import ElevenLabs
from elevenlabs import Voice as ElevenVoiceObject, VoiceSettings as ElevenVoiceSettings 
from pydub import AudioSegment
import re
import io
import json # For potential future communication with MCP server
import google.generativeai as genai # Import Gemini library

# --- API Key Configurations ---
ELEVENLABS_API_KEY = "sk_fe6faf571491c9b26bef909dce2e19a8e1d7239bf518027b" # User provided
ELEVENLABS_VOICE_ID = "7nFoun39JV8WgdJ3vGmC" # User provided

# IMPORTANT: For deployment, this should be an environment variable.
# For local testing and development, ensure it's set correctly.
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyAqko3NqGS-GtXhzm8LeiZ3xUEyo_XIqLo") # User provided, with fallback for os.environ

if not GEMINI_API_KEY or GEMINI_API_KEY == "AIzaSyAqko3NqGS-GtXhzm8LeiZ3xUEyo_XIqLo": # Check if it's the placeholder or not found
    print("WARNING: GEMINI_API_KEY is using the hardcoded placeholder or was not found in environment variables. Direct Gemini calls might fail if this key is invalid or has restrictions.")
    if not os.environ.get("GEMINI_API_KEY"):
        print("         Consider setting the GEMINI_API_KEY environment variable for robust configuration.")

try:
    genai.configure(api_key=GEMINI_API_KEY)
    print("Gemini API configured successfully.")
except Exception as e:
    print(f"ERROR: Failed to configure Gemini API: {e}. Please check your API key.")
    # Potentially exit or prevent further Gemini-dependent operations if critical

# MODIFIED: Instantiate ElevenLabs client
elevenlabs_client = None
if ELEVENLABS_API_KEY:
    try:
        elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        print("ElevenLabs client initialized successfully.")
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

Instructions for AI (Gemini):
*   Adhere to this structure and the spirit of the Monroe Institute's Gateway Experience.
*   The total script length (speech + pauses) should be crafted to fit the `total_duration_minutes` passed by the user.
*   Integrate the specific `user_goal` naturally and creatively into sections 1 (aim), 4 (affirmation), 6 (core themed content), and 8 (closing/integration).
*   Use clear, calm, reassuring, and evocative language. Employ present tense and suggestive phrasing (e.g., "you may perceive...", "allow yourself to experience...").
*   Intersperse `[PAUSE:X]` (where X is seconds) markers thoughtfully throughout the script, especially in section 6 and during Focus level inductions/returns. Typical pauses might range from 5 to 60 seconds. Longer pauses can be used for deeper reflection or experiential segments.
*   The dialogue must be original and insightful, drawing inspiration from the Monroe style but tailored to the user's goal. Do not simply copy existing scripts.
*   Output *only* the script text, including the `[PAUSE:X]` markers, ready for TTS.
*   Ensure the script is coherent, flows well, and is of high quality, suitable for a guided meditation.
*   For a '{total_duration_minutes}' minute meditation on the theme '{user_goal}', generate the full script now.
"""

# --- DIRECT GEMINI API CALL FUNCTION ---
def generate_script_with_gemini(user_goal, total_duration_minutes, structure_summary):
    print(f"\n=== Calling Gemini API for Script Generation ===")
    print(f"  User Goal: {user_goal}")
    print(f"  Requested Total Duration: {total_duration_minutes} minutes")

    # Construct the prompt for Gemini
    # The MONROE_STRUCTURE_SUMMARY already includes placeholders for these, but we can re-emphasize.
    prompt = f"{structure_summary.format(user_goal=user_goal, total_duration_minutes=total_duration_minutes)}"
    prompt += f"\n\nGenerate a Hemi-Sync style meditation script of approximately {total_duration_minutes} minutes (including pauses) for the goal: '{user_goal}'."
    prompt += "\nThe script should be complete, from introduction to closing, with [PAUSE:X] markers."
    
    try:
        # model = genai.GenerativeModel('gemini-1.5-flash-latest') # Good for speed and general tasks
        model = genai.GenerativeModel('gemini-1.5-pro-latest') # Better for complex generation and longer context
        
        # Configuration for generation (can be tuned)
        generation_config = genai.types.GenerationConfig(
            temperature=0.75, # Controls randomness. Lower is more predictable.
            top_p=0.95,
            top_k=64,
            max_output_tokens=8192, # Max for Pro model
            # response_mime_type="text/plain", # Ensure text output
        )
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"}, # Allowing more esoteric/body-related terms for meditation
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]

        print("Sending prompt to Gemini...")
        # print(f"DEBUG PROMPT (first 300 chars): {prompt[:300]}...") # For debugging prompt issues
        response = model.generate_content(
            prompt,
            generation_config=generation_config,
            safety_settings=safety_settings,
            stream=False # Get the full response at once
        )
        
        # print(f"DEBUG Response Parts: {response.parts}")
        # print(f"DEBUG Prompt Feedback: {response.prompt_feedback}")
        # print(f"DEBUG Candidates: {response.candidates}")

        if response.parts:
            generated_script = response.text
            print("Script successfully generated by Gemini.")
            return generated_script.strip()
        elif response.prompt_feedback and response.prompt_feedback.block_reason:
            reason = response.prompt_feedback.block_reason
            block_message = f"[ERROR: Gemini prompt blocked. Reason: {reason}. Rating: {response.prompt_feedback.safety_ratings}]"
            print(block_message)
            return block_message
        else:
            print("ERROR: Gemini returned no content or an unexpected response structure.")
            return "[ERROR: Gemini returned no content or unexpected structure.]"

    except Exception as e:
        print(f"ERROR: An exception occurred during Gemini API call: {e}")
        return f"[ERROR: Gemini API call failed: {str(e)}]"

# --- AI-POWERED SCRIPT GENERATION FUNCTION (using direct Gemini call) ---
def generate_meditation_script_with_ai(user_goal, total_duration_minutes):
    print(f"\n--- Preparing to generate AI script for: '{user_goal}' ({total_duration_minutes} min) using direct Gemini call ---")
    
    ai_generated_script = generate_script_with_gemini(
        user_goal, 
        total_duration_minutes, 
        MONROE_STRUCTURE_SUMMARY
    )

    if not ai_generated_script or ai_generated_script.startswith("[ERROR:"):
        print(f"Failed to generate script from AI for '{user_goal}'. See error above.")
        # Return the error message itself for logging/display
        return ai_generated_script 
    
    print(f"\n--- AI-Generated Transcript for '{user_goal}' (Actual Gemini Output) ---")
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
        output_filename_base = f"{safe_goal_name}_{total_duration_minutes}min_elevenlabs_AI_Gemini.mp3"
        
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


# --- MAIN EXECUTION FOR GENERATING REAL AI TRANSCRIPTS ---
if __name__ == "__main__":
    goals = [
        "Manifesting $90k" # Focus on this goal for audio test
    ]
    duration_for_scripts = 10 # Duration for the AI to aim for each script

    print("===== GENERATING AUDIO FOR SELECTED AI MEDITATION SCRIPT =====")
    if not GEMINI_API_KEY or GEMINI_API_KEY == "AIzaSyAqko3NqGS-GtXhzm8LeiZ3xUEyo_XIqLo": # Default key check
        print("CRITICAL WARNING: A valid GEMINI_API_KEY is not configured. Script generation will likely fail or use a restricted key.")
        print("Please set the GEMINI_API_KEY environment variable or update the hardcoded key in the script with a valid one.")

    for goal in goals: # Loop will run once
        # Set create_audio_file=True to generate the MP3
        print(f"\n--- Generating audio for goal: '{goal}' ---")
        generated_content = generate_complete_meditation(goal, duration_for_scripts, create_audio_file=True)
        
        if isinstance(generated_content, str) and generated_content.startswith("[ERROR:"):
            print(f"Failed to generate content for '{goal}': {generated_content}")
        elif isinstance(generated_content, str) and not generated_content.startswith("[ERROR:"):
            # This case implies script was returned, but audio wasn't created (e.g. BG file missing, or other non-script error)
            print(f"Script was generated for '{goal}', but audio file creation might have failed. Check messages above.")
            print(f"Script content:\n{generated_content[:300]}...") # Print beginning of script
        elif generated_content: # Should be the MP3 path if successful
            print(f"Successfully generated MP3 for '{goal}': {generated_content}")
        else:
            print(f"An unexpected issue occurred for '{goal}'. No content generated.")
        print("\n" + "="*80 + "\n")

    print("\nAudio generation test complete.")
    # The summary part is removed as we are focusing on one audio generation.
