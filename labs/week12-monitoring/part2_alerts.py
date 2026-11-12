"""Part 2: run the alert rule over eight weeks. Run:  python labs/week12-monitoring/part2_alerts.py"""
from pathlib import Path
import pandas as pd
from src.alerts import alert
from src.drift import psi

NUM = ["distance_km", "items", "hour", "raining", "courier_months"]

LAB = Path(__file__).resolve().parent
ref = pd.read_csv(LAB / "data" / "deliveries.csv")
history = []
print("week  worst PSI  feature          rule says")
for week in range(1, 9):
    cur = pd.read_csv(LAB / "windows" / f"week_{week:02d}.csv")
    scores = {c: psi(ref[c], cur[c]) for c in NUM}
    worst = max(scores, key=scores.get)               # the feature that moved most this week
    history.append(scores[worst])
    print(f"{week:>4}  {history[-1]:>9.3f}  {worst:<15}  {alert(history)}")
print()
print("alert([0.03, 0.04, 0.31]) ->", alert([0.03, 0.04, 0.31]))
print("alert([0.03, 0.28, 0.31]) ->", alert([0.03, 0.28, 0.31]))
print("alert([0.12, 0.15])       ->", alert([0.12, 0.15]))
