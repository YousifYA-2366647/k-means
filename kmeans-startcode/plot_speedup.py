#!/usr/bin/env python3
"""
Plot speedup and efficiency from SLURM output files named
omp_<threads>.slurm.o<jobid>

Usage:
    python plot_speedup.py [directory]      (default: ./output files)

Output:
    speedup.png, efficiency.png
"""

import re
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

# ----------------------------- settings --------------------------------------
IMPL_NAME = "openmp"          # implementation to analyse (first CSV field)
RUNTIME_COL = -1              # runtime is the last CSV column
FILE_RE = re.compile(r"^omp_(\d+)\.slurm\.o\d+$")
DEFAULT_DIR = "./output files"  # folder containing the SLURM output files
# ------------------------------------------------------------------------------


def parse_file(path):
    """Return list of runtimes of IMPL_NAME lines in one SLURM output file."""
    runtimes = []
    with open(path) as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) > 3 and parts[0] == IMPL_NAME:
                try:
                    runtimes.append(float(parts[RUNTIME_COL]))
                except ValueError:
                    pass
    return runtimes


def load_data(directory):
    data = defaultdict(list)  # threads -> runtimes
    for p in sorted(Path(directory).iterdir()):
        m = FILE_RE.match(p.name)
        if not m:
            continue
        threads = int(m.group(1))
        runs = parse_file(p)
        if not runs:
            print(f"Warning: no '{IMPL_NAME}' lines found in {p.name}")
            continue
        data[threads].extend(runs)
    return data


def main():
    directory = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DIR
    if not Path(directory).is_dir():
        sys.exit(f"Error: directory '{directory}' not found.")
    data = load_data(directory)

    if 1 not in data:
        sys.exit("Error: no 1-thread file (omp_1.slurm.o...) found, cannot compute baseline.")

    threads = np.array(sorted(data))
    mean = np.array([np.mean(data[t]) for t in threads])
    std = np.array([np.std(data[t], ddof=1) if len(data[t]) > 1 else 0.0 for t in threads])

    t1, s1 = mean[threads == 1][0], std[threads == 1][0]

    speedup = t1 / mean
    # error propagation for S = T1 / Tp
    speedup_err = speedup * np.sqrt((s1 / t1) ** 2 + (std / mean) ** 2)

    efficiency = speedup / threads
    efficiency_err = speedup_err / threads

    # console summary
    print(f"{'threads':>8} {'runs':>5} {'mean[s]':>10} {'std[s]':>10} {'speedup':>9} {'effic.':>8}")
    for i, t in enumerate(threads):
        print(f"{t:>8} {len(data[t]):>5} {mean[i]:>10.4f} {std[i]:>10.4f} "
              f"{speedup[i]:>9.2f} {efficiency[i]:>8.2f}")

    # ------------------------------ speedup plot ------------------------------
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.errorbar(threads, speedup, yerr=speedup_err, fmt="o-", capsize=5,
                label="Measured speedup")
    ax.plot(threads, threads, "--", color="gray", label="Ideal speedup")
    ax.set_xscale("log", base=2)
    ax.set_yscale("log", base=2)
    ax.set_xticks(threads)
    ax.set_xticklabels(threads)
    ax.set_xlabel("Threads")
    ax.set_ylabel("Speedup (T1 / Tp)")
    ax.set_title("OpenMP speedup")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig("speedup.png", dpi=200)
    plt.close(fig)

    # ---------------------------- efficiency plot -----------------------------
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.errorbar(threads, efficiency, yerr=efficiency_err, fmt="o-", capsize=5,
                label="Measured efficiency")
    ax.axhline(1.0, linestyle="--", color="gray", label="Ideal efficiency")
    ax.set_xscale("log", base=2)
    ax.set_xticks(threads)
    ax.set_xticklabels(threads)
    ax.set_ylim(0, max(1.1, np.max(efficiency + efficiency_err) * 1.05))
    ax.set_xlabel("Threads")
    ax.set_ylabel("Efficiency (speedup / threads)")
    ax.set_title("OpenMP efficiency")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig("efficiency.png", dpi=200)
    plt.close(fig)

    print("\nSaved speedup.png and efficiency.png")


if __name__ == "__main__":
    main()