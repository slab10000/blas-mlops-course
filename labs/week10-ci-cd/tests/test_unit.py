import pandas as pd

from src.features import add_rush_flag


def test_add_rush_flag():
    df = pd.DataFrame({"hour": [17, 18, 20, 21]})
    result = add_rush_flag(df)
    assert list(result["rush"]) == [0, 1, 1, 0]


def test_add_rush_flag_does_not_change_the_input():
    df = pd.DataFrame({"hour": [17, 19]})
    add_rush_flag(df)
    assert list(df.columns) == ["hour"]          # the original table is untouched
