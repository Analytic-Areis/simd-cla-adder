#!/usr/bin/env python3
"""Size the TSPC flip-flop for least clock-to-Q plus setup at the given load."""
import csv
import sys
from concurrent.futures import ThreadPoolExecutor

from cellgen import config as cfg
from dff import characterise, tspc

LOAD = float(sys.argv[1]) if len(sys.argv) > 1 else 25.0
OPTIONS = {"s1": [0.6, 0.8, 1.0, 1.3, 1.6], "s2": [0.7, 1.0, 1.4, 2.0, 2.8], "s3": [0.7, 1.0, 1.4, 2.0, 2.8],
           "q": [1.0, 1.5, 2.0, 3.0, 4.0, 6.0]}
RESULTS = {}


def score(p):
    key = tuple(sorted(p.items()))
    if key not in RESULTS:
        row = characterise(tspc(p["s1"], p["s2"], p["s3"], p["q"]), load_ff=LOAD)
        row.update(p)
        row["tcq_plus_tsu_ps"] = row["tcq_ps"] + row["tsu_ps"]
        row["course_sum_ps"] = row["tsu_ps"] + row["thold_ps"]
        RESULTS[key] = row
        print({k: float(row[k]) for k in ("s1", "s2", "s3", "q", "tcq_ps", "tsu_ps", "thold_ps", "tcq_plus_tsu_ps")}, flush=True)
    return RESULTS[key]


def main():
    current = dict(s1=1.0, s2=1.0, s3=1.0, q=2.0)
    best = score(current)["tcq_plus_tsu_ps"]
    for _ in range(4):
        changed = False
        for k, values in OPTIONS.items():
            for v in values:
                trial = dict(current, **{k: v})
                val = score(trial)["tcq_plus_tsu_ps"]
                if val < best - 0.5:
                    best, current, changed = val, trial, True
        if not changed:
            break
    rows = sorted(RESULTS.values(), key=lambda r: r["tcq_plus_tsu_ps"])
    with open(cfg.PART1 / "results" / "phase5_dff_sizing.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print("BEST", current, {k: float(rows[0][k]) for k in ("tcq_ps", "tsu_ps", "thold_ps", "tcq_plus_tsu_ps")})


if __name__ == "__main__":
    main()
