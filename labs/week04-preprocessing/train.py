"""
Week 4 Lab starter -- Loan Default Prediction

Loads loan_applications.csv and trains a simple classifier to predict
whether a loan applicant will default.

This script has NOT been checked for train/test leakage yet.
That's today's lab.
"""
import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

# Resolve the CSV relative to this script's own location, not the caller's
# working directory -- so this runs the same whether you launch it from the
# repo root (python labs/week04-preprocessing/train.py) or from inside this
# folder (python train.py).
DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "loan_applications.csv")
NUMERIC_FEATURES = ["age", "annual_income", "months_employed", "loan_amount", "account_balance"]
CATEGORICAL_FEATURES = ["employment_type", "home_ownership"]


def load_data():
    return pd.read_csv(DATA_PATH)


def main():
    df = load_data()
    X = df.drop(columns=["defaulted"])
    y = df["defaulted"]

    # --- preprocessing ---
    imputer = SimpleImputer(strategy="mean")
    X[NUMERIC_FEATURES] = imputer.fit_transform(X[NUMERIC_FEATURES])

    scaler = StandardScaler()
    X[NUMERIC_FEATURES] = scaler.fit_transform(X[NUMERIC_FEATURES])

    X = pd.get_dummies(X, columns=CATEGORICAL_FEATURES)

    # --- split ---
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # --- train + evaluate ---
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print(f"Test accuracy: {acc:.4f}")


if __name__ == "__main__":
    main()
