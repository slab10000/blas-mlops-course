"""
Week 4's leak-free pipeline (ColumnTransformer + Pipeline + PCA + GridSearchCV),
unmodified. This is this week's starting point -- Parts 2-4 add data validation
in front of it; Part 5 adds dataset versioning around it.
"""
import os
import sys
import hashlib
from io import BytesIO
from pathlib import Path
import subprocess
import mlflow
from get_data_hash import get_data_hash
from validate_data import validate
import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression

DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "loan_applications.csv")
NUMERIC_FEATURES = ["age", "annual_income", "months_employed", "loan_amount", "account_balance"]
CATEGORICAL_FEATURES = ["employment_type", "home_ownership"]


def load_data(df=None):
    if df is None:
        df = pd.read_csv(DATA_PATH)
    X = df[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    y = df["defaulted"]
    return X, y


def build_pipeline():
    numeric_pipe = Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
    ])
    categorical_pipe = Pipeline([
        ("impute", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ])
    preprocessor = ColumnTransformer([
        ("num", numeric_pipe, NUMERIC_FEATURES),
        ("cat", categorical_pipe, CATEGORICAL_FEATURES),
    ])
    return Pipeline([
        ("preprocess", preprocessor),
        ("pca", PCA(n_components=5)),
        ("clf", LogisticRegression(max_iter=1000)),
    ])


def main():
    # Validate and hash the same bytes used for training.
    raw_bytes = Path(DATA_PATH).read_bytes()
    raw_df = pd.read_csv(BytesIO(raw_bytes))
    if not validate(raw_df):
        print("Training aborted before preprocessing or GridSearchCV.")
        return 1
    data_hash = get_data_hash()
    if hashlib.md5(raw_bytes).hexdigest() != data_hash:
        print("Training aborted: CSV does not match the DVC pointer. Run dvc add or dvc checkout.")
        return 1

    X, y = load_data(raw_df)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    pipe = build_pipeline()
    param_grid = {"pca__n_components": [3, 5, 8], "clf__C": [0.1, 1, 10]}
    grid = GridSearchCV(pipe, param_grid, cv=5)

    repo = Path(__file__).resolve().parents[2]
    mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", f"sqlite:///{repo / 'mlflow.db'}"))
    mlflow.set_experiment("week5-lab")
    code_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
    code_dirty = bool(subprocess.check_output(
        ["git", "status", "--porcelain", "--", str(Path(__file__).parent)], cwd=repo, text=True).strip())
    with mlflow.start_run(run_name=os.environ.get("MLFLOW_RUN_NAME")) as run:
        mlflow.log_param("data_hash", data_hash)
        mlflow.log_params({"rows": len(raw_df), "random_state": 42, "test_size": 0.2,
                           "cv_folds": 5, "min_annual_income": 1000})
        mlflow.set_tags({"mlflow.source.git.commit": code_commit,
                         "code_dirty": str(code_dirty).lower(), "validation": "passed"})
        grid.fit(X_train, y_train)
        test_acc = grid.best_estimator_.score(X_test, y_test)
        mlflow.log_params(grid.best_params_)
        mlflow.log_metric("cv_accuracy", grid.best_score_)
        mlflow.log_metric("test_accuracy", test_acc)
        for filename in ["train.py", "validate_data.py", "get_data_hash.py", "loan_applications.csv.dvc"]:
            mlflow.log_artifact(str(Path(__file__).with_name(filename)), artifact_path="lineage")
        print("MLflow run:", run.info.run_id)
    print("data_hash:", data_hash)
    print("best params:", grid.best_params_)
    print("best CV accuracy:", grid.best_score_)
    print("test accuracy:", test_acc)
    return 0


if __name__ == "__main__":
    sys.exit(main())
