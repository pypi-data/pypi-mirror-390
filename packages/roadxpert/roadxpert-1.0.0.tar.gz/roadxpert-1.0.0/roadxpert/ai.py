import os, requests
from .config import HF_API_URL, HF_TOKEN

HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

def send_to_model(prompt, image_path, model):
    """Send prompt + image to AI model."""
    abs_path = os.path.abspath(image_path)

    payload = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"file://{abs_path}"}}
                ]
            }
        ],
        "model": model
    }

    response = requests.post(HF_API_URL, headers=HEADERS, json=payload)
    response.raise_for_status()
    return response.json()
