"""Preprocessing and the model pipeline."""
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler

NUM = ["distance_km", "items", "raining", "courier_months"]
RUSH_FIRST, RUSH_LAST = 18, 20          # dinner rush: hours 18, 19 and 20


def add_rush_flag(df):
    """Return a copy of df with a new column `rush`: 1 if hour is 18, 19 or 20, else 0."""
    df = df.copy()
    df["rush"] = df["hour"].between(RUSH_FIRST, RUSH_LAST).astype(int)
    return df


def build_pipeline():
    prep = ColumnTransformer([
        ("num", StandardScaler(), NUM),
        ("cat", OneHotEncoder(handle_unknown="ignore"), ["restaurant"]),
        ("rush", "passthrough", ["rush"]),
    ])
    return Pipeline([
        ("flag", FunctionTransformer(add_rush_flag)),
        ("prep", prep),
        ("clf", LogisticRegression(max_iter=1000)),
    ])
