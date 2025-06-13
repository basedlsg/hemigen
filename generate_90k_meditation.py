import google.generativeai as genai
import os
from datetime import datetime
import re

# --- Gemini API Key Configuration ---
GEMINI_API_KEY = "AIzaSyAqko3NqGS-GtXhzm8LeiZ3xUEyo_XIqLo"
genai.configure(api_key=GEMINI_API_KEY)

generation_config = {
    "temperature": 0.8,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

def generate_90k_meditation():
    prompt = """
Create a 25-minute Hemi-Sync style meditation script specifically for manifesting $90,000 (ninety thousand dollars).

Follow this exact structure:

1. **Introduction/Orientation (1-2 min)**: Welcome and state the goal of manifesting $90,000

2. **Energy Conversion Box (1-2 min)**: Guide to place worries in mental container

3. **Resonant Tuning (2-3 min)**: Breathing exercises with humming, include [PAUSE:10-15] markers

4. **Resonant Energy Balloon (2-3 min)**: Create protective energy field

5. **Affirmation Phase (1-2 min)**: 
   - Standard: "I am more than my physical body..."
   - Specific: Affirmations about already having $90,000

6. **Focus 10 Induction (3-4 min)**: Count 1-10 with relaxation suggestions

7. **Main Content (10-12 min)**: 
   - Visualize having $90,000 in your bank account
   - Feel the emotions of financial abundance
   - See yourself using the money wisely
   - Experience the freedom and security it brings
   - Use present tense as if already achieved
   - Include multiple [PAUSE:30-60] for deep integration

8. **Integration (2-3 min)**: Reinforce neural pathways and daily practice

9. **Return (2-3 min)**: Count 10-1 back to full consciousness

10. **Closing (30 sec-1 min)**: Brief reinforcement

IMPORTANT: 
- Include the specific amount "$90,000" or "ninety thousand dollars" multiple times
- Use [PAUSE:X] markers throughout (X = seconds)
- Make it feel authentic and transformative
- Focus on the feeling of already having the money
"""

    try:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-pro-latest",
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error: {e}")
        return None

# Generate the script
print("Generating Manifesting $90k meditation transcript...")
script = generate_90k_meditation()

if script:
    # Save to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"transcripts/Manifesting_90k_25min_{timestamp}.txt"
    
    os.makedirs("transcripts", exist_ok=True)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"Meditation Transcript\n")
        f.write(f"Goal: Manifesting $90k\n")
        f.write(f"Duration: 25 minutes\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{'='*60}\n\n")
        f.write(script)
    
    print(f"\n✓ Script generated successfully!")
    print(f"✓ Saved to: {filename}")
    
    # Print the transcript
    print(f"\n--- TRANSCRIPT ---")
    print(script)
    print(f"--- END TRANSCRIPT ---\n")
else:
    print("Failed to generate script")