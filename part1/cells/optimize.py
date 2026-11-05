#!/usr/bin/env python3
"""Sizing and input-order search for one candidate. Every iteration is logged.

Objective: a soft maximum of tpd_drv (measured from the driver input, so a design pays
for its input capacitance) over a working set of critical arcs. Each accepted result is
then checked against all 4608 transitions; any arc the working set missed is added.

Usage: optimize.py LABEL
"""
import csv
import json
import math
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from arcs import INPUTS, all_arcs, describe_state, run_segment, write_arcs
from candidates import candidate_c2, candidate_c4, candidate_r
from cellgen import config as cfg

ROOT = cfg.PART1 / "simulations" / "optimisation"
BITS = range(4)
FRONT = [f"{k}{i}" for k in ("nand", "nor", "aoi", "oai") for i in BITS]
SUM_AOI = [f"{k}{i}" for k in ("xor", "xinv") for i in BITS]
SUM_TG = [f"{k}{i}" for k in ("xor", "xinv", "xtg") for i in BITS]

CONFIGS = {
    "R_aoi22": (candidate_r, "aoi22", FRONT + SUM_AOI + ["invc0", "c1", "c2", "c3", "c4m", "invc4"], ["c1", "c2", "c3"]),
    "R_tg": (candidate_r, "tg", FRONT + SUM_TG + ["invc0", "c1", "c2", "c3", "c4m", "invc4"], ["c1", "c2", "c3"]),
    "C2_tg": (candidate_c2, "tg", FRONT + SUM_TG + ["invc0", "c1", "c2", "c3", "c4"], ["c1", "c2", "c3", "c4"]),
    "C4_aoi22": (candidate_c4, "aoi22", FRONT + SUM_AOI + ["invc0", "g10", "t10", "g32", "t32", "ig2", "it2", "g30", "t30",
                 "g20", "t20", "ig10", "it10", "c1", "c2", "c3", "c4g"], ["g10", "g32", "g30", "g20", "c1", "c2", "c3", "c4g"]),
    "C4_tg": (candidate_c4, "tg", FRONT + SUM_TG + ["invc0", "g10", "t10", "g32", "t32", "ig2", "it2", "g30", "t30",
              "g20", "t20", "ig10", "it10", "c1", "c2", "c3", "c4g"], ["g10", "g32", "g30", "g20", "c1", "c2", "c3", "c4g"]),
}
STEP = 1.25
MIN_DRIVE, MAX_DRIVE = 0.3, 12.0
P_NORM = 12
SOFT_PERIOD = 1.6e-9


NET_CAPS = {}   # wire load from an extracted layout, when optimising for post-layout delay


def make(label, sizes, flips, tag="t"):
    build, style, _, _ = CONFIGS[label]
    adder = build(sizes=sizes, sum_style=style, flips={k: tuple(v) for k, v in flips.items()}, name=f"cla_{label}_{tag}")
    if NET_CAPS:
        adder.net_caps = dict(NET_CAPS)
    return adder


def working_states(arcs_list):
    """Each arc becomes two vectors: the state before it, then the toggled state."""
    states = []
    for arc in arcs_list:
        pin_index = INPUTS.index(arc["pin"])
        states += [arc["state"], arc["state"] ^ (1 << pin_index)]
    return states


def evaluate(label, sizes, flips, states, work_dir):
    adder = make(label, sizes, flips)
    with tempfile.TemporaryDirectory(dir=work_dir) as d:
        arcs, functional = run_segment(adder, states, Path(d) / "s.cir", period=SOFT_PERIOD, reltol="1e-3")
    if functional:
        return math.inf, math.inf, None, arcs
    values = [a["tpd_drv_ps"] for a in arcs]
    soft = sum(v ** P_NORM for v in values) ** (1 / P_NORM)
    worst = max(arcs, key=lambda a: a["tpd_drv_ps"])
    return soft, worst["tpd_drv_ps"], worst, arcs


def select_arcs(arcs, count=200):
    """Worst arc in each (input, edge, output, edge) class, then the slowest classes."""
    best = {}
    for a in arcs:
        key = (a["pin"], a["pin_edge"], a["output"], a["out_edge"])
        if key not in best or a["tpd_drv_ps"] > best[key]["tpd_drv_ps"]:
            best[key] = a
    return sorted(best.values(), key=lambda a: -a["tpd_drv_ps"])[:count]


def main():
    label = sys.argv[1]
    workers = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    # optional: start point, wire-load file and output folder, for layout-aware refinement
    start_file = Path(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3] else None
    caps_file = Path(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[4] else None
    out_name = sys.argv[5] if len(sys.argv) > 5 else label
    if caps_file:
        NET_CAPS.update(json.loads(caps_file.read_text()))
    base_label = label
    build, style, params, flip_keys = CONFIGS[label]
    out = ROOT / out_name
    out.mkdir(parents=True, exist_ok=True)
    (out / "work").mkdir(exist_ok=True)
    sizes = {k: 1.0 for k in params}
    flips = {k: [False, False] for k in flip_keys}
    if start_file:
        start = json.loads(start_file.read_text())
        sizes, flips = start["sizes"], start["flips"]
    log = open(out / "log.csv", "w", newline="")
    writer = csv.DictWriter(log, fieldnames=["iteration", "round", "soft_ps", "worst_working_ps", "total_width_lambda",
                                             "transistors", "changes", "critical_arc", "elapsed_s"])
    writer.writeheader()
    t0 = time.time()
    arcs, functional = all_arcs(make(label, sizes, flips), out / "work", workers)
    full_worst = max(a["tpd_drv_ps"] for a in arcs)
    print(label, "start, full worst", round(full_worst, 1), "functional errors", functional, flush=True)
    working = select_arcs(arcs)
    iteration = 0
    for rnd in range(3):
        states = working_states(working)
        soft, worst, crit, arcs_now = evaluate(label, sizes, flips, states, out / "work")
        for _ in range(30):
            # moves are screened on the slowest classes, then confirmed on every class
            fast_states = working_states(select_arcs(arcs_now, 36))
            base_fast = evaluate(label, sizes, flips, fast_states, out / "work")[0]
            moves = []
            for k in params:
                for factor in (STEP, 1 / STEP):
                    new = min(MAX_DRIVE, max(MIN_DRIVE, round(sizes[k] * factor, 2)))
                    if new != sizes[k]:
                        moves.append(("size", k, new))
            for k in flip_keys:
                for which in (0, 1):
                    moves.append(("flip", k, which))

            def apply(base_s, base_f, picks):
                s2, f2 = dict(base_s), {k: list(v) for k, v in base_f.items()}
                for mv in picks:
                    if mv[0] == "size":
                        s2[mv[1]] = mv[2]
                    else:
                        f2[mv[1]][mv[2]] = not f2[mv[1]][mv[2]]
                return s2, f2

            def attempt(move):
                s2, f2 = apply(sizes, flips, [move])
                try:
                    return (evaluate(label, s2, f2, fast_states, out / "work")[0], move)
                except RuntimeError:
                    return (math.inf, move)

            with ThreadPoolExecutor(workers) as ex:
                results = sorted(ex.map(attempt, moves), key=lambda r: r[0])
            improving = [r for r in results if r[0] < base_fast * 0.9995]
            if not improving:
                break
            chosen, used = [], set()
            for r in improving:
                if r[1][1] not in used:
                    chosen.append(r[1])
                    used.add(r[1][1])
                if len(chosen) == 4:
                    break
            accepted = None
            for picks in (chosen, chosen[:2], chosen[:1]):
                s2, f2 = apply(sizes, flips, picks)
                soft2, worst2, crit2, arcs2 = evaluate(label, s2, f2, states, out / "work")
                if soft2 < soft * 0.9995:
                    accepted = picks
                    sizes, flips, soft, worst, crit, arcs_now = s2, f2, soft2, worst2, crit2, arcs2
                    break
            if accepted is None:
                break
            iteration += 1
            adder = make(label, sizes, flips)
            writer.writerow(dict(iteration=iteration, round=rnd, soft_ps=round(soft, 2), worst_working_ps=round(worst, 2),
                                 total_width_lambda=adder.total_width_lam, transistors=adder.transistor_count,
                                 changes="; ".join(f"{m[1]} {m[0]}={m[2]}" for m in accepted),
                                 critical_arc=f"{crit['pin']} {crit['pin_edge']} to {crit['output']} {crit['out_edge']}, "
                                              f"{describe_state(crit['state'])}",
                                 elapsed_s=round(time.time() - t0)))
            log.flush()
            print(label, "iter", iteration, "worst", round(worst, 1), "width", adder.total_width_lam,
                  f"{time.time() - t0:.0f}s", flush=True)
            (out / "best.json").write_text(json.dumps(dict(sizes=sizes, flips=flips), indent=1))
        # full check of the result
        arcs, functional = all_arcs(make(label, sizes, flips), out / "work", workers)
        write_arcs(arcs, out / "arcs.csv")
        full = max(arcs, key=lambda a: a["tpd_drv_ps"])
        print(label, "round", rnd, "full worst", round(full["tpd_drv_ps"], 1), "pin", round(max(a["tpd_pin_ps"] for a in arcs), 1),
              "functional errors", functional, flush=True)
        # the slowest input state of a class can change as sizes change, so the working set is
        # rebuilt from the full check whenever it has fallen behind
        if full["tpd_drv_ps"] <= worst + 3:
            break
        working = select_arcs(arcs)
    write_arcs(arcs, out / "arcs.csv")
    (out / "summary.json").write_text(json.dumps(dict(
        label=out_name, config=label, sizes=sizes, flips=flips, transistors=make(label, sizes, flips).transistor_count,
        total_width_lambda=make(label, sizes, flips).total_width_lam, functional_errors=functional,
        worst_drv_ps=max(a["tpd_drv_ps"] for a in arcs), worst_pin_ps=max(a["tpd_pin_ps"] for a in arcs),
        critical=str(full), elapsed_s=round(time.time() - t0)), indent=1))
    print(label, "DONE", flush=True)


if __name__ == "__main__":
    main()
