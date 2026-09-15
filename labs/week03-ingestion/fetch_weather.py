"""Week 3: fetch Open-Meteo weather with retries and land complete raw JSON.

Run from the course repository root (or the lab3 folder). Output is relative
to the current working directory: data/raw/<city>_<UTC timestamp>.json.
"""
import json
from datetime import datetime, timezone
from pathlib import Path
import time

import requests

API_URL = "https://api.open-meteo.com/v1/forecast"
RAW_DATA_DIR = "data/raw"
REQUEST_TIMEOUT = 5
MAX_RETRIES = 4  # Four total attempts, matching the lab's loop.
BASE_DELAY = 1  # Wait 1, 2, 4 seconds between the four attempts.
CITIES = {
    "Seattle": (47.6062, -122.3321),
    "New York": (40.7128, -74.0060),
    "Austin": (30.2672, -97.7431),
}


def _request_weather(lat, lon, url, timeout):
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,wind_speed_10m,relative_humidity_2m",
        "timezone": "auto",
    }
    response = requests.get(url, params=params, timeout=timeout)
    response.raise_for_status()
    return response.json()


def _http_message(error):
    return f"HTTP {error.response.status_code} {error.response.reason}"


def fetch_current_weather(lat, lon, *, url=API_URL, timeout=REQUEST_TIMEOUT):
    """Part 4: one attempt, with a distinct message for each failure type."""
    try:
        return _request_weather(lat, lon, url, timeout)
    except requests.exceptions.Timeout:
        print("Request timed out.")
    except requests.exceptions.ConnectionError:
        print("Could not connect to the API.")
    except requests.exceptions.HTTPError as error:
        print(f"API returned an error: {_http_message(error)}.")
    except requests.exceptions.JSONDecodeError:
        print("API returned invalid JSON.")
    return None


def fetch_with_retry(lat, lon, *, url=API_URL, timeout=REQUEST_TIMEOUT):
    """Retry only transport failures; HTTP errors are terminal in this lab."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return _request_weather(lat, lon, url, timeout)
        except (requests.exceptions.Timeout,
                requests.exceptions.ConnectionError) as error:
            if attempt == MAX_RETRIES:
                print(f"Giving up after {MAX_RETRIES} attempts: "
                      f"{type(error).__name__}.")
                return None
            delay = BASE_DELAY * (2 ** (attempt - 1))
            print(f"Attempt {attempt} failed ({type(error).__name__}). "
                  f"Retrying in {delay}s...")
            time.sleep(delay)
        except requests.exceptions.HTTPError as error:
            print("Request rejected by the API, not retrying: "
                  f"{_http_message(error)}.")
            return None
        except requests.exceptions.JSONDecodeError:
            print("API returned invalid JSON, not retrying.")
            return None
    return None


def save_raw_response(payload, city_name, raw_data_dir=RAW_DATA_DIR):
    """Keep the complete decoded payload, with no field selection or conversion."""
    if payload is None:
        raise ValueError("Cannot land a failed request as raw data.")
    directory = Path(raw_data_dir)
    directory.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%fZ")
    city_slug = city_name.lower().replace(" ", "_")
    path = directory / f"{city_slug}_{timestamp}.json"
    # Exclusive creation prevents silently overwriting an existing landing.
    with path.open("x", encoding="utf-8") as file:
        json.dump(payload, file, indent=2, ensure_ascii=False)
        file.write("\n")
    return path


def ingest_weather(cities=None, raw_data_dir=RAW_DATA_DIR):
    """Land each successful city; a failed city does not stop the rest."""
    landed = {}
    for city_name, (lat, lon) in (CITIES if cities is None else cities).items():
        payload = fetch_with_retry(lat, lon)
        if payload is None:
            print(f"Skipping {city_name} — no data ingested this run.")
            continue
        path = save_raw_response(payload, city_name, raw_data_dir)
        landed[city_name] = path
        print(f"Landed {city_name} weather at {path}")
    return landed


if __name__ == "__main__":
    ingest_weather()
