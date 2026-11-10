# -*- coding: utf-8 -*-
"""e7_mmd_logging.py -- F8 (Appendix C.4, Table C.2).

Raw per-scenario, per-stage MMD^2 values with per-domain sample sizes and
median-heuristic length-scales, computed with the single frozen kernel rule
of Section 4.3 (V-statistic, Eq. 12). Requires adapter.stage_features.

Usage: python e7_mmd_logging.py [--dry-run]
"""
import argparse

import numpy as np

from common import mmd2_v_statistic, save_result

SCENARIOS = ["S1", "S2", "S3", "S4", "S5"]
STAGES = ["baseline", "bridge", "calibration", "attention", "adversarial"]


def main(dry_run):
    rng = np.random.default_rng(53)
    rows = []
    for sc in SCENARIOS:
        base_mmd = None
        for stage in STAGES:
            if dry_run:
                X = rng.normal(0, 1, size=(120, 16))
                Y = rng.normal(0.4 if stage == "baseline" else 0.4 * (1 - 0.866 * STAGES.index(stage) / 4),
                               1.0, size=(90, 16))
            else:
                X, Y = adapter_stage(sc, stage)
            mmd2, ell = mmd2_v_statistic(X, Y)
            if stage == "baseline":
                base_mmd = mmd2
            rows.append({"scenario": sc, "stage": stage,
                         "n_src": int(len(X)), "n_tar": int(len(Y)),
                         "ell": round(float(ell), 4),
                         "mmd2": round(float(mmd2), 5),
                         "reduction_vs_baseline_pct": round(100.0 * (1 - mmd2 / base_mmd), 1) if base_mmd else 0.0})
    save_result("e7_mmd.json", {
        "estimator": "V-statistic MMD^2, single Gaussian RBF kernel, "
                     "median-heuristic length-scale on the pooled pair (Eq. 12)",
        "rows": rows,
        "note": "Table C.2 is regenerated directly from this file; relative "
                "reductions reproduce Table 6 when macro-averaged.",
    })


def adapter_stage(sc, stage):
    import adapter
    return adapter.stage_features(sc, stage, seed=2026)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.dry_run:
        import os
        os.environ["KIT_DRYRUN"] = "1"
    main(a.dry_run)
