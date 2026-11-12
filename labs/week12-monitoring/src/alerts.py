"""The alert rule: decided before the incident (Week 12, Part 4)."""


def alert(psi_history, warn=0.10, act=0.25, windows=2):
    """Look at the last `windows` PSI values. ACT or WARN only if ALL of them are at or above the level."""
    # TODO 3 (Part 2): last = the final `windows` values of psi_history.
    # Return "ACT: retrain candidate" if there are `windows` values and ALL are >= act,
    # else "WARN: investigate" if there are `windows` values and ALL are >= warn, else "ok".
    # Hint: all(v >= act for v in last)
    raise NotImplementedError("TODO 3: finish alert() in src/alerts.py")
