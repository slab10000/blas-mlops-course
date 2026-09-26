"""Week 4: train and tune a preprocessing pipeline without train/test leakage."""
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

DATA_PATH = Path(__file__).resolve().with_name("loan_applications.csv")
NUMERIC_FEATURES = [
    "age", "annual_income", "months_employed", "loan_amount", "account_balance"
]
CATEGORICAL_FEATURES = ["employment_type", "home_ownership"]


def load_data():
    return pd.read_csv(DATA_PATH)


def build_pipeline(n_components=5):
    """Construct unfitted steps; use None for the Part 5 comparison without PCA."""
    numeric_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])
    categorical_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore")),
    ])
    preprocessor = ColumnTransformer([
        ("num", numeric_pipeline, NUMERIC_FEATURES),
        ("cat", categorical_pipeline, CATEGORICAL_FEATURES),
    ])
    return Pipeline([
        ("preprocess", preprocessor),
        ("pca", "passthrough" if n_components is None else
         PCA(n_components=n_components, random_state=42)),
        ("clf", LogisticRegression(max_iter=1000)),
    ])


def main():
    df = load_data()
    X = df.drop(columns=["defaulted"])
    y = df["defaulted"]

    # Split raw rows before any imputer, scaler, encoder, or PCA is fitted.
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    pipe = build_pipeline()
    param_grid = {
        "pca__n_components": [3, 5, 8],
        "clf__C": [0.1, 1, 10],
    }
    grid = GridSearchCV(pipe, param_grid, cv=5, scoring="accuracy")
    grid.fit(X_train, y_train)

    print("Best params:", grid.best_params_)
    print("Best CV accuracy:", round(grid.best_score_, 4))
    final_acc = accuracy_score(y_test, grid.best_estimator_.predict(X_test))
    print("Final test accuracy:", round(final_acc, 4))
    # GridSearchCV fits clones; inspect the fitted winner, not the blueprint.
    print("Best PCA explained variance ratio:",
          grid.best_estimator_.named_steps["pca"].explained_variance_ratio_)
    return grid


if __name__ == "__main__":
    main()
