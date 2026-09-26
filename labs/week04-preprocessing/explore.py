from pathlib import Path
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

df = pd.read_csv(Path(__file__).resolve().with_name("loan_applications.csv"))

print(df.info())

print(df.isna().sum())

print(df["defaulted"].value_counts(normalize=True))



NUMERIC_FEATURES = [
    "age", "annual_income", "months_employed", "loan_amount", "account_balance"
]
X = df.drop(columns=["defaulted"])
y = df["defaulted"]
leaky_scaler = StandardScaler().fit(
    SimpleImputer(strategy="mean").fit_transform(X[NUMERIC_FEATURES])
)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
correct_scaler = StandardScaler().fit(
    SimpleImputer(strategy="median").fit_transform(X_train[NUMERIC_FEATURES])
)
print("\nNumeric feature order:", NUMERIC_FEATURES)
print("Full-data mean imputation / scaler.mean_:")
print(leaky_scaler.mean_.round(2))
print("Train-only median imputation / scaler.mean_:")
print(correct_scaler.mean_.round(2))

# Hold the imputation strategy fixed to isolate the effect of including test rows.
train_mean_scaler = StandardScaler().fit(
    SimpleImputer(strategy="mean").fit_transform(X_train[NUMERIC_FEATURES])
)
print("Train-only mean imputation / scaler.mean_ (control):")
print(train_mean_scaler.mean_.round(2))
