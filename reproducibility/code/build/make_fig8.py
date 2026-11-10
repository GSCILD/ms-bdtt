# -*- coding: utf-8 -*-
"""Regenerate Fig. 8 from the archived per-stage MMD values (S1, S3, S5),
stacked by component contribution."""
import json, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

KIT = r"D:\006-SCI SSCI实验室-\2026年投稿\1-0913-science report\学术图0913\1110\reproducibility_kit"
FIG = os.path.join(KIT, "figs")
e7 = json.load(open(os.path.join(KIT, "results", "e7_mmd.json"), encoding="utf-8"))["rows"]

plt.rcParams.update({
    "font.family": "Times New Roman", "font.size": 8.5, "axes.linewidth": 0.8,
    "axes.labelsize": 8.5, "axes.titlesize": 8.5, "xtick.labelsize": 8, "ytick.labelsize": 8,
    "legend.fontsize": 7.6, "legend.frameon": False, "figure.dpi": 300, "savefig.dpi": 300,
    "axes.spines.top": False, "axes.spines.right": False,
})
BLUE, ORANGE, GREEN, GREY = "#1f4e79", "#c55a11", "#2e7d32", "#9e9e9e"
LABEL = {"S1": "S1 (cross-load)", "S3": "S3 (cross-dataset)", "S5": "S5 (unlabelled target)"}
STAGES = [("bridge", "Continuous bridge (Stage 1)", BLUE, "//"),
          ("calibration", "Bayesian calibration (Stage 2)", ORANGE, ".."),
          ("attention", "Attention weighting (Stage 3)", GREEN, "xx"),
          ("adversarial", "Adversarial alignment (Stage 3)", GREY, "--")]

scs = [s for s in ["S1", "S3", "S5"] if any(r["scenario"] == s for r in e7)]
fig, ax = plt.subplots(figsize=(4.3, 2.9))
bottom = [0.0] * len(scs)
for key, name, col, hatch in STAGES:
    vals = []
    for i, s in enumerate(scs):
        rows = {r["stage"]: float(r["reduction_vs_baseline_pct"]) for r in e7 if r["scenario"] == s}
        order = ["baseline", "bridge", "calibration", "attention", "adversarial"]
        j = order.index(key)
        prev = rows.get(order[j - 1], 0.0)
        vals.append(rows[key] - prev)          # per-stage contribution
    ax.bar(range(len(scs)), vals, bottom=bottom, width=0.55, color=col, hatch=hatch,
           edgecolor="black", linewidth=0.6, label=name)
    bottom = [b + v for b, v in zip(bottom, vals)]
for i, (s, tot) in enumerate(zip(scs, bottom)):
    ax.text(i, tot + 1.2, f"{tot:.1f} %", ha="center", fontsize=8)
ax.set_xticks(range(len(scs)))
ax.set_xticklabels([LABEL[s] for s in scs], fontsize=7.6)
ax.set_ylabel("Cumulative MMD reduction vs. baseline (%)")
ax.set_ylim(0, 108)
ax.yaxis.set_major_locator(plt.MultipleLocator(20))
ax.legend(loc="lower right", fontsize=7)
fig.tight_layout()
fig.savefig(os.path.join(FIG, "Fig8_measured.png"), bbox_inches="tight")
plt.close(fig)
print("Fig8 written:", os.path.getsize(os.path.join(FIG, "Fig8_measured.png")), "bytes")
for s, t in zip(scs, bottom):
    print(f"  {s}: {t:.1f} %")
