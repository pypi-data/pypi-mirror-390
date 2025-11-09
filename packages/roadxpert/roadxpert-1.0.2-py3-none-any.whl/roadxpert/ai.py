import base64
import requests
from .config import HF_API_URL, HF_TOKEN, DEFAULT_MODEL

def send_to_model(prompt, image_path):
    """Send prompt + image to the WholeExpert model."""
    # Convert image file → base64 data URI
    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")
    data_uri = f"data:image/jpeg;base64,{img_b64}"

    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": data_uri}}
                ],
            }
        ],
        "model": DEFAULT_MODEL,
    }

    response = requests.post(HF_API_URL, headers=headers, json=payload)
    if response.status_code != 200:
        raise RuntimeError(
            f"Model query failed: {response.status_code}, {response.text}"
        )
    return response.json()
