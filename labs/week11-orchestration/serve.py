"""Serve the flow on a schedule, so nobody has to start it by hand.

Run from your repo root, in a second terminal, with the Prefect server already running:
    export PREFECT_API_URL=http://127.0.0.1:4200/api
    python labs/week11-orchestration/serve.py
Stop it with Ctrl+C.
"""
from pipeline import delivery_pipeline

if __name__ == "__main__":
    # Every minute for the lab; a nightly 2 a.m. run would use "0 2 * * *".
    delivery_pipeline.serve(name="nightly-retrain", cron="* * * * *")
