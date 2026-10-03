"""
Week 4's leak-free pipeline (ColumnTransformer + Pipeline + PCA + GridSearchCV),
unmodified. This is this week's starting point -- Parts 2-4 add data validation
in front of it; Part 5 adds dataset versioning around it.
"""
import os
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


def load_data():
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


if __name__ == "__main__":
    X, y = load_data()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    pipe = build_pipeline()

    param_grid = {"pca__n_components": [3, 5, 8], "clf__C": [0.1, 1, 10]}
    grid = GridSearchCV(pipe, param_grid, cv=5)
    grid.fit(X_train, y_train)

    print("best params:", grid.best_params_)
    print("best CV accuracy:", grid.best_score_)
    print("test accuracy:", grid.best_estimator_.score(X_test, y_test))
