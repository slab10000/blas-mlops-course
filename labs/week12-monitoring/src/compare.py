"""Paired comparison of two models on the SAME rows (Week 7 idea, Week 9 rule)."""
import numpy as np


def paired_diff(champion_p, challenger_p, y):
    """Brier error per order for each model. Return the mean difference (challenger minus champion) and its 95% interval.
    A negative difference means the challenger is better."""
    y = np.asarray(y)
    # TODO 4 (Part 3):
    #  d  = (challenger_p - y) ** 2 - (champion_p - y) ** 2        # Brier error per order, challenger minus champion
    #  se = d.std(ddof=1) / np.sqrt(len(d))
    #  return float(d.mean()), float(d.mean() - 1.96 * se), float(d.mean() + 1.96 * se)
    raise NotImplementedError("TODO 4: finish paired_diff() in src/compare.py")
