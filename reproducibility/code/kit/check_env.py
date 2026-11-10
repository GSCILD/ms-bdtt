# -*- coding: utf-8 -*-
"""check_env.py -- one-shot readiness check for the confirmatory re-runs.

Verifies everything e1/e2/e3/e4 need and prints the expected GPU budget.
Run this FIRST on the machine that owns the datasets and the GPU.

Usage: python check_env.py
"""
import importlib
import os
import shutil
import subprocess
import sys

KIT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, KIT)

OK, BAD = "OK  ", "FAIL"
lines = []


def check(label, fn):
    try:
        detail = fn()
        lines.append(f"[{OK}] {label}" + (f" — {detail}" if detail else ""))
        return True
    except Exception as e:
        lines.append(f"[{BAD}] {label} — {type(e).__name__}: {str(e)[:140]}")
        return False


def _numpy():
    import numpy
    return f"numpy {numpy.__version__}"


def _scipy():
    import scipy
    return f"scipy {scipy.__version__}"


def _torch():
    import torch
    cuda = torch.cuda.is_available()
    dev = torch.cuda.get_device_name(0) if cuda else "CPU only"
    return f"torch {torch.__version__}, cuda={cuda}, device={dev}"


def _gpu():
    exe = shutil.which("nvidia-smi")
    if not exe:
        raise RuntimeError("nvidia-smi not found")
    out = subprocess.run([exe, "--query-gpu=name,memory.total,driver_version",
                          "--format=csv,noheader"], capture_output=True, text=True, timeout=20)
    return out.stdout.strip().replace("\n", " | ")


def _repo():
    root = os.environ.get("MS_BDTT_ROOT", "")
    if not root:
        raise RuntimeError("MS_BDTT_ROOT is not set")
    if not os.path.isdir(root):
        raise RuntimeError(f"MS_BDTT_ROOT does not exist: {root}")
    return root


def _adapter():
    import adapter
    fn = adapter._find_pipeline()
    if fn is None:
        raise RuntimeError("no run_one() found; edit adapter.py (see its docstring)")
    return f"auto-wired: {fn.__module__}.{fn.__name__}"


def _datasets():
    need = {"XJTU_ROOT": os.environ.get("XJTU_ROOT", ""),
            "SPFD_MANIFEST": os.environ.get("SPFD_MANIFEST", ""),
            "MANIFEST_DIR": os.environ.get("MANIFEST_DIR", "")}
    missing = [k for k, v in need.items() if not v or not os.path.exists(v)]
    if missing:
        raise RuntimeError("missing/not set: " + ", ".join(missing))
    return ", ".join(f"{k} ok" for k in need)


lines.append("=" * 74)
lines.append("MS-BDTT confirmatory re-run readiness check")
lines.append("=" * 74)
check("python >= 3.9", lambda: sys.version.split()[0])
check("numpy", _numpy)
check("scipy", _scipy)
check("torch", _torch)
check("nvidia-smi", _gpu)
check("MS_BDTT_ROOT", _repo)
check("adapter auto-wiring", _adapter)
check("dataset roots", _datasets)

runs = {
    "e1_ten_seed.py":   2 * 10 * 5,     # 2 methods x 10 seeds x 5 scenarios = 100
    "e2_openset_s4.py": 4 * 3,          # 4 methods x 3 runs
    "e3_retention_sweep.py": 5 * 5 * 5, # 5 ratios x 5 runs x 5 scenarios
    "e4_budget_sweep.py":   2 * 6 * 5,  # 2 rules x 6 budgets x 5 runs
}
total = sum(runs.values())
per_run = 4.0  # minutes, RTX 4090 estimate from Table 10 (85 min full pipeline)
lines.append("-" * 74)
lines.append("Expected GPU budget (single RTX 4090, ~%.0f min per full run):" % per_run)
for k, v in runs.items():
    lines.append(f"   {k:<26} {v:>4} runs  ~{v * per_run / 60:>6.1f} h")
lines.append(f"   {'TOTAL':<26} {total:>4} runs  ~{total * per_run / 60:>6.1f} h")
lines.append("   e5/e6/e7/leakage_check are CPU-bound and need no training.")
lines.append("-" * 74)
n_fail = sum(1 for l in lines if l.startswith("[FAIL"))
lines.append("RESULT: " + ("READY" if n_fail == 0 else f"{n_fail} CHECK(S) FAILED"))
lines.append("")

out = os.path.join(KIT, "check_env_report.txt")
with open(out, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("\n".join(lines))
print(f"[saved] {out}")
