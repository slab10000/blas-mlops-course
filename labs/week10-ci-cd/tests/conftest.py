import json
from pathlib import Path

import pandas as pd
import pytest
from sklearn.model_selection import train_test_split

from src.features import build_pipeline

LAB = Path(__file__).resolve().parent.parent   # the lab folder, wherever pytest is started from


@pytest.fixture(scope="session")
def base():
    return pd.read_csv(LAB / "data" / "deliveries.csv")


@pytest.fixture(scope="session")
def data(base):
    """A fixed split (seed 42): every run, and every model, uses the same rows."""
    X, y = base.drop(columns="late"), base["late"]
    return train_test_split(X, y, test_size=0.25, stratify=y, random_state=42)


@pytest.fixture(scope="session")
def model(data):
    X_train, X_test, y_train, y_test = data
    return build_pipeline().fit(X_train, y_train)


@pytest.fixture(scope="session")
def champion():
    return json.load(open(LAB / "models" / "champion.json"))
