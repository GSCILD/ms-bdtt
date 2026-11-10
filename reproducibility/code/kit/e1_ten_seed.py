# -*- coding: utf-8 -*-
"""e1_ten_seed.py -- F2 / F2b.

Ten-seed, seed-paired comparison of MS-BDTT against COSDA on S1-S5
(manuscript Table 9, Section 5.6). Runs are paired BY SEED; the paired
t-test, the seed-level bootstrap CI and Cohen's d follow Section 4.6.

Resume-safe: every finished (scenario, method, seed) triple is written to
results/e1_table9.json immediately. Re-running the script continues where it
stopped -- 100 GPU runs must never be lost to a crash.

Usage:
    python e1_ten_seed.py                       # real runs (needs adapter wiring)
    python e1_ten_seed.py --dry-run             # pipeline test only (refused by the filler)
    python e1_ten_seed.py --scenarios S5        # restrict to one scenario
"""
import argparse
import json
import os

import numpy as np

import adapter
from adapter import CONFIRM_SEEDS, SCENARIOS
from common import (RESULTS, cohens_d_paired, paired_t, save_result,
                    seed_bootstrap_ci, set_seed)

OUT = "e1_table9.json"


def load_existing():
    p = os.path.join(RESULTS, OUT)
    if not os.path.exists(p):
        return {"per_scenario": {}}
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def run_scenario_pair(scenario, seed):
    set_seed(seed)
    a = adapter.train_and_evaluate(scenario, "MS-BDTT", seed)
    b = adapter.train_and_evaluate(scenario, "COSDA", seed)
    return float(a["oa"]), float(b["oa"])


def main(dry_run, scenarios):
    state = load_existing()
    if state.get("dry_run"):
        state = {"per_scenario": {}}
    ps = state.setdefault("per_scenario", {})
    rng = np.random.default_rng(7)
    for sc in scenarios:
        entry = ps.setdefault(sc, {"ms_bdtt": {}, "cosda": {}})
        for seed in CONFIRM_SEEDS:
            s = str(seed)
            if s in entry.get("ms_bdtt", {}) and s in entry.get("cosda", {}):
                print(f"[skip] {sc} seed {seed} already done")
                continue
            if dry_run:
                oa_a = 80.0 + 4.0 + rng.normal(0, 1.2)
                oa_b = 80.0 + rng.normal(0, 1.0)
            else:
                oa_a, oa_b = run_scenario_pair(sc, seed)
            entry.setdefault("ms_bdtt", {})[s] = round(oa_a, 2)
            entry.setdefault("cosda", {})[s] = round(oa_b, 2)
            save_result(OUT, state)          # incremental checkpoint
            print(f"[done] {sc} seed {seed}: MS-BDTT {oa_a:.2f} / COSDA {oa_b:.2f}")
        d = np.array([entry["ms_bdtt"][str(s)] - entry["cosda"][str(s)]
                      for s in CONFIRM_SEEDS if str(s) in entry["ms_bdtt"]])
        if d.size >= 2:
            t, df, p = paired_t(d)
            lo, hi = seed_bootstrap_ci(d)
            entry.update({"delta_mean": round(float(d.mean()), 2),
                          "delta_sd": round(float(d.std(ddof=1)), 2),
                          "ci95": [round(lo, 2), round(hi, 2)],
                          "p_paired_t": p, "t": t, "df": df,
                          "cohens_d": round(cohens_d_paired(d), 2)})
            print(f"{sc}: dOA={d.mean():.2f}+-{d.std(ddof=1):.2f} "
                  f"CI[{lo:.2f},{hi:.2f}] p={p:.4g} d={entry['cohens_d']}")
    done = [s for s in SCENARIOS if s in ps and len(ps[s].get("ms_bdtt", {})) == len(CONFIRM_SEEDS)]
    if done:
        ms_macro = float(np.mean([np.mean(list(ps[s]["ms_bdtt"].values())) for s in done]))
        cos_macro = float(np.mean([np.mean(list(ps[s]["cosda"].values())) for s in done]))
        state["macro_avg_ms_bdtt"] = round(ms_macro, 2)
        state["macro_avg_cosda"] = round(cos_macro, 2)
        state["scenarios_completed"] = done
    state["n_seeds"] = len(CONFIRM_SEEDS)
    save_result(OUT, state)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--scenarios", nargs="*", default=SCENARIOS)
    a = ap.parse_args()
    if a.dry_run:
        os.environ["KIT_DRYRUN"] = "1"
    main(a.dry_run, a.scenarios)
