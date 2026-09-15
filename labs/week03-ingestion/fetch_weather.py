"""
Week 3 Lab — Starter Script (uninstrumented)

Fetches the current weather for a single hardcoded city from the free
Open-Meteo API (https://open-meteo.com) — no API key or signup required.

This version is intentionally fragile: no timeout, no status check, no
error handling, no retry logic, and it doesn't save (land) the raw
response anywhere. Run it once as-is to see the happy path, then build
all of that up yourself — that's today's lab.
"""
import requests

CITY_NAME = "Seattle"
LATITUDE = 47.6062
LONGITUDE = -122.3321


def fetch_current_weather(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,wind_speed_10m,relative_humidity_2m",
        "timezone": "auto",
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data


if __name__ == "__main__":
    weather = fetch_current_weather(LATITUDE, LONGITUDE)
    current = weather["current"]
    print(f"Current weather in {CITY_NAME}:")
    print(f"  Temperature: {current['temperature_2m']}°C")
    print(f"  Wind speed:  {current['wind_speed_10m']} km/h")
    print(f"  Humidity:    {current['relative_humidity_2m']}%")
