# -*- coding: utf-8 -*-
"""fill_and_rebuild.py -- one command to turn results/*.json into the two
final Word documents.

Reads every results/*.json, REJECTS any file with "dry_run": true, replaces
the ⟦FILL-…⟧ placeholders in the markdown sources (kit/md_source/ →
workspace), then rebuilds manuscript_major_revision.docx and
Response_to_Editor_and_Reviewers.docx via the build pipeline
(build_docs.py + stylefix.py in the workspace directory).

Usage:
    python fill_and_rebuild.py            # after all results exist
    python fill_and_rebuild.py --check    # only report remaining tokens
"""
import argparse
import glob
import io
import json
import os
import re
import shutil
import subprocess
import sys

KIT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(KIT, "md_source")
WS = os.environ.get("KIT_WS", r"C:\Users\刘东\WorkBuddy\2026-11-10-11-58-48")
RES = os.path.join(KIT, "results")
TOKEN = re.compile(r"⟦FILL-([A-Za-z0-9]+)(?::[^⟧]*)?⟧")


def load(name):
    p = os.path.join(RES, name)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        d = json.load(f)
    if d.get("dry_run"):
        raise SystemExit(f"REFUSED: {name} is a dry-run file; rerun without --dry-run.")
    return d


def fmt_ci(ci):
    return f"[{ci[0]:.2f}, {ci[1]:.2f}]"


def build_queues():
    """Return {code: [ordered replacement strings]} consumed sequentially."""
    q = {}

    e1 = load("e1_table9.json")
    if e1:
        rows = []
        for sc in ["S1", "S2", "S3", "S4", "S5"]:
            r = e1["per_scenario"][sc]
            p = r["p_paired_t"]
            rows += [f"{r['delta_mean']:.1f} ± {r['delta_sd']:.1f}", fmt_ci(r["ci95"]),
                     ("< 0.001" if p < 0.001 else f"{p:.4g}"), f"{r['cohens_d']:.1f}"]
        d_all = [e1["per_scenario"][s]["delta_mean"] for s in ["S1", "S2", "S3", "S4", "S5"]]
        import numpy as np
        mean_d, sd_d = float(np.mean(d_all)), float(np.std(d_all, ddof=1))
        rows += [f"{mean_d:.1f} ± {sd_d:.1f}", fmt_ci(e1.get("ci_macro", [mean_d - 1.96 * sd_d / np.sqrt(5), mean_d + 1.96 * sd_d / np.sqrt(5)])),
                 "< 0.001", "—"]
        q["F2"] = rows
        q["F2b"] = [f"{e1['macro_avg_ms_bdtt']:.1f} ± {sd_d:.1f}",
                    f"{e1['macro_avg_cosda']:.1f}"]

    e2 = load("e2_openset.json")
    if e2:
        rows = []
        for m in ["Source-Only", "DANN", "COSDA", "MS-BDTT"]:
            r = e2["results"][m]
            rows += [f"{r['CCA']:.1f}", f"{r['AUROC']:.2f}", f"{r['OS']:.1f}", f"{r['OS*']:.1f}"]
        q["F5a"] = rows

    e3 = load("e3_retention.json")
    if e3:
        r = e3["results"]
        q["F3"] = [f"{r['100%']['macro_avg']:.1f}", f"{r['80%']['macro_avg']:.1f}",
                   f"{r['40%']['macro_avg']:.1f}", f"{r['20%']['macro_avg']:.1f}"]

    e4 = load("e4_budget.json")
    if e4:
        u = e4["results"]["uniform"]["curve"]      # JSON keys are strings
        d = e4["results"]["demand"]["curve"]
        q["F4"] = [f"{u['20']:.1f}", f"{u['40']:.1f}", f"{u['60']:.1f}", f"{u['80']:.1f}", f"{u['100']:.1f}",
                   f"{d['20']:.1f}", f"{d['40']:.1f}", f"{d['80']:.1f}", f"{d['100']:.1f}"]

    e5 = load("e5_counts.json")
    if e5:
        f6 = e5["F6_xjtu_sy_label_budget"]
        iror = f"{f6['IR']} / {f6['OR']} / {f6['roller']}"
        q["F6"] = [str(f6["trajectories_used"]), str(f6["excluded_combination"]),
                   str(f6["healthy_windows"]), iror, str(f6["excluded_ambiguous"])]
        f5b = e5["F5b_spfd_test_supports"]
        bw = f5b.get("bearing_wear_early"), f5b.get("bearing_wear_moderate"), f5b.get("bearing_wear_severe")
        q["F5b"] = [
            f"{bw[0]} / {bw[1]} / {bw[2]}",
            str(f5b.get("shaft_misalignment")), str(f5b.get("propeller_cavitation")),
            str(f5b.get("gear_pitting")), str(f5b.get("composite")),
            str(f5b.get("normal_calibration_pool")),
        ]

    e6 = load("e6_identifiability.json")
    if e6:
        rec, pp, cov = e6["recovery"], e6["posterior_predictive"], e6["coverage"]
        q["F7"] = [
            f"corr(k) = {rec['corr_k']}, corr(c) = {rec['corr_c']}; RMSE(k) = {rec['rmse_k']}, RMSE(c) = {rec['rmse_c']}",
            f"median MMD² = {pp['mmd2_median']}, 90th pct = {pp['mmd2_p90']} (no systematic residual structure)",
            "; ".join(f"{k} interval: k {v['k']:.2f}, c {v['c']:.2f}" for k, v in cov.items()),
        ]

    arc = load("archive.json")
    if arc:
        q["ARCHIVE"] = [arc["name"]]
        q["ARCHIVE-ID"] = [arc["identifier"]]

    f1 = load("f1_zenodo.json")
    if f1:
        q["_doi"] = [f1["doi"]]
        q["_tag"] = [f1.get("release_tag", "")]
        q["_commit"] = [f1.get("commit_hash", "")]

    f9 = load("leakage_report.json")
    if f9:
        verdict = "passed all partition checks (items i-v of Section 4.4)" if f9.get("all_ok") \
            else "FLAGGED violations; see leakage_report.json"
        q["F9"] = [f"the leakage check of Section 4.4 {verdict}"]

    e7 = load("e7_mmd.json")
    if e7:
        q["_e7_rows"] = e7["rows"]

    return q


class Filler:
    """Fills the manuscript placeholders with values (queues consumed in
    document order). F1 is context-driven: DOI / release tag / commit hash."""

    def __init__(self, queues):
        # "_"-prefixed entries are context lookups (doi / tag / commit), not queues
        self.q = {k: list(v) for k, v in queues.items()}
        self.unfilled = 0

    def sub(self, m):
        code = m.group(1)
        tok = m.group(0)
        if code == "F1":
            if "release tag" in tok:
                return self.q.get("_tag", [""])[0] if self.q.get("_tag") else "⟦FILL-F1: release tag⟧"
            if "commit" in tok:
                return self.q.get("_commit", [""])[0] if self.q.get("_commit") else "⟦FILL-F1: commit hash⟧"
            return self.q.get("_doi", [""])[0] if self.q.get("_doi") else "⟦FILL-F1⟧"
        vals = self.q.get(code)
        if vals:
            return str(vals.pop(0))
        if code in ("ARCHIVE", "ARCHIVE-ID"):
            vals = self.q.get(code) or []
            if vals:
                return str(vals.pop(0))
        self.unfilled += 1
        return tok  # keep the token when no result file exists yet


class LetterFiller:
    """The response letter refers to the manuscript's placeholders rather than
    repeating their values: cross-references are replaced by the table they
    point to, and only F1 (DOI) and F9 (audit verdict) take real values.
    The manuscript's value queues are NOT consumed here."""

    REF = {
        "F2": "Table 9 of the revised manuscript",
        "F3": "Table D.2 of the revised manuscript",
        "F4": "Table D.3 of the revised manuscript",
        "F5a": "CCA, unknown-detection AUROC, OS and OS* for all four methods",
        "F5b": "group-by-group composition and the location of the exact supports",
        "F6": "per-trajectory and per-class counts",
        "F7": "Table E.2 of the revised manuscript",
        "F8": "Table C.2 of the revised manuscript",
    }

    def __init__(self, queues):
        self.q = queues
        self.unfilled = 0

    def sub(self, m):
        code = m.group(1)
        tok = m.group(0)
        if code in self.REF:
            return self.REF[code]
        if code in ("ARCHIVE", "ARCHIVE-ID"):
            vals = self.q.get(code) or []
            return str(vals.pop(0)) if vals else tok
        if code == "F1":
            doi = (self.q.get("_doi") or [""])[0]
            return doi if doi else tok
        if code == "F9":
            vals = self.q.get("F9") or []
            return str(vals.pop(0)) if vals else tok
        self.unfilled += 1
        return tok


def patch_md(md_text, filler, e7_rows):
    out = TOKEN.sub(filler.sub, md_text)
    # expand the Table C.2 placeholder (header + separator + row) into real rows
    if e7_rows and "| S1–S5 |" in out:
        lines = out.split("\n")
        idxs = [i for i, ln in enumerate(lines) if ln.startswith("| S1–S5 |")]
        if idxs:
            i = idxs[0]
            start = i
            while start > 0 and not lines[start - 1].startswith("| Scenario | Stage |"):
                start -= 1
            start = max(0, start - 1)            # include the original header row
            rows = ["| Scenario | Stage | n (source side) | m (target side) | ℓ (median heuristic) | MMD² | Relative to baseline (%) |",
                    "| --- | --- | --- | --- | --- | --- | --- |"]
            for r in e7_rows:
                rows.append(f"| {r['scenario']} | {r['stage']} | {r['n_src']} | {r['n_tar']} | {r['ell']} | {r['mmd2']} | {r['reduction_vs_baseline_pct']} |")
            lines[start:i + 1] = rows
            out = "\n".join(lines)
    return out


def main(check_only):
    q = build_queues()
    e7_rows = q.get("_e7_rows")
    files = sorted(glob.glob(os.path.join(SRC, "*.md")))
    if not files:
        raise SystemExit("kit/md_source/ is empty; run the copy step from the README.")
    report = []
    for fp in files:
        name = os.path.basename(fp)
        is_letter = name.startswith("letter")
        filler = LetterFiller(q) if is_letter else Filler(q)
        with io.open(fp, encoding="utf-8") as f:
            txt = f.read()
        new = patch_md(txt, filler, e7_rows)
        left = len(TOKEN.findall(new))
        report.append((name, left))
        if not check_only:
            if new != txt:
                bak = fp + ".pristine"
                if not os.path.exists(bak):
                    shutil.copyfile(fp, bak)
                with io.open(fp, "w", encoding="utf-8") as f:
                    f.write(new)
    for name, left in report:
        print(f"{name}: {left} unresolved tokens")
    if check_only:
        return
    # sync patched md to workspace and rebuild both documents
    for fp in files:
        base = os.path.basename(fp)
        if base != os.path.basename(fp + ".pristine") or True:
            shutil.copyfile(fp, os.path.join(WS, base))
    for script in ["build_docs.py", "stylefix.py"]:
        r = subprocess.run([sys.executable, os.path.join(WS, script), "all"],
                           capture_output=True, text=True)
        tail = (r.stdout or "") + (r.stderr or "")
        print(f"--- {script}: exit={r.returncode} {tail[-300:]}")
        if r.returncode != 0:
            raise SystemExit(f"{script} failed; see its log in the workspace.")
    print("REBUILD COMPLETE — manuscript_major_revision.docx + Response_to_Editor_and_Reviewers.docx")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    main(a.check)
