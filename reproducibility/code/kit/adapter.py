# -*- coding: utf-8 -*-
"""adapter.py -- THE ONLY FILE YOU MAY NEED TO EDIT.

Auto-discovery: set MS_BDTT_ROOT to your repo; this adapter tries the most
common entry points first. If none match, implement the functions below
manually (exact return schemas are documented and enforced by the e*.py
scripts).

Tried automatically for train_and_evaluate (first match wins):
  1. ms_bdtt.experiment.run_one(scenario, method, seed, **kw) -> dict
  2. ms_bdtt.main.run_one(...)
  3. ms_bdtt.train.evaluate(...)
  4. src.experiment.run_one(...)
  5. experiment.run_one(...)

Each candidate must accept (scenario, method, seed) and optional
(retention, budget, allocation) keyword arguments and return a dict with at
least {"oa": float, "records": [...], "max_softmax": [...]}.
"""
import importlib
import os
import sys

MS_BDTT_ROOT = os.environ.get("MS_BDTT_ROOT", "")

SCENARIOS = ["S1", "S2", "S3", "S4", "S5"]
MAIN_SEEDS = [42, 43, 44]                    # exploratory grid (Tables 5/7/8)
CONFIRM_SEEDS = list(range(42, 52))          # ten seeds for Table 9
SWEEP_RUNS = 5                               # runs per point (Appendix D.2)
RETENTION_RATIOS = [100, 80, 63, 40, 20]     # percent retained (Fig. 5 / Table D.2)
BUDGETS = [20, 40, 60, 80, 100, 120]         # bridge samples per condition (Table D.3)

# Label vocabulary of the S4 open-set track (Section 4.2.4). Adjust here if
# your pipeline uses different class names -- e2_openset_s4.py reads them
# from here and fails loudly if no target-private sample is found.
OPEN_SET_CFG = {
    "mapped_classes": ["healthy", "crack-type", "surface-type"],
    "private_target_labels": ["missing tooth", "surface wear"],
    "private_source_labels": ["combined IR+OR"],
}

_CANDIDATES = [
    ("ms_bdtt.experiment", "run_one"),
    ("ms_bdtt.main", "run_one"),
    ("ms_bdtt.train", "evaluate"),
    ("src.experiment", "run_one"),
    ("experiment", "run_one"),
]

_pipeline = None
_tried = False


def _find_pipeline():
    """Locate a callable run_one(...) in MS_BDTT_ROOT. Returns fn or None."""
    global _pipeline, _tried
    if _tried:
        return _pipeline
    _tried = True
    if not MS_BDTT_ROOT:
        return None
    if MS_BDTT_ROOT not in sys.path:
        sys.path.insert(0, MS_BDTT_ROOT)
    for modname, fnname in _CANDIDATES:
        try:
            mod = importlib.import_module(modname)
            fn = getattr(mod, fnname, None)
            if callable(fn):
                _pipeline = fn
                print(f"[adapter] auto-wired: {modname}.{fnname}")
                break
        except Exception:
            continue
    return _pipeline


def train_and_evaluate(scenario: str, method: str, seed: int,
                       retention: float = None,
                       budget: int = None,
                       allocation: str = None) -> dict:
    """Train one model and evaluate on the scenario test partition.

    Returns dict with keys:
      "oa"          : float, sample-weighted overall accuracy in percent
      "macro_f1"    : float
      "per_class"   : {"class": {"support": int, "precision": f, "recall": f, "f1": f}}
      "records"     : [{"record_id": str, "label": str, "pred": str}, ...]
                      one entry per TEST RECORD (for the record bootstrap)
      "max_softmax" : [float, ...] aligned with "records" (open-set AUROC)
      "runtime_min" : float
    """
    fn = _find_pipeline()
    if fn is not None:
        return fn(scenario, method, seed, retention=retention,
                  budget=budget, allocation=allocation)
    raise NotImplementedError(
        "No pipeline found. Either (a) set MS_BDTT_ROOT to a repo exposing "
        f"one of {[m + '.' + f for m, f in _CANDIDATES]}, or (b) edit "
        "adapter.train_and_evaluate below to call your training entry point "
        "directly. Searched root: " + (MS_BDTT_ROOT or "<MS_BDTT_ROOT not set>"))


def source_validation_max_softmax(method: str, seed: int) -> list:
    """Max-softmax scores on HELD-OUT SOURCE-VALIDATION data (Section 4.2.4).

    Used to fix tau_rej at the 95th percentile WITHOUT any target label.
    If your pipeline exposes e.g. ms_bdtt.experiment.source_val_scores,
    it will be picked up here automatically.
    """
    if MS_BDTT_ROOT and MS_BDTT_ROOT not in sys.path:
        sys.path.insert(0, MS_BDTT_ROOT)
    for modname, fnname in [("ms_bdtt.experiment", "source_val_scores"),
                            ("experiment", "source_val_scores")]:
        try:
            fn = getattr(importlib.import_module(modname), fnname, None)
            if callable(fn):
                return list(fn(method, seed))
        except Exception:
            continue
    raise NotImplementedError(
        "Provide source-validation max-softmax scores for the S4 rejection "
        "threshold (95th-percentile rule, Section 4.2.4).")


def run_particle_filter(observations) -> dict:
    """Run Algorithm-1 on simulated observations. Returns dict with
    "k_samples", "c_samples", "k_mean", "c_mean", "predictive_features"."""
    if MS_BDTT_ROOT and MS_BDTT_ROOT not in sys.path:
        sys.path.insert(0, MS_BDTT_ROOT)
    for modname, fnname in [("ms_bdtt.calibration", "particle_filter"),
                            ("experiment", "run_particle_filter")]:
        try:
            fn = getattr(importlib.import_module(modname), fnname, None)
            if callable(fn):
                return fn(observations)
        except Exception:
            continue
    raise NotImplementedError("Wire run_particle_filter to your Algorithm-1 "
                              "implementation (Appendix C.1).")


def simulate_observations(k: float, c: float, n_segments: int, seed: int) -> list:
    """Stage-1 kernel with known corrections and Section 3.2 noise; returns
    a list of band-limited spectral feature vectors."""
    if MS_BDTT_ROOT and MS_BDTT_ROOT not in sys.path:
        sys.path.insert(0, MS_BDTT_ROOT)
    for modname, fnname in [("ms_bdtt.simulator", "healthy_observations"),
                            ("experiment", "simulate_observations")]:
        try:
            fn = getattr(importlib.import_module(modname), fnname, None)
            if callable(fn):
                return fn(k, c, n_segments, seed)
        except Exception:
            continue
    raise NotImplementedError("Wire simulate_observations to your Stage-1 "
                              "rotordynamic kernel (Appendix A).")


def stage_features(scenario: str, stage: str, seed: int):
    """(X_src, X_tar) 512-d features for one scenario/stage (Appendix C.4)."""
    if MS_BDTT_ROOT and MS_BDTT_ROOT not in sys.path:
        sys.path.insert(0, MS_BDTT_ROOT)
    for modname, fnname in [("ms_bdtt.analysis", "stage_features"),
                            ("experiment", "stage_features")]:
        try:
            fn = getattr(importlib.import_module(modname), fnname, None)
            if callable(fn):
                return fn(scenario, stage, seed)
        except Exception:
            continue
    raise NotImplementedError("Wire stage_features to your per-stage feature "
                              "extraction (Appendix C.4).")
