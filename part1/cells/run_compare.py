#!/usr/bin/env python3
"""Phases 2 and 3: functional check and all-arc timing for every candidate at unit sizing."""
import csv
import sys
import time

from arcs import all_arcs, describe_state, write_arcs
from candidates import CANDIDATES, candidate_r
from cellgen import config as cfg
from cellgen.bench import run_truth_table

OUT = cfg.PART1 / "simulations" / "timing" / "phase3_unit"
FUNC = cfg.PART1 / "simulations" / "functional" / "phase2_candidates"


def summarise(label, adder, arcs, functional, truth):
    worst_pin = max(arcs, key=lambda a: a["tpd_pin_ps"])
    worst_drv = max(arcs, key=lambda a: a["tpd_drv_ps"])
    hint_state_c0 = 0b00001111  # A = 1111, B = 0000 with C0 in bit 8
    hint = [a for a in arcs if a["pin"] == "c0" and (a["state"] & 0xFF) == hint_state_c0]
    hint_worst = max(hint, key=lambda a: a["tpd_pin_ps"]) if hint else None
    c0_worst = max((a for a in arcs if a["pin"] == "c0"), key=lambda a: a["tpd_pin_ps"])
    row = dict(candidate=label, adder=adder.name, transistors=adder.transistor_count,
               total_width_lambda=adder.total_width_lam, arcs=len(arcs), settled_errors=functional,
               truth_table_errors=truth, worst_pin_ps=round(worst_pin["tpd_pin_ps"], 1),
               worst_pin_arc=f"{worst_pin['pin']} {worst_pin['pin_edge']} to {worst_pin['output']} "
                             f"{worst_pin['out_edge']}, {describe_state(worst_pin['state'])}",
               worst_drv_ps=round(worst_drv["tpd_drv_ps"], 1),
               worst_drv_arc=f"{worst_drv['pin']} {worst_drv['pin_edge']} to {worst_drv['output']} "
                             f"{worst_drv['out_edge']}",
               worst_c0_pin_ps=round(c0_worst["tpd_pin_ps"], 1),
               hint_vector_pin_ps=round(hint_worst["tpd_pin_ps"], 1) if hint_worst else None,
               hint_arc=f"{hint_worst['pin_edge']} to {hint_worst['output']} {hint_worst['out_edge']}" if hint_worst else "")
    return row


def main():
    started = time.time()
    jobs = [(k, f()) for k, f in CANDIDATES.items()]
    jobs += [(f"R/{style}", candidate_r(sum_style=style)) for style in ("tg", "static12", "nand4")]
    only = set(sys.argv[1:])
    rows = []
    for label, adder in jobs:
        if only and label not in only:
            continue
        t0 = time.time()
        tag = label.replace("/", "_")
        truth = run_truth_table(adder, FUNC / tag, cfg.plot_title("1.6", f"{tag}-function"), period=3e-9)
        truth_row = truth[0] if isinstance(truth, tuple) else truth
        arcs, functional = all_arcs(adder, OUT / tag)
        write_arcs(arcs, OUT / tag / "arcs.csv")
        row = summarise(label, adder, arcs, functional, truth_row["errors"])
        rows.append(row)
        print({k: row[k] for k in ("candidate", "transistors", "total_width_lambda", "arcs", "settled_errors",
                                   "truth_table_errors", "worst_pin_ps", "worst_drv_ps", "worst_c0_pin_ps",
                                   "hint_vector_pin_ps")}, f"{time.time() - t0:.0f}s", flush=True)
        print("   worst:", row["worst_pin_arc"], "| hint:", row["hint_arc"], flush=True)
    if not only:
        with open(cfg.PART1 / "results" / "phase3_unit_comparison.csv", "w", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    print(f"done in {time.time() - started:.0f}s")


if __name__ == "__main__":
    main()
