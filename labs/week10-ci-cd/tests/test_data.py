import glob

import pandas as pd
from conftest import LAB

from src.checks import COLUMNS, RESTAURANTS, problems


def test_base_data_schema_and_ranges(base):
    df = base
    assert list(df.columns) == COLUMNS
    assert not df.isna().any().any()
    # Each check is one `assert` line on the table `df`. Patterns to copy and adapt (other columns):
    #     assert df["items"].between(1, 30).all()          # every value is inside a range
    #     assert df["raining"].isin([0, 1]).all()          # every value is one of a list
    #     assert 0.1 < df["raining"].mean() < 0.9          # an average is inside a range
    # YOUR CODE (gap 1): every distance_km is between 0.1 and 50          (first pattern)
    # YOUR CODE (gap 2): every restaurant is one of RESTAURANTS           (second pattern, the list is RESTAURANTS)
    # YOUR CODE (gap 3): the late rate (the mean of `late`) is between 0.05 and 0.40   (third pattern)
    raise NotImplementedError


def test_incoming_batches_pass_the_data_checks():
    """Any new file placed in data/incoming/ must pass the same checks before we train on it."""
    for path in sorted(glob.glob(str(LAB / "data" / "incoming" / "*.csv"))):
        found = problems(pd.read_csv(path))
        assert found == [], f"{path}: {found}"
