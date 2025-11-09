import os, requests
from .config import HF_API_URL, HF_TOKEN
import base64

HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

def send_to_model(prompt, image_path, model):
    """Send prompt + image to AI model."""
    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")
        data_uri = f"data:image/jpeg;base64,{img_b64}"
    payload = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": data_uri}}
                ]
            }
        ],
        "model": "meta-llama/Llama-4-Maverick-17B-128E-Instruct:groq"
    }

    response = requests.post(HF_API_URL, headers=HEADERS, json=payload)
    response.raise_for_status()
    return response.json()
