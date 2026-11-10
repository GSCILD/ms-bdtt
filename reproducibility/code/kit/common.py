# -*- coding: utf-8 -*-
"""common.py -- statistics and I/O shared by the confirmatory scripts.

Implements exactly the definitions of manuscript Section 4.6:
  * resampling unit of the bootstrap = test RECORD (cluster of windows),
    class-stratified, within each training run;
  * aggregation across seeds = seed-level PAIRED differences (never pooled
    test samples);
  * Cohen's d for paired data = mean(diff)/sd(diff).
"""
import json
import math
import os
import random

import numpy as np

RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(RESULTS, exist_ok=True)

try:
    from scipy import stats as _sps
except Exception:  # pragma: no cover
    _sps = None


def save_result(name: str, payload: dict):
    payload["dry_run"] = bool(os.environ.get("KIT_DRYRUN", "0") == "1" or payload.get("_dryrun"))
    payload.pop("_dryrun", None)
    path = os.path.join(RESULTS, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    print(f"[saved] {path}")
    return path


def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
    except Exception:
        pass


def paired_t(diff):
    """Two-sided paired t-test on seed-level differences. Returns (t, df, p)."""
    d = np.asarray(diff, dtype=float)
    n = d.size
    df = n - 1
    m = d.mean()
    s = d.std(ddof=1)
    if s == 0:
        return float("inf"), df, 0.0
    t = m / (s / math.sqrt(n))
    if _sps is not None:
        p = float(2.0 * _sps.t.sf(abs(t), df))
    else:  # conservative normal fallback (flagged in output)
        p = float(2.0 * (0.5 * math.erfc(abs(t) / math.sqrt(2))))
    return float(t), int(df), p


def cohens_d_paired(diff):
    d = np.asarray(diff, dtype=float)
    s = d.std(ddof=1)
    return float(d.mean() / s) if s > 0 else float("inf")


def seed_bootstrap_ci(diff, b=10000, alpha=0.05, seed=2026):
    """Percentile CI of the mean of seed-level paired differences (unit: seed)."""
    d = np.asarray(diff, dtype=float)
    rng = np.random.default_rng(seed)
    n = d.size
    boots = d[rng.integers(0, n, size=(b, n))].mean(axis=1)
    lo, hi = np.percentile(boots, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return float(lo), float(hi)


def record_bootstrap_ci(records, b=1000, alpha=0.05, seed=2026):
    """Class-stratified record-level bootstrap of overall accuracy.

    records: [{"record_id", "label", "pred"}] -- one entry per test record.
    Resamples records with replacement WITHIN each true class, then computes
    the sample-weighted OA of the resample. Preserves within-record
    correlation and class composition (Section 4.6).
    """
    rng = np.random.default_rng(seed)
    by_class = {}
    for r in records:
        by_class.setdefault(r["label"], []).append(r)
    oas = []
    for _ in range(b):
        correct = total = 0
        for _, rows in by_class.items():
            pick = rng.integers(0, len(rows), size=len(rows))
            for i in pick:
                total += 1
                correct += int(rows[i]["pred"] == rows[i]["label"])
        oas.append(100.0 * correct / max(total, 1))
    lo, hi = np.percentile(oas, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return float(lo), float(hi)


def auroc_unknown(max_softmax_known, max_softmax_unknown):
    """AUROC of unknown detection with score = 1 - p_max (rank-based, no deps).

    Higher score == more unknown-like. Standard UROC via rank statistics.
    """
    pos = [1.0 - v for v in max_softmax_unknown]   # positives = unknowns
    neg = [1.0 - v for v in max_softmax_known]
    if not pos or not neg:
        return float("nan")
    allv = sorted(pos + neg)
    rank = {v: i + 1 for i, v in enumerate(allv)}
    # average ranks for ties
    from collections import defaultdict
    groups = defaultdict(list)
    for i, v in enumerate(allv):
        groups[v].append(i + 1)
    avg = {v: sum(r) / len(r) for v, r in groups.items()}
    rp = sum(avg[v] for v in pos)
    n1, n0 = len(pos), len(neg)
    return float((rp - n1 * (n1 + 1) / 2) / (n1 * n0))


def mmd2_v_statistic(X, Y):
    """Biased (V-statistic) MMD^2 with a single Gaussian RBF kernel whose
    length-scale is the median heuristic on the pooled sample (Eq. 12;
    identical rule before and after every stage, Section 4.3)."""
    X = np.asarray(X, dtype=float)
    Y = np.asarray(Y, dtype=float)
    n, m = len(X), len(Y)
    Z = np.vstack([X, Y])
    d2 = ((Z[:, None, :] - Z[None, :, :]) ** 2).sum(-1)
    med = np.median(d2[np.triu_indices_from(d2, k=1)])
    ell2 = med if med > 0 else 1.0
    K = np.exp(-d2 / (2 * ell2))
    kxx = K[:n, :n].mean()
    kyy = K[n:, n:].mean()
    kxy = K[:n, n:].mean()
    return float(kxx + kyy - 2 * kxy), float(math.sqrt(ell2))
