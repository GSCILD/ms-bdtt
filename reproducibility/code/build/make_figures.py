# -*- coding: utf-8 -*-
"""Regenerate Fig. 5 and Fig. 10 from the measured supplemental data
(MS-BDTT.xlsx). Journal style: Times New Roman, colourblind-safe, hatched
markers, no top/right spines, greyscale-legible."""
import json, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

KIT = r"D:\006-SCI SSCI实验室-\2026年投稿\1-0913-science report\学术图0913\1110\reproducibility_kit"
RES = os.path.join(KIT, "results")
FIG = os.path.join(KIT, "figs")
os.makedirs(FIG, exist_ok=True)

e3 = json.load(open(os.path.join(RES, "e3_retention.json"), encoding="utf-8"))["results"]
e4 = json.load(open(os.path.join(RES, "e4_budget.json"), encoding="utf-8"))["results"]

plt.rcParams.update({
    "font.family": "Times New Roman", "font.size": 8.5,
    "axes.linewidth": 0.8, "axes.labelsize": 8.5, "axes.titlesize": 8.5,
    "xtick.labelsize": 8, "ytick.labelsize": 8, "legend.fontsize": 7.6,
    "legend.frameon": False, "figure.dpi": 300, "savefig.dpi": 300,
    "axes.spines.top": False, "axes.spines.right": False,
})
BLUE, ORANGE, GREY = "#1f4e79", "#c55a11", "#808080"
PCT = ["100%", "80%", "63%", "40%", "20%"]
X = [100, 80, 63, 40, 20]

# ---------------------------------------------------------------- Fig. 5 ----
fig, ax = plt.subplots(1, 3, figsize=(7.2, 2.45))
a = ax[0]
macro = [e3[k]["macro_avg"] for k in PCT]
msd = [e3[k]["macro_sd"] for k in PCT]
s5 = [e3[k]["s5_oa"] for k in PCT]
s5sd = [e3[k]["s5_sd"] for k in PCT]
a.errorbar(X, macro, yerr=msd, color=BLUE, marker="o", mfc="white", mew=1.1,
           capsize=2.5, lw=1.3, ms=4.2, label="Five-scenario macro-average")
a.errorbar(X, s5, yerr=s5sd, color=ORANGE, marker="s", mfc="white", mew=1.1,
           capsize=2.5, lw=1.3, ms=4.0, ls="--", label="S5 (unlabelled target)")
a.axvline(63, color=GREY, lw=0.9, ls=":")
a.text(63, 64.4, "37th-percentile threshold", ha="center", va="bottom",
       fontsize=7, color=GREY)
a.set_ylim(64.2, 87.5)
a.annotate(f"{macro[2]:.1f} %", (63, macro[2]), textcoords="offset points",
           xytext=(6, 6), fontsize=7.4, color=BLUE)
a.set_xlabel("Bridge samples retained (%)")
a.set_ylabel("Overall accuracy (%)")
a.set_title("(a) Measured retention sweep")
a.set_xticks(X)
a.invert_xaxis()
a.yaxis.set_major_locator(MultipleLocator(2))
a.legend(loc="lower left", fontsize=7)

b = ax[1]
mmd = [e3[k]["post_suppression_mmd2"] for k in PCT]
b.plot(X, mmd, color=BLUE, marker="D", mfc="white", mew=1.1, lw=1.3, ms=4.2)
b.axvline(63, color=GREY, lw=0.9, ls=":")
for xi, yi in zip(X, mmd):
    b.annotate(f"{yi:.3f}", (xi, yi), textcoords="offset points", xytext=(0, 6),
               ha="center", fontsize=7)
b.set_xlabel("Bridge samples retained (%)")
b.set_ylabel("Post-suppression MMD$^2$")
b.set_title("(b) Domain gap after suppression")
b.set_xticks(X)
b.invert_xaxis()

c = ax[2]
labels = ["Full\nMS-BDTT", "w/o attention"]
avg = [84.9, 82.3]
s5v = [76.0, 72.1]
xp = [0, 1]
c.bar([i - 0.19 for i in xp], avg, width=0.34, color=BLUE, hatch="//", edgecolor="black",
      linewidth=0.6, label="Avg. (S1/S3/S5)")
c.bar([i + 0.19 for i in xp], s5v, width=0.34, color=ORANGE, hatch="..", edgecolor="black",
      linewidth=0.6, label="S5")
for i, (av, sv) in enumerate(zip(avg, s5v)):
    c.text(i - 0.19, av + 0.5, f"{av:.1f}", ha="center", fontsize=7.4)
    c.text(i + 0.19, sv + 0.5, f"{sv:.1f}", ha="center", fontsize=7.4)
c.set_xticks(xp)
c.set_xticklabels(labels)
c.set_ylabel("Overall accuracy (%)")
c.set_title("(c) Ablation of the attention module")
c.set_ylim(60, 92)
c.legend(loc="upper right", fontsize=7)
fig.tight_layout()
fig.savefig(os.path.join(FIG, "Fig5_measured.png"), bbox_inches="tight")
plt.close(fig)

# --------------------------------------------------------------- Fig. 10 ----
fig, ax = plt.subplots(figsize=(4.4, 2.9))
uni = e4["uniform"]["curve"]
dem = e4["demand"]["curve"]
usd = e4["uniform"]["sd"]
dsd = e4["demand"]["sd"]
ns = sorted(int(k) for k in uni)
ax.errorbar(ns, [uni[str(n)] for n in ns], yerr=[usd[str(n)] for n in ns], color=ORANGE,
            marker="s", mfc="white", mew=1.1, capsize=2.5, lw=1.3, ms=4.0,
            label="Uniform grid")
ax.errorbar(ns, [dem[str(n)] for n in ns], yerr=[dsd[str(n)] for n in ns], color=BLUE,
            marker="o", mfc="white", mew=1.1, capsize=2.5, lw=1.3, ms=4.2,
            label="Demand-guided (Eq. 5)")
ax.axhline(75.5, color=GREY, lw=0.9, ls=":")
ax.text(122, 75.5, " 75.5 % = 90 % of the\n demand-guided full budget",
        va="center", fontsize=6.8, color=GREY)
ax.annotate("60", (60, dem["60"]), textcoords="offset points", xytext=(-12, 4), fontsize=7.2, color=BLUE)
ax.annotate("80", (80, uni["80"]), textcoords="offset points", xytext=(-2, 6), fontsize=7.2, color=ORANGE)
ax.set_xlabel("Bridge samples per operating condition")
ax.set_ylabel("Five-scenario macro-average accuracy (%)")
ax.set_title("Measured budget sweep (5 runs per point)")
ax.set_xticks(ns)
ax.set_xlim(14, 132)
ax.yaxis.set_major_locator(MultipleLocator(5))
ax.legend(loc="lower right")
fig.tight_layout()
fig.savefig(os.path.join(FIG, "Fig10_measured.png"), bbox_inches="tight")
plt.close(fig)

print("figures written to", FIG)
for f in ["Fig5_measured.png", "Fig10_measured.png"]:
    print(" ", f, os.path.getsize(os.path.join(FIG, f)), "bytes")
