#!/usr/bin/env python3
"""Part II: SIMD-reconfigurable 8-bit adder from two Part I 4-bit CLAs.

  simd_mode = 0: CLA0's carry-out feeds CLA1's carry-in, one 8-bit add
  simd_mode = 1: the inter-block carry is forced to 0, two 4-bit adds

The baseline is the same two CLAs wired directly, C4 of CLA0 into C0 of CLA1, with no gating.
Both use the final Part I adder with its final sizes, and are laid out by the same Part I flow,
so the only difference between them is the gating cell.

Stages, each run on its own:
  netlists   hierarchical and flat netlists, gate drawing
  gate       size the gating cell on the schematic, then its own layout: DRC, LVS, extraction
  layout     layout of the SIMD adder and the baseline: DRC, extraction, LVS
  search     guided worst-case search, schematic or post-layout:  search <design> <mode> <sch|post>
  penalty    worst-case vector A=FF B=00 Cin toggling: Cin to S7, both designs, both views
  power      average power over 10 cycles at fmax, plus a 200-vector check
  summary    tables in results/
"""
import csv
import json
import os
import random
import re
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

P2 = Path(__file__).resolve().parents[1]
P1_CELLS = P2.parent / "part1" / "cells"
sys.path.insert(0, str(P1_CELLS))

import numpy as np

from arcs import TB_CELLS, crossings, euler_walk
from cellgen import Block, config as cfg
from cellgen.bench import pwl_lines
from cellgen.schematic import draw
from cellgen.sim import run_ngspice
from final_flow import build, final_design
from library import inv, nand
from postlayout import ExtractedCell, net_capacitance
from run_layout_cells import layout_cell
from top import CARRY_ORDER, assemble

RESULTS = P2 / "results"
LAYOUT = P2 / "layout"
SIM = P2 / "simulations"
MODEL = P2.parent / "part1" / "spice" / "models" / "TSMC_180nm.txt"
PART1_FINAL = P2.parent / "part1" / "results" / "final"

A = [f"a{i}" for i in range(8)]
B = [f"b{i}" for i in range(8)]
S = [f"s{i}" for i in range(8)]
PERIOD = 2.0e-9
SEGMENT = 240


# ------------------------------------------------------------------ netlists

def gate_cell(nand_drive, inv_drive):
    """Carry-gating cell: cin_hi = cout_lo AND NOT mode. Static CMOS NAND2 and inverter on the
    carry path, a unit inverter for the mode, which is static and off the carry path."""
    return Block(f"carry_gate_n{nand_drive:g}_i{inv_drive:g}".replace(".", "p"), ["cout_lo", "mode"], ["cin_hi"],
                 lambda v: {"cin_hi": v["cout_lo"] & (1 - v["mode"])},
                 [("invm", inv(1.0), {"a": "mode", "y": "modeb"}),
                  ("nandg", nand(2, nand_drive), {"i0": "cout_lo", "i1": "modeb", "y": "gn"}),
                  ("invg", inv(inv_drive), {"a": "gn", "y": "cin_hi"})],
                 "carry-gating cell: cin_hi = cout_lo AND NOT mode")


def adder4():
    label, sizes, flips, _ = final_design()
    return build(label, sizes, flips, "cla4_final")


def logic8(simd):
    def f(v):
        a = sum(v[f"a{i}"] << i for i in range(8))
        b = sum(v[f"b{i}"] << i for i in range(8))
        mode = v.get("mode", 0) if simd else 0
        lo = (a & 15) + (b & 15) + v["c0"]
        hi = (a >> 4) + (b >> 4) + (0 if mode else lo >> 4)
        out = {f"s{i}": ((lo & 15) | ((hi & 15) << 4)) >> i & 1 for i in range(8)}
        out["c8"] = hi >> 4
        if simd:
            out["c4lo"] = lo >> 4
        return out
    return f


def ports(simd):
    ins = A + B + ["c0"] + (["mode"] if simd else [])
    outs = S + ["c8"] + (["c4lo"] if simd else [])
    return ins, outs


def block_maps(kind):
    """Net renaming for CLA0 ('l') and CLA1 ('h')."""
    maps = {}
    for pre, k in (("l", 0), ("h", 1)):
        m = {}
        for i in range(4):
            m[f"a{i}"], m[f"b{i}"], m[f"s{i}"] = f"a{i + 4 * k}", f"b{i + 4 * k}", f"s{i + 4 * k}"
        m["c0"] = "c0" if k == 0 else ("cinh" if kind == "simd" else "c4lo")
        m["c4"] = "c4lo" if k == 0 else "c8"
        maps[pre] = m
    return maps


def hierarchical(kind, gate=None):
    """Two instances of the Part I adder, and the gating cell between them for the SIMD design."""
    cla = adder4()
    ins, outs = ports(kind == "simd")
    maps = block_maps(kind)
    insts = [("cla0", cla, {p: maps["l"][p] for p in cla.inputs + cla.outputs})]
    if kind == "simd":
        insts.append(("gate", gate, {"cout_lo": "c4lo", "mode": "mode", "cin_hi": "cinh"}))
    insts.append(("cla1", cla, {p: maps["h"][p] for p in cla.inputs + cla.outputs}))
    name = "simd8" if kind == "simd" else "base8"
    desc = "SIMD-reconfigurable 8-bit adder: CLA0, carry-gating cell, CLA1" if kind == "simd" else \
        "baseline 8-bit adder: CLA0 carry-out wired straight to CLA1 carry-in"
    return Block(name, ins, outs, logic8(kind == "simd"), insts, desc)


def flat(kind, gate=None):
    """The same circuit with every leaf gate at the top level, for placement in rows."""
    cla = adder4()
    ins, outs = ports(kind == "simd")
    maps = block_maps(kind)
    insts = []
    for pre in ("l", "h"):
        for inst, cell, pins in cla.instances:
            insts.append((f"{pre}_{inst}", cell, {p: maps[pre].get(n, f"{pre}_{n}") for p, n in pins.items()}))
    if kind == "simd":
        local = {"cout_lo": "c4lo", "mode": "mode", "cin_hi": "cinh"}
        for inst, cell, pins in gate.instances:
            insts.append((f"g_{inst}", cell, {p: local.get(n, f"g_{n}") for p, n in pins.items()}))
    return Block(("simd8" if kind == "simd" else "base8") + "_flat", ins, outs, logic8(kind == "simd"), insts)


def gate_choice():
    path = RESULTS / "gate.json"
    d = json.loads(path.read_text()) if path.exists() else {"nand": 2.0, "inv": 2.0}
    return gate_cell(d["nand"], d["inv"])


# ------------------------------------------------------------------ benches

def bench(cell, ins, outs, vectors, path, period=PERIOD, tstep="20p", meas_power=False):
    """Every input through a shaper x1 and driver x2, every output loaded by a 20/10 lambda inverter.
    The circuit under test has its own supply, so power excludes drivers and loads."""
    model = os.path.relpath(MODEL, path.parent)
    total = len(vectors) * period
    net = (f"* {cell.name}\n.include {model}\n.options reltol=1e-4\nVDD vdd gnd 1.8\nVdut vdut gnd 1.8\n"
           + cell.spice() + TB_CELLS)
    for pin in ins:
        net += pwl_lines(f"V{pin}", f"src_{pin}", [1 - v[pin] for v in vectors], period, 20e-12)
        net += f"Xs_{pin} src_{pin} drv_{pin} vdd gnd tb_x1\nXd_{pin} drv_{pin} {pin} vdd gnd tb_x2\n"
    for out in outs:
        net += f"Xl_{out} {out} lo_{out} vdd gnd tb_x1\n"
    net += f"X0 {' '.join(cell.ports[:-2])} vdut gnd {cell.name}\n"
    probes = " ".join(f"v({n})" for n in ins + [f"drv_{p}" for p in ins] + outs)
    net += f".tran {tstep} {total:.5e}\n"
    if meas_power:
        net += f".meas tran iavg AVG i(Vdut) FROM={period:.5e} TO={total:.5e}\n"
    net += (".control\nset wr_singlescale\nset wr_vecnames\nrun\n"
            f"wrdata {path.stem}.txt {probes}\nquit\n.endc\n.end\n")
    path.write_text(net)


def run(cell, ins, outs, logic, vectors, path, period=PERIOD, meas_power=False):
    """Simulate, check every settled output, and time every output change from the changed input."""
    bench(cell, ins, outs, vectors, path, period, meas_power=meas_power)
    values, result = run_ngspice(path, timeout=3000)
    wave = path.with_suffix(".txt")
    if not wave.exists() or "too small" in result.stderr:
        raise RuntimeError(f"{path.name}: simulation failed: {result.stderr[-300:]}")
    names = wave.read_text().split("\n", 1)[0].split()
    data = np.loadtxt(wave, skiprows=1)
    wave.unlink()
    col = {n.lower(): i for i, n in enumerate(names)}
    t = data[:, 0]
    if t[-1] < len(vectors) * period * 0.9999:
        raise RuntimeError(f"{path.name}: stopped early")
    series = {n: data[:, col[f"v({n})"]] for n in ins + outs}
    drv = {p: data[:, col[f"v(drv_{p})"]] for p in ins}
    arcs, errors = [], 0
    for k in range(1, len(vectors)):
        lo, hi = np.searchsorted(t, [k * period, (k + 1) * period])
        tw = t[lo:hi + 1]
        changed = [p for p in ins if vectors[k][p] != vectors[k - 1][p]]
        old, new = logic(vectors[k - 1]), logic(vectors[k])
        for out in outs:
            settled = series[out][min(hi, len(t) - 1)]
            if (new[out] and settled < 0.9 * cfg.VDD) or (not new[out] and settled > 0.1 * cfg.VDD):
                errors += 1
        if len(changed) != 1:
            continue
        pin = changed[0]
        t_pin = crossings(tw, series[pin][lo:hi + 1])
        t_drv = crossings(tw, drv[pin][lo:hi + 1])
        for out in outs:
            if old[out] == new[out]:
                continue
            cross = crossings(tw, series[out][lo:hi + 1])
            if not len(cross) or not len(t_pin):
                errors += 1
                continue
            arcs.append(dict(pin=pin, pin_edge="rise" if vectors[k][pin] else "fall", output=out,
                             out_edge="rise" if new[out] else "fall",
                             state=vec_text(vectors[k - 1]), next_state=vec_text(vectors[k]),
                             tpd_pin_ps=(cross[-1] - t_pin[0]) * 1e12, tpd_drv_ps=(cross[-1] - t_drv[0]) * 1e12))
    power = abs(values["iavg"]) * cfg.VDD if meas_power and "iavg" in values else None
    return arcs, errors, power


def vec_text(v):
    if "a0" not in v:
        return " ".join(f"{k}={x}" for k, x in v.items())
    a = sum(v[f"a{i}"] << i for i in range(8))
    b = sum(v[f"b{i}"] << i for i in range(8))
    return f"A={a:02X} B={b:02X} C0={v['c0']}" + (f" M={v['mode']}" if "mode" in v else "")


def vector(a, b, c0, mode=None):
    v = {**{f"a{i}": (a >> i) & 1 for i in range(8)}, **{f"b{i}": (b >> i) & 1 for i in range(8)}, "c0": c0}
    if mode is not None:
        v["mode"] = mode
    return v


def search_vectors(mode):
    """Guided worst-case search, single-input changes only, in four walks:
      1, 2  every transition of CLA0's nine inputs (a0-a3, b0-b3, C0), with CLA1 set to pass a carry
            through all four bits (A_hi = F, B_hi = 0, then A_hi = 0, B_hi = F)
      3, 4  every transition of CLA1's eight inputs, with CLA0 producing a carry-out of 0, then of 1
    Walks 1 and 2 hold every path from a CLA0 input across the block boundary to S7 and C8."""
    walks = []
    for hi_a, hi_b in ((0xF, 0x0), (0x0, 0xF)):
        seq = []
        for s in euler_walk(9):
            a_lo, b_lo, c0 = s & 15, (s >> 4) & 15, (s >> 8) & 1
            seq.append(vector(a_lo | hi_a << 4, b_lo | hi_b << 4, c0, mode))
        walks.append(seq)
    for lo_a, lo_b in ((0x0, 0x0), (0xF, 0x1)):
        seq = []
        for s in euler_walk(8):
            a_hi, b_hi = s & 15, (s >> 4) & 15
            seq.append(vector(lo_a | a_hi << 4, lo_b | b_hi << 4, 0, mode))
        walks.append(seq)
    return walks


def design_cell(design, view):
    """design: simd or base. view: sch or post."""
    simd = design == "simd"
    ins, outs = ports(simd)
    if view == "sch":
        return hierarchical(design, gate_choice() if simd else None), ins, outs
    spice = LAYOUT / design / f"{design}8_flat.spice"
    return ExtractedCell(spice, f"{design}8", ins, outs), ins, outs


# ------------------------------------------------------------------ stages

def stage_netlists():
    from cellgen.schematic import draw_block
    out = P2 / "schematics"
    out.mkdir(exist_ok=True)
    gate = gate_choice()
    for kind in ("simd", "base"):
        h = hierarchical(kind, gate if kind == "simd" else None)
        (out / f"{h.name}.sp").write_text(h.spice())
        draw(h, out / f"{h.name}_blocks")
    (out / f"{gate.name}.sp").write_text(gate.spice())
    draw(gate, out / f"{gate.name}_blocks")
    for _, cell, _ in gate.instances:
        draw(cell, out / f"gate_{cell.name}")
    print("netlists and drawings in", out)


def stage_gate():
    """Size the gating cell for the fastest Cin to S7 in 8-bit mode, on the schematic."""
    work = SIM / "gate_sizing"
    work.mkdir(parents=True, exist_ok=True)
    ins, outs = ports(True)
    vectors = [vector(0xFF, 0x00, k % 2, 0) for k in range(6)]
    jobs = [(n, i) for n in (0.6, 0.8, 1.0, 1.5, 2.0) for i in (1.0, 1.5, 2.0, 2.5, 3.0)]

    def one(job):
        n, i = job
        cell = hierarchical("simd", gate_cell(n, i))
        arcs, errors, _ = run(cell, ins, outs, logic8(True), vectors, work / f"g_n{n:g}_i{i:g}.cir")
        s7 = [a["tpd_pin_ps"] for a in arcs if a["output"] == "s7"]
        return dict(nand=n, inv=i, worst_cin_to_s7_ps=round(max(s7), 2), errors=errors)

    with ThreadPoolExecutor(8) as ex:
        rows = list(ex.map(one, jobs))
    best = min((r for r in rows if r["errors"] == 0), key=lambda r: r["worst_cin_to_s7_ps"])
    with open(RESULTS / "gate_sizing.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    gate = gate_cell(best["nand"], best["inv"])
    cell_dir = LAYOUT / "gate_cell"
    if cell_dir.exists():
        shutil.rmtree(cell_dir)
    lay = layout_cell(gate, work=cell_dir)
    if lay["drc"] or not lay["lvs"]:
        raise RuntimeError(f"gate cell layout: {lay}")
    # gate on its own, extracted: delay from cout_lo to cin_hi, mode 0, with a 20/10 inverter load
    ext = ExtractedCell(cell_dir / gate.name / f"{gate.name}.spice", "gate", ["cout_lo", "mode"], ["cin_hi"])
    res = {}
    for view, cell in (("sch", gate), ("post", ext)):
        vecs = [{"cout_lo": k % 2, "mode": 0} for k in range(5)] + [{"cout_lo": k % 2, "mode": 1} for k in range(1, 5)]
        arcs, errors, _ = run(cell, ["cout_lo", "mode"], ["cin_hi"], cell.logic if view == "sch" else gate.logic,
                              vecs, work / f"gate_alone_{view}.cir")
        res[view] = dict(errors=errors, worst_ps=round(max(a["tpd_pin_ps"] for a in arcs), 2),
                         rise_ps=round(max(a["tpd_pin_ps"] for a in arcs if a["out_edge"] == "rise"), 2),
                         fall_ps=round(max(a["tpd_pin_ps"] for a in arcs if a["out_edge"] == "fall"), 2))
    out = dict(nand=best["nand"], inv=best["inv"], cell=gate.name, transistors=gate.transistor_count,
               schematic_cin_to_s7_ps=best["worst_cin_to_s7_ps"], layout=lay, alone=res)
    (RESULTS / "gate.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


def layout_rows(kind):
    pg = [(f"pg{i + 4 * k}", [f"{pre}_{g}{i}" for g in ("nand", "nor", "aoi", "oai")])
          for pre, k in (("l", 0), ("h", 1)) for i in range(4)]
    cla = adder4()
    order = [i[0] for i in cla.instances if not re.match(r"(nand|nor|aoi|oai|x)\d$", i[0])]
    order.sort(key=lambda n: CARRY_ORDER.index(n) if n in CARRY_ORDER else 99)
    carry = [("carry0", [f"l_{n}" for n in order])]
    if kind == "simd":
        carry.append(("gate", ["g_invm", "g_nandg", "g_invg"]))
    carry.append(("carry1", [f"h_{n}" for n in order]))
    sums = [(f"sum{i + 4 * k}", [f"{pre}_x{i}"]) for pre, k in (("l", 0), ("h", 1)) for i in range(4)]
    return [pg, carry, sums]


def stage_layout(*kinds):
    from top import partition
    gate = gate_choice()
    out = {}
    for kind in kinds or ("simd", "base"):
        g = gate if kind == "simd" else None
        f, h = flat(kind, g), hierarchical(kind, g)
        ins, outs = ports(kind == "simd")
        work = LAYOUT / kind
        if work.exists():
            shutil.rmtree(work)
        rows = partition(f, layout_rows(kind), ins + outs)
        res = assemble(f"{kind}8_top", rows, h, ins + outs, work, align={2: 0})
        ext = ExtractedCell(work / f"{kind}8_top.spice", f"{kind}8", ins, outs)
        nets = {n for _, _, pins in f.instances for n in pins.values()}
        caps = net_capacitance(work / f"{kind}8_top.spice", nets)
        res.update(transistors=ext.transistors, wire_cap_ff=round(ext.cap_total_ff, 1),
                   carry_net_caps={n: round(caps.get(n, 0.0), 2) for n in ("c4lo", "cinh", "c0", "c8")})
        shutil.copy(work / f"{kind}8_top.spice", P2 / "extraction" / f"{kind}8_extracted.spice")
        out[kind] = res
        print(kind, {k: v for k, v in res.items() if k != "placements"}, flush=True)
        if res["drc"] != 0 or not res["lvs"]:
            raise RuntimeError(f"{kind}: DRC {res['drc']} LVS {res['lvs_message']}")
        (RESULTS / f"layout_{kind}.json").write_text(json.dumps(res, indent=1))


def stage_search(design, mode, view):
    mode = int(mode)
    simd = design == "simd"
    cell, ins, outs = design_cell(design, view)
    if not simd and mode:
        raise ValueError("the baseline has no dual mode")
    walks = search_vectors(mode if simd else None)
    tag = f"{design}_m{mode}_{view}"
    work = SIM / "search" / tag
    work.mkdir(parents=True, exist_ok=True)
    jobs = []
    for w, seq in enumerate(walks):
        for start in range(0, len(seq) - 1, SEGMENT):
            jobs.append((seq[start:start + SEGMENT + 1], work / f"w{w}_s{start // SEGMENT:02d}.cir"))
    with ThreadPoolExecutor(8) as ex:
        results = list(ex.map(lambda j: run(cell, ins, outs, logic8(simd), j[0], j[1]), jobs))
    arcs = [a for r in results for a in r[0]]
    errors = sum(r[1] for r in results)
    with open(work / "arcs.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(arcs[0]))
        w.writeheader()
        w.writerows(arcs)
    worst = max(arcs, key=lambda a: a["tpd_pin_ps"])
    worst_drv = max(arcs, key=lambda a: a["tpd_drv_ps"])
    per_out = {o: round(max(a["tpd_pin_ps"] for a in arcs if a["output"] == o), 2) for o in outs if any(a["output"] == o for a in arcs)}
    out = dict(design=design, mode=mode, view=view, transitions=sum(len(s) - 1 for s in walks), arcs=len(arcs),
               errors=errors, tpd_max_ps=round(worst["tpd_pin_ps"], 2), worst=worst,
               tpd_max_drv_ps=round(worst_drv["tpd_drv_ps"], 2), per_output=per_out)
    (RESULTS / f"search_{tag}.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({k: v for k, v in out.items() if k != "per_output"}), flush=True)


def stage_penalty():
    """A = 0xFF, B = 0x00, Cin toggling: delay from Cin to S7 and to C8, both edges."""
    rows = []
    jobs = []
    for view in ("sch", "post"):
        for design, mode in (("base", None), ("simd", 0), ("simd", 1)):
            jobs.append((view, design, mode))

    def one(job):
        view, design, mode = job
        cell, ins, outs = design_cell(design, view)
        vecs = [vector(0xFF, 0x00, k % 2, mode) for k in range(7)]
        tag = f"penalty_{design}_m{mode}_{view}"
        arcs, errors, _ = run(cell, ins, outs, logic8(design == "simd"), vecs, SIM / "penalty" / f"{tag}.cir")
        pick = lambda out, edge: max((a["tpd_pin_ps"] for a in arcs if a["output"] == out and a["pin_edge"] == edge), default=None)
        return dict(view=view, design=design, mode=mode, errors=errors,
                    cin_rise_to_s7_ps=pick("s7", "rise"), cin_fall_to_s7_ps=pick("s7", "fall"),
                    cin_rise_to_c8_ps=pick("c8", "rise"), cin_fall_to_c8_ps=pick("c8", "fall"),
                    cin_rise_to_s3_ps=pick("s3", "rise"), cin_rise_to_c4lo_ps=pick("c4lo", "rise"))

    (SIM / "penalty").mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(6) as ex:
        rows = list(ex.map(one, jobs))
    for view in ("sch", "post"):
        base = next(r for r in rows if r["view"] == view and r["design"] == "base")
        simd = next(r for r in rows if r["view"] == view and r["design"] == "simd" and r["mode"] == 0)
        for edge in ("rise", "fall"):
            b, s = base[f"cin_{edge}_to_s7_ps"], simd[f"cin_{edge}_to_s7_ps"]
            simd[f"penalty_{edge}_ps"] = round(s - b, 2)
            simd[f"penalty_{edge}_pct"] = round(100 * (s - b) / b, 2)
    (RESULTS / "penalty.json").write_text(json.dumps(rows, indent=1))
    for r in rows:
        print(r, flush=True)


def dff_times():
    d = json.loads((PART1_FINAL / "dff.json").read_text())["postlayout"]
    return d["tcq_ps"], d["tsu_ps"], d["thold_ps"]


def stage_settle(*periods_ps):
    """Shortest clock at which every design settles on the same 200 random multi-input vectors.
    The worst-case search changes one input at a time; random vectors change several at once."""
    rng = random.Random(7)
    vecs = [(rng.randrange(256), rng.randrange(256), rng.randrange(2)) for _ in range(201)]
    jobs = [(d, m, float(T)) for T in periods_ps for d, m in (("base", 0), ("simd", 0), ("simd", 1))]

    def one(job):
        design, mode, T = job
        cell, ins, outs = design_cell(design, "post")
        vv = [vector(a, b, c, mode if design == "simd" else None) for a, b, c in vecs]
        _, errors, _ = run(cell, ins, outs, logic8(design == "simd"), vv, SIM / "settle" / f"{design}_m{mode}_T{int(T)}.cir",
                           period=T * 1e-12)
        return dict(design=design, mode=mode, period_ps=T, errors=errors)

    (SIM / "settle").mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(8) as ex:
        rows = list(ex.map(one, jobs))
    (RESULTS / "settle.json").write_text(json.dumps(rows, indent=1))
    for r in rows:
        print(r, flush=True)


def stage_power(common_ps=None):
    """fmax from the course formula, 1 / (tpd,max + tsetup + thold), with the Part I flip-flop.
    Power: identical input vectors for every design: 10 cycles at one common clock, the lowest
    fmax of the three, so all three are compared at the same activity and frequency. Each design
    is also run at its own fmax, and on 200 vectors as a check on the short 10-cycle sample."""
    tcq, tsu, th = dff_times()
    tpd = {}
    for design, mode in (("base", 0), ("simd", 0), ("simd", 1)):
        tpd[(design, mode)] = json.loads((RESULTS / f"search_{design}_m{mode}_post.json").read_text())["tpd_max_ps"]
    fmax = {k: 1e3 / (v + tsu + th) for k, v in tpd.items()}
    common_T = (float(common_ps) if common_ps else max(v + tsu + th for v in tpd.values())) * 1e-12
    rng = random.Random(2025102061)
    base_vecs = [(rng.randrange(256), rng.randrange(256), rng.randrange(2)) for _ in range(11)]
    rng = random.Random(7)
    long_vecs = [(rng.randrange(256), rng.randrange(256), rng.randrange(2)) for _ in range(201)]
    jobs = []
    for design, mode in tpd:
        own_T = (tpd[(design, mode)] + tsu + th) * 1e-12
        for label, T, vecs in (("common", common_T, base_vecs), ("own", own_T, base_vecs), ("long200", common_T, long_vecs)):
            jobs.append((design, mode, label, T, vecs))

    def one(job):
        design, mode, label, T, vecs = job
        cell, ins, outs = design_cell(design, "post")
        vv = [vector(a, b, c, mode if design == "simd" else None) for a, b, c in vecs]
        _, errors, p = run(cell, ins, outs, logic8(design == "simd"), vv,
                           SIM / "power" / f"{design}_m{mode}_{label}.cir", period=T, meas_power=True)
        return dict(design=design, mode=mode, run=label, period_ps=round(T * 1e12, 1), cycles=len(vecs) - 1,
                    errors=errors, power_uw=round(p * 1e6, 1))

    (SIM / "power").mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(6) as ex:
        rows = list(ex.map(one, jobs))
    out = dict(dff=dict(tcq_ps=tcq, tsu_ps=tsu, thold_ps=th), tpd_max_ps={f"{d}_m{m}": v for (d, m), v in tpd.items()},
               fmax_ghz={f"{d}_m{m}": round(v, 4) for (d, m), v in fmax.items()}, common_period_ps=round(common_T * 1e12, 1),
               runs=rows)
    P = {(r["design"], r["mode"]): r["power_uw"] for r in rows if r["run"] == "common"}
    out["power_penalty_pct"] = round(100 * (P[("simd", 0)] - P[("base", 0)]) / P[("base", 0)], 2)
    out["edp"] = {f"{d}_m{m}": dict(power_uw=P[(d, m)], tpd_ps=tpd[(d, m)],
                                    edp_fj_ps=round(P[(d, m)] * 1e-6 * (tpd[(d, m)] * 1e-12) ** 2 * 1e27, 1))
                  for (d, m) in tpd}
    (RESULTS / "power.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


# ------------------------------------------------------------------ hierarchical layout

CELLS = LAYOUT / "cells"
CLA_TOP = "cla4_cell"
PAD_X = {"c4": 463, "c0": 499, "cout_lo": 13, "cin_hi": 49}   # 9k + 4: midway between routing tracks


def stage_cells():
    """The Part I adder and the gating cell, each laid out by the Part I flow with two extra
    carry pads above the top row, where the top level can land a via on plain metal 3."""
    from candidates import INPUTS, OUTPUTS
    from top import adder_rows, partition
    if CELLS.exists():
        shutil.rmtree(CELLS)
    cla = adder4()
    rows = partition(cla, adder_rows(cla), INPUTS + OUTPUTS)
    res = assemble(CLA_TOP, rows, cla, INPUTS + OUTPUTS, CELLS, align={2: 0},
                   extra_pins={"c4": [PAD_X["c4"]], "c0": [PAD_X["c0"]]})
    gate = gate_choice()
    g = Block("gtile_blk", gate.inputs, gate.outputs, gate.logic, gate.instances)
    grows = partition(g, [[("gtile", [i[0] for i in gate.instances])]], gate.inputs + gate.outputs)
    gres = assemble("gate_top", grows, gate, gate.inputs + gate.outputs, CELLS,
                    extra_pins={"cout_lo": [PAD_X["cout_lo"]], "cin_hi": [PAD_X["cin_hi"]]})
    out = {}
    for name, r in (("cla4_cell", res), ("gate_top", gres)):
        print(name, {k: v for k, v in r.items() if k != "placements"}, flush=True)
        if r["drc"] or not r["lvs"]:
            raise RuntimeError(f"{name}: DRC {r['drc']} LVS {r['lvs_message']}")
        out[name] = {k: v for k, v in r.items() if k != "placements"}
    (RESULTS / "layout_cells.json").write_text(json.dumps(out, indent=1))


def mag_labels(path):
    """Port labels of a MAGIC cell: name -> (layer, x0, y0, x1, y1)."""
    out = {}
    for line in Path(path).read_text().splitlines():
        tok = line.split()
        if tok[:1] == ["rlabel"]:
            out[tok[7]] = (tok[1], int(tok[2]), int(tok[3]), int(tok[4]), int(tok[5]))
    return out


def stage_layout_h(*kinds):
    """Two instances of the Part I adder layout and, for the SIMD design, the gating cell between them.
    Inter-block carries run on metal 5, which neither cell uses. Power joins under the cells."""
    from top import DRC_TCL, EXTRACT_TCL, magic
    from cellgen import parse_flat
    from cellgen.lvs import compare, read_extracted, schematic_devices
    gate = gate_choice()
    for kind in kinds or ("simd", "base"):
        simd = kind == "simd"
        work = LAYOUT / kind
        if work.exists():
            shutil.rmtree(work)
        work.mkdir(parents=True)
        for f in CELLS.glob("*.mag"):
            shutil.copy(f, work)
        cells = json.loads((RESULTS / "layout_cells.json").read_text())
        cla = mag_labels(work / f"{CLA_TOP}.mag")
        cla_w = 548
        top_y = cells["cla4_cell"]["height_lambda"]
        place = {"cla0": 0}
        if simd:
            glab = mag_labels(work / "gate_top.mag")
            gate_w = cells["gate_top"]["width_lambda"]
            place["gate"] = cla_w + 70
            place["cla1"] = place["gate"] + gate_w + 70
            gate_y = 200
        else:
            place["cla1"] = cla_w + 90
        x1 = place["cla1"]
        lines = [f"cellname rename (UNNAMED) {kind}8_top",
                 f"getcell {CLA_TOP} child 0 0 parent 0 0", f"getcell {CLA_TOP} child 0 0 parent {x1} 0"]
        if simd:
            lines.append(f"getcell gate_top child 0 0 parent {place['gate']} {gate_y}")
        rects, labels = [], []

        def stub(name, layer, x0, y0, dx, dy, label=None, port=False):
            """A metal 3 box on a cell's pin stub, labelled in the parent."""
            px, py = x0 + dx, y0 + dy
            rects.append(("m3", px, py, px + 1, py + 5))
            if label:
                labels.append((label, px, py, port))
            return px, py

        maps = block_maps(kind)
        pin_xy = {}
        for inst, dx in (("l", 0), ("h", x1)):
            for net, (layer, x0, y0, _, _) in cla.items():
                if net in ("vdd", "gnd"):
                    continue
                top_net = maps[inst][net]
                ins, outs = ports(simd)
                pin_xy[(inst, net)] = stub(net, layer, x0, y0, dx, 0, top_net, top_net in ins + outs)
        if simd:
            for net, (layer, x0, y0, _, _) in glab.items():
                if net in ("vdd", "gnd"):
                    continue
                top_net = {"cout_lo": "c4lo", "mode": "mode", "cin_hi": "cinh"}[net]
                pin_xy[("g", net)] = stub(net, layer, x0, y0, place["gate"], gate_y, top_net, top_net in ports(True)[0] + ports(True)[1])

        def metal5_path(a, b, channel):
            """Via stack up from pin a, metal 5 up or down to the channel, across, and down to pin b."""
            for (px, py) in (a, b):
                rects.append(("m345c", px - 2, py, px + 3, py + 5))   # one stacked via, metal 3 to 5
                rects.append(("m5", px - 2, py, px + 3, py + 5))
            (ax, ay), (bx, by) = a, b
            for (px, py) in (a, b):
                rects.append(("m5", px - 1, min(py, channel), px + 3, max(py + 5, channel + 4)))
            rects.append(("m5", min(ax, bx) - 1, channel, max(ax, bx) + 3, channel + 4))

        def pad(cell, net, ox, oy):
            (x, y), = cells[cell]["pads"][net]
            return x + ox, y + oy

        c4_pad = pad("cla4_cell", "c4", 0, 0)
        c0_pad = pad("cla4_cell", "c0", x1, 0)
        if simd:
            metal5_path(c4_pad, pad("gate_top", "cout_lo", place["gate"], gate_y), top_y + 30)
            metal5_path(pad("gate_top", "cin_hi", place["gate"], gate_y), c0_pad, top_y + 50)
        else:
            metal5_path(c4_pad, c0_pad, top_y + 30)

        # power: each cell's straps at x - 28 (vdd) and x - 16 (gnd), joined by buses below
        origins = [(0, 0), (x1, 0)] + ([(place["gate"], gate_y)] if simd else [])
        xmin, xmax = -40, x1 + cla_w + 10
        for ox, oy in origins:
            rects.append(("m2", ox - 28, -60, ox - 22, oy + 2))
            rects.append(("m2", ox - 16, -42, ox - 10, oy + 2))
            rects.append(("m3c", ox - 16, -42, ox - 10, -36))
        rects.append(("m2", xmin, -60, xmax, -54))
        rects.append(("m3", xmin, -42, xmax, -36))
        ins, outs = ports(simd)
        # the placed cells are saved as they are, then flattened so the vias sit in the same cell as the pins
        lines += [f"save {kind}8_top", "select top cell", "expand", f"flatten -nolabels {kind}8_flat", f"load {kind}8_flat"]
        body = "\n".join(lines) + "\n"
        body += "\n".join(f"box {x0} {y0} {x1_} {y1}; paint {layer}" for layer, x0, y0, x1_, y1 in rects) + "\n"
        idx = 1
        for name, px, py, port in labels:
            body += f"box {px} {py} {px + 1} {py + 5}; label {name} center m3"
            if port:
                body += f"; port make {idx}"
                idx += 1
            body += "\n"
        body += f"box {xmin} -60 {xmin + 6} -54; label vdd center m2; port make {idx}\n"
        body += f"box {xmin} -42 {xmin + 6} -36; label gnd center m3; port make {idx + 1}\n"
        body += f"save {kind}8_flat\n" + DRC_TCL + f"save {kind}8_flat\n" + EXTRACT_TCL
        out = magic(work, f"{kind}8_top", body)
        count = re.search(r"DRC_COUNT (\d+)", out)
        errors = [l for l in out.splitlines() if l.startswith("DRC_ERR")]
        spice_path = work / f"{kind}8_flat.spice"
        h = hierarchical(kind, gate if simd else None)
        extracted = read_extracted(spice_path.read_text()) if spice_path.exists() else []
        matched, message = compare(extracted, schematic_devices(parse_flat(h.spice(), h.name)), set(ins + outs) | {"vdd", "gnd"})
        width = xmax - xmin
        height = (top_y + 60) - (-60)
        res = dict(name=f"{kind}8_top", drc=int(count.group(1)) if count else -1, drc_first=errors[:6], lvs=matched,
                   lvs_message=message, width_lambda=width, height_lambda=height,
                   area_um2=round(width * height * 0.09 ** 2, 1), placement=place)
        if spice_path.exists():
            ext = ExtractedCell(spice_path, f"{kind}8", ins, outs)
            nets = {n for _, _, pins in flat(kind, gate if simd else None).instances for n in pins.values()}
            caps = net_capacitance(spice_path, nets)
            res.update(transistors=ext.transistors, wire_cap_ff=round(ext.cap_total_ff, 1),
                       carry_net_caps={n: round(caps.get(n, 0.0), 2) for n in ("c4lo", "cinh", "c0", "c8")})
            (P2 / "extraction").mkdir(exist_ok=True)
            shutil.copy(spice_path, P2 / "extraction" / f"{kind}8_extracted.spice")
        (RESULTS / f"layout_{kind}.json").write_text(json.dumps(res, indent=1))
        print(kind, json.dumps(res), flush=True)


def stage_waves():
    """Post-layout waveforms of the worst-case vector, A = FF, B = 00, Cin toggling, for the report."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig_dir = P2 / "documentation" / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    cases = [("base", None, "baseline"), ("simd", 0, "SIMD_MODE=0"), ("simd", 1, "SIMD_MODE=1")]
    fig, axes = plt.subplots(5, 1, figsize=(11, 8), sharex=True)
    signals = [("c0", "Cin (C0)"), ("c4lo", "Cout of CLA0"), ("cinh", "Cin of CLA1"), ("s7", "S7"), ("c8", "Cout (C8)")]
    colours = {"baseline": "#444444", "SIMD_MODE=0": "#1f5fa8", "SIMD_MODE=1": "#b8362f"}
    for design, mode, label in cases:
        cell, ins, outs = design_cell(design, "post")
        vecs = [vector(0xFF, 0x00, k % 2, mode) for k in range(4)]
        path = SIM / "waves" / f"wave_{design}_m{mode}.cir"
        path.parent.mkdir(parents=True, exist_ok=True)
        # internal nets of the extracted cell sit two levels down: bench X0, wrapper X0
        probe = {"c0": "c0", "s7": "s7", "c8": "c8",
                 "c4lo": "c4lo" if design == "simd" else "x0.x0.c4lo",
                 "cinh": "x0.x0.cinh" if design == "simd" else "x0.x0.c4lo"}
        bench(cell, ins, outs, vecs, path)
        text = path.read_text().replace(f"wrdata {path.stem}.txt", f"wrdata {path.stem}.txt "
                                        + " ".join(f"v({probe[k]})" for k in ("c4lo", "cinh") if "." in probe[k]))
        path.write_text(text)
        run_ngspice(path, timeout=600)
        wave = path.with_suffix(".txt")
        data = np.loadtxt(wave, skiprows=1)
        names = wave.read_text().split("\n", 1)[0].split()
        col = {n.lower(): i for i, n in enumerate(names)}
        t = data[:, 0] * 1e9
        for ax, (sig, title) in zip(axes, signals):
            key = f"v({probe[sig]})"
            if key in col:
                ax.plot(t, data[:, col[key]], color=colours[label], lw=1.3, label=label)
            ax.set_ylabel(title, rotation=0, ha="right", va="center", fontsize=9)
            ax.set_ylim(-0.2, 2.0)
            ax.grid(alpha=0.3)
    pen = json.loads((RESULTS / "penalty.json").read_text())
    post = {(r["design"], r["mode"]): r for r in pen if r["view"] == "post"}
    note = (f"Cin rise to S7: baseline {post[('base', None)]['cin_rise_to_s7_ps']:.1f} ps, "
            f"SIMD mode 0 {post[('simd', 0)]['cin_rise_to_s7_ps']:.1f} ps "
            f"(+{post[('simd', 0)]['penalty_rise_ps']:.1f} ps, {post[('simd', 0)]['penalty_rise_pct']:.1f} %). "
            "In mode 1 the carry stops at CLA0: Cin of CLA1 and S7 stay put.")
    axes[0].legend(ncol=3, fontsize=8, loc="upper left")
    axes[-1].set_xlabel("time (ns)")
    axes[-1].text(0.0, -0.55, note, transform=axes[-1].transAxes, fontsize=8.5)
    fig.suptitle(cfg.plot_title("2.4", "worst-case-vector-A=FF-B=00-Cin-toggling-postlayout"), fontsize=10)
    fig.tight_layout()
    fig.savefig(fig_dir / "2.4_worst-case-vector-postlayout.png", dpi=150)
    plt.close(fig)
    print("wrote 2.4")


def stage_summary():
    """One table of everything Part II asks for, as CSV and Markdown."""
    lay = {k: json.loads((RESULTS / f"layout_{k}.json").read_text()) for k in ("simd", "base")}
    gate = json.loads((RESULTS / "gate.json").read_text())
    pen = json.loads((RESULTS / "penalty.json").read_text())
    pw = json.loads((RESULTS / "power.json").read_text())
    srch = {}
    for d, m in (("base", 0), ("simd", 0), ("simd", 1)):
        for v in ("sch", "post"):
            f = RESULTS / f"search_{d}_m{m}_{v}.json"
            if f.exists():
                srch[(d, m, v)] = json.loads(f.read_text())
    P = lambda d, m, view: next(r for r in pen if r["design"] == d and r["mode"] == m and r["view"] == view)
    rows = []
    for view in ("sch", "post"):
        for d, m, mm in (("base", 0, None), ("simd", 0, 0), ("simd", 1, 1)):
            r = P(d, mm, view)
            sr = srch.get((d, m, view), {})
            rows.append(dict(view="schematic" if view == "sch" else "post-layout", design="baseline" if d == "base" else f"SIMD, mode {m}",
                             tpd_max_ps=sr.get("tpd_max_ps"), worst_arc=(f"{sr['worst']['pin']} {sr['worst']['pin_edge']} to {sr['worst']['output']} "
                                                                       f"{sr['worst']['out_edge']}, {sr['worst']['state']}") if sr else None,
                             search_errors=sr.get("errors"), cin_rise_to_s7_ps=r["cin_rise_to_s7_ps"], cin_fall_to_s7_ps=r["cin_fall_to_s7_ps"],
                             cin_rise_to_c8_ps=r["cin_rise_to_c8_ps"]))
    with open(RESULTS / "part2_summary.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(json.dumps(rows, indent=1))


if __name__ == "__main__":
    globals()[f"stage_{sys.argv[1]}"](*sys.argv[2:])
