# Week 10 Testing and CI for ML

The completed lab contains data contract checks, a rush-hour boundary test, model AUC and behavior tests, and the supplied serialization and pipeline tests. Run all 10 tests from the repository root:

```bash
source .venv/bin/activate
pip install -r labs/week10-ci-cd/requirements.txt
pytest -q labs/week10-ci-cd
```

The model test uses a fixed stratified 75/25 split with seed 42. The AUC floor remains 0.70 and the margin over the distance-only logistic baseline remains 0.05. The measured model AUC is 0.803135 and the baseline AUC is 0.640945.

The active workflows are in `.github/workflows/`; identical copies are kept in `workflow_templates/`. `ci` runs the full suite on lab pushes and pull requests. `retrain` runs on incoming-data pull requests or manual dispatch, validates data first, and then compares a challenger with the champion on fixed held-out rows. A passing workflow may keep the champion: promotion requires an AUC gain of at least 0.01.

The bad and good batch demonstrations use separate pull requests into `week10-ci-cd`, closed without merging. The final branch contains no CSV in `data/incoming/`. The base data and example batches are unchanged instructor inputs. The upstream duplicate `champion.json` at the repository root was removed; the application reads `models/champion.json` in this lab.
