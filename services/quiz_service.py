import json
from openai import OpenAI
from config import Config

def generate_quiz(transcript_text):
    if not Config.AI_API_KEY:
        raise ValueError("AI_API_KEY is not configured.")

    client_args = {"api_key": Config.AI_API_KEY}
    if Config.AI_BASE_URL:
        client_args["base_url"] = Config.AI_BASE_URL
        
    client = OpenAI(**client_args)
    
    system_prompt = """
    You are an expert AI Quiz Generator.
    Generate a 10-question multiple choice quiz based strictly on the provided lecture transcript.
    
    IMPORTANT: 
    - Use ONLY information contained in the uploaded lecture.
    - Never fabricate questions or answers.
    - If the transcript doesn't have enough information for 10 questions, generate as many valid ones as possible.

    Return the output strictly in the following JSON format:
    {
      "questions": [
        {
          "question": "...",
          "options": {
            "A": "...",
            "B": "...",
            "C": "...",
            "D": "..."
          },
          "correct_answer": "A", 
          "explanation": "..."
        }
      ]
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
        print(f"Quiz generation error: {e}")
        raise e
