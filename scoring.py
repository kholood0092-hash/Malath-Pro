import requests

# ─────────────────────────────────────────────────────────────
# Open-Meteo API — مجاني، لا يحتاج API key، لا قيود
# سبب الاستبدال: OpenWeatherMap كان يرجع 403 "Host not in allowlist"
# ─────────────────────────────────────────────────────────────

def get_environmental_data(lat, lon):
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&current=temperature_2m,relative_humidity_2m,wind_speed_10m"
        "&timezone=auto"
    )
    try:
        response = requests.get(url, timeout=6)
        if response.status_code != 200:
            raise ValueError(f"HTTP {response.status_code}")

        current    = response.json()["current"]
        temp       = round(float(current["temperature_2m"]),        1)
        humidity   = round(float(current["relative_humidity_2m"]),  0)
        wind_speed = round(float(current["wind_speed_10m"]) / 3.6,  1)  # km/h → m/s

        print(f"[scoring] LIVE: {temp}°C  {humidity}%  {wind_speed} m/s")
        return {"temp": temp, "humidity": humidity, "wind_speed": wind_speed,
                "lat": lat, "lon": lon, "source": "live"}

    except Exception as e:
        print(f"[scoring] API error: {e} — fallback")
        temp, humidity, wind_speed = _fallback_values(lat, lon)
        return {"temp": temp, "humidity": humidity, "wind_speed": wind_speed,
                "lat": lat, "lon": lon, "source": "fallback"}


# ── قيم احتياطية واقعية لكل مدينة خليجية ──────────────────
_GULF_FALLBACK = [
    # lat_min, lat_max, lon_min, lon_max, temp, humidity, wind_m/s
    (29.0, 30.2, 47.0, 48.5,  38, 30, 5.0),  # الكويت
    (28.9, 29.5, 47.5, 47.7,  37, 32, 4.5),  # الجهراء
    (29.0, 29.2, 48.0, 48.2,  39, 60, 5.5),  # الأحمدي
    (24.5, 25.0, 46.4, 47.0,  40, 15, 4.0),  # الرياض
    (21.3, 21.8, 39.0, 39.4,  36, 70, 6.0),  # جدة
    (26.3, 26.5, 49.8, 50.2,  39, 55, 6.0),  # الدمام
    (25.0, 25.5, 55.1, 55.5,  38, 60, 4.5),  # دبي
    (24.3, 24.7, 54.2, 54.6,  39, 58, 4.0),  # أبوظبي
    (25.2, 25.5, 51.4, 51.7,  39, 55, 5.0),  # الدوحة
    (25.3, 25.6, 51.4, 51.6,  39, 52, 4.5),  # لوسيل
    (23.5, 23.7, 58.3, 58.5,  35, 60, 4.0),  # مسقط
    (16.9, 17.2, 54.0, 54.2,  27, 75, 6.0),  # صلالة
    (26.1, 26.4, 50.5, 50.7,  38, 60, 5.5),  # المنامة
    (26.2, 26.4, 50.5, 50.7,  38, 58, 5.0),  # المحرق
]

def _fallback_values(lat, lon):
    for lat_min, lat_max, lon_min, lon_max, t, h, w in _GULF_FALLBACK:
        if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
            return t, h, w
    temp     = 42 if lat < 23 else (38 if lat < 26 else 34)
    humidity = 65 if lon > 55 else (55 if lon > 50 else 28)
    return temp, humidity, 5.0


# ── درجة الاستدامة (0–100) ─────────────────────────────────
def calculate_sustainability_score(env_data):
    score      = 100
    temp       = env_data.get("temp",       35)
    humidity   = env_data.get("humidity",   40)
    wind_speed = env_data.get("wind_speed",  0)

    if temp > 45:   score -= 30
    elif temp > 40: score -= 20
    elif temp > 35: score -= 12
    elif temp > 30: score -= 6

    if humidity > 80:   score -= 20
    elif humidity > 65: score -= 12
    elif humidity > 50: score -= 6
    elif humidity > 35: score -= 3

    if wind_speed >= 7:   score += 5
    elif wind_speed >= 4: score += 3
    elif wind_speed < 1:  score -= 3

    return max(0, min(100, round(score)))
