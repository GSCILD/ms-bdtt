# -*- coding: utf-8 -*-
"""e4_budget_sweep.py -- F4 (Appendix D.2, Table D.3; replaces fit-derived
thresholds of Table C.1 / Fig. 10 with directly measured values).

Budget sweep: bridge budgets {20, 40, 60, 80, 100, 120} samples per
operating condition x allocation rules {uniform grid, demand-guided Eq. (5)}
x SWEEP_RUNS independent runs, five-scenario macro-average.

Also computes, per rule, the measured budget at which the rule first reaches
90 % of its OWN full-budget accuracy -- the auditable replacement for the
fit-derived "102 samples" threshold.

Usage: python e4_budget_sweep.py [--dry-run]
"""
import argparse
import numpy as np

import adapter
from adapter import BUDGETS, SCENARIOS, SWEEP_RUNS
from common import save_result, set_seed


def main(dry_run):
    rng = np.random.default_rng(31)
    out = {}
    for rule in ["uniform", "demand"]:
        curve = {}
        for n in BUDGETS:
            macro = []
            for sc in SCENARIOS:
                vals = []
                for run in range(SWEEP_RUNS):
                    seed = 2000 + 89 * run
                    set_seed(seed)
                    if dry_run:
                        base = {"uniform": 86.8, "demand": 83.9}[rule]
                        tau = {"uniform": 30.0, "demand": 22.0}[rule]
                        v = base * (1 - np.exp(-n / tau)) + rng.normal(0, 0.7)
                    else:
                        v = float(adapter.train_and_evaluate(
                            sc, "MS-BDTT", seed, budget=n, allocation=rule)["oa"])
                    vals.append(v)
                macro.append(np.mean(vals))
            curve[n] = round(float(np.mean(macro)), 2)
            print(f"{rule} n={n}: macro {np.mean(macro):.2f}")
        full = curve[max(BUDGETS)]
        target = 0.9 * full
        thr = min(n for n in BUDGETS if curve[n] >= target)
        out[rule] = {"curve": curve, "full_budget_oa": full,
                     "target_90pct": round(target, 2),
                     "measured_threshold_n": thr}
    gain = out["uniform"]["measured_threshold_n"] / out["demand"]["measured_threshold_n"]
    out["measured_budget_efficiency_gain"] = round(gain, 2)
    save_result("e4_budget.json", {
        "protocol": "budgets {20,40,60,80,100,120} x {uniform, demand-guided Eq.(5)}, "
                    "5 runs/point, five-scenario macro-average",
        "results": out,
        "note": "replaces the saturating-fit thresholds of Table C.1/Fig.10; "
                "the 1.7x figure in the manuscript becomes the measured "
                "measured_budget_efficiency_gain",
    })


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.dry_run:
        import os
        os.environ["KIT_DRYRUN"] = "1"
    main(a.dry_run)
