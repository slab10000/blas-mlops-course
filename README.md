# MLOps Course — Materials Template

This is the **template repository** for the MLOps course. Each student clicks
**"Use this template"** on this repo's GitHub page to create their own
independent copy (with a clean history) — that copy is where you'll do all of
your work this semester. See the Week 1 Lab Student Handout for the full
step-by-step walkthrough of cloning and configuring your copy.

## How this repo is used

- **New weekly lab starter files** are added to this repo (`course-org/mlops-course-materials`)
  before each lab session.
- Your personal copy has this repo configured as a remote named `upstream`
  (set up in the Week 1 lab). To pull each new week's starter files into your
  own repo:

  ```
  git fetch upstream
  git merge upstream/main
  ```

- You do your actual lab work on a branch, then open a pull request into your
  own `main` branch — the same PR workflow practiced (twice) in Week 1.

## Repo structure

| Path | Purpose |
|---|---|
| `README.md` | This file — course overview and setup instructions |
| `environment/requirements.txt` | Pinned Python dependencies for the course |
| `docker/` | Dockerfile & docker-compose.yml — used starting Week 8 |
| `labs/week01-setup … week16-capstone/` | One folder per week — starter files plus your work |
| `src/` | Shared code you build up across the semester |
| `data/` | Local datasets — gitignored; DVC-tracked starting Week 5 |
| `.github/workflows/` | CI/CD pipelines — added in Week 10 |
| `.gitignore`, `.env.example` | Standard repo hygiene files |

## Getting started

Follow the **Week 1 Lab Student Handout** — it covers dev environment setup
(Python 3.11 + venv), Git/GitHub configuration, and cloning your copy of this
repo, in order, step by step.
