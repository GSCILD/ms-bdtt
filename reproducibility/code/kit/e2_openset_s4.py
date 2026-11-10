# -*- coding: utf-8 -*-
"""e2_openset_s4.py -- F5a.

Open-set evaluation on S4 (manuscript Section 4.2.4 / Table 8b).

Protocol (identical for every method):
  * mapped classes  : {healthy, crack-type, surface-type}
    source-private  : {combined IR+OR}   (Paderborn)
    target-private  : {missing tooth, surface wear} (SEU gearbox)
  * rejection rule  : reject as "unknown" when max softmax < tau_rej
  * threshold       : tau_rej = 95th percentile of the max-softmax
    distribution on held-out SOURCE-VALIDATION data (leakage-safe,
    Section 4.6); fixed across all methods
  * metrics         : CCA (closed-set accuracy over mapped classes,
                      no rejection), unknown-detection AUROC,
                      OS (unknown must be rejected; per Busto & Gall,
                      mean of known-class accuracies and unknown-rejection
                      accuracy, normalised by |C_L|+1),
                      OS* (unknown treated as its own class).

Usage: python e2_openset_s4.py [--dry-run]
"""
import argparse
import numpy as np

import adapter
from adapter import MAIN_SEEDS
from common import auroc_unknown, save_result, set_seed

METHODS = ["Source-Only", "DANN", "COSDA", "MS-BDTT"]
MAPPED = set(adapter.OPEN_SET_CFG["mapped_classes"])
PRIVATE_TARGET = set(adapter.OPEN_SET_CFG["private_target_labels"])
TAU_QUANTILE = 0.95


def evaluate_run(method, seed, dry_run, rng):
    if dry_run:
        recs = []
        priv = sorted(PRIVATE_TARGET)
        for i in range(300):
            lab = priv[0] if i % 3 == 0 else sorted(MAPPED)[i % 3]
            s = rng.uniform(0.2, 0.9)
            pred = lab if s > 0.5 else rng.choice(sorted(MAPPED))
            recs.append({"record_id": f"r{i}", "label": lab, "pred": pred, "max_softmax": float(s)})
        val_scores = list(rng.uniform(0.3, 1.0, size=200))
    else:
        val_scores = adapter.source_validation_max_softmax(method, seed)
        tau = float(np.quantile(np.asarray(val_scores, dtype=float), TAU_QUANTILE))
        res = adapter.train_and_evaluate("S4", method, seed)
        recs = []
        for r, s in zip(res["records"], res["max_softmax"]):
            pred = "REJECT" if float(s) < tau else r["pred"]
            recs.append({"record_id": r["record_id"], "label": r["label"],
                         "pred": pred, "max_softmax": float(s)})
        val_scores = list(val_scores)
    return recs, val_scores


def metrics(recs):
    known = [r for r in recs if r["label"] in MAPPED]
    unknown = [r for r in recs if r["label"] in PRIVATE_TARGET]
    if not unknown:
        raise RuntimeError(
            "No target-private samples found in the S4 test records, so the "
            "open-set track cannot be computed. Check that your prediction "
            "records use the label names in adapter.OPEN_SET_CFG "
            f"(mapped={sorted(MAPPED)}, private target={sorted(PRIVATE_TARGET)}) "
            "or adapt that dictionary to your pipeline's labels.")
    stray = {r["label"] for r in recs} - MAPPED - PRIVATE_TARGET
    if stray:
        print(f"[warn] labels outside the mapped/private sets: {sorted(stray)}")
    # CCA: closed-set accuracy over mapped classes, rejection NOT applied
    cca = 100.0 * np.mean([r["pred"] == r["label"] for r in known])
    # OS*: unknown as its own class over ALL samples
    os_star = 100.0 * np.mean([
        (r["pred"] == r["label"]) or (r["label"] in PRIVATE_TARGET and r["pred"] == "REJECT")
        for r in recs])
    # OS: mean of known-class accuracies (reject = error) and unknown-rejection accuracy,
    # normalised by |C_L|+1 (Busto & Gall convention)
    per_class = []
    for c in sorted(MAPPED):
        rows = [r for r in known if r["label"] == c]
        if rows:
            per_class.append(np.mean([r["pred"] == r["label"] for r in rows]))
    acc_u = np.mean([r["pred"] == "REJECT" for r in unknown]) if unknown else 0.0
    os_ = 100.0 * (sum(per_class) + acc_u) / (len(per_class) + 1)
    auroc = auroc_unknown([r["max_softmax"] for r in known],
                          [r["max_softmax"] for r in unknown])
    return {"CCA": round(float(cca), 2), "AUROC": round(float(auroc), 3),
            "OS": round(float(os_), 2), "OS*": round(float(os_star), 2)}


def main(dry_run):
    rng = np.random.default_rng(11)
    out = {}
    for m in METHODS:
        runs = []
        for seed in MAIN_SEEDS[:3]:
            recs, _ = evaluate_run(m, seed, dry_run, rng)
            runs.append(metrics(recs))
        agg = {k: round(float(np.mean([r[k] for r in runs])), 2) for k in runs[0]}
        agg["per_run"] = runs
        out[m] = agg
        print(m, agg)
    save_result("e2_openset.json", {"tau_rule": f"p{int(TAU_QUANTILE*100)} of source-val max-softmax",
                                    "results": out})


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.dry_run:
        import os
        os.environ["KIT_DRYRUN"] = "1"
    main(a.dry_run)
