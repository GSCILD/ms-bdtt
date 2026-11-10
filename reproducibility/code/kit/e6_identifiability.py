# -*- coding: utf-8 -*-
"""e6_identifiability.py -- F7 (Appendix E.2).

Identifiability diagnostics for the two-component calibration state [k, c]:
  1. controlled parameter recovery over a grid of known true corrections
     spanning +/-20 % around nominal; reports correlation and RMSE between
     recovered and true values, per component;
  2. posterior predictive checks: MMD^2 (Eq. 12, median-heuristic kernel)
     between posterior-predictive and observed spectral features, plus a
     visual residual dump;
  3. frequentist coverage of the 50/90/95 % posterior credible intervals
     across the grid.

Requires adapter.simulate_observations and adapter.run_particle_filter.

Usage: python e6_identifiability.py [--dry-run]
"""
import argparse

import numpy as np

from common import mmd2_v_statistic, save_result

GRID = np.linspace(-0.20, 0.20, 9)      # 9 x 9 grid of (k*, c*) corrections
SEGMENTS = 40
COVERAGE_LEVELS = [0.50, 0.90, 0.95]


def credible_interval(samples, level):
    lo, hi = np.percentile(np.asarray(samples), [100 * (1 - level) / 2,
                                                100 * (1 + level) / 2])
    return float(lo), float(hi)


def main(dry_run):
    rng = np.random.default_rng(41)
    rec_k, rec_c = [], []
    covered = {f"{int(l*100)}": {"k": 0, "c": 0} for l in COVERAGE_LEVELS}
    pp_mmd = []
    for kstar in GRID:
        for cstar in GRID:
            if dry_run:
                obs = [list(rng.normal(0, 1, size=16)) for _ in range(SEGMENTS)]
                post = {"k_samples": rng.normal(kstar, 0.01, 500),
                        "c_samples": rng.normal(cstar, 0.02, 500),
                        "k_mean": kstar + rng.normal(0, 0.01),
                        "c_mean": cstar + rng.normal(0, 0.02),
                        "predictive_features": list(rng.normal(0, 1, size=16))}
            else:
                obs = adapter_simulate(kstar, cstar)
                post = adapter_run(obs)
            rec_k.append((post["k_mean"], kstar))
            rec_c.append((post["c_mean"], cstar))
            for l in COVERAGE_LEVELS:
                lo, hi = credible_interval(post["k_samples"], l)
                covered[f"{int(l*100)}"]["k"] += int(lo <= kstar <= hi)
                lo, hi = credible_interval(post["c_samples"], l)
                covered[f"{int(l*100)}"]["c"] += int(lo <= cstar <= hi)
            obs_feats = np.asarray(obs if isinstance(obs[0], (list, tuple)) else obs)
            pred_feats = np.asarray(post["predictive_features"], dtype=float)[None, :] \
                if np.asarray(post["predictive_features"]).ndim == 1 \
                else np.asarray(post["predictive_features"], dtype=float)
            m, _ = mmd2_v_statistic(obs_feats[:len(pred_feats)], pred_feats)
            pp_mmd.append(m)
    rec_k = np.asarray(rec_k)
    rec_c = np.asarray(rec_c)
    n = len(GRID) ** 2
    out = {
        "grid_points": int(n),
        "recovery": {
            "corr_k": round(float(np.corrcoef(rec_k[:, 0], rec_k[:, 1])[0, 1]), 3),
            "corr_c": round(float(np.corrcoef(rec_c[:, 0], rec_c[:, 1])[0, 1]), 3),
            "rmse_k": round(float(np.sqrt(np.mean((rec_k[:, 0] - rec_k[:, 1]) ** 2))), 4),
            "rmse_c": round(float(np.sqrt(np.mean((rec_c[:, 0] - rec_c[:, 1]) ** 2))), 4),
        },
        "posterior_predictive": {
            "mmd2_median": round(float(np.median(pp_mmd)), 5),
            "mmd2_p90": round(float(np.percentile(pp_mmd, 90)), 5),
        },
        "coverage": {f"{int(l*100)}%": {
            "k": round(covered[f"{int(l*100)}"]["k"] / n, 3),
            "c": round(covered[f"{int(l*100)}"]["c"] / n, 3)} for l in COVERAGE_LEVELS},
    }
    print(out)
    save_result("e6_identifiability.json", out)


def adapter_simulate(k, c):
    import adapter
    return adapter.simulate_observations(1.0 + k, 1.0 + c, SEGMENTS, seed=hash((k, c)) % (2**31))


def adapter_run(obs):
    import adapter
    return adapter.run_particle_filter(obs)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.dry_run:
        import os
        os.environ["KIT_DRYRUN"] = "1"
    main(a.dry_run)
