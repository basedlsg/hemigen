import os
from elevenlabs.client import ElevenLabs
from pydub import AudioSegment
import re
import io

# ElevenLabs Configuration
ELEVENLABS_API_KEY = "sk_fe6faf571491c9b26bef909dce2e19a8e1d7239bf518027b"
ELEVENLABS_VOICE_ID = "7nFoun39JV8WgdJ3vGmC"

# Background audio path
BACKGROUND_FILE = "/Users/carlos/Focus-Creation/Focus-Creation/background_audio/y2mate.is - Robert Monroe Institute Astral Projection Gateway Process 40 minutes no talking -edB7QI8I02c-192k-1700669353.mp3"

# Initialize ElevenLabs client
elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

def read_transcript():
    """Read the $90k meditation transcript."""
    with open("/Users/carlos/Focus-Creation/transcripts/Manifesting_90k_25min_20250613_152944.txt", 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract just the meditation script (skip the header)
    lines = content.split('\n')
    start_idx = 0
    for i, line in enumerate(lines):
        if line.strip().startswith("## Hemi-Sync Style Meditation"):
            start_idx = i
            break
    
    # Join the script lines and clean up markdown formatting
    script = '\n'.join(lines[start_idx:])
    
    # Remove markdown formatting
    script = re.sub(r'\*\*\d+\.\s*([^*]+)\*\*', r'\1', script)  # Remove section headers
    script = re.sub(r'\*\*([^*]+)\*\*', r'\1', script)  # Remove bold
    script = re.sub(r'\*([^*]+)\*', r'\1', script)  # Remove italics
    script = re.sub(r'^#+\s*', '', script, flags=re.MULTILINE)  # Remove headers
    script = re.sub(r'^\*\s*', '', script, flags=re.MULTILINE)  # Remove bullet points
    script = re.sub(r'\n\n+', '\n\n', script)  # Clean up excessive newlines
    
    return script.strip()

def synthesize_text_elevenlabs(text, voice_id):
    """Synthesize text using ElevenLabs API."""
    try:
        print(f"Synthesizing: {text[:50]}...")
        audio_data_iterator = elevenlabs_client.text_to_speech.convert(
            voice_id=voice_id,
            text=text,
            model_id="eleven_multilingual_v2"
        )
        full_audio_bytes = b"".join(list(audio_data_iterator))
        return full_audio_bytes
    except Exception as e:
        print(f"Error during synthesis: {e}")
        return None

def create_meditation_audio(script_text):
    """Create the complete meditation audio with background music."""
    print("Starting audio generation for Manifesting $90k meditation...")
    
    # Split script into segments
    segments_raw = re.split(r'(\[PAUSE:\d+\])', script_text)
    voice_track = AudioSegment.empty()
    
    total_segments = len([s for s in segments_raw if s.strip()])
    current_segment = 0
    
    for segment_text in segments_raw:
        segment_text = segment_text.strip()
        if not segment_text:
            continue
        
        current_segment += 1
        print(f"\nProcessing segment {current_segment}/{total_segments}")
        
        pause_match = re.match(r'\[PAUSE:(\d+)\]', segment_text)
        if pause_match:
            pause_duration = int(pause_match.group(1))
            print(f"Adding {pause_duration}s pause...")
            voice_track += AudioSegment.silent(duration=pause_duration * 1000)
        else:
            # Synthesize speech
            audio_bytes = synthesize_text_elevenlabs(segment_text, ELEVENLABS_VOICE_ID)
            if audio_bytes:
                try:
                    audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")
                    voice_track += audio_segment
                    print(f"Added {len(audio_segment)/1000:.1f}s of speech")
                except Exception as e:
                    print(f"Error processing audio segment: {e}")
                    voice_track += AudioSegment.silent(duration=1000)
            else:
                print("Failed to synthesize, adding 1s silence")
                voice_track += AudioSegment.silent(duration=1000)
    
    print(f"\nVoice track complete. Total duration: {len(voice_track)/1000/60:.1f} minutes")
    
    # Load and prepare background music
    print("\nLoading background music...")
    try:
        background = AudioSegment.from_mp3(BACKGROUND_FILE)
        print(f"Background music loaded: {len(background)/1000/60:.1f} minutes")
    except Exception as e:
        print(f"Error loading background music: {e}")
        return None
    
    # Adjust volumes
    background = background - 12  # Reduce background volume
    voice_track = voice_track - 4  # Slightly reduce voice volume
    
    # Extend background if needed
    if len(voice_track) > len(background):
        print("Extending background music to match voice track...")
        silence_needed = len(voice_track) - len(background)
        background += AudioSegment.silent(duration=silence_needed)
    
    # Mix tracks
    print("\nMixing voice and background...")
    final_mix = background.overlay(voice_track, position=0)
    
    # Export
    output_dir = "generated_meditations"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "Manifesting_90k_HemiSync_Meditation.mp3")
    
    print(f"\nExporting to: {output_path}")
    try:
        final_mix.export(output_path, format="mp3", bitrate="192k")
        print(f"\n✓ Success! Meditation audio created: {output_path}")
        print(f"✓ Total duration: {len(final_mix)/1000/60:.1f} minutes")
        return output_path
    except Exception as e:
        print(f"Error exporting audio: {e}")
        return None

if __name__ == "__main__":
    print("="*60)
    print("Manifesting $90k Hemi-Sync Meditation Audio Generator")
    print("="*60)
    
    # Read the transcript
    script = read_transcript()
    
    if script:
        print(f"\nTranscript loaded successfully")
        print(f"Script preview: {script[:200]}...")
        
        # Generate the audio
        result = create_meditation_audio(script)
        
        if result:
            print(f"\n{'='*60}")
            print("GENERATION COMPLETE!")
            print(f"{'='*60}")
            print(f"Your meditation audio is ready at:")
            print(f"  {result}")
            print("\nTo use this meditation:")
            print("1. Find a quiet, comfortable space")
            print("2. Use stereo headphones for the Hemi-Sync effect")
            print("3. Listen daily for best results")
            print("4. Allow yourself to fully experience the visualization")
        else:
            print("\nError: Failed to generate audio")
    else:
        print("Error: Could not read transcript")