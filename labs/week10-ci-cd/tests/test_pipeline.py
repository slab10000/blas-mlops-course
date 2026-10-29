import joblib
import numpy as np

from src.features import build_pipeline


def test_save_and_load_gives_the_same_predictions(model, data, tmp_path):
    X_test = data[1]
    joblib.dump(model, tmp_path / "model.joblib")
    loaded = joblib.load(tmp_path / "model.joblib")
    expected = model.predict_proba(X_test)
    assert np.allclose(expected, loaded.predict_proba(X_test))


def test_pipeline_runs_end_to_end_on_a_tiny_sample(data):
    X_train, X_test, y_train, y_test = data
    tiny = build_pipeline().fit(X_train.head(200), y_train.head(200))
    assert tiny.predict_proba(X_test.head(5)).shape == (5, 2)
