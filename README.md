# Forgetting Mechanics — C1 Toy Pipeline (Mini Smoke)

This repository contains a **minimal, one-person, toy pipeline** to smoke‑test the C1 volume:
- **N‑P (Pruning)** with 3 points (p = 0.0, 0.4, 0.8)
- Generates `outputs/C1/metrics.json` and `figs/C1/fig_C1_2.svg`
- No heavy ML; functions are **deterministic stubs** so you can run it anywhere

---

## 0) Create a new GitHub repository
**Recommended name**: `forgetting-mechanics-C1-toy` (public or private)

1. Sign in to GitHub → **New repository**
2. Repository name: `forgetting-mechanics-C1-toy`
3. Description: `C1 toy pipeline (N-P mini smoke): metrics + figure`
4. Public (or Private), **do NOT** add README/License at creation (we will push ours)
5. Click **Create repository** → copy the repo’s HTTPS URL

---

## 1) Prepare your local folder
Option A (ZIP):
1. Download the ZIP attached to this guide.
2. Unzip it locally (e.g., `~/work/forgetting-mechanics-C1-toy`).
3. Open a terminal in that folder.

Option B (git init):
```bash
mkdir -p ~/work/forgetting-mechanics-C1-toy
cd ~/work/forgetting-mechanics-C1-toy
```

---

## 2) Initialize git and set remote
```bash
git init
git branch -M main
git remote add origin https://github.com/<YOUR-USER>/forgetting-mechanics-C1-toy.git
```

---

## 3) (Optional) Create a working branch
```bash
git checkout -b C1/NP-mini-smoke
```

---

## 4) Install Python (3.9+) and run the mini smoke
Make sure Python is available (`python --version`). Then:

```bash
python scripts/run_C1_NP_min.py
python scripts/plot_C1_2_min.py
```

**Outputs created:**
- `outputs/C1/metrics.json`
- `figs/C1/fig_C1_2.svg`

---

## 5) Commit & push
```bash
git add -A
git commit -m "C1 mini-smoke: N-P 3 points -> metrics + fig"
git push -u origin C1/NP-mini-smoke
```
Then open GitHub and create a Pull Request.

---

## 6) (Optional) Enable GitHub Actions to archive outputs
This repo includes `.github/workflows/artifacts.yml` that uploads the figure and metrics as PR artifacts.
On GitHub: **Actions** → enable workflows if prompted.

---

## 7) Files overview
```
specs/
  axes_extractor_neuro.yaml
  claims_rules.yaml
  prereg_C1.yaml
scripts/
  run_C1_NP_min.py
  plot_C1_2_min.py
outputs/C1/            # generated at runtime
figs/C1/               # generated at runtime
texts/
  doc1.txt
  doc2.txt
.github/workflows/
  artifacts.yml
README.md
LICENSE (MIT)
.gitignore
```
