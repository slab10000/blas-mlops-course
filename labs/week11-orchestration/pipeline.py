"""Week 11: the delivery-lateness chain as a Prefect flow.

Run from your repo root (venv active):
    python labs/week11-orchestration/pipeline.py
    python labs/week11-orchestration/pipeline.py --batch batches/batch_bad_metres.csv
    python labs/week11-orchestration/pipeline.py --run-date 2026-11-01
    FLAKY=1 python labs/week11-orchestration/pipeline.py        # a read that fails twice
"""
import argparse
import json
import os
from datetime import date
from pathlib import Path

import joblib
import pandas as pd
from prefect import flow, task
from prefect.runtime import task_run
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

from src.checks import problems
from src.features import build_pipeline
from src.promotion import should_promote

LAB = Path(__file__).resolve().parent      # so paths work from any folder


# YOUR CODE (Part 3): give this task 3 retries, 2 seconds apart.
# Hint: @task(retries=___, retry_delay_seconds=___)
@task
def ingest(path):
    """Read one new batch of deliveries."""
    if os.environ.get("FLAKY") == "1" and task_run.run_count <= 2:
        raise ConnectionError(f"simulated network blip while reading {path}")   # Part 3 only
    df = pd.read_csv(LAB / path)
    print(f"ingest: read {len(df)} rows from {path}")
    return df


@task
def validate(df):
    """Stop the chain if the new batch breaks the data contract (src/checks.py)."""
    found = problems(df)          # a list of messages; an empty list means the data is fine
    # YOUR CODE (Part 2): if found is not empty, stop the chain by raising an error that lists the problems.
    # Hint (fill the blanks):
    #     if ___:
    #         raise ValueError("data check failed: " + "; ".join(___))
    print("validate: finished")
    return df


@task
def train(new):
    """Train on the base data plus the new batch; score on the frozen test split (same as Week 10)."""
    base = pd.read_csv(LAB / "data" / "deliveries.csv")
    X, y = base.drop(columns="late"), base["late"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, stratify=y, random_state=42)
    data = pd.concat([pd.concat([X_train, y_train], axis=1), new], ignore_index=True)
    model = build_pipeline().fit(data.drop(columns="late"), data["late"])
    auc = float(roc_auc_score(y_test, model.predict_proba(X_test)[:, 1]))
    print(f"train: {len(data)} rows, test AUC {auc:.4f}")
    return model, auc


@task
def register(model, auc, run_date):
    """Save this run's model as a version, and record what the promotion rule says (Week 9)."""
    champion = json.load(open(LAB / "models" / "champion.json"))
    promote = should_promote(champion["auc"], auc, min_gain=0.01)
    decision = {
        "run_date": run_date,
        "champion_auc": champion["auc"],
        "challenger_auc": round(auc, 4),
        "decision": "PROMOTE" if promote else "KEEP CHAMPION",
    }
    (LAB / "runs").mkdir(exist_ok=True)
    (LAB / "models" / "versions").mkdir(exist_ok=True)
    joblib.dump(model, LAB / "models" / "versions" / f"model_{run_date}.joblib")
    # Part 5 problem: every run ADDS one more line to the same file.
    with open(LAB / "runs" / "history.csv", "a") as f:
        f.write(f"{run_date},{auc:.4f},{decision['decision']}\n")
    # YOUR CODE (Part 5): delete the two lines above and write one file per run date instead.
    # Hint (fill the blanks):
    #     (LAB / "runs" / f"___{run_date}.json").write_text(json.dumps(___, indent=2))
    print("register:", decision)


@flow(log_prints=True)
def delivery_pipeline(batch="batches/batch_good.csv", run_date=None):
    run_date = run_date or date.today().isoformat()
    new = ingest(batch)
    # YOUR CODE (Part 2): call the other three tasks in order, passing each result on.
    # Hint (same shape as the line above; fill the blanks):
    #     ok = validate(___)
    #     model, auc = train(___)
    #     register(___, ___, run_date)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", default="batches/batch_good.csv")
    ap.add_argument("--run-date", default=None)
    a = ap.parse_args()
    delivery_pipeline(batch=a.batch, run_date=a.run_date)
