# Week 3 Data Ingestion Pipeline

## Run

From the course repository root with the existing Python 3.11 virtual environment:

```sh
source .venv/bin/activate
python -m pip install requests==2.34.2
python labs/week03-ingestion/fetch_weather.py
ls data/raw/
```

The script requests current temperature, wind speed, and relative humidity from Open-Meteo for Seattle, New York, and Austin. It lands each successful complete JSON response under `data/raw/` before any downstream processing. All raw output is ignored by Git. The tracked `data/README.md` from the course template remains available.

## Implementation

- Five-second Requests timeout and `raise_for_status()` on every call.
- `fetch_current_weather()` retains the Part 4 single-attempt error demonstrations.
- `fetch_with_retry()` retries timeouts and connection errors, for four total attempts.
- Delays are **1, 2, and 4 seconds**. The handout's loop has four attempts and three gaps, so there is no final 8-second sleep. Four retries after the initial request would require five attempts.
- HTTP errors terminate immediately, following this lab's policy; invalid JSON also stops without landing.
- A failed city is skipped before saving, and later cities still run. This corrects the intermediate handout snippet that could write `null` before checking for failure.
- UTC timestamps include microseconds. New York becomes `new_york` in filenames; exclusive creation prevents overwriting an existing file.
- The complete decoded JSON is retained, including metadata and units. Pretty-printing changes whitespace, not the fields or values. This is semantic preservation, not a byte-for-byte copy of the HTTP body.

## Recorded results

Live run on September 14, 2026 (September 15, 2026 UTC). Three files landed successfully.

| City | API local time | Temperature °C | Wind km/h | Humidity % |
| --- | --- | ---: | ---: | ---: |
| Seattle | 2026-09-14 17:45 | 17.2 | 4.5 | 68 |
| New York | 2026-09-14 20:45 | 19.8 | 10.1 | 54 |
| Austin | 2026-09-14 19:45 | 33.7 | 17.3 | 45 |

The complete submission bundle in `lab3` also includes the unmodified starter, live failure/retry scripts, raw files, screenshots, a results manifest, and nine deterministic behavioral tests. The tests use mocks; the checkpoint demonstrations used actual network requests.

## Reflection

### Which failure was easiest or hardest to trigger

The invalid latitude was the easiest to trigger predictably: `latitude=999` returned HTTP 400 on the first request. The hostname typo also produced a connection error. The timeout was the most environment-dependent trigger because DNS, cached connections, proxies, and network timing can affect the exception. In this run, a 0.001-second timeout reliably triggered the timeout handler. The observed single-attempt durations were approximately 0.051 seconds for timeout, 1.221 seconds for the hostname typo, and 0.617 seconds for HTTP 400; the typo took the longest to resolve as a failure.

### How backoff changed the timing

The printed waits doubled from 1 second to 2 seconds to 4 seconds. The four-attempt timeout demonstration lasted 7.035 seconds in total, consistent with seven seconds of scheduled waiting plus request overhead. The program did not sleep after the final failed attempt. Increasing the gap between attempts gives a transient problem time to recover and reduces repeated pressure on the service.

### Why HTTP 400 was not retried

A latitude of 999 is an invalid request, so sending the same parameters again cannot repair it. In the lecture's distinction between transient and permanent failures, the request must be corrected by the producer. Repeating it would add load without useful work; many clients doing so could amplify an outage. This implementation follows the lab by not retrying any HTTP status error. A production policy would need to distinguish retryable statuses such as 429 or selected 5xx responses and consider Retry-After and jitter.

### Data contract for another team

**Schema:** Specify the top-level metadata, `current`, and `current_units` objects; required field names, JSON types, and nullable/missing-field behavior. `current.time` is an ISO local-time string, `current.interval` is a number of seconds, and the three weather values are numeric. Consumers should preserve or tolerate additional fields and quarantine missing required fields.

**Semantics:** Temperature is at 2 metres in °C, wind speed is at 10 metres in km/h, and relative humidity is at 2 metres in percent. Use `timezone` and `utc_offset_seconds` with local timestamps; a UTC filename marks ingestion time, not measurement time. Coordinates returned by the API may describe the selected grid cell. These are model-based current weather estimates, not guaranteed station observations. Distinguish a missing file caused by failure from a null weather value.

**SLA:** This lab runs manually and makes no uptime or freshness guarantee. For a scheduled consumer, propose an agreed cadence, a maximum lateness after each scheduled run, per-city completeness monitoring, alerts for missed runs, and a documented replay/retention policy. A candidate schedule is every 15 minutes with an alert after 30 minutes without a successful city landing; this is a proposal, not a measured service commitment.

**Change management:** Assign an owner and contract version, validate sample payloads before changes, announce field/type/unit/timezone changes, give consumers a migration window, and use a new version or parallel path for breaking changes. Retain original raw data so consumers can reprocess it after fixing their readers.

## Sources

- Lab 3 Data Ingestion Pipeline handout.
- [Open-Meteo forecast API documentation](https://open-meteo.com/en/docs).
- [Requests quickstart: errors and timeouts](https://requests.readthedocs.io/en/latest/user/quickstart/).
