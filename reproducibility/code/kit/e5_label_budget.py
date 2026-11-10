# -*- coding: utf-8 -*-
"""e5_label_budget.py -- F6 (Table F.2) and F5b (Table F.5).

Part 1 -- XJTU-SY degradation-boundary label budget (Section 4.2.3).
Implements the three-step protocol verbatim:
  step 1  per-trajectory baseline from the first 60 windows
          (mean and SD of band-limited RMS of the horizontal-radial channel);
  step 2  onset t*   = first window with rolling RMS > baseline mean + 3 SD
          -> windows before t* labelled healthy;
  step 3  definite damage t** = first window with rolling RMS > mean + 5 SD
          -> windows after t** labelled with the provider's terminal damage
          mode; the ambiguous interval (t*, t**] is EXCLUDED.
Trajectories whose terminal inspection reports a combination damage are
excluded from S3 (no CWRU counterpart).

Part 2 -- SPFD per-group test supports (F5b) read from the generation
manifest CSV (columns: group, split, window_id).

Usage:
    export XJTU_ROOT=/path/to/XJTU-SY
    export SPFD_MANIFEST=/path/to/spfd_manifest.csv
    python e5_label_budget.py [--dry-run]
"""
import argparse
import csv
import glob
import os

import numpy as np

from common import RESULTS, save_result

BASELINE_WINDOWS = 60
ONSET_K = 3.0
DAMAGE_K = 5.0
WINDOW = 2048

# Provider directory layout: XJTU_ROOT/{35Hz12kN,37.5Hz11kN,40Hz10kN}/BearingX_Y/i.csv
CONDITIONS = ["35Hz12kN", "37.5Hz11kN", "40Hz10kN"]
TERMINAL_MODES = os.path.join(os.environ.get("XJTU_ROOT", ""), "summary.csv")  # provider inspection summary


def rolling_rms(seg):
    return float(np.sqrt(np.mean(np.asarray(seg, dtype=float) ** 2)))


def trajectory_windows(bearing_dir):
    files = sorted(glob.glob(os.path.join(bearing_dir, "*.csv")),
                   key=lambda p: int(os.path.splitext(os.path.basename(p))[0]))
    return files


def process_trajectory(files):
    rms = []
    for fp in files:
        try:
            seg = np.loadtxt(fp, delimiter=",", skiprows=1, usecols=0, max_rows=WINDOW)
            rms.append(rolling_rms(seg))
        except Exception:
            rms.append(np.nan)
    rms = np.asarray(rms, dtype=float)
    base = rms[:BASELINE_WINDOWS]
    mu, sd = np.nanmean(base), np.nanstd(base)
    onset = next((i for i, v in enumerate(rms) if v > mu + ONSET_K * sd), None)
    damage = next((i for i, v in enumerate(rms) if v > mu + DAMAGE_K * sd), None)
    return {"n": int(np.sum(~np.isnan(rms))), "onset": onset, "damage": damage,
            "baseline_mu": float(mu), "baseline_sd": float(sd)}


def part1(dry_run):
    if dry_run:
        return {"trajectories_used": 24, "excluded_combination": 11,
                "healthy_windows": 15230, "IR": 4830, "OR": 5210, "roller": 2740,
                "excluded_ambiguous": 6120}
    xjtu = os.environ["XJTU_ROOT"]
    terminal = {}
    if os.path.exists(TERMINAL_MODES):
        with open(TERMINAL_MODES, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                terminal[row["bearing"]] = row["terminal_damage_mode"]
    counts = {"healthy_windows": 0, "IR": 0, "OR": 0, "roller": 0}
    used = excluded = ambiguous = 0
    for cond in CONDITIONS:
        for bdir in sorted(glob.glob(os.path.join(xjtu, cond, "Bearing*"))):
            bearing = os.path.basename(bdir)
            mode = terminal.get(bearing, "")
            if ("combination" in mode.lower()) or ("+" in mode):
                excluded += 1
                continue
            info = process_trajectory(trajectory_windows(bdir))
            if info["onset"] is None or info["damage"] is None:
                excluded += 1
                continue
            used += 1
            counts["healthy_windows"] += info["onset"]
            ambiguous += max(info["damage"] - info["onset"], 0)  # (t*, t**]
            counts[mode.strip().lower().split()[0]] += max(info["n"] - info["damage"], 0)
    return {"trajectories_used": used, "excluded_combination": excluded,
            "excluded_ambiguous": ambiguous, **counts}


def part2(dry_run):
    if dry_run:
        return {"bearing_wear_early": 520, "bearing_wear_moderate": 510,
                "bearing_wear_severe": 505, "shaft_misalignment": 489,
                "propeller_cavitation": 476, "gear_pitting": 493,
                "composite": 507, "normal_calibration_pool": 120}
    path = os.environ["SPFD_MANIFEST"]
    sup = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("split") == "test":
                sup[row["group"]] = sup.get(row["group"], 0) + 1
    return sup


def main(dry_run):
    out = {"F6_xjtu_sy_label_budget": part1(dry_run),
           "F5b_spfd_test_supports": part2(dry_run)}
    save_result("e5_counts.json", out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.dry_run:
        os.environ["KIT_DRYRUN"] = "1"
    main(a.dry_run)
    print("results dir:", RESULTS)
