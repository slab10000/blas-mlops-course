"""
Week 2 Lab -- starter training script (NOT YET INSTRUMENTED)

Trains a RandomForestClassifier on the digits dataset (built into
scikit-learn -- 1,797 images of handwritten digits 0-9, no download needed).
Your job in this lab is to add MLflow experiment tracking around this
script -- logging hyperparameters, metrics, and a confusion matrix
artifact -- without changing what the script actually does.

Run it as-is first to see the baseline behavior:
    python train.py
"""

from sklearn.datasets import load_digits
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split

# ---- config: edit these between runs to compare results ----
N_ESTIMATORS = 10
MAX_DEPTH = 3
RANDOM_STATE = 42
# --------------------------------------------------------------


def main():
    data = load_digits()
    X, y = data.data, data.target

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE
    )

    model = RandomForestClassifier(
        n_estimators=N_ESTIMATORS,
        max_depth=MAX_DEPTH,
        random_state=RANDOM_STATE,
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average="macro")
    recall = recall_score(y_test, y_pred, average="macro")
    f1 = f1_score(y_test, y_pred, average="macro")

    print(f"n_estimators={N_ESTIMATORS}, max_depth={MAX_DEPTH}")
    print(f"accuracy:  {accuracy:.4f}")
    print(f"precision: {precision:.4f}")
    print(f"recall:    {recall:.4f}")
    print(f"f1:        {f1:.4f}")


if __name__ == "__main__":
    main()
