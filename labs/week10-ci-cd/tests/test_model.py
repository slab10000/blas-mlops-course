import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

AUC_FLOOR = 0.70       # decided BEFORE looking at the result
MARGIN = 0.5          # a new model must beat the baseline by at least this much

ORDER = dict(distance_km=4.0, items=3, hour=19, raining=0, courier_months=6, restaurant="sushi")


def risk(model, **changes):
    row = pd.DataFrame([{**ORDER, **changes}])
    return model.predict_proba(row)[0, 1]


def test_model_beats_the_floor_and_the_baseline(model, data):
    X_train, X_test, y_train, y_test = data
    auc = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])
    baseline = LogisticRegression().fit(X_train[["distance_km"]], y_train)
    baseline_auc = roc_auc_score(
        y_test, baseline.predict_proba(X_test[["distance_km"]])[:, 1]
    )
    assert auc >= AUC_FLOOR
    assert auc >= baseline_auc + MARGIN


def test_rain_raises_the_risk(model):
    dry = risk(model, raining=0)
    wet = risk(model, raining=1)
    assert wet > dry


def test_probabilities_are_valid(model, data):
    p = model.predict_proba(data[1])[:, 1]
    assert ((p >= 0) & (p <= 1)).all()


def test_model_is_not_worse_than_the_champion(model, data, champion):
    X_train, X_test, y_train, y_test = data
    auc = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])
    assert auc >= champion["auc"] - 0.01          # allow for a little noise
