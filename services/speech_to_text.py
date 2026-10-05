import os
from openai import OpenAI
from config import Config

def transcribe_audio(audio_path):
    if not Config.AI_API_KEY:
        raise ValueError("AI_API_KEY is not configured.")

    # Configure client
    client_args = {"api_key": Config.AI_API_KEY}
    if Config.AI_BASE_URL:
        client_args["base_url"] = Config.AI_BASE_URL
        
    client = OpenAI(**client_args)

    with open(audio_path, "rb") as audio_file:
        try:
            transcript = client.audio.transcriptions.create(
                model=Config.ASR_MODEL,
                file=audio_file
            )
            return transcript.text
        except Exception as e:
            print(f"Transcription error: {e}")
            raise e
