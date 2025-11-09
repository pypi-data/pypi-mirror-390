import os, json, base64, datetime, time, requests
from .utils import safe_load_json, extract_ai_content, json_to_text

# ✅ Your permanent Hugging Face credentials and model
HF_API_URL = "https://router.huggingface.co/v1/chat/completions"
HF_TOKEN = "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"  # 🔒 Replace this with your private token
DEFAULT_MODEL = "meta-llama/Llama-4-Maverick-17B-128E-Instruct:groq"


# ----------------------------------------------------------
# 1️⃣ WEATHER FETCH FUNCTION
# ----------------------------------------------------------
def get_weather_forecast(latitude: float, longitude: float):
    """Fetch a 7-day weather forecast from Open-Meteo for given coordinates."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_min,temperature_2m_max,precipitation_sum,precipitation_probability_mean",
        "timezone": "auto",
        "forecast_days": 7
    }

    try:
        response = requests.get(url, params=params)
        output = []

        if response.status_code == 200:
            data = response.json()
            if "daily" in data:
                daily = data["daily"]
                output.append("7-Day Weather Forecast:")
                output.append("=" * 40)
                for i in range(len(daily["time"])):
                    date = daily["time"][i]
                    min_temp = daily["temperature_2m_min"][i]
                    max_temp = daily["temperature_2m_max"][i]
                    precip_sum = daily["precipitation_sum"][i]
                    precip_prob = daily["precipitation_probability_mean"][i]
                    output.append(f"Date: {date}")
                    output.append(f"Temp Range: {min_temp}°C to {max_temp}°C")
                    output.append(f"Rainfall: {precip_sum} mm")
                    output.append(f"Rain Probability: {precip_prob}%")
                    output.append("-" * 20)
                
                # Simple trend summary
                temp_trend = "warming" if daily["temperature_2m_max"][-1] > daily["temperature_2m_max"][0] else "cooling/stable"
                precip_trend = "increasing rain risk" if daily["precipitation_probability_mean"][-1] > daily["precipitation_probability_mean"][0] else "decreasing/stable"
                output.append(f"\nOverall Trends: {temp_trend}; {precip_trend}.")
            else:
                output.append("Error: No daily data available.")
        else:
            output.append(f"Error fetching weather data: {response.status_code}")

        return "\n".join(output)
    
    except Exception as e:
        return f"⚠️ Weather API Error: {e}"


# ----------------------------------------------------------
# 2️⃣ AI QUERY FUNCTION
# ----------------------------------------------------------
def send_to_model(prompt: str, image_path: str, model_name: str = DEFAULT_MODEL):
    """Send text + image to Hugging Face chat model."""
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"file://{os.path.abspath(image_path)}"}}
                ]
            }
        ],
        "model": model_name
    }

    response = requests.post(HF_API_URL, headers=headers, json=payload)
    if response.status_code != 200:
        raise RuntimeError(f"Model query failed: {response.status_code}, {response.text}")
    return response.json()


# ----------------------------------------------------------
# 3️⃣ MAIN ANALYSIS FUNCTION
# ----------------------------------------------------------
def analyze_road(image_input, latitude: float, longitude: float, location_name="Unknown Area"):
    """
    Analyze a road image with weather, traffic, and AI reasoning.
    - image_input: file path or base64 string.
    - latitude, longitude: user's coordinates.
    - location_name: optional readable name.
    """
    # --- Prepare image file ---
    if os.path.exists(image_input):
        image_path = image_input
    else:
        # assume base64 input
        if "," in image_input:
            image_input = image_input.split(",")[1]
        image_bytes = base64.b64decode(image_input)
        os.makedirs("frames", exist_ok=True)
        image_path = os.path.join("frames", f"frame_{int(time.time())}.jpg")
        with open(image_path, "wb") as f:
            f.write(image_bytes)

    # --- Get weather ---
    weather_data = get_weather_forecast(latitude, longitude)

    # --- Get traffic (if logged) ---
    vehicle_count, avg_speed_kmph, avg_speed_kmps = 0, 0, 0
    if os.path.exists("vehicle_log.json"):
        try:
            with open("vehicle_log.json", "r") as f:
                lines = f.readlines()
                if lines:
                    last_entry = json.loads(lines[-1])
                    vehicle_count = last_entry.get("vehicles", 0)
                    speeds = [obj.get("speed_kmph", 0) for obj in last_entry.get("objects", [])]
                    if speeds:
                        avg_speed_kmph = sum(speeds) / len(speeds)
                        avg_speed_kmps = avg_speed_kmph / 3600.0
        except Exception:
            pass

    # --- Prompt for AI ---
    prompt = f"""
You are RoadXpert AI, a civil engineering and road safety expert.

INPUT DATA:
- Location: {location_name} ({latitude}, {longitude})
- Weather: {weather_data}
- Vehicle count: {vehicle_count}
- Average speed: {avg_speed_kmph:.2f} km/h
- Image: attached

INSTRUCTIONS:
Analyze the road image + conditions and output only valid JSON like this:

{{
  "road_damage": {{
    "potholes_detected": true/false,
    "cracks_detected": true/false,
    "damage_severity": "low/medium/high",
    "predicted_damage_in_days": number
  }},
  "traffic": {{
    "vehicle_count": {vehicle_count},
    "average_speed_kmph": {avg_speed_kmph:.2f},
    "congestion_level": "low/medium/high"
  }},
  "weather": {{
    "summary": "short summary"
  }},
  "accident": {{
    "detected": true/false,
    "details": "short description"
  }},
  "recommendations": {{
    "needs_repair": true/false,
    "repair_priority": "low/medium/high",
    "speed_bump_suggestion": "install/remove/none",
    "safety_alert": "short alert"
  }},
  "emergency": true/false
}}
"""

    # --- AI Processing ---
    ai_response = send_to_model(prompt, image_path)
    result_text = extract_ai_content(ai_response["choices"][0]["message"])
    parsed = safe_load_json(result_text)

    # --- Convert to readable text ---
    human_text = json_to_text(parsed)

    # --- Save Logs ---
    log_entry = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "location": location_name,
        "coordinates": [latitude, longitude],
        "analysis": parsed,
        "summary": human_text
    }
    os.makedirs("logs", exist_ok=True)
    with open("logs/analysis_log.json", "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    return {"json": parsed, "summary": human_text}
