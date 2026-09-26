# Week 4 Preprocessing Pipeline

The loan-default classifier now splits raw rows before fitting preprocessing.
A ColumnTransformer applies median imputation and StandardScaler to the five
numeric features, and most-frequent imputation plus OneHotEncoder with
`handle_unknown="ignore"` to employment_type and home_ownership. PCA and
LogisticRegression are inside the same Pipeline, which GridSearchCV refits
independently within each training fold.

## Run

From the repository root, using the existing virtual environment:

```bash
source .venv/bin/activate
python labs/week04-preprocessing/explore.py
python labs/week04-preprocessing/train.py
```

Both scripts resolve the CSV relative to their own location. These results
were obtained with Python 3.11.16, pandas 3.0.5, NumPy 2.4.6, and scikit-learn 1.5.1.
The 400 rows contain 38 missing account_balance values and class counts of
241 non-defaults and 159 defaults. The stratified 80/20 split uses random_state=42:
320 training rows (193/127) and 80 test rows (48/32).

## Measured results

| Stage | Test accuracy |
| --- | ---: |
| Original leaky starter | 0.6375 |
| Correct pipeline without PCA | 0.6375 |
| Correct pipeline with five PCA components | 0.6375 |
| Best pipeline selected by five-fold CV | 0.6500 |

GridSearchCV tried PCA component counts [3, 5, 8] and classifier C values
[0.1, 1, 10]. The winner was `clf__C=10, pca__n_components=8` with mean CV accuracy
0.70625 (console rounding: 0.7062). There are nine candidates and 45 fold fits,
followed by one refit on all 320 training rows. The 80 test rows never enter
GridSearchCV. Test scores from earlier stages are recorded for the lab comparison;
they are not used to select the grid winner.

Five PCA components explain 0.837968 of the variance in the preprocessed
training data. The eight-component winner explains 0.973973. Preprocessing
produces 11 columns: five numeric features and six one-hot indicator columns.

## Reflection

### Why similar accuracy does not make the leak harmless

The starter and corrected pipeline without PCA both scored 63.75%, while the
tuned pipeline scored 65.00%. An unchanged accuracy does not establish that
preprocessing was independent of the test data. The full-data fit had already
used held-out feature values to estimate the transform. A small change in
transformed values can leave the same class predictions, and accuracy on only
80 test cases changes in steps of 1.25 percentage points. The valid evidence is
the scope of the fit and the learned statistics, not whether a score improves.

### Exact leak and how I proved it

The original lines `X[NUMERIC_FEATURES] = imputer.fit_transform(X[NUMERIC_FEATURES])`
and `X[NUMERIC_FEATURES] = scaler.fit_transform(X[NUMERIC_FEATURES])` ran before
`train_test_split`. The full-data `pd.get_dummies` also established categories
using test rows. I compared the scalers' `mean_` arrays in the order age,
annual_income, months_employed, loan_amount, account_balance:

```text
Full data, mean imputation:  [40.33, 43761.45, 79.25, 15335.68, 6877.48]
Train only, median:         [40.25, 43213.02, 77.66, 15104.94, 6750.84]
Train only, mean control:   [40.25, 43213.02, 77.66, 15104.94, 6848.15]
```

The handout changes both fit scope and imputation strategy. The extra train-only
mean-imputation comparison holds the strategy fixed and still differs from the
full-data fit. Annual income has no missing values, so its 548.4275 difference
is independent of the imputation strategy. The corrected scaler sees 320 rows;
each cross-validation fold's scaler sees only its 256 training rows.

### Recomputing the scaler in production

This would be training-serving skew. The classifier was trained in the coordinate
system defined by the saved training means and scales. Refitting a scaler on
last-hour requests changes that coordinate system while leaving the classifier
fixed, so the same applicant could receive a different prediction depending on
other requests. The lab bug is train/test leakage during evaluation; the serving
bug is a mismatch between the training and inference transformations. Serving
must load the fitted pipeline and call predict without refitting its steps.

### PCA state and reuse at serving time

PCA state includes the training center (`mean_`), component directions
(`components_`), and explained variances. The classifier's coefficients correspond
to those particular component axes. A fresh PCA fit on incoming requests would
learn a different center and rotation, with potentially different signs and
component ordering. Applying the old classifier to those new coordinates makes
its inputs inconsistent. Serving must reuse the fitted PCA inside the saved
pipeline. After grid search, the fitted object is `grid.best_estimator_`; the
original `pipe` is still an unfitted blueprint.
