import os
from dotenv import load_dotenv
import json
import requests

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"


async def ask_gemini(pdf_content, user_message):
    if not GEMINI_API_KEY:
        raise ValueError("Gemini API Key is missing.")

    payload = json.dumps({
        "contents": [
            {
                "parts": [
                    {
                        "text": f"{pdf_content}\n" + "Use this content and answer the following question\n" + f"{user_message}"
                    }
                ]
            }
        ]
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", GEMINI_API_URL, headers=headers, data=payload)

    response_text = response.json()["candidates"][0]["content"]["parts"][0]["text"]

    if response.status_code != 200:
        raise ValueError(f"Gemini API Error: {response.text}")

    return response_text
