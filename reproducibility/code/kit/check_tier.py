# -*- coding: utf-8 -*-
"""check_tier.py -- compare the ten-seed confirmatory result with the
three-seed exploratory grid of Table 5 and decide the wording tier.

Decision rule (also stated in wording_options.md):
  * band: |dOA_10 - dOA_3| <= 2 * max(SD_3(MS-BDTT), SD_3(COSDA)) -- a
    practical "same dispersion band" test, since the three-seed grid reports
    only the per-scenario run-to-run SD.
  * Tier C if any scenario's 95 % CI of the mean paired difference includes 0
    (or the mean difference is not positive).
  * Tier B if all CIs exclude 0 but at least one scenario falls outside the
    band, or the macro-average differs from the grid value by > 1.0 pp.
  * Tier A otherwise.

Usage:
    python check_tier.py                 # uses results/e1_table9.json
    python check_tier.py --results DIR   # point at a copied-back folder
"""
import argparse
import json
import os
import sys

# Table 5 of the revised manuscript: COSDA minus MS-BDTT per scenario
# (three seeds) with the per-scenario run-to-run SDs of both methods.
GRID3 = {
    "S1": {"delta": 1.7, "sd_ms": 0.6, "sd_cosda": 0.8},
    "S2": {"delta": 2.7, "sd_ms": 1.0, "sd_cosda": 1.4},
    "S3": {"delta": 2.9, "sd_ms": 0.9, "sd_cosda": 1.1},
    "S4": {"delta": 3.8, "sd_ms": 1.1, "sd_cosda": 1.5},
    "S5": {"delta": 6.8, "sd_ms": 3.5, "sd_cosda": 2.1},
}
MACRO3 = 3.6
SCEN = ["S1", "S2", "S3", "S4", "S5"]


def band(sc):
    """Claim-level consistency band.

    The three-seed grid reports only the per-scenario run-to-run SD, so a
    purely statistical band (2 SD) is too wide to detect a systematic
    shrinkage of a headline margin. We therefore require the ten-seed effect
    to agree with the grid value both in absolute terms (<= 1.0 pp) and in
    relative terms (<= 25 % of the grid value); a larger deviation changes
    what the abstract may claim even when the interval excludes zero.
    """
    g = GRID3[sc]
    return max(1.0, 0.25 * abs(g["delta"]))


def evaluate(e1):
    rows, tier_reasons = [], []
    tier = "A"
    for sc in SCEN:
        r = e1["per_scenario"][sc]
        d10 = float(r["delta_mean"])
        lo, hi = [float(x) for x in r["ci95"]]
        p = float(r["p_paired_t"])
        b = band(sc)
        inside = abs(d10 - GRID3[sc]["delta"]) <= b
        excludes_zero = (lo > 0) and (d10 > 0)
        rows.append({"scenario": sc, "grid3_delta": GRID3[sc]["delta"],
                     "ten_seed_delta": d10, "ten_seed_sd": float(r["delta_sd"]),
                     "ci95": [lo, hi], "p": p, "d": float(r["cohens_d"]),
                     "band": [GRID3[sc]["delta"] - b, GRID3[sc]["delta"] + b],
                     "inside_band": inside, "ci_excludes_zero": excludes_zero})
        if not excludes_zero:
            tier = "C"
            tier_reasons.append(f"{sc}: CI [{lo:.2f}, {hi:.2f}] includes zero -> withdraw the "
                                f"comparative claim for {sc}")
        elif not inside:
            tier = "B" if tier != "C" else tier
            tier_reasons.append(f"{sc}: dOA {d10:.2f} outside the three-seed band "
                                f"[{GRID3[sc]['delta'] - b:.2f}, {GRID3[sc]['delta'] + b:.2f}] -> soften")
    macro10 = float(e1.get("macro_avg_ms_bdtt", 0)) - float(e1.get("macro_avg_cosda", 0))
    if tier == "A" and abs(macro10 - MACRO3) > max(1.0, 0.25 * abs(MACRO3)):
        tier = "B"
        tier_reasons.append(f"macro-average dOA {macro10:.2f} differs from the grid value "
                            f"{MACRO3:.1f} by more than 0.9 pp -> soften")
    return rows, macro10, tier, tier_reasons


def main(results_dir):
    p = os.path.join(results_dir, "e1_table9.json")
    if not os.path.exists(p):
        print(f"[missing] {p}")
        return 2
    with open(p, encoding="utf-8") as f:
        e1 = json.load(f)
    if e1.get("dry_run"):
        print("REFUSED: this is a dry-run result file; it must not drive the manuscript.")
        return 2
    done = e1.get("scenarios_completed", [])
    if len(done) < len(SCEN):
        print(f"[incomplete] scenarios finished: {done} -- rerun e1 before deciding the tier.")
    rows, macro10, tier, reasons = evaluate(e1)
    print(f"{'sc':>3} {'grid3':>7} {'10-seed':>8} {'band':>17} {'95% CI':>17} {'p':>9} {'d':>5}  in-band")
    for r in rows:
        print(f"{r['scenario']:>3} {r['grid3_delta']:>7.2f} {r['ten_seed_delta']:>8.2f} "
              f"[{r['band'][0]:>6.2f},{r['band'][1]:>6.2f}] [{r['ci95'][0]:>6.2f},{r['ci95'][1]:>6.2f}] "
              f"{r['p']:>9.4g} {r['d']:>5.2f}  {'yes' if r['inside_band'] else 'NO'}")
    print(f"\nmacro-average dOA: grid {MACRO3:.1f} pp | ten-seed {macro10:.2f} pp")
    print(f"RECOMMENDED TIER: {tier}")
    for r in reasons:
        print(f"  - {r}")
    if tier == "A":
        print("  -> wording_options.md Tier A: keep the current wording; optionally add the "
              "sentence about the ten-seed replication reproducing the three-seed effect sizes.")
    elif tier == "B":
        print("  -> wording_options.md Tier B: soften (abstract, Section 5.1, Section 6.1/6.2, "
              "letter point 5). Run: python apply_tier.py --tier B")
    else:
        print("  -> wording_options.md Tier C: withdraw the comparative claim for the affected "
              "scenario(s). Run: python apply_tier.py --tier C")
    out = {"rows": rows, "macro10": macro10, "tier": tier, "reasons": reasons}
    with open(os.path.join(results_dir, "tier_decision.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"[saved] {os.path.join(results_dir, 'tier_decision.json')}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "results"))
    a = ap.parse_args()
    sys.exit(main(a.results))
