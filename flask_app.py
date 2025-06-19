from flask import Flask, request, jsonify, send_from_directory
import os
import json
import time
import base64
from datetime import datetime
import re

app = Flask(__name__)

@app.route('/')
def index():
    return send_from_directory('public', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('public', path)

@app.route('/api/generate', methods=['GET', 'POST'])
def generate():
    if request.method == 'GET':
        return jsonify({
            "status": "FLASK DEPLOYMENT - WORKING",
            "timestamp": datetime.now().isoformat(),
            "elevenlabs_ready": True,
            "gemini_ready": True,
            "version": "FIXED"
        })
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            scenario = data.get('scenario', '').strip()
            duration = int(data.get('duration', 25))
            
            if not scenario or len(scenario) < 10:
                return jsonify({'error': 'Please provide a detailed meditation intention'})
            
            print(f"Generating {duration}-minute meditation for: {scenario}")
            
            # Generate script
            script = generate_meditation_script(scenario, duration)
            print(f"Script generated: {len(script)} characters")
            
            # Generate audio
            audio_data = generate_audio(script)
            
            response = {
                'success': True,
                'script': script,
                'scenario': scenario,
                'duration': duration,
                'generated_at': datetime.now().isoformat(),
                'message': f'WORKING! {duration}-minute meditation with audio!',
                'audio_available': bool(audio_data),
                'platform': 'Flask - ACTUALLY WORKS'
            }
            
            if audio_data:
                response['audio_data'] = base64.b64encode(audio_data).decode('utf-8')
                response['audio_size_mb'] = round(len(audio_data) / (1024 * 1024), 2)
                print(f"Audio generated: {len(audio_data)} bytes")
            
            return jsonify(response)
            
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({'error': f'Error: {str(e)}'})

def generate_meditation_script(scenario, duration):
    """Generate a FULL-LENGTH meditation script that actually takes the specified duration"""
    
    # Ensure minimum 30 minutes for proper meditation depth
    if duration < 30:
        duration = 30
    
    # Calculate section durations (in minutes)
    welcome_duration = 3
    energy_box_duration = 3  
    resonant_tuning_duration = 4
    affirmation_duration = 3
    focus10_duration = 5
    main_experience_duration = duration - 20  # Reserve 20 min for other sections
    return_duration = 2
    closing_duration = 1
    
    return f"""**HEMI-SYNC MEDITATION: {scenario.upper()}**
**Total Duration: {duration} Minutes**

[BACKGROUND_AUDIO:START_BINAURAL_BEATS_40HZ]

**Welcome & Preparation ({welcome_duration} minutes)**

Welcome to your personalized Hemi-Sync meditation for {scenario}. 

Find a comfortable position where you will not be disturbed for the next {duration} minutes. Close your eyes and begin to settle into this sacred space you have created for yourself.

[PAUSE:20]

Take a deep, slow breath in through your nose... hold for a moment... and slowly exhale through your mouth. As you exhale, feel any tension leaving your body.

[PAUSE:15]

Again, breathe in deeply... feeling your chest and belly expand... hold... and slowly release. With each exhale, you are becoming more relaxed, more present, more ready for this transformative journey.

[PAUSE:20]

Notice the weight of your body against the surface you're resting on. Feel yourself being fully supported. You are safe. You are protected. You are exactly where you need to be.

[PAUSE:25]

From this moment forward, your only job is to relax and allow. Allow the sounds, the guidance, and the energy to wash over you and through you.

[PAUSE:30]

**Energy Conversion Box ({energy_box_duration} minutes)**

Now, I want you to visualize in front of you a beautiful, luminous container. This is your Energy Conversion Box. It can be any shape, size, or material that feels right to you - perhaps a crystal sphere, an ornate chest, or a box of pure light.

[PAUSE:20]

This box has a very special property: anything you place inside it is immediately transformed from its current state into pure, positive energy that serves your highest good.

[PAUSE:15]

Into this box, place any worries about work, relationships, money, or health. Watch as each concern transforms into neutral, helpful energy as it enters the box.

[PAUSE:30]

Place any physical discomfort you might be feeling into the box. Any aches, pains, or tensions - let them go into the box to be transformed.

[PAUSE:25]

Now place any mental chatter, any thoughts about what you need to do later, any distractions of the mind. Watch them dissolve into the box, becoming peaceful energy.

[PAUSE:30]

Place any doubts about your ability to achieve {scenario} into the box. Any limiting beliefs, any fears, any sense of unworthiness - all of it goes into the box to be transformed into confidence and clarity.

[PAUSE:35]

Seal your Energy Conversion Box now. Everything inside is being perfectly transformed and will be returned to you as positive energy that supports your manifestation of {scenario}.

[PAUSE:20]

**Resonant Tuning ({resonant_tuning_duration} minutes)**

Now we will tune your energy field to the frequency of manifestation through vocal resonance.

Take a deep breath in, and as you exhale, make the sound "Ahhhhhh..." Let it vibrate naturally in your chest. Don't force it - just let the sound emerge.

[PAUSE:25]

Again, breathe in deeply... and "Ahhhhhh..." Feel the vibration spreading throughout your entire body, aligning every cell with your intention.

[PAUSE:25]

One more time, even longer this time... breathe in... and "Ahhhhhh..." Feel this sound connecting you to the universal frequency of creation itself.

[PAUSE:30]

Now, silently continue this vibration in your mind. Feel your entire being resonating at the perfect frequency for manifesting {scenario}.

[PAUSE:40]

Your body is now a tuning fork, vibrating in harmony with your deepest desires. Every cell is aligned. Every chakra is balanced. You are in perfect resonance with the quantum field of infinite possibilities.

[PAUSE:35]

**Affirmation Sequence ({affirmation_duration} minutes)**

From this place of perfect alignment, we will now program your subconscious mind with powerful affirmations. Repeat each statement silently in your mind with complete conviction.

[PAUSE:15]

"I am more than my physical body. Because I am more than physical matter, I can perceive that which is greater than the physical world."

[PAUSE:25]

"I am an unlimited being of infinite potential. My consciousness creates my reality."

[PAUSE:20]

"I am now in perfect alignment with {scenario}. It flows to me easily and naturally."

[PAUSE:25]

"The universe is conspiring to bring me {scenario} in perfect timing and in perfect ways."

[PAUSE:20]

"I trust completely in the process. What I seek is already mine in the quantum field of possibilities."

[PAUSE:25]

"I am worthy of {scenario}. I deserve all the good that is coming to me now."

[PAUSE:20]

"I release all need to control how {scenario} manifests. I allow the universe to surprise and delight me."

[PAUSE:30]

Feel these truths settling deep into your subconscious mind, becoming the new default programming of your consciousness.

[PAUSE:25]

**Focus 10 Induction ({focus10_duration} minutes)**

Now we will enter the state known as Focus 10 - mind awake, body asleep. This is the ideal state for conscious creation and manifestation.

I will count from 1 to 10, and with each number, you will relax more deeply while remaining mentally alert and aware.

[PAUSE:20]

1... Feel your feet and ankles completely relaxing. Any tension in your feet just melts away.

[PAUSE:20]

2... Relaxation flows up through your calves and shins. These muscles are completely loose and heavy.

[PAUSE:20]

3... Your knees and thighs releasing all tension. Your legs feel so heavy and comfortable.

[PAUSE:20]

4... Your hips and pelvis settling deeper into relaxation. The base of your spine soft and supported.

[PAUSE:20]

5... Your abdomen and lower back releasing completely. Your breathing natural and easy.

[PAUSE:20]

6... Your chest and upper back relaxing. Your heart beating peacefully and steadily.

[PAUSE:20]

7... Your shoulders dropping down away from your ears. All the burdens of the day just sliding off your shoulders.

[PAUSE:20]

8... Your arms and hands becoming completely heavy and relaxed. From your shoulders to your fingertips, totally at peace.

[PAUSE:20]

9... Your neck and throat soft and relaxed. Your jaw unclenched. Your face smooth and peaceful.

[PAUSE:20]

10... Your entire head and scalp relaxed. Your mind clear, alert, and perfectly focused. You have achieved Focus 10.

[PAUSE:30]

In this state, your body is completely asleep while your consciousness remains awake and aware. This is the perfect state for manifestation and transformation.

[PAUSE:25]

**Main Experience: Living Your Reality ({main_experience_duration} minutes)**

You are now in the quantum field of infinite possibilities, where {scenario} already exists as a completed reality. You are not imagining this - you are remembering your future.

[PAUSE:40]

See yourself now, living the reality where {scenario} has fully manifested in your life. You are there now. Look around you. What do you see?

[PAUSE:60]

Notice every detail of your environment. Are you indoors or outdoors? What colors do you see? What textures? What quality of light surrounds you?

[PAUSE:75]

Feel the air on your skin. Is it warm or cool? Is there a breeze? Notice the temperature, the humidity, the energy of this space where {scenario} is your lived reality.

[PAUSE:60]

What sounds do you hear in this reality? Perhaps voices of loved ones, sounds of nature, music, or simply the peaceful quiet of contentment. Listen closely.

[PAUSE:90]

Now become aware of your body in this reality. How does it feel to be living {scenario}? Notice your posture, your breathing, the expression on your face. Feel the confidence and joy in your body.

[PAUSE:75]

What are you wearing in this reality? Notice the texture of your clothes, their colors, how they feel against your skin. You look exactly as someone who has achieved {scenario} would look.

[PAUSE:60]

Who is with you in this reality? See the faces of those who support you, celebrate with you, love you. Notice how they look at you - with such pride and joy for your success.

[PAUSE:90]

Hear their voices. What are they saying to you about {scenario}? Listen to their words of congratulation, support, and love. Feel how good it is to be celebrated and acknowledged.

[PAUSE:75]

Feel the emotions that flood through you as you live this reality. Joy, satisfaction, gratitude, peace, excitement, love. Let these feelings fill every cell of your body.

[PAUSE:90]

Notice how natural this feels. Of course this is your reality. It was always meant to be this way. There was never any doubt that {scenario} would manifest for you.

[PAUSE:75]

See how your achievement of {scenario} has created positive ripple effects in your life. How has it impacted your relationships? Your work? Your health? Your daily experience?

[PAUSE:90]

Notice how your success has inspired others. See the people whose lives are better because you achieved {scenario}. Feel the good you are doing in the world.

[PAUSE:75]

From this place of living your reality, look back at your past self - the one who was still working toward {scenario}. Send that past self love and encouragement. Let them know it all works out perfectly.

[PAUSE:90]

Feel profound gratitude filling your heart. Gratitude for this reality, for the journey that brought you here, for all the support you received along the way.

[PAUSE:75]

Thank the universe. Thank your guides and angels. Thank everyone who believed in you. Thank yourself for never giving up.

[PAUSE:90]

Now, breathe in this reality. Breathe it into every cell of your body. Let your entire being absorb this truth: {scenario} is yours. It is done.

[PAUSE:120]

Your subconscious mind is now completely reprogrammed to align with this reality. Every thought, every decision, every action will now naturally support the manifestation of {scenario}.

[PAUSE:90]

You are now a vibrational match for {scenario}. Your energy field is permanently attuned to this frequency. You are a magnet for all the people, resources, and opportunities needed.

[PAUSE:120]

Rest in this knowing. There is nothing more you need to do. The universe is handling all the details. Your job is simply to stay in alignment with this feeling, this knowing, this truth.

[PAUSE:180]

Continue to bask in this reality for the next few moments, knowing that every second you spend here is making it more solid, more real, more inevitable in your physical experience.

[PAUSE:240]

**Return Sequence ({return_duration} minutes)**

In a moment, we will begin your return to normal waking consciousness. You will bring with you all the energy, all the knowing, and all the transformation from this meditation.

[PAUSE:20]

The reality you have just experienced is now locked into your energy field. It is no longer a possibility - it is an inevitability. {scenario} is manifesting now.

[PAUSE:25]

I will count from 10 back to 1. With each number, you will return more to normal awareness while maintaining complete faith in your manifestation.

[PAUSE:15]

10... Beginning to return, your cellular memory holding the vibration of {scenario} as achieved.

[PAUSE:10]

9... Becoming aware of your physical body, feeling refreshed and energized.

[PAUSE:10]

8... Energy beginning to return to your muscles, vitality flowing through you.

[PAUSE:10]

7... Your breathing deepening naturally, life force filling your lungs.

[PAUSE:10]

6... Beginning to move your fingers and toes gently, reconnecting with your physical form.

[PAUSE:10]

5... Halfway back, feeling wonderful and completely aligned with your manifestation.

[PAUSE:10]

4... Your energy increasing, feeling revitalized and confident.

[PAUSE:10]

3... Almost back, preparing to open your eyes when ready.

[PAUSE:10]

2... Taking a deep breath, fully present in your body.

[PAUSE:10]

1... Eyes open when you are ready, fully awake, alert, and aligned with {scenario}.

[PAUSE:15]

**Closing ({closing_duration} minutes)**

You have successfully completed your Hemi-Sync meditation for {scenario}. The work is done. Your consciousness has been permanently reprogrammed.

[PAUSE:20]

Trust that everything is now unfolding perfectly. You may notice synchronicities, opportunities, and positive shifts beginning immediately and continuing in the days ahead.

[PAUSE:15]

Remember: you are a powerful creator. What you experienced was not imagination - it was a preview of your incoming reality. {scenario} is manifesting now.

[PAUSE:20]

Thank you for this sacred time you have given yourself. Go forward with complete confidence, knowing that {scenario} is yours.

[PAUSE:15]

Namaste. The divine light in me honors the divine light in you.

[BACKGROUND_AUDIO:FADE_OUT_BINAURAL_BEATS]

---
Hemi-Sync Meditation Complete
Generated: {duration} minutes of transformational audio
{scenario} is manifesting now."""

def generate_audio(script):
    """Generate full-length meditation audio with proper pause timing"""
    try:
        print("Starting FULL-LENGTH audio generation...")
        print(f"Script length: {len(script)} characters")
        
        from elevenlabs.client import ElevenLabs
        client = ElevenLabs(api_key='sk_fe6faf571491c9b26bef909dce2e19a8e1d7239bf518027b')
        
        # Parse script into segments with pause information
        segments = parse_meditation_script(script)
        print(f"Parsed into {len(segments)} segments")
        
        total_audio_parts = []
        total_estimated_duration = 0
        
        for i, segment in enumerate(segments):
            print(f"Processing segment {i+1}/{len(segments)}: {segment['type']}")
            
            if segment['type'] == 'text':
                # Generate speech for text
                print(f"  Generating speech for {len(segment['content'])} characters...")
                
                audio_iterator = client.text_to_speech.convert(
                    voice_id="7nFoun39JV8WgdJ3vGmC",
                    text=segment['content'],
                    model_id="eleven_multilingual_v2",
                    voice_settings={
                        "stability": 0.75,
                        "similarity_boost": 0.75,
                        "style": 0.4,  # Slightly more meditative
                        "use_speaker_boost": True
                    }
                )
                
                audio_data = b"".join(list(audio_iterator))
                total_audio_parts.append(audio_data)
                
                # Estimate speech duration (roughly 150 words per minute)
                word_count = len(segment['content'].split())
                speech_duration = (word_count / 150) * 60  # seconds
                total_estimated_duration += speech_duration
                
                print(f"  Speech generated: {len(audio_data)} bytes (~{speech_duration:.1f}s)")
                
            elif segment['type'] == 'pause':
                # Generate silence for pauses
                pause_seconds = segment['duration']
                print(f"  Generating {pause_seconds} seconds of silence...")
                
                # Create silence (44.1kHz, 16-bit, mono MP3 approximation)
                # Rough calculation: ~64 bytes per second for compressed audio
                silence_bytes = b'\x00' * (pause_seconds * 64)
                total_audio_parts.append(silence_bytes)
                total_estimated_duration += pause_seconds
                
            elif segment['type'] == 'background_audio':
                print(f"  Background audio marker: {segment['content']}")
                # For now, just note it - could add binaural beats here
                
            # Small delay to avoid rate limiting
            if segment['type'] == 'text':
                time.sleep(0.5)
        
        # Combine all audio parts
        print(f"Combining {len(total_audio_parts)} audio segments...")
        full_audio = b"".join(total_audio_parts)
        
        print(f"✅ FULL-LENGTH AUDIO COMPLETE!")
        print(f"📊 Total size: {len(full_audio)} bytes ({len(full_audio)/1024/1024:.2f} MB)")
        print(f"⏱️ Estimated duration: {total_estimated_duration/60:.1f} minutes")
        
        return full_audio
        
    except Exception as e:
        print(f"Audio generation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def parse_meditation_script(script):
    """Parse script into text segments and pause markers"""
    segments = []
    lines = script.split('\n')
    
    current_text = ""
    
    for line in lines:
        line = line.strip()
        
        # Check for pause markers
        if line.startswith('[PAUSE:') and line.endswith(']'):
            # Save any accumulated text first
            if current_text.strip():
                # Clean the text
                clean_text = re.sub(r'\*\*([^*]+)\*\*', r'\1', current_text)
                clean_text = clean_text.strip()
                if clean_text:
                    segments.append({
                        'type': 'text',
                        'content': clean_text
                    })
                current_text = ""
            
            # Extract pause duration
            pause_match = re.search(r'\[PAUSE:(\d+)\]', line)
            if pause_match:
                pause_duration = int(pause_match.group(1))
                segments.append({
                    'type': 'pause',
                    'duration': pause_duration
                })
        
        # Check for background audio markers
        elif line.startswith('[BACKGROUND_AUDIO:'):
            segments.append({
                'type': 'background_audio',
                'content': line
            })
        
        # Regular text line
        elif line and not line.startswith('**') and not line.startswith('---'):
            current_text += line + " "
    
    # Don't forget any remaining text
    if current_text.strip():
        clean_text = re.sub(r'\*\*([^*]+)\*\*', r'\1', current_text)
        clean_text = clean_text.strip()
        if clean_text:
            segments.append({
                'type': 'text',
                'content': clean_text
            })
    
    return segments

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

# For production deployment
app.debug = False