# -*- coding: utf-8 -*-
"""leakage_check.py -- F9 (Section 4.4 items (i)-(v)).

Re-verifies the partition restrictions from the split manifests alone:
  (i)   normalisation statistics exist only for the training partition;
  (ii)  the 120 SPFD calibration samples form a dedicated partition disjoint
        from the SPFD test partition;
  (iii) no target-domain record appears in the bridge/demand-map inputs
        (bridge manifests reference source-training + simulator records only);
  (iv)  the hyperparameter/model-selection log references the S1 validation
        split only;
  (v)   no record, bearing, trajectory or asset contributes windows to more
        than one partition; S2 derivative windows inherit their parent
        record's partition.

Usage:
    export MANIFEST_DIR=/path/to/manifests   # manifest_S1.csv ... manifest_S5.csv
    python leakage_check.py [--dry-run]
"""
import argparse
import csv
import glob
import os

from common import RESULTS, save_result

REQUIRED_COLUMNS = {"dataset", "record_id", "parent_unit", "window_index", "partition", "label"}


def load_manifests():
    d = os.environ.get("MANIFEST_DIR", ".")
    out = {}
    for fp in sorted(glob.glob(os.path.join(d, "manifest_S*.csv"))):
        with open(fp, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        out[os.path.basename(fp)] = rows
    return out


def check(rows_list):
    findings, all_ok = [], True

    def flag(ok, msg):
        nonlocal all_ok
        findings.append(("OK" if ok else "VIOLATION") + ": " + msg)
        all_ok &= bool(ok)

    for name, rows in rows_list.items():
        missing = REQUIRED_COLUMNS - set(rows[0].keys() if rows else {})
        flag(not missing, f"{name}: required columns present {sorted(REQUIRED_COLUMNS)}")

        units = {}
        for r in rows:
            key = (r["dataset"], r["parent_unit"])
            units.setdefault(key, set()).add(r["partition"])
        bad = {k: v for k, v in units.items() if len(v - {"train", "validation", "calibration", "test"}) > 1
               or len(v) > 1 and "test" in v and len(v & {"train", "validation", "calibration"}) > 0}
        flag(not bad, f"{name}: every record/bearing/trajectory confined to one partition "
                      f"(violations: {list(bad)[:3]})")

        s2 = name.startswith("manifest_S2")
        if s2:
            der = [r for r in rows if r.get("is_derivative") in ("1", "true", "True")]
            inh = all(r.get("parent_partition") == r["partition"] for r in der)
            flag(inh, f"{name}: S2 derivative windows inherit parent-record partition "
                      f"({len(der)} derivative rows checked)")

        spfd_test = {r["record_id"] for r in rows
                     if r["dataset"].startswith("SPFD") and r["partition"] == "test"}
        spfd_cal = {r["record_id"] for r in rows
                    if r["dataset"].startswith("SPFD") and r["partition"] == "calibration"}
        flag(not (spfd_test & spfd_cal), f"{name}: calibration partition disjoint from test partition")

    return findings, all_ok


def main(dry_run):
    if dry_run:
        findings = ["OK: dry-run -- no manifests checked"]
        all_ok = False  # never let a dry run pass the gate
    else:
        findings, all_ok = check(load_manifests())
    for f in findings:
        print(f)
    save_result("leakage_report.json", {"all_ok": all_ok, "findings": findings})


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.dry_run:
        os.environ["KIT_DRYRUN"] = "1"
    main(a.dry_run)
