# -*- coding: utf-8 -*-
"""run_all.py -- one command for the GPU machine.

    python run_all.py             # check env -> e1 -> e2 -> e3 -> e4 -> e5/e6/e7
                                  # -> leakage check -> tier decision -> fill & rebuild
    python run_all.py --through e1   # stop after a given stage
    python run_all.py --skip e3,e4   # e.g. only the statistics that feed Table 9

Every stage is resumable: e1 checkpoints per (scenario, method, seed); the
others overwrite their own result file. The script aborts before the fill
step if any required results file is missing or still flagged dry_run.
"""
import argparse
import json
import os
import subprocess
import sys
import time

KIT = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(KIT, "results")
PY = sys.executable

STAGES = [
    ("check", ["check_env.py"]),
    ("e1", ["e1_ten_seed.py"]),
    ("e2", ["e2_openset_s4.py"]),
    ("e3", ["e3_retention_sweep.py"]),
    ("e4", ["e4_budget_sweep.py"]),
    ("e5", ["e5_label_budget.py"]),
    ("e6", ["e6_identifiability.py"]),
    ("e7", ["e7_mmd_logging.py"]),
    ("leakage", ["leakage_check.py"]),
    ("tier", ["check_tier.py"]),
]
# result files required before the documents may be regenerated
REQUIRED = {"e1": "e1_table9.json", "e2": "e2_openset.json", "e3": "e3_retention.json",
            "e4": "e4_budget.json", "e5": "e5_counts.json", "e6": "e6_identifiability.json",
            "e7": "e7_mmd.json", "leakage": "leakage_report.json"}


def run(script, args=()):
    t0 = time.time()
    print(f"\n=== {script} {' '.join(args)} ===", flush=True)
    r = subprocess.run([PY, os.path.join(KIT, script), *args], cwd=KIT, text=True)
    print(f"--- {script} exit={r.returncode} ({time.time() - t0:.0f}s)", flush=True)
    return r.returncode


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--through", default="tier", choices=[s[0] for s in STAGES])
    ap.add_argument("--skip", default="")
    ap.add_argument("--fill", action="store_true", help="also fill and rebuild the two Word files")
    ap.add_argument("--apply-tier", action="store_true", help="apply the Tier B/C wording edits")
    a = ap.parse_args()
    skip = {s.strip() for s in a.skip.split(",") if s.strip()}

    for name, cmd in STAGES:
        if name in skip:
            print(f"[skip] {name}")
            continue
        if name == "check":
            rc = run(cmd[0])
            if rc != 0:
                print("Environment check failed -- fix the reported items first.")
                return rc
            continue
        rc = run(cmd[0])
        if rc != 0:
            print(f"[abort] stage {name} failed (exit {rc})")
            return rc
        if name == a.through:
            break

    # gate: every required result file must exist and be non-dry-run
    missing = []
    for stage, fname in REQUIRED.items():
        p = os.path.join(RES, fname)
        if not os.path.exists(p):
            missing.append(fname)
            continue
        with open(p, encoding="utf-8") as f:
            if json.load(f).get("dry_run"):
                missing.append(fname + " (dry_run)")
    if missing:
        print("[gate] not regenerating the documents; missing/placeholder results: "
              + ", ".join(missing))
        return 3

    if a.fill:
        if a.apply_tier:
            rc = run("apply_tier.py", ["--tier", "auto"])
            if rc != 0:
                print("[warn] tier wording edits incomplete -- inspect the MISS lines above")
        rc = run("fill_and_rebuild.py")
        if rc != 0:
            return rc
        print("\nDONE. Copy the kit/results folder and the two regenerated .docx files back "
              "to the submission folder, then re-run check_tier output check.")
    else:
        print("\nDONE. Review check_tier output, then run:\n"
              "  python apply_tier.py --tier auto   # only if tier is B or C\n"
              "  python fill_and_rebuild.py          # regenerate both Word documents")
    return 0


if __name__ == "__main__":
    sys.exit(main())
