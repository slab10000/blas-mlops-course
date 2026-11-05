"""Serve the flow on a schedule, so nobody has to start it by hand.

Run from your repo root, in a second terminal, with the Prefect server already running:
    export PREFECT_API_URL=http://127.0.0.1:4200/api
    python labs/week11-orchestration/serve.py
Stop it with Ctrl+C.
"""
from pipeline import delivery_pipeline

if __name__ == "__main__":
    # YOUR CODE (Part 6): run the flow every minute (for the lab only; a real job would run once a night).
    # The cron string has five fields: minute hour day-of-month month day-of-week.
    # Hint: a star in every field means "every". A nightly 2 a.m. run is "0 2 * * *".
    delivery_pipeline.serve(name="nightly-retrain", cron="___")
