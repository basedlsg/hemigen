import google.generativeai as genai
import os
from pydub import AudioSegment
import re
import io
import json
from datetime import datetime

# --- Gemini API Key Configuration ---
GEMINI_API_KEY = "AIzaSyAqko3NqGS-GtXhzm8LeiZ3xUEyo_XIqLo"
genai.configure(api_key=GEMINI_API_KEY)

generation_config = {
    "temperature": 0.8,  # Slightly higher for more creative meditation scripts
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,  # Increased for longer scripts
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

# Enhanced Monroe structure based on research
ENHANCED_MONROE_STRUCTURE = """
Based on the latest neuroscience research (2024) and Monroe Institute methodology, create a Hemi-Sync style meditation following this enhanced structure:

1. **Introduction/Orientation (1-2 min)**: 
   - Brief welcome stating the specific goal
   - Mention this is a journey into expanded awareness
   - Create immediate engagement with the goal

2. **Preparation Phase**:
   a) Energy Conversion Box (1-2 min):
      - Guide to create a mental container
      - Place all worries, concerns, and distractions inside
      - Emphasize the box's security and that items can be retrieved later
   
   b) Resonant Tuning (2-3 min):
      - Guide breathing: inhale energy from all body parts up to head
      - Exhale with humming (mention the vibrational aspect)
      - Include at least 2-3 breathing cycles with [PAUSE:10-15] between

3. **Resonant Energy Balloon (2-3 min)**:
   - Create protective energy field
   - Describe energy flowing out top of head, around body, entering feet
   - Emphasize two functions: retaining personal energy, protecting from external energies

4. **Affirmation Phase (1-2 min)**:
   - Standard: "I am more than my physical body..."
   - Goal-specific affirmation incorporating the desired outcome
   - Use present tense as if already achieved

5. **Focus 10 Induction (3-4 min)**:
   - Count from 1 to 10 with specific suggestions at each number
   - Progressive relaxation while maintaining mental alertness
   - Key phrase: "mind awake, body asleep"
   - Include appropriate pauses between counts

6. **Main Themed Content (varies based on total duration)**:
   Based on neuroscience research:
   - Use visualization techniques proven to create new neural pathways
   - Incorporate multi-sensory imagery (visual, auditory, kinesthetic, emotional)
   - For manifestation: Focus on the feeling of already having achieved the goal
   - Include periods of silence for deep integration [PAUSE:30-60]
   - Use present tense, positive language
   - Incorporate quantum field concepts when appropriate
   - Guide to higher Focus levels if needed (12 for enhanced perception, 15 for manifestation)

7. **Integration and Anchoring (2-3 min)**:
   - Reinforce the new neural pathways created
   - Suggest daily practice for neuroplasticity
   - Create a mental/emotional anchor for the experience

8. **Return Sequence (2-3 min)**:
   - Count from 10 to 1 (or current Focus level to 1)
   - Progressive return to full waking consciousness (C-1)
   - Suggestions of feeling refreshed, energized, positive
   - Integration of the experience

9. **Closing (30 sec - 1 min)**:
   - Brief reinforcement of the goal
   - Suggestion to carry the energy forward
   - Gentle encouragement for regular practice

IMPORTANT GUIDELINES:
- Total duration should match requested time
- Use clear, calm, reassuring voice tone descriptions
- Include [PAUSE:X] markers thoughtfully (X = seconds)
- Language should be suggestive, not commanding ("you may notice", "allow yourself")
- Incorporate latest neuroscience insights on visualization and neural pathway formation
- For manifestation goals: emphasize emotional state of achievement
- Maintain Monroe Institute's exploratory, non-dogmatic approach
"""

def generate_enhanced_meditation_script(user_goal, total_duration_minutes=30):
    """Generate an enhanced meditation script using Gemini AI with latest research insights."""
    
    # Calculate approximate time allocations
    fixed_sections_time = 15  # Approximate minutes for all sections except main content
    main_content_time = max(5, total_duration_minutes - fixed_sections_time)
    
    prompt = f"""
{ENHANCED_MONROE_STRUCTURE}

Create a complete {total_duration_minutes}-minute Hemi-Sync style meditation script for the following goal:
"{user_goal}"

The main themed content section should be approximately {main_content_time} minutes (including pauses).

Based on 2024 neuroscience research:
- Visualization during meditative states creates neural pathways as effectively as physical practice
- Alpha and theta brainwave states are optimal for subconscious reprogramming
- Repetition and emotional engagement are key to neuroplasticity
- Multi-sensory visualization enhances manifestation effectiveness

For this specific goal, incorporate:
- Detailed sensory visualization of the achieved goal
- Emotional states associated with success
- Specific affirmations in present tense
- Quantum field concepts if appropriate
- Suggestions for creating new neural pathways

Output only the complete script with [PAUSE:X] markers. Make it profound, transformative, and scientifically grounded while maintaining the Monroe Institute's exploratory spirit.
"""

    try:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-pro-latest",  # Using Pro for better quality
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error generating script for '{user_goal}': {e}")
        return None

def validate_script(script_text, goal):
    """Validate the generated script for coherence and quality."""
    if not script_text:
        return False, "Script is empty"
    
    # Check for essential components
    essential_phrases = [
        "energy conversion box",
        "resonant tuning",
        "resonant energy balloon",
        "i am more than my physical body",
        "focus 10",
        "mind awake",
        "body asleep"
    ]
    
    script_lower = script_text.lower()
    missing = [phrase for phrase in essential_phrases if phrase not in script_lower]
    
    if missing:
        return False, f"Missing essential components: {', '.join(missing)}"
    
    # Check for goal integration
    if goal.lower() not in script_lower:
        return False, "Goal not properly integrated into script"
    
    # Check for pause markers
    pause_count = len(re.findall(r'\[PAUSE:\d+\]', script_text))
    if pause_count < 10:
        return False, f"Insufficient pause markers (found {pause_count}, need at least 10)"
    
    # Estimate duration
    words = len(script_text.split())
    speaking_rate = 150  # words per minute
    speech_time = words / speaking_rate
    
    pauses = re.findall(r'\[PAUSE:(\d+)\]', script_text)
    pause_time = sum(int(p) for p in pauses) / 60  # convert to minutes
    
    total_time = speech_time + pause_time
    
    return True, f"Valid script. Estimated duration: {total_time:.1f} minutes"

def save_transcript(script_text, goal, duration):
    """Save the transcript to a file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_goal = re.sub(r'[^a-zA-Z0-9_\- ]', '', goal).replace(' ', '_')
    filename = f"transcripts/{safe_goal}_{duration}min_{timestamp}.txt"
    
    os.makedirs("transcripts", exist_ok=True)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"Meditation Transcript\n")
        f.write(f"Goal: {goal}\n")
        f.write(f"Duration: {duration} minutes\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{'='*60}\n\n")
        f.write(script_text)
    
    return filename

def generate_all_meditation_transcripts():
    """Generate all 5 requested meditation transcripts."""
    goals = [
        ("Manifesting $90k", 25),
        ("Manifesting entrance into University of Washington Summer Semester", 25),
        ("Manifesting extremely clean skin and a healthy body", 25),
        ("Manifesting clean eating habits", 25),
        ("Manifesting a transformative psychedelic experience", 30)  # Longer for this deeper topic
    ]
    
    results = {}
    
    for goal, duration in goals:
        print(f"\n{'='*60}")
        print(f"Generating meditation script for: {goal}")
        print(f"Target duration: {duration} minutes")
        print(f"{'='*60}\n")
        
        script = generate_enhanced_meditation_script(goal, duration)
        
        if script:
            # Validate the script
            is_valid, validation_msg = validate_script(script, goal)
            
            if is_valid:
                # Save transcript
                filename = save_transcript(script, goal, duration)
                print(f"\n✓ Script generated successfully!")
                print(f"✓ {validation_msg}")
                print(f"✓ Saved to: {filename}")
                
                # Store result
                results[goal] = {
                    "status": "success",
                    "script": script,
                    "filename": filename,
                    "validation": validation_msg
                }
                
                # Print the script
                print(f"\n--- TRANSCRIPT ---")
                print(script)
                print(f"--- END TRANSCRIPT ---\n")
            else:
                print(f"\n✗ Script validation failed: {validation_msg}")
                results[goal] = {
                    "status": "validation_failed",
                    "error": validation_msg,
                    "script": script
                }
        else:
            print(f"\n✗ Failed to generate script")
            results[goal] = {
                "status": "generation_failed",
                "error": "Script generation returned None"
            }
    
    return results

if __name__ == "__main__":
    print("Enhanced Meditation Script Generator")
    print("Using latest neuroscience research and Monroe Institute methodology")
    print("Powered by Gemini AI\n")
    
    results = generate_all_meditation_transcripts()
    
    print("\n" + "="*60)
    print("GENERATION SUMMARY")
    print("="*60)
    
    success_count = sum(1 for r in results.values() if r["status"] == "success")
    print(f"\nSuccessfully generated: {success_count}/{len(results)} transcripts")
    
    for goal, result in results.items():
        print(f"\n{goal}:")
        print(f"  Status: {result['status']}")
        if result["status"] == "success":
            print(f"  File: {result['filename']}")
            print(f"  {result['validation']}")
        else:
            print(f"  Error: {result.get('error', 'Unknown error')}")