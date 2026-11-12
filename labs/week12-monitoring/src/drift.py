"""Drift measures: PSI for numbers, chi-square for categories, KS for a second opinion."""
import numpy as np
import pandas as pd
from scipy import stats


def psi(ref, cur, bins=10):
    """Population Stability Index of one numeric feature: how far the recent shares moved from the reference shares."""
    # TODO 1 (Part 1):
    #  a. edges: the quantiles of ref at np.linspace(0, 1, bins + 1); np.unique them; make the first -inf and the last +inf
    #  b. r and c: np.histogram(x, edges)[0] divided by len(x), for ref and cur
    #  c. clip both at 1e-4 (np.clip(..., 1e-4, None)) so log never sees 0
    #  d. return float(np.sum((c - r) * np.log(c / r)))
    edges = np.unique(np.quantile(ref, np.linspace(0, 1, bins + 1)))
    edges[0], edges[-1] = -np.inf, np.inf
    r = np.histogram(ref, edges)[0] / len(ref)
    c = np.histogram(cur, edges)[0] / len(cur)
    r, c = np.clip(r, 1e-4, None), np.clip(c, 1e-4, None)
    return float(np.sum((c - r) * np.log(c / r)))


def drift_report(ref, cur, numeric, categorical):
    """One row per feature: PSI and KS for numbers, chi-square p-value for categories."""
    rows = []
    for col in numeric:
        ks = stats.ks_2samp(ref[col], cur[col])
        rows.append((col, "numeric", psi(ref[col], cur[col]), ks.statistic, ks.pvalue))
    for col in categorical:
        # TODO 2 (Part 1): build a table of counts with one column for ref and one for cur
        #   counts = pd.concat([ref[col].value_counts(), cur[col].value_counts()], axis=1).fillna(0)
        # then p = stats.chi2_contingency(counts.values)[1]  and append (col, "categorical", None, None, p)
        counts = pd.concat([ref[col].value_counts(), cur[col].value_counts()], axis=1).fillna(0)
        p = stats.chi2_contingency(counts.values)[1]
        rows.append((col, "categorical", None, None, p))
    return pd.DataFrame(rows, columns=["feature", "type", "psi", "ks_stat", "p_value"])
