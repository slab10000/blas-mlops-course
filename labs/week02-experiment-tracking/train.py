"""Track the Week 2 digits classifier with MLflow.

Run from this directory so training and `mlflow ui --backend-store-uri
sqlite:///mlflow.db --port 5001` use the same local tracking store.
The default configuration reproduces the uninstrumented starter baseline.
"""

import argparse
import tempfile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mlflow
from sklearn.datasets import load_digits
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    ConfusionMatrixDisplay, accuracy_score, precision_score, recall_score, f1_score,
)
from sklearn.model_selection import train_test_split

N_ESTIMATORS = 10
MAX_DEPTH = 3
RANDOM_STATE = 42


def main(n_estimators=N_ESTIMATORS, max_depth=MAX_DEPTH,
         random_state=RANDOM_STATE, run_name=None):
    # Explicit SQLite storage avoids version-dependent MLflow defaults.
    mlflow.set_tracking_uri("sqlite:///mlflow.db")
    mlflow.set_experiment("week2-lab")
    X, y = load_digits(return_X_y=True)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=random_state
    )

    with mlflow.start_run(run_name=run_name) as run:
        model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state,
        )
        mlflow.log_params({
            "n_estimators": n_estimators,
            "max_depth": max_depth,
            "random_state": random_state,
        })
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred, average="macro"),
            "recall": recall_score(y_test, y_pred, average="macro"),
            "f1": f1_score(y_test, y_pred, average="macro"),
        }
        mlflow.log_metrics(metrics)
        fig, ax = plt.subplots(figsize=(6, 6))
        try:
            ConfusionMatrixDisplay.from_predictions(y_test, y_pred, ax=ax)
            fig.tight_layout()
            # Each run receives its own artifact; no shared PNG is overwritten.
            with tempfile.TemporaryDirectory() as tmp_dir:
                plot_path = Path(tmp_dir) / "confusion_matrix.png"
                fig.savefig(plot_path, dpi=160)
                mlflow.log_artifact(str(plot_path))
        finally:
            plt.close(fig)

        print(f"n_estimators={n_estimators}, max_depth={max_depth}")
        print(f"accuracy:  {metrics['accuracy']:.4f}")
        print(f"precision: {metrics['precision']:.4f}")
        print(f"recall:    {metrics['recall']:.4f}")
        print(f"f1:        {metrics['f1']:.4f}")
        return run.info.run_id


def parse_depth(value):
    if value.lower() == "none":
        return None
    depth = int(value)
    if depth < 1:
        raise argparse.ArgumentTypeError("max-depth must be positive or None")
    return depth


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-estimators", type=int, default=N_ESTIMATORS)
    parser.add_argument("--max-depth", type=parse_depth, default=MAX_DEPTH)
    parser.add_argument("--random-state", type=int, default=RANDOM_STATE)
    parser.add_argument("--run-name", default=None)
    args = parser.parse_args()
    if args.n_estimators < 1:
        parser.error("--n-estimators must be positive")
    main(args.n_estimators, args.max_depth, args.random_state, args.run_name)
