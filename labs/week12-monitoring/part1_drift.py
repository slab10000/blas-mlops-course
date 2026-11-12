"""Part 1: which feature moved? Run:  python labs/week12-monitoring/part1_drift.py [week_number]"""
import sys
from pathlib import Path
import pandas as pd
from src.drift import drift_report

LAB = Path(__file__).resolve().parent
NUM = ["distance_km", "items", "hour", "raining", "courier_months"]
CAT = ["restaurant"]

week = int(sys.argv[1]) if len(sys.argv) > 1 else 5
ref = pd.read_csv(LAB / "data" / "deliveries.csv")                  # the reference: what the model learned from
cur = pd.read_csv(LAB / "windows" / f"week_{week:02d}.csv")         # a recent window
print(f"week {week}: {len(cur)} orders, late rate {cur['late'].mean():.3f}")
print(drift_report(ref, cur, NUM, CAT).round(4).to_string(index=False))
