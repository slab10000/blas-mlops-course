"""Retrain on the base data plus any new batches, then compare with the champion.

Run from the lab folder:  python -m src.retrain
Exit code 1 means the new data failed the data checks (nothing is trained).
"""
import glob
import json
import os
import sys

import joblib
import pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

from src.checks import problems
from src.features import build_pipeline
from src.promotion import should_promote


def frozen_split(base):
    """The test split never changes, so every model is scored on the same rows."""
    X, y = base.drop(columns="late"), base["late"]
    return train_test_split(X, y, test_size=0.25, stratify=y, random_state=42)


def main():
    base = pd.read_csv("data/deliveries.csv")
    batches = sorted(glob.glob("data/incoming/*.csv"))
    new = [pd.read_csv(f) for f in batches]

    bad = False
    for f, df in zip(batches, new):
        found = problems(df)
        for line in found:
            print(f"DATA CHECK FAILED in {f}: {line}")
        bad = bad or bool(found)
    if bad:
        write_summary("Data checks failed: nothing was trained.")
        sys.exit(1)

    X_train, X_test, y_train, y_test = frozen_split(base)
    train = pd.concat([pd.concat([X_train, y_train], axis=1)] + new, ignore_index=True)
    model = build_pipeline().fit(train.drop(columns="late"), train["late"])
    challenger = float(roc_auc_score(y_test, model.predict_proba(X_test)[:, 1]))

    champion = json.load(open("models/champion.json"))
    promote = should_promote(champion["auc"], challenger, min_gain=0.01)
    decision = {
        "new_rows": int(sum(len(d) for d in new)),
        "batches": [os.path.basename(f) for f in batches],
        "champion_auc": champion["auc"],
        "challenger_auc": round(challenger, 4),
        "gain": round(challenger - champion["auc"], 4),
        "min_gain": 0.01,
        "decision": "PROMOTE" if promote else "KEEP CHAMPION",
    }
    json.dump(decision, open("decision.json", "w"), indent=2)
    if promote:
        joblib.dump(model, "models/challenger.joblib")
    print(json.dumps(decision, indent=2))
    write_summary(
        f"**{decision['decision']}**: challenger AUC {decision['challenger_auc']} vs champion "
        f"{decision['champion_auc']} (gain {decision['gain']}, needs {decision['min_gain']}), "
        f"trained with {decision['new_rows']} new rows."
    )


def write_summary(text):
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a") as f:
            f.write(text + "\n")


if __name__ == "__main__":
    main()
