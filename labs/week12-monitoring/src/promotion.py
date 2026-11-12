"""The promotion rule from Week 9."""


def should_promote(champion_auc, challenger_auc, min_gain=0.01):
    """Promote only if the challenger is at least min_gain better than the champion."""
    return challenger_auc - champion_auc >= min_gain - 1e-12
