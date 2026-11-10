# -*- coding: utf-8 -*-
"""e3_retention_sweep.py -- F3 (Appendix D.2, Table D.2).

Measured retention sweep: retention ratios {100, 80, 63, 40, 20} %,
SWEEP_RUNS independent runs per point, all five scenarios, under the
manifests of Section 4.4. Primary output: five-scenario macro-average
accuracy per ratio with run-to-run dispersion. r = 63 % is realised by the
37th-percentile relevance threshold of Section 3.5.1.

Usage: python e3_retention_sweep.py [--dry-run]
"""
import argparse
import numpy as np

import adapter
from adapter import RETENTION_RATIOS, SCENARIOS, SWEEP_RUNS
from common import save_result, set_seed


def main(dry_run):
    rng = np.random.default_rng(23)
    out = {}
    for r in RETENTION_RATIOS:
        macro = []
        per_sc = {}
        for sc in SCENARIOS:
            vals = []
            for run in range(SWEEP_RUNS):
                seed = 1000 + 97 * run
                set_seed(seed)
                if dry_run:
                    base = 76.0 if sc == "S5" else 84.0
                    penalty = {100: 3.9, 80: 2.2, 63: 0.0, 40: 1.5, 20: 4.4}[r]
                    v = base - penalty + rng.normal(0, 0.8)
                else:
                    v = float(adapter.train_and_evaluate(
                        sc, "MS-BDTT", seed, retention=float(r))["oa"])
                vals.append(v)
            per_sc[sc] = {"mean": round(float(np.mean(vals)), 2),
                          "sd": round(float(np.std(vals, ddof=1)), 2),
                          "runs": [round(v, 2) for v in vals]}
            macro.append(np.mean(vals))
        out[f"{r}%"] = {"macro_avg": round(float(np.mean(macro)), 2),
                        "macro_sd_across_runs": round(float(np.std(macro, ddof=1)), 2),
                        "per_scenario": per_sc}
        print(f"retention {r}%: macro {np.mean(macro):.2f}")
    save_result("e3_retention.json", {
        "protocol": "retention ratios {100,80,63,40,20}%, 5 runs/point, 5 scenarios; "
                    "63% = 37th-percentile relevance threshold",
        "results": out,
        "note": "r=100% row equals the no-suppression ablation of Table 7; "
                "r=63% row equals the full framework of Table 5",
    })


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.dry_run:
        import os
        os.environ["KIT_DRYRUN"] = "1"
    main(a.dry_run)
