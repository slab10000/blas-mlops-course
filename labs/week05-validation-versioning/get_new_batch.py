"""
Simulates a new monthly batch of loan applications landing from upstream --
exactly like Week 3's ingestion pipeline would receive. Run this once, in
Part 3, to append 100 new rows to loan_applications.csv.

Do not look inside this file before finishing Part 3's write-up -- the whole
point is to find what's wrong with the new data using your validation suite,
the same way you would with a real data drop you didn't produce yourself.
"""
import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(HERE, "loan_applications.csv")

rs = np.random.RandomState(43)
df = pd.read_csv(DATA_PATH)

n = 100
new_batch = pd.DataFrame({
    "age": rs.randint(21, 70, n),
    "annual_income": rs.normal(45000, 18000, n).clip(12000, None).round(2),
    "months_employed": rs.randint(0, 240, n),
    "loan_amount": rs.normal(15000, 8000, n).clip(1000, None).round(2),
    "account_balance": rs.normal(7000, 5000, n).clip(0, None).round(2),
    "employment_type": rs.choice(
        ["salaried", "self_employed", "unemployed", "contractor"], n, p=[0.55, 0.27, 0.10, 0.08]
    ),
    "home_ownership": rs.choice(["own", "mortgage", "rent"], n, p=[0.2, 0.4, 0.4]),
    "defaulted": rs.randint(0, 2, n),
})

# A source-system bug reports income in $K instead of $ for a slice of this batch.
bug_idx = rs.choice(n, 15, replace=False)
new_batch.loc[bug_idx, "annual_income"] = (new_batch.loc[bug_idx, "annual_income"] / 1000).round(2)

combined = pd.concat([df, new_batch], ignore_index=True)
combined.to_csv(DATA_PATH, index=False)
print(f"Landed {n} new rows. loan_applications.csv now has {len(combined)} total rows.")
