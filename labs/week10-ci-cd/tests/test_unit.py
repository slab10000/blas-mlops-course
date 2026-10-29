import pandas as pd

from src.features import add_rush_flag


def test_add_rush_flag():
    # Three parts: make a tiny input, call the function, compare with the answer you worked out by hand.
    #     df = pd.DataFrame({"hour": [___, ___, ___, ___]})
    #     result = add_rush_flag(df)
    #     assert list(result["rush"]) == [___, ___, ___, ___]     # 1 = rush hour, 0 = not
    # YOUR CODE: use the hours 17, 18, 20 and 21 (two just outside the rush window, two exactly on its edges).
    # Rush hour is hours 18, 19 and 20. Work out the four answers on paper BEFORE you write them in.
    raise NotImplementedError


def test_add_rush_flag_does_not_change_the_input():
    df = pd.DataFrame({"hour": [17, 19]})
    add_rush_flag(df)
    assert list(df.columns) == ["hour"]          # the original table is untouched
