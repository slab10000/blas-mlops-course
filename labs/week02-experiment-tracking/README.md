# Week 2 Experiment Tracking with MLflow

**Student:** Blas Moreno

**GitHub:** slab10000

## Setup and execution

I used the existing Python 3.11.16 virtual environment and pulled the course
starter. The implementation keeps the starter's built-in digits dataset,
80/20 split, random seed 42, RandomForestClassifier, and macro averaging for
precision, recall, and F1. The dataset contains 1,797 images and 64 features;
the split contains 1,437 training and 360 test examples.

Activate `.venv` at the repository root, then run:

```bash
source .venv/bin/activate
pip install scikit-learn==1.5.1 mlflow==3.16.0 matplotlib==3.11.2
cd labs/week02-experiment-tracking
python train.py --run-name run1-baseline
python train.py --n-estimators 100 --max-depth 5 --run-name run2-depth5
python train.py --n-estimators 200 --max-depth None --run-name run3-unrestricted
mlflow ui --backend-store-uri sqlite:///mlflow.db --host 127.0.0.1 --port 5001
```

Open http://127.0.0.1:5001 and select **Model training → week2-lab → Runs**.
Training and the UI must use this same working directory. Optional CLI arguments
make the three configurations reproducible without editing source between runs;
the constants still provide the baseline defaults. Every execution creates a
new run. The local database and artifact directory are excluded by `.gitignore`.

Each run logs `n_estimators`, `max_depth`, and `random_state`, the four metrics
below, and its own `confusion_matrix.png` artifact. MLflow stores unlimited
maximum depth as the parameter string `None`.

## Results

| Run | Trees | Max depth | Accuracy | Precision macro | Recall macro | F1 macro |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| 1 baseline | 10 | 3 | 0.8306 | 0.8307 | 0.8236 | 0.8178 |
| 2 | 100 | 5 | 0.9444 | 0.9457 | 0.9438 | 0.9438 |
| 3 best | 200 | None | 0.9722 | 0.9742 | 0.9723 | 0.9729 |

The uninstrumented starter and the tracked baseline both printed exactly:

```text
n_estimators=10, max_depth=3
accuracy:  0.8306
precision: 0.8307
recall:    0.8236
f1:        0.8178
```

I verified that all three runs finished and that each stored the three parameters,
four metrics, and confusion matrix. Run IDs, in the order above:

- `b05eb6e13ca748fb86ac8fe78dc466d0`
- `5c78966a06524854b3c16b27e33fbaeb`
- `8fa2f08a2fb64039885b94bfddda29a8`

## Reflection

**Which run performed best and by how much?** Run 3, with 200 trees and no maximum
depth, achieved 97.22% accuracy versus 83.06% for the baseline: an increase of
14.17 percentage points (17.06% relative). It correctly classified 350 of 360
test images, compared with 299 for the baseline, so it made 51 fewer errors.
It also had the highest macro precision, recall, and F1.

**Why did this combination win?** Depth-3 trees have limited capacity to learn
relationships among the 64 pixel features and can underfit handwritten digits.
Allowing deeper trees lets each tree model more detailed patterns, and averaging
200 trees reduces the variability of individual trees. Both hyperparameters
changed together, so this comparison cannot isolate their separate effects.
The result describes this fixed split; additional validation would be needed
before claiming that the configuration generalizes best.

**Which leg of reproducibility does MLflow add?** Configuration. The bare script
printed scores but did not retain a run-specific record of the settings. MLflow
now links the exact hyperparameters and random seed to metrics and artifacts for
each run. Git still versions code, and reproducing results also requires the same
data and environment. Manual parameter and metric logging alone does not fully
version the dataset or capture the complete Python environment.

## Reference

[MLflow experiment tracking documentation](https://mlflow.org/docs/latest/ml/tracking/)
