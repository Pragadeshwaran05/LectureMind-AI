import json
from openai import OpenAI
from config import Config

def analyze_transcript(transcript_text):
    if not Config.AI_API_KEY:
        raise ValueError("AI_API_KEY is not configured.")

    client_args = {"api_key": Config.AI_API_KEY}
    if Config.AI_BASE_URL:
        client_args["base_url"] = Config.AI_BASE_URL
        
    client = OpenAI(**client_args)
    
    system_prompt = """
    You are an expert AI Study Assistant.
    Analyze the provided lecture transcript and extract the following:
    1. A concise but meaningful summary.
    2. Important Topics (name and short explanation).
    3. Key Points (bullet points of important facts).
    4. Structured Study Notes (clean, student-friendly notes with headings).

    IMPORTANT AI INSTRUCTION:
    Use ONLY the supplied transcript. Do not invent information. If information is not present in the transcript, do not add it.

    Return the output strictly in the following JSON format:
    {
      "summary": "...",
      "topics": [
        {
          "name": "...",
          "description": "..."
        }
      ],
      "key_points": [
        "...",
        "..."
      ],
      "study_notes": "..."
    }
    """
    
    try:
        response = client.chat.completions.create(
            model=Config.AI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Transcript: {transcript_text}"}
            ],
            response_format={"type": "json_object"}
        )
        result_text = response.choices[0].message.content.strip()
        if result_text.startswith("```json"):
            result_text = result_text[7:]
        if result_text.startswith("```"):
            result_text = result_text[3:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]
        return json.loads(result_text.strip())
    except Exception as e:
        print(f"Analysis error: {e}")
        raise e
