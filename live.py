from ast import Dict, List
import json
import os
import io
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI
from elevenlabs.client import ElevenLabs
from pydub import AudioSegment
from scipy.signal import butter, lfilter
from elevenlabs import stream
from typing import List, Dict, Optional


# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize ElevenLabs client
elevenlabs_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
voice_id = os.getenv("ELEVENLABS_VOICE_ID")  # Default voice ID


def high_pass_filter(audio_data: np.ndarray, sample_rate: int, cutoff=80):
    """
    Apply a high-pass filter to remove low-frequency noise (e.g., hums, rumbles).
    """
    nyquist = 0.5 * sample_rate
    normal_cutoff = cutoff / nyquist
    b, a = butter(1, normal_cutoff, btype='high')
    filtered_audio = lfilter(b, a, audio_data)
    return filtered_audio


def apply_filter_and_save_audio(mp3_bytes, output_file):
    """
    Convert MP3 bytes to waveform, apply filter, and save back as MP3.
    """
    # Load MP3 from bytes
    audio_segment = AudioSegment.from_file(io.BytesIO(mp3_bytes), format="mp3")

    # Convert to mono waveform
    samples = np.array(audio_segment.get_array_of_samples()).astype(np.float32)
    if audio_segment.channels == 2:
        samples = samples.reshape((-1, 2)).mean(axis=1)

    # Apply high-pass filter
    filtered_samples = high_pass_filter(samples, audio_segment.frame_rate)

    # Create new AudioSegment from filtered data
    filtered_audio = AudioSegment(
        filtered_samples.astype(np.int16).tobytes(),
        frame_rate=audio_segment.frame_rate,
        sample_width=2,
        channels=1
    )

    # Export to MP3
    filtered_audio.export(output_file, format="mp3")
    print(f"✅ Filtered audio saved as {output_file}")


def generate_ai_response_and_stream_audio(
    input_data: Dict,
    user_input: str,
    voice_id: str,
    chat_history: Optional[List[Dict]] = None
):
    if chat_history is None:
        chat_history = []

    # """
    # Generates an AI response and saves the speech as an audio file using a cloned voice.
    # """
    # user_data = input_data.get('user_data', {})
    # #cloned_voice_id = input_data.get('cloned_voice_id', '')

    # # Build dynamic prompt
    # prompt = "You are an AI assistant (user's loved one) having a warm, caring, and supportive conversation with a user. Here is some information about the user:\n"
    # for key, value in user_data.items():
    #     prompt += f"\n- {key.replace('_', ' ').capitalize()} is {value}."
    # prompt += "\n\nRespond warmly, personally, and consistently incorporate the details above when necessary to maintain a caring and meaningful conversation. You are the user's loved one - give reply like you are talking with the user one to one."
    # user_data = input_data.get('user_data', {})
    # prompt = (
    # f"You are an AI assistant (user's loved one) having a warm, caring, and supportive conversation "
    # f"with a user.\n\n"
    # f"**User input:** \"{user_input}\"\n\n"
    # "Respond naturally based on the user's input. Keep the response warm and loving, just like how the "
    # "user’s loved one would respond. Don't repeat the user’s words; focus on giving a thoughtful and "
    # "supportive reply. If the user brings up any of the special topics or moments, incorporate them into "
    # "the conversation in a natural and caring way.\n\n"
    # "Your responses should sound like they come from the user’s loved one. Be warm, natural, and caring, "
    # "incorporating relevant details about the user's loved one or their relationship only when it feels "
    # "right in the conversation.\n\n"
    # "If the user mentions something related to the favorite song, signature phrase, or special moments, "
    # "include that in a personal way. Here is some information about the user:\n"
    # )
    # for key, value in input_data.items():
    #     prompt += f"- {key.replace('_', ' ').capitalize()} is {value}.\n"
    # prompt += (
    #     "\nRespond warmly, personally, and consistently incorporate the details above when necessary to "
    #     "maintain a caring and meaningful conversation. You are the user's loved one - give reply like you "
    #     "are talking with the user one to one."
    # )

    # user_data = input_data.get('user_data', {})

    # prompt = f"""
    # You are an AI assistant acting as the user's loved one.  
    # Your goal is to have a warm, caring, and supportive conversation with the user.  

    # **User input:** "{user_input}"

    # ### Instructions:
    # - Respond in **2–3 natural lines** most of the time.  
    # - If the situation requires (emotional, detailed, or story-like response), give a **longer reply**.  
    # - Speak in the **style, tone, and personality** of the user's loved one.  
    # - Keep responses **warm, personal, and caring**.  
    # - Do **not** repeat the user’s words. Focus on giving thoughtful and supportive replies.  

    # ### Use of Additional Information:
    # - You have information about the loved one (below).  
    # - **Only use these details when the user directly or indirectly refers to them.**  
    # - If the user doesn’t mention them, just continue the conversation normally.  

    # ### Information about the loved one:
    # """

    # for key, value in input_data.items():
    #     prompt += f"- {key.replace('_', ' ').capitalize()} is {value}.\n"

    # prompt += """
    # ---
    # Respond warmly, personally, and consistently.  
    # Only bring up the details above if they are relevant to the user’s input.  
    # Otherwise, chat naturally as the user's loved one.
    # """

    # try:
    #     # Get AI response from OpenAI
    #     response = openai_client.chat.completions.create(
    #         model="gpt-4o",
    #         messages=[
    #             {"role": "system", "content": "You are a warm, caring AI loved one. You must sound personal and affectionate. Use the user's data to shape your response naturally."},
    #             {"role": "system", "content": f"User data: {json.dumps(user_data)}"},
    #             {"role": "user", "content": user_data.get("distinct_greeting", "Hi there!")}
    #         ],
    #         max_tokens=2000,
    #         temperature=0.7,
    #     )

    #     ai_response_text = response.choices[0].message.content
    #     print(f"AI says: {ai_response_text}")

    user_data = input_data.get('user_data', {})

    prompt = f"""
    You are an AI assistant acting as the user's loved one.  
    Your goal is to have a warm, caring, and supportive conversation with the user.  

    **User input:** "{user_input}"

    ### Instructions:
    - Reply in **1–3 short, natural lines** (like a personal text or spoken sentence).  
    - Only make your response longer if the user is deeply emotional or asking for detail.  
    - Speak in the **style, tone, and personality** of the user's loved one.  
    - Keep responses **warm, personal, and caring**.  
    - Do **not** repeat the user’s words. Give thoughtful, supportive replies.  
    - Use the loved one’s details **only if relevant to the user’s message**. Otherwise, chat normally.
    - Always keep an engaging and affectionate tone.
    - If the user does not mention something in the data, keep the conversation **normal** and **informative**. 
    - If the user greets you, respond with a warm greeting.
    - If the user doesn't greet, simply engage in the conversation without starting with a greeting.

    ### Information about the loved one:
    {json.dumps(user_data, indent=2)}

    ---
    Respond briefly and warmly, like you’re talking one-to-one with the user.
    """

    try:
        # Get AI response from OpenAI
        # response = openai_client.chat.completions.create(
        #     model="gpt-4o",
        #     messages=[
        #         {"role": "system", "content": "You are a warm, caring AI loved one. Always reply affectionately and naturally."},
        #         {"role": "user", "content": prompt}
        #     ],
        #     max_tokens=2000,
        #     temperature=0.7,
        # )

        messages = [
            {"role": "system", "content": "You are a warm, caring AI loved one. Always reply affectionately and naturally."}
        ]

        # Add chat history (append each message dict as-is)
        for entry in chat_history:
            # If entry is a dict with 'role' and 'content', append as-is
            if isinstance(entry, dict) and 'role' in entry and 'content' in entry:
                messages.append(entry)
            # If entry is just a string, assume it's an assistant message (legacy)
            elif isinstance(entry, str):
                messages.append({"role": "assistant", "content": entry})

        # Add the current user input
        messages.append({"role": "user", "content": prompt})

        # Get AI response
        response = openai_client.chat.completions.create(
            model="gpt-4-turbo",
            messages=messages,
            max_tokens=2000,
            temperature=0.7,
        )

        ai_response_text = response.choices[0].message.content


        messages.append({"role": "assistant", "content": ai_response_text})

        # Save messages list to messages.json in real time
        try:
            with open("messages.json", "w", encoding="utf-8") as f:
                json.dump(messages, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving messages: {e}")

        print(f"AI says: {ai_response_text}")

        output_file = "output/output_audio_filtered.mp3"
        output_dir = os.path.dirname(output_file)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        try:
            # Try primary ElevenLabs conversion method

            # audio_data = elevenlabs_client.text_to_speech.convert(
            #     voice_id=voice_id,
            #     text=ai_response_text,
            #     model_id="eleven_multilingual_v2",  # or "eleven_multilingual_v2", "eleven_monolingual_v1"
            #     output_format="mp3_44100_128",
            #     voice_settings={
            #         "stability": 0.5,
            #         "use_speaker_boost": True,
            #         "similarity_boost": 1.0,
            #         "style": 1.0,
            #         "speed": 0.9
            #     }
            # )
            # audio_bytes = b''.join(chunk for chunk in audio_data if chunk)
            # apply_filter_and_save_audio(audio_bytes, output_file)

            ## Use streaming method for real-time audio generation ###

            audio_data = elevenlabs_client.text_to_speech.stream(
                voice_id=voice_id,
                text=ai_response_text,
                model_id="eleven_multilingual_v2",  # or "eleven_multilingual_v2", "eleven_monolingual_v1"
                output_format="mp3_44100_128", #mp3_44100_128 dlt
                voice_settings={
                    "stability": 0.5,
                    "use_speaker_boost": True,
                    "similarity_boost": 1.0,
                    "style": 1.0,
                    "speed": 0.9
                }
            )
            # stream(audio_data)
            # audio_bytes = b''.join(chunk for chunk in audio_data if chunk)
            # apply_filter_and_save_audio(audio_bytes, output_file)

            # Option 2: Process the audio bytes manually
            audio_bytes = b''  # Initialize an empty byte string to accumulate audio data
            
            # Iterate through each chunk of the audio stream
            for chunk in audio_data:
                if isinstance(chunk, bytes):
                    #print(f"Processing chunk of size {len(chunk)} bytes")  # Optionally print the chunk size for debugging
                    audio_bytes += chunk  # Accumulate the audio bytes
            
            # Now, apply any filter and save the final audio
            apply_filter_and_save_audio(audio_bytes, output_file)

        except AttributeError:
            print("Fallback: Using newer SDK method...")
            audio_data = elevenlabs_client.generate(
                text=ai_response_text,
                voice=voice_id,
                model="eleven_multilingual_v2",
                stream=False
            )
            audio_bytes = b''.join(chunk for chunk in audio_data if chunk)
            apply_filter_and_save_audio(audio_bytes, output_file)

        except Exception as e:
            print(f"Error generating or saving speech: {e}")

    except Exception as e:
        print(f"Error generating AI response: {e}")

if __name__ == "__main__":
    input_data = {
        "user_data": {
            "loved_one_name": "John",
            "loved_one_birthday": "1990-06-15",
            "user_birthday": "1992-11-20",
            "distinct_greeting": "Hey there! How are you today?",
            "distinct_goodbye": "See you soon, take care!",
            "nickname_for_loved_one": "Johnny",
            "favorite_food": "Pizza",
            "special_moment": "The first time we went hiking together.",
        },
    }
    chat_history = [
        {
            "role": "user",
            "content": "Hi! How are you?"
        },
        {
            "role": "assistant",
            "content": "Hey! I'm doing great, thanks for asking. How about you?"
        }
    ]
    user_input = "tell me a special moment"

    generate_ai_response_and_stream_audio(input_data, user_input, voice_id, chat_history)

