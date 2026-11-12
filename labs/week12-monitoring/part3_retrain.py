"""Part 3: candidate versus champion. Run:  python labs/week12-monitoring/part3_retrain.py"""
from pathlib import Path
import json
import pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from src.compare import paired_diff
from src.features import build_pipeline
from src.promotion import should_promote

LAB = Path(__file__).resolve().parent
base = pd.read_csv(LAB / "data" / "deliveries.csv")
X, y = base.drop(columns="late"), base["late"]
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25, stratify=y, random_state=42)
train_base = pd.concat([X_tr, y_tr], axis=1)

# Champion: trained on the base data only (this is what is in production).
champion = build_pipeline().fit(X_tr, y_tr)

# Candidate: base data plus weeks 5 and 6 (new area, labels now known).
recent_train = pd.concat([pd.read_csv(LAB / "windows" / f"week_{w:02d}.csv") for w in (5, 6)])
data = pd.concat([train_base, recent_train], ignore_index=True)
candidate = build_pipeline().fit(data.drop(columns="late"), data["late"])

# Judge both on the SAME newest orders: weeks 7 and 8.
test = pd.concat([pd.read_csv(LAB / "windows" / f"week_{w:02d}.csv") for w in (7, 8)], ignore_index=True)
Xn, yn = test.drop(columns="late"), test["late"]
p_champ = champion.predict_proba(Xn)[:, 1]
p_cand = candidate.predict_proba(Xn)[:, 1]
auc_champ, auc_cand = roc_auc_score(yn, p_champ), roc_auc_score(yn, p_cand)
print(f"AUC on weeks 7 and 8: champion {auc_champ:.4f}, candidate {auc_cand:.4f}")
print("promotion rule (min gain 0.01):", "PROMOTE" if should_promote(auc_champ, auc_cand) else "KEEP CHAMPION")

diff, lo, hi = paired_diff(p_champ, p_cand, yn)
print(f"paired Brier difference (candidate - champion): {diff:.4f}, 95% CI [{lo:.4f}, {hi:.4f}]")
print("(AUC: higher is better. Brier error: lower is better. A negative difference means the candidate is better.)")
print("whole interval below zero: candidate is better" if hi < 0 else
      "whole interval above zero: candidate is worse" if lo > 0 else "interval contains zero: cannot tell")
