# Travel Guide

Travel Guide is a full-stack AI travel app that helps users explore famous destinations, generate a short or detailed description in their chosen language, and convert the text into an audio guide.

The project has:
- a Python Flask backend that calls Google Generative AI and Murf Speech APIs
- a static frontend built with HTML, JavaScript, and Tailwind CSS

## Project structure

- `Backend/app.py` - Flask API server
- `Frontend/` - static frontend files
- `.env` - local environment variables (not committed)
- `.env.example` - sample environment variables for setup
- `requirements.txt` - Python dependencies

## Features

- Browse featured places
- Search destinations
- Select response length: Summary or Detailed
- Choose language and voice gender
- Generate rich destination descriptions in the selected language
- Receive an MP3 audio guide in the browser

## Environment setup

This project expects API keys in a local `.env` file at the repository root.

The `.env` file is already included in `.gitignore`, so your secrets are not pushed to git.

Create a `.env` file from the example:

```bash
copy .env.example .env
```

Then update the values:

```env
API_KEY=your_google_ai_api_key_here
MURF_API_KEY=your_murf_api_key_here
```

## Install dependencies

From the project root:

```bash
python -m pip install -r requirements.txt
```

## Run the project

Start the backend:

```bash
python Backend/app.py
```

The API runs on:
- http://127.0.0.1:5000

Serve the frontend:

```bash
python -m http.server 8000 --directory Frontend
```

Open the app in a browser:
- http://localhost:8000

## API endpoint

The backend exposes:

- `POST http://127.0.0.1:5000/generate-audio-guide`

Request body example:

```json
{
  "place": "Taj Mahal",
  "answerType": "Summary",
  "language": "English",
  "voiceId": "Matthew",
  "locale": "en-US"
}
```

## Notes

- The backend needs valid Google AI and Murf API keys to generate descriptions and speech.
- The frontend is intentionally lightweight and does not require a build step.
- You can stop the server with `Ctrl + C` in the terminal where it is running.
