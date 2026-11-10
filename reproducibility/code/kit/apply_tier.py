# -*- coding: utf-8 -*-
"""apply_tier.py -- apply the Tier B (soften) or Tier C (withdraw) wording
decided by check_tier.py to the markdown sources.

All replacements are anchored on unique substrings of the current text, so a
replacement that cannot be anchored is reported as MISSED instead of silently
skipping. Every applied edit is listed.

Usage:
    python apply_tier.py --tier B
    python apply_tier.py --tier C --results DIR
    python apply_tier.py --tier auto      # read tier_decision.json
"""
import argparse
import io
import json
import os
import re
import sys

KIT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(KIT, "md_source")


def _fmt_ci(ci):
    return f"[{ci[0]:.1f}, {ci[1]:.1f}]"


def build_edits(tier, e1, affected):
    """Return {filename: [(anchor_substring, replacement)]}."""
    s5 = e1["per_scenario"]["S5"]
    d_s5 = float(s5["delta_mean"])
    ci_s5 = [float(x) for x in s5["ci95"]]
    d_macro = float(e1.get("macro_avg_ms_bdtt", 0)) - float(e1.get("macro_avg_cosda", 0))
    ms_macro = float(e1.get("macro_avg_ms_bdtt", 0))
    edits = {}

    if tier == "B":
        edits.setdefault("ms1.md", []).append((
            "exceeding the strongest baseline by 3.6 and 6.8 percentage points, respectively.",
            f"exceeding the strongest baseline by 3.6 percentage points on the five-scenario "
            f"macro-average and by {d_s5:.1f} percentage points in the fully unlabelled-target "
            f"scenario, where the ten-seed paired comparison gives a 95 % confidence interval of "
            f"{_fmt_ci(ci_s5)} percentage points."))
        edits.setdefault("ms5.md", []).append((
            "The advantage is most pronounced in the unlabelled-target scenario S5, where MS-BDTT "
            "exceeds COSDA by 6.8 percentage points, and remains consistent in the cross-dataset "
            "and cross-equipment scenarios S3 and S4, where the margins over COSDA are 2.9 and 3.8 "
            "percentage points, respectively.",
            f"The advantage is most pronounced in the unlabelled-target scenario S5, where the "
            f"ten-seed paired replication gives {d_s5:.1f} percentage points over COSDA "
            f"(95 % CI {_fmt_ci(ci_s5)}), and it remains consistent in the cross-dataset and "
            f"cross-equipment scenarios S3 and S4. The three-seed grid of Table 5 is retained for "
            f"completeness and is labelled exploratory; the confirmatory values are those of "
            f"Table 9, whose effect size in S5 is smaller than the three-run grid suggested."))
        edits.setdefault("ms6.md", []).append((
            "exceeding the strongest baseline COSDA by 3.6 percentage points, and 76.0 ± 3.5 % "
            "sample-weighted overall accuracy in the most challenging unlabelled-target scenario, "
            "in which it surpasses all baselines by at least 6.8 percentage points.",
            f"exceeding the strongest baseline COSDA by 3.6 percentage points, and 76.0 ± 3.5 % "
            f"sample-weighted overall accuracy in the most challenging unlabelled-target scenario, "
            f"in which the ten-seed paired comparison gives {d_s5:.1f} percentage points over the "
            f"strongest baseline (95 % CI {_fmt_ci(ci_s5)})."))
        edits.setdefault("ms6.md", []).append((
            "and yielded the largest scenario-level margin over the baselines, 6.8 percentage points.",
            f"and yielded the largest scenario-level margin over the baselines, {d_s5:.1f} "
            f"percentage points in the ten-seed paired comparison."))
        edits.setdefault("ms5.md", []).append((
            "The ten-seed replication also yields five-scenario macro-averages of",
            "The ten-seed replication confirms the direction of the improvement in every "
            "scenario; the effect size in S5 is smaller than the three-run grid suggested, and "
            "the grid values should accordingly be read as exploratory. The ten-seed replication "
            "also yields five-scenario macro-averages of"))
        edits.setdefault("letter2.md", []).append((
            "and the conclusions are bounded by the ten-seed intervals rather than by the grid.",
            "and the conclusions are bounded by the ten-seed intervals rather than by the grid. The "
            "ten-seed replication confirms the direction of the improvement in every scenario; the "
            "effect size in S5 is smaller than the three-run grid suggested, and the grid values "
            "should accordingly be read as exploratory."))

    elif tier == "C":
        sc_txt = ", ".join(affected)
        ok_txt = ", ".join([s for s in ["S1", "S2", "S3", "S4", "S5"] if s not in affected])
        edits.setdefault("ms1.md", []).append((
            "exceeding the strongest baseline by 3.6 and 6.8 percentage points, respectively.",
            f"with the ten-seed paired replication confirming the improvement over the strongest "
            f"baseline on {ok_txt}, while in {sc_txt} the paired confidence interval includes zero "
            f"and no difference is established at that sample size."))
        edits.setdefault("ms5.md", []).append((
            "The advantage is most pronounced in the unlabelled-target scenario S5, where MS-BDTT "
            "exceeds COSDA by 6.8 percentage points, and remains consistent in the cross-dataset "
            "and cross-equipment scenarios S3 and S4, where the margins over COSDA are 2.9 and 3.8 "
            "percentage points, respectively.",
            f"The improvement over the strongest baseline is established on {ok_txt}. In {sc_txt}, "
            f"the ten-seed paired comparison does not establish a difference, and we therefore "
            f"make no comparative claim for that scenario; the corresponding rows of Table 9 are "
            f"reported with their intervals, which include zero."))
        edits.setdefault("ms6.md", []).append((
            "exceeding the strongest baseline COSDA by 3.6 percentage points, and 76.0 ± 3.5 % "
            "sample-weighted overall accuracy in the most challenging unlabelled-target scenario, "
            "in which it surpasses all baselines by at least 6.8 percentage points.",
            f"exceeding the strongest baseline COSDA by 3.6 percentage points, and 76.0 ± 3.5 % "
            f"sample-weighted overall accuracy in the most challenging unlabelled-target scenario, "
            f"in which the ten-seed paired comparison does not establish a difference over the "
            f"baselines."))
        edits.setdefault("ms6.md", []).append((
            "and yielded the largest scenario-level margin over the baselines, 6.8 percentage points.",
            "an effect that the ten-seed replication does not resolve at scenario level."))
        edits.setdefault("ms5.md", []).append((
            "The ten-seed replication also yields five-scenario macro-averages of",
            "The ten-seed replication confirms the direction of the improvement in the scenarios "
            "whose intervals exclude zero; in the remaining scenario the interval includes zero, "
            "and we have removed the comparative claim for that scenario accordingly rather than "
            "retaining a significance statement that the data do not support. The ten-seed "
            "replication also yields five-scenario macro-averages of"))
        edits.setdefault("letter2.md", []).append((
            "and the conclusions are bounded by the ten-seed intervals rather than by the grid.",
            "and the conclusions are bounded by the ten-seed intervals rather than by the grid. The "
            "ten-seed replication confirms the direction of the improvement in the scenarios whose "
            "intervals exclude zero; in the remaining scenario the interval includes zero, and we "
            "have removed the comparative claim for that scenario accordingly rather than "
            "retaining a significance statement that the data do not support."))
    return edits


def main(tier, results_dir):
    with open(os.path.join(results_dir, "e1_table9.json"), encoding="utf-8") as f:
        e1 = json.load(f)
    if e1.get("dry_run"):
        print("REFUSED: dry-run results cannot drive the manuscript wording.")
        return 2
    affected = []
    for sc in ["S1", "S2", "S3", "S4", "S5"]:
        r = e1["per_scenario"][sc]
        lo, hi = [float(x) for x in r["ci95"]]
        if not (lo > 0 and float(r["delta_mean"]) > 0):
            affected.append(sc)
    if tier == "auto":
        dp = os.path.join(results_dir, "tier_decision.json")
        if not os.path.exists(dp):
            print("tier_decision.json missing -- run check_tier.py first")
            return 2
        with open(dp, encoding="utf-8") as f:
            tier = json.load(f)["tier"]
    print(f"applying Tier {tier}" + (f" (affected: {affected})" if affected else ""))
    if tier == "A":
        print("Tier A: no wording change required; the current text stands.")
        return 0
    edits = build_edits(tier, e1, affected)
    applied, missed = 0, 0
    for fname, pairs in edits.items():
        p = os.path.join(SRC, fname)
        if not os.path.exists(p):
            print(f"[MISS] {fname} not found")
            continue
        with io.open(p, encoding="utf-8") as f:
            txt = f.read()
        for anchor, repl in pairs:
            if anchor in txt:
                txt = txt.replace(anchor, repl, 1)
                applied += 1
                print(f"[ok] {fname}: {anchor[:58]}... -> applied")
            else:
                missed += 1
                print(f"[MISS] {fname}: anchor not found -> {anchor[:70]}")
        bak = p + ".pristine"
        if not os.path.exists(bak):
            shutil_copy(p, bak)
        with io.open(p, "w", encoding="utf-8") as f:
            f.write(txt)
    print(f"applied {applied}, missed {missed}")
    if missed:
        print("MISSED anchors need a manual edit (the wording drifted from this script).")
    return 0 if applied and not missed else 1


def shutil_copy(a, b):
    import shutil
    shutil.copyfile(a, b)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tier", default="auto", choices=["A", "B", "C", "auto"])
    ap.add_argument("--results", default=os.path.join(KIT, "results"))
    a = ap.parse_args()
    sys.exit(main(a.tier, a.results))
