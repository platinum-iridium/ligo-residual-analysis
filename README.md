# LIGO Residual Analysis — Platinum-Iridium

A deterministic, archival-grade pipeline for gravitational-wave residual analysis.

This repository provides a deterministic, archival-grade pipeline for reproducing the residual analysis described in version v.1.2.7. All execution paths are mechanically guarded to prevent silent divergence.

Environment setup.
Reproduction must be performed using the exact dependency versions specified in requirements-strict.lock. Create a clean Python 3.11 environment and install dependencies using pip install -r requirements-strict.lock The pipeline enforeces strict runtime checks and will refuse execution if any dependency version, file origin, or preregistred parameter differs from the archival specification.

Execution
Run the analysis entry point directly:
python ligo-residual_analysis_v1.2.7.py
No command-line arguments are required. All analysis parameters are cryptographically preregistered and verified at runtime.

Verification.
Successful execution produces a stable artifact (run_record_LATEST.json) that is guaranteed to be bit-for-bit identical across repeated runs in the same environment. Any deviation in environment, configuration, or algorithmic path results in a hard failure rather than silent variation.

This repository implements a **Platinum-Iridium reproducibility contract**: if two independent users run this code with the same inputs and pinned environment, they will produce a **bit-for-bit identical forensic artifact**. Any deviation is treated as a reproducibility failure, not a numerical curiosity.

---

## What This Is

This project provides a rigorously controlled analysis pipeline for LIGO strain data, with a focus on **residual analysis** under strict reproducibility guarantees.

Key design goals:

- Deterministic algorithm paths (no silent fallbacks)
- Strict runtime dependency enforcement
- Cryptographically bound preregistration of analysis windows
- Separation of **stable forensic artifacts** from **audit metadata**
- Mechanical verification via an executable test suite

The intent is not performance or convenience, but **scientific trust**.

---

## Repository Contents

- `ligo_residual_analysis_v1_2_7.py`  
  The full analysis pipeline (strict archival mode by default)

- `requirements-strict.txt`  
  Human-readable dependency specification

- `requirements-strict.lock`  
  Fully pinned, hash-locked environment for archival reproduction

- `tests/`  
  Mechanical pytest suite enforcing strict reproducibility guarantees

- `run_record_LATEST.json` (generated)  
  Stable forensic artifact for bit-for-bit comparison

---

## Reproducibility Contract

This pipeline is considered **reproduced** if and only if:

- It is executed from a file-based context (not interactive)
- Dependencies exactly match the pinned versions
- `STRICT_ARCHIVAL = True`
- The resulting `run_record_LATEST.json` file is **bit-for-bit identical** across runs

Any violation causes the pipeline to halt with a `RuntimeError`.

---

## How to Reproduce (Exact)

### 1. Create a clean environment
Install Python **3.11.\*** and create a fresh virtual environment.

### 2. Install dependencies
```bash
pip install -r requirements-strict.lock
