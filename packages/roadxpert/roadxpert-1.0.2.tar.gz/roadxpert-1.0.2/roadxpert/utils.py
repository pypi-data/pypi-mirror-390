import json, ast, requests
from .config import HF_API_URL, HF_TOKEN, SUMMARY_MODEL

def safe_load_json(text):
    if not isinstance(text, str):
        return None
    txt = text.strip()
    try:
        return json.loads(txt)
    except Exception:
        pass
    start = txt.find('{')
    if start != -1:
        stack = []
        for i in range(start, len(txt)):
            ch = txt[i]
            if ch == '{':
                stack.append(i)
            elif ch == '}':
                if stack:
                    stack.pop()
                    if not stack:
                        candidate = txt[start:i+1]
                        try:
                            return json.loads(candidate)
                        except Exception:
                            break
    try:
        obj = ast.literal_eval(txt)
        if isinstance(obj, dict):
            return obj
    except Exception:
        pass
    return None


def query_ai(payload):
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    response = requests.post(HF_API_URL, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()


def extract_ai_content(response):
    if isinstance(response, dict) and "content" in response:
        return response["content"]
    return ""


def json_to_text(content):
    command = f"""
You are RoadXpert AI, an expert civil and pavement engineer.
Convert the following JSON into a professional and concise summary report.

INPUT:
{content}

TASK:
Return only a readable English summary (no JSON, no formatting, no emojis).
"""
    payload = {
        "messages": [{"role": "user", "content": command}],
        "model": SUMMARY_MODEL
    }
    response = query_ai(payload)
    return extract_ai_content(response["choices"][0]["message"])
