#!/usr/bin/env python3
"""Independent check of the separate design in part1_agy. That folder is only read.

part1_agy was removed from the project on 3 Nov 2026, so this script cannot be rerun here.
Its results are in part1/results/agy_comparison/.

Stages:
  static   logic of its netlists at switch level, its junction values, bounding box
  layout   DRC, fresh extraction, and LVS of its layout on a copy, using this project's tools
"""
import csv
import json
import random
import re
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from itertools import product
from pathlib import Path

import numpy as np

from arcs import crossings, euler_walk
from candidates import INPUTS, OUTPUTS, adder_logic
from cellgen import config as cfg
from cellgen.lvs import _num, compare, read_extracted
from cellgen.switchlevel import evaluate
from dff import characterise, tspc
from final_flow import FINAL, build, final_design
from library import inv
from postlayout import ExtractedCell
from registered import REG_INPUTS, REG_OUTPUTS, find_failing_period, registered_top, run_system, state_vec, vector_set
from render_mag import read_mag

SRC = cfg.ROOT / "part1_agy"
WORK = cfg.PART1 / "simulations" / "agy_check"
OUT = cfg.PART1 / "results" / "agy_comparison"
TOP_PORTS = [f"{p}_in" for p in INPUTS] + ["clk"] + [f"{p}_out" for p in OUTPUTS]


def parse_defs(text):
    defs, current = {}, None
    for line in text.splitlines():
        tok = line.split()
        if not tok or tok[0].startswith("*"):
            continue
        low = tok[0].lower()
        if low == ".subckt":
            current = defs.setdefault(tok[1], dict(ports=tok[2:], devices=[], instances=[]))
        elif low == ".ends":
            current = None
        elif current is None:
            continue
        elif tok[0][0] in "mM":
            params = {k.upper(): _num(v) for k, v in (t.split("=") for t in tok[6:] if "=" in t)}
            current["devices"].append(dict(name=tok[0], drain=tok[1], gate=tok[2], source=tok[3], bulk=tok[4],
                                           kind="n" if tok[5].upper() == "CMOSN" else "p", **params))
        elif tok[0][0] in "xX":
            current["instances"].append((tok[0], tok[-1], tok[1:-1]))
    return defs


def flatten(defs, top):
    def expand(name, mapping, path):
        out = []
        for d in defs[name]["devices"]:
            f = dict(d)
            f["name"] = path + d["name"]
            for term in ("drain", "gate", "source", "bulk"):
                f[term] = mapping.get(d[term], path + d[term])
            out.append(f)
        for inst, sub, nets in defs[name]["instances"]:
            actual = [mapping.get(n, path + n) for n in nets]
            out += expand(sub, dict(zip(defs[sub]["ports"], actual)), f"{path}{inst}.")
        return out
    return expand(top, {p: p for p in defs[top]["ports"]}, "")


def stage_static():
    OUT.mkdir(parents=True, exist_ok=True)
    cells = (SRC / "netlist" / "cells.sp").read_text()
    cla = (SRC / "netlist" / "cla4.sp").read_text()
    top = (SRC / "netlist" / "top.sp").read_text()
    defs = parse_defs(cells + "\n" + cla + "\n" + top)
    core = flatten(defs, "CLA4")
    full = flatten(defs, "TOP")
    bad, shorts = 0, 0
    for bits in product([0, 1], repeat=9):
        vec = dict(zip(INPUTS, bits))
        values, sh = evaluate(core, vec)
        shorts += bool(sh)
        want = adder_logic(vec)
        if any(values.get(o) != want[o] for o in OUTPUTS):
            bad += 1
    lengths = sorted({round(d["L"] * 1e9) for d in full})
    width_core = sum(d["W"] for d in core) * 1e6
    width_full = sum(d["W"] for d in full) * 1e6
    bodies_ok = all((d["bulk"] == "gnd") == (d["kind"] == "n") for d in full)
    mag_dir = SRC / "layout"
    rects = read_mag("TOP", mag_dir)
    xs = [r[0] for v in rects.values() for r in v] + [r[2] for v in rects.values() for r in v]
    ys = [r[1] for v in rects.values() for r in v] + [r[3] for v in rects.values() for r in v]
    w, h = max(xs) - min(xs), max(ys) - min(ys)
    result = dict(core_transistors=len(core), full_transistors=len(full), logic_vectors=512, logic_errors=bad, logic_shorts=shorts,
                  channel_lengths_nm=lengths, bodies_correct=bodies_ok, core_width_um=round(width_core, 1), full_width_um=round(width_full, 1),
                  top_width_lambda=w, top_height_lambda=h, top_area_um2=round(w * h * 0.09 ** 2, 1))
    (OUT / "static.json").write_text(json.dumps(result, indent=1))
    print(result)


def stage_layout():
    """DRC and fresh flat extraction on a copy, then full LVS against the schematic."""
    OUT.mkdir(parents=True, exist_ok=True)
    work = WORK / "layout"
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    for f in (SRC / "layout").glob("*.mag"):
        shutil.copy(f, work)
    shutil.copy(SRC / "layout" / "SCN6M_DEEP.09.tech27", work)
    body = """load TOP
select top cell
expand
drc euclidean on
drc style drc
drc check
drc catchup
set why [drc listall why]
set total 0
foreach {m b} $why { incr total [llength $b]; puts "DRC_ERR $m : [lrange $b 0 2]" }
puts "DRC_COUNT $total"
extract do local
extract all
ext2spice lvs
ext2spice cthresh 0
ext2spice rthresh 0
ext2spice format ngspice
ext2spice hierarchy off
ext2spice subcircuit top on
ext2spice -o TOP_fresh.spice
puts DONE
quit -noprompt
"""
    (work / "check.tcl").write_text(body)
    res = subprocess.run(["magic", "-dnull", "-noconsole", "-T", "SCN6M_DEEP.09.tech27", "check.tcl"], cwd=work,
                         capture_output=True, text=True, timeout=1800)
    (work / "check.log").write_text(res.stdout + res.stderr)
    count = re.search(r"DRC_COUNT (\d+)", res.stdout)
    errors = [l for l in res.stdout.splitlines() if l.startswith("DRC_ERR")][:6]
    fresh = work / "TOP_fresh.spice"
    defs = parse_defs((SRC / "netlist" / "cells.sp").read_text() + "\n" + (SRC / "netlist" / "top.sp").read_text())
    sch = [dict(kind=d["kind"], gate=d["gate"].lower(), a=d["drain"].lower(), b=d["source"].lower(), w=d["W"], l=d["L"])
           for d in flatten(defs, "TOP")]
    ports = set(TOP_PORTS) | {"vdd", "gnd"}
    out = dict(drc=int(count.group(1)) if count else -1, drc_first=errors)
    for name, path in (("fresh_extraction", fresh), ("their_top_ext", SRC / "layout" / "extracted" / "top_ext.sp")):
        text = path.read_text()
        ext = read_extracted(text)
        ok, message = compare(ext, sch, ports)
        out[name] = dict(devices=len(ext), capacitors=len(re.findall(r"(?m)^C", text)), cap_total_ff=round(_cap_total(text), 1), lvs=ok,
                         message=message, nets_labelled=sorted(set(TOP_PORTS) - {n for d in ext for n in (d["gate"], d["a"], d["b"])})[:12])
    (OUT / "layout_check.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


def _cap_total(text):
    total = 0.0
    for m in re.finditer(r"(?m)^C\S+\s+\S+\s+\S+\s+(\S+)", text):
        v = m.group(1).lower()
        if v.endswith("f"):
            total += float(v[:-1]) if not v.endswith("ff") else float(v[:-2])
        elif v.endswith("p"):
            total += float(v[:-1]) * 1e3
        else:
            total += float(v) * 1e15
    return total


class TextCell:
    """A registered circuit given as SPICE text, behind the port names the bench expects."""

    def __init__(self, name, body, inner, inner_ports=None):
        self.name, self.body, self.inner = name, body, inner
        self.ports = REG_INPUTS + REG_OUTPUTS + ["vdd", "gnd"]
        self.inner_ports = inner_ports or self.ports
        self.transistors = len(re.findall(r"(?mi)^M", body))
        self.transistor_count = self.transistors
        self.total_width_lam = 0

    def spice(self):
        return (self.body + f"\n.subckt {self.name} {' '.join(self.ports)}\nX0 {' '.join(self.inner_ports)} {self.inner}\n.ends\n")


NODES = INPUTS + OUTPUTS
INVL_LINES = ("M{n}p {y} {a} vdd vdd CMOSP W=1.8e-06 L=1.8e-07 AS=9.72e-13 PS=4.68e-06 AD=9.72e-13 PD=4.68e-06\n"
              "M{n}n {y} {a} gnd gnd CMOSN W=9.0e-07 L=1.8e-07 AS=4.86e-13 PS=2.88e-06 AD=4.86e-13 PD=2.88e-06\n")


def design(name):
    """Returns (circuit, {logical net: probe name}). Every design carries the 20L/10L inverter on S and C4 nets."""
    if name == "agy_post":
        text = (SRC / "layout" / "extracted" / "top_ext.sp").read_text().replace("/", "__")
        cell = TextCell("agy_post_w", text, "TOP")
        return cell, {n: f"x0.x0.{n}" for n in NODES}
    if name == "agy_sch":
        text = (SRC / "netlist" / "cells.sp").read_text() + "\n" + (SRC / "netlist" / "top.sp").read_text()
        cell = TextCell("agy_sch_w", text, "TOP")
        return cell, {n: f"x0.x0.{n}" for n in NODES}
    if name in ("mine_post", "mine_post_asis"):
        asis = name.endswith("asis")
        text = (cfg.PART1 / "extraction" / "registered_extracted.spice").read_text()
        text = re.sub(r"\bnfet\b", "CMOSN", text)
        text = re.sub(r"\bpfet\b", "CMOSP", text)
        text = re.sub(r"(?im)^\.global.*$", "", text).replace("/", "__")
        joined = re.sub(r"\n\+", " ", text)
        match = re.search(r"(?im)^\.subckt\s+(\S+)\s*(.*)$", joined)
        inner, inner_ports = match.group(1), [p.lower() for p in match.group(2).split()]
        # net names come from device terminals only: capacitors are also called C0, C4, ...
        tokens = set()
        for line in joined.splitlines():
            if line[:1] in "mM":
                tokens.update(line.lower().split()[1:5])
        probes = {}
        for n in NODES:
            options = sorted(t for t in tokens if t == n or t.endswith(f"__{n}"))
            if len(options) != 1:
                raise ValueError(f"net {n}: expected one extracted net, found {options}")
            probes[n] = options[0]
        loads = "".join(INVL_LINES.format(n=f"ld{k}", y=f"ldout{k}", a=probes[o]) for k, o in enumerate(OUTPUTS))
        if asis:
            loads = ""
        pos = text.lower().rfind(".ends")
        text = text[:pos] + loads + text[pos:]
        cell = TextCell("mine_post_w", text, inner, inner_ports)
        # ports keep their own name in the wrapper, so map them in inner order
        cell.spice = lambda: text + (f"\n.subckt mine_post_w {' '.join(cell.ports)}\nX0 {' '.join(inner_ports)} {inner}\n.ends\n")
        return cell, {n: f"x0.x0.{probes[n]}" for n in NODES}
    if name == "mine_sch":
        label, sizes, flips, tag = final_design()
        p = json.loads((FINAL / "dff.json").read_text())["params"]
        adder = build(label, sizes, flips, "cla_final")
        top = registered_top(adder, tspc(p["s1"], p["s2"], p["s3"], p["q"]), "mine_sch_w")
        load = inv(1.0, "invl_load")
        top.instances = list(top.instances) + [(f"ld{k}", load, {"a": o, "y": f"ldout{k}"}) for k, o in enumerate(OUTPUTS)]
        return top, {n: f"x0.{n}" for n in NODES}
    raise ValueError(name)


def walk_segment(cell, probes, states, work, tag, period=2.0e-9):
    """Registered circuit, one input change per clock. Delay runs from the first changing flip-flop Q, and from
    the buffered clock, to the last crossing of each output whose value changes."""
    extra = [probes[n] for n in NODES]

    def measure(t, data, col, edges):
        arcs = []
        for k in range(1, len(states)):
            changed = [i for i in range(9) if ((states[k] ^ states[k - 1]) >> i) & 1]
            if not changed:
                continue
            lo, hi = np.searchsorted(t, [edges[k] - 60e-12, edges[k + 1] - 60e-12])
            tw = t[lo:hi + 1]
            launch = {}
            for i in changed:
                c = crossings(tw, data[lo:hi + 1, col[f"v({probes[INPUTS[i]]})"]])
                if len(c):
                    launch[INPUTS[i]] = c[0]
            ck = crossings(tw, data[lo:hi + 1, col["v(clk)"]])
            if not launch or not len(ck):
                continue
            pin = min(launch, key=launch.get)
            old, new = state_vec(states[k - 1]), state_vec(states[k])
            want_old, want_new = adder_logic(old), adder_logic(new)
            for o in OUTPUTS:
                if want_old[o] == want_new[o]:
                    continue
                c = crossings(tw, data[lo:hi + 1, col[f"v({probes[o]})"]])
                if len(c):
                    arcs.append(dict(pin=pin, pin_edge="rise" if new[pin] else "fall", state=states[k - 1], next_state=states[k], output=o,
                                     out_edge="rise" if want_new[o] else "fall", inputs_changed=len(changed),
                                     tpd_q_ps=(c[-1] - launch[pin]) * 1e12, tcq_ps=(launch[pin] - ck[0]) * 1e12,
                                     clk_to_out_ps=(c[-1] - ck[0]) * 1e12))
        return arcs

    return run_system(cell, period, states, work, tag, extra_probes=extra, on_wave=measure, tstep="10p")


def _sweep(name, label, sequence, stride=1):
    cell, probes = design(name)
    size = 120
    jobs = [(sequence[s:s + size + 1], s // size) for s in range(0, len(sequence) - 1, size)][:: int(stride)]
    work = WORK / label / name
    work.mkdir(parents=True, exist_ok=True)
    start = time.time()
    with ThreadPoolExecutor(6) as ex:
        results = list(ex.map(lambda job: walk_segment(cell, probes, job[0], work, f"s{job[1]:03d}"), jobs))
    arcs = [a for r in results for a in r.get("measured", [])]
    errors = sum(max(0, r.get("errors", 0)) for r in results)
    bad = sum(1 for r in results if r.get("errors", 0) < 0)
    print(name, label, "segments", len(jobs), "arcs", len(arcs), "wrong samples", errors, "failed runs", bad, f"{time.time() - start:.0f}s", flush=True)
    if bad or not arcs:
        raise RuntimeError(f"{name} {label}: {bad} failed runs: {[r.get('note') for r in results if r.get('errors', 0) < 0][:1]}")
    with open(OUT / f"{label}_{name}.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(arcs[0].keys()))
        writer.writeheader()
        writer.writerows(arcs)
    worst = max(arcs, key=lambda a: a["tpd_q_ps"])
    worst_clk = max(arcs, key=lambda a: a["clk_to_out_ps"])
    per = {}
    for o in OUTPUTS:
        for edge in ("rise", "fall"):
            sel = [a["tpd_q_ps"] for a in arcs if a["output"] == o and a["out_edge"] == edge]
            per[f"{o}_{edge}"] = round(max(sel), 2) if sel else None
    hint = {f"{a['pin_edge']}:{a['output']}:{a['out_edge']}": round(a["tpd_q_ps"], 2) for a in arcs
            if a["inputs_changed"] == 1 and a["pin"] == "c0" and (a["state"] & 0xFF) == 0b1111}
    out = dict(design=name, sweep=label, segments=len(jobs), stride=int(stride), arcs=len(arcs), transitions=len({(a["state"], a["next_state"]) for a in arcs}),
               wrong_samples=errors, failed_runs=bad, tpd_max_from_q_ps=round(worst["tpd_q_ps"], 2), worst=worst,
               worst_clk_to_out_ps=round(worst_clk["clk_to_out_ps"], 2), worst_tcq_ps=round(max(a["tcq_ps"] for a in arcs), 2),
               per_output=per, hint=hint, hint_worst_ps=max(hint.values()) if hint else None)
    (OUT / f"{label}_{name}.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps({k: v for k, v in out.items() if k not in ("per_output", "hint")}, default=float), flush=True)
    return out


def stage_walk(name, stride="1"):
    """All 4608 single-input transitions, launched by the design's own flip-flops. Stride above 1 samples for timing."""
    return _sweep(name, "walk", euler_walk(), int(stride))


def stage_random(name, count="6000"):
    """Same random multi-input sequence on every design."""
    rng = random.Random(2025102061)
    return _sweep(name, "random", [rng.randrange(512) for _ in range(int(count) + 1)])


def worst_pairs(count=30):
    """The slowest transitions by clock-to-output of both designs, as (from, to) state pairs."""
    pairs = []
    for name in ("agy_post", "mine_post"):
        rows = sorted(csv.DictReader(open(OUT / f"walk_{name}.csv")), key=lambda r: -float(r["clk_to_out_ps"]))
        seen = []
        for r in rows:
            pair = (int(r["state"]), int(r["next_state"]))
            if pair not in seen:
                seen.append(pair)
            if len(seen) == count:
                break
        pairs += seen
    return pairs


def common_vectors():
    return vector_set(worst_pairs(), count=200, seed=7)


def stage_fmax(name):
    """Shortest working period on the common vector set, then a check that every longer period tried also works."""
    cell, _ = design(name)
    states = common_vectors()
    work = WORK / "fmax" / name
    limit, good, history = find_failing_period(cell, states, work, name, high=1.6e-9, low=0.5e-9, resolution=2e-12)
    checks = {}
    with ThreadPoolExecutor(5) as ex:
        margins = (2, 5, 10, 20, 50, 100)
        runs = ex.map(lambda m: run_system(cell, limit + m * 1e-12, states, work, f"{name}_check{m}"), margins)
        for m, r in zip(margins, runs):
            checks[m] = r["errors"]
    below = run_system(cell, limit - 2e-12, states, work, f"{name}_below")
    out = dict(design=name, vectors=len(states), T_min_ps=round(limit * 1e12, 1), f_ghz=round(1e-9 / limit, 3),
               errors_above_ps=checks, errors_2ps_below=below["errors"], first_error_below=below.get("note"), history=[(h["period_ps"], h["errors"]) for h in history])
    (OUT / f"fmax_{name}.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({k: v for k, v in out.items() if k != "history"}), flush=True)


POWER_SETS = dict(random=lambda: vector_set((), count=200, seed=7)[4:], hint=lambda: [0b1111 | ((k % 2) << 8) for k in range(60)],
                  idle=lambda: [0b1111 | (1 << 8)] * 60)


def stage_power(name, *periods_ps):
    """Supply of the circuit under test only. Bench drivers, clock buffers and Q load inverters use their own source."""
    cell, _ = design(name)
    work = WORK / "power" / name
    rows = []
    jobs = [(float(T), pat) for T in periods_ps for pat in POWER_SETS]
    with ThreadPoolExecutor(6) as ex:
        results = ex.map(lambda j: run_system(cell, j[0] * 1e-12, POWER_SETS[j[1]](), work, f"p{int(j[0])}_{j[1]}"), jobs)
        for (T, pat), r in zip(jobs, results):
            rows.append(dict(design=name, T_ps=T, pattern=pat, errors=r["errors"], power_uw=round(r["pavg_w"] * 1e6, 1) if r["errors"] >= 0 else None))
    (OUT / f"power_{name}.json").write_text(json.dumps(rows, indent=1))
    print(json.dumps(rows), flush=True)


def stage_dff(name, *loads_ff):
    if name == "agy":
        text = (SRC / "layout" / "extracted" / "cells_ext.sp").read_text()
        match = re.search(r"(?ims)^\.subckt DFF d clk q vdd gnd\n.*?^\.ends", text)
        cell = TextCell("agy_dff_ext", "", "")
        body = match.group(0).replace("/", "__").replace(".subckt DFF", ".subckt agy_dff_ext", 1)
        cell.spice = lambda: body + "\n"
    else:
        tspc_name = tspc(*[json.loads((FINAL / "dff.json").read_text())["params"][k] for k in ("s1", "s2", "s3", "q")]).name
        cell = ExtractedCell(cfg.PART1 / "layout" / "individual_blocks" / tspc_name / f"{tspc_name}.spice", "mine_dff_ext", ["d", "clk"], ["q"])
        cell.name = "mine_dff_ext"
    if name == "agy":
        cell.transistor_count, cell.total_width_lam = 13, 0
    rows = [characterise(cell, load_ff=float(load)) for load in loads_ff]
    (OUT / f"dff_{name}.json").write_text(json.dumps(rows, indent=1))
    print(json.dumps(rows), flush=True)


def stage_area():
    """Drawn extent without MAGIC's checkpaint bookkeeping layer, by one method for both layouts."""
    out = {}
    for label, cell, folder in (("agy", "TOP", SRC / "layout"), ("mine", "reg_final_top", cfg.PART1 / "layout" / "integrated" / "registered")):
        rects = read_mag(cell, folder)
        keep = [r for layer, v in rects.items() if layer != "checkpaint" for r in v]
        w = max(r[2] for r in keep) - min(r[0] for r in keep)
        h = max(r[3] for r in keep) - min(r[1] for r in keep)
        out[label] = dict(w_lambda=w, h_lambda=h, area_um2=round(w * h * 0.09 ** 2, 1), aspect=round(max(w, h) / min(w, h), 2))
    (OUT / "area.json").write_text(json.dumps(out, indent=1))
    print(out, flush=True)


if __name__ == "__main__":
    globals()[f"stage_{sys.argv[1]}"](*sys.argv[2:])
