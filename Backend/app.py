from pathlib import Path
import base64
import os
import tempfile

import requests
from dotenv import load_dotenv
from flask import Flask, request
from flask_cors import CORS
from google import genai

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

app = Flask(__name__)
CORS(app)

MURF_API_KEY = os.getenv("MURF_API_KEY") or os.getenv("murf_api_key")
API_KEY = os.getenv("API_KEY") or os.getenv("api_key")

if not API_KEY:
    raise RuntimeError("API_KEY is missing. Add it to the project's .env file.")
if not MURF_API_KEY:
    raise RuntimeError("MURF_API_KEY is missing. Add it to the project's .env file.")

client = genai.Client(api_key=API_KEY)

PROMPTS = {
    "Summary": """
You are a professional tourist guide.
Provide a high-level overview of "{place}" in {language}.

Focus on:
- The historical significance
- Why the place is famous
- Key architectural or cultural highlights

Keep the explanation concise, engaging, and easy to follow.
Avoid excessive details and dates.
Limit the response to around 200 words.

Respond ONLY in {language}.
""",
    "Detailed": """
You are a professional tourist guide.
Provide a detailed and immersive explanation of "{place}" in {language}.

Cover:
- Historical background and timeline
- Architectural design and unique features
- Cultural importance and notable events
- Interesting facts and visitor insights

Explain concepts clearly and in a storytelling manner.
Include relevant details and examples to create a rich experience.
Limit the response to around 400 words.

Respond ONLY in {language}.
""",
}


@app.get("/")
def health_check():
    return {"status": "ok", "message": "Travel Guide API is running."}


def generate_speech(text, voice_id, locale):
    temp_audio = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)

    url = "https://global.api.murf.ai/v1/speech/stream"
    headers = {
        "api-key": MURF_API_KEY,
        "Content-Type": "application/json",
    }
    data = {
        "voice_id": voice_id,
        "text": text,
        "locale": locale,
        "model": "FALCON",
        "format": "MP3",
        "sampleRate": 24000,
        "channelType": "MONO",
    }

    response = requests.post(url, headers=headers, json=data, timeout=120)

    if response.status_code == 200:
        with open(temp_audio.name, "wb") as audio_file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    audio_file.write(chunk)
        return temp_audio.name

    raise RuntimeError(f"Murf speech generation failed with status {response.status_code}: {response.text[:200]}")


def generate_description(place, answer_type, language):
    prompt = PROMPTS[answer_type].format(place=place, language=language)
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
    )
    return response.text


@app.route("/generate-audio-guide", methods=["POST"])
def generate_audio_guide():
    data = request.get_json(silent=True) or {}
    place = data.get("place")
    answer_type = data.get("answerType")
    language = data.get("language")
    voice_id = data.get("voiceId")
    locale = data.get("locale")

    if not all([place, answer_type, language, voice_id, locale]):
        return {"error": "Missing required fields."}, 400

    text_description = generate_description(place, answer_type, language)
    audio_path = generate_speech(text_description, voice_id, locale)

    with open(audio_path, "rb") as audio_file:
        encoded_audio = base64.b64encode(audio_file.read()).decode("utf-8")

    os.remove(audio_path)

    return {
        "description": text_description,
        "audioBase64": encoded_audio,
    }


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)