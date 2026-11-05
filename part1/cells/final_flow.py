#!/usr/bin/env python3
"""Everything measured on one chosen design. Run after the architecture and sizing are chosen.

Stages (each can be run alone, later ones read the earlier results):
  layout    adder layout, DRC, extraction, LVS, post-layout all-arc timing
  refine    layout-aware sizing loop using wire load from extraction
  dff       size and characterise the flip-flop at the real load, schematic and extracted
  blocks    each block: schematic against extracted delay
  system    registered layout; frequency search, schematic and extracted; power
  multi     multi-input transitions on the final adder
  plots     report figures
"""
import csv
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np

from arcs import all_arcs, describe_state, write_arcs
from candidates import INPUTS, OUTPUTS, adder_logic, candidate_c2, candidate_c4, candidate_r
from cellgen import config as cfg
from cellgen.schematic import draw
from dff import characterise, tspc
from postlayout import ExtractedCell, net_capacitance
from registered import REG_INPUTS, REG_OUTPUTS, find_failing_period, registered_top, run_system, vector_set
from top import adder_rows, assemble, partition

RESULTS = cfg.PART1 / "results"
FINAL = cfg.PART1 / "results" / "final"
CHOICE = FINAL / "choice.json"


def builders():
    return {"C4_tg": (candidate_c4, "tg"), "C4_aoi22": (candidate_c4, "aoi22"), "R_tg": (candidate_r, "tg"),
            "R_aoi22": (candidate_r, "aoi22"), "C2_tg": (candidate_c2, "tg")}


def load_choice():
    return json.loads(CHOICE.read_text())


def build(label, sizes, flips, name, caps=None):
    fn, style = builders()[label]
    adder = fn(sizes=sizes, sum_style=style, flips={k: tuple(v) for k, v in flips.items()}, name=name)
    if caps:
        adder.net_caps = dict(caps)
    return adder


def arcs_summary(arcs):
    out = {}
    worst_pin = max(arcs, key=lambda a: a["tpd_pin_ps"])
    worst_drv = max(arcs, key=lambda a: a["tpd_drv_ps"])
    out["worst_pin_ps"] = round(worst_pin["tpd_pin_ps"], 2)
    out["worst_pin_arc"] = f"{worst_pin['pin']} {worst_pin['pin_edge']} to {worst_pin['output']} {worst_pin['out_edge']}, " \
                           f"{describe_state(worst_pin['state'])}"
    out["worst_drv_ps"] = round(worst_drv["tpd_drv_ps"], 2)
    per = {}
    for name in OUTPUTS:
        for edge, key in (("rise", "tplh"), ("fall", "tphl")):
            sel = [a for a in arcs if a["output"] == name and a["out_edge"] == edge]
            per[f"{name}_{key}_ps"] = round(max(a["tpd_pin_ps"] for a in sel), 2)
    out["per_output"] = per
    hint = {}
    for a in arcs:
        if a["pin"] == "c0" and (a["state"] & 0xFF) == 0b00001111:
            hint[f"{a['pin_edge']}:{a['output']}:{a['out_edge']}"] = round(a["tpd_pin_ps"], 2)
    out["hint"] = hint
    out["hint_worst_ps"] = max(hint.values())
    return out


def layout_adder(label, sizes, flips, tag):
    """Layout, extraction and post-layout timing. Returns a result dict."""
    adder = build(label, sizes, flips, f"cla_{tag}")
    ports = INPUTS + OUTPUTS
    work = cfg.PART1 / "layout" / "integrated" / tag
    if work.exists():
        shutil.rmtree(work)
    rows = partition(adder, adder_rows(adder), ports)
    res = assemble(f"top_{tag}", rows, adder, ports, work, align={2: 0})
    if res["drc"] != 0 or not res["lvs"]:
        raise RuntimeError(f"{tag}: DRC {res['drc']} LVS {res['lvs_message']} {res['drc_first'][:3]}")
    spice = work / f"top_{tag}.spice"
    ext = ExtractedCell(spice, f"post_{tag}", INPUTS, OUTPUTS)
    arcs, functional = all_arcs(ext, cfg.PART1 / "simulations" / "timing" / f"post_{tag}", workers=8)
    write_arcs(arcs, cfg.PART1 / "simulations" / "timing" / f"post_{tag}" / "arcs.csv")
    if functional:
        raise RuntimeError(f"{tag}: {functional} functional errors post-layout")
    summary = arcs_summary(arcs)
    summary.update(area_um2=res["area_um2"], width_lambda=res["width_lambda"], height_lambda=res["height_lambda"],
                   drc=res["drc"], lvs=res["lvs_message"], wire_cap_ff=round(ext.cap_total_ff, 1),
                   capacitors=ext.capacitors, transistors=ext.transistors, placements=res["placements"])
    nets = set()
    for _, _, pins in adder.instances:
        nets |= set(pins.values())
    summary["net_caps"] = {k: round(v, 3) for k, v in net_capacitance(spice, nets).items()}
    return summary


def stage_layout():
    c = load_choice()
    summary = layout_adder(c["label"], c["sizes"], c["flips"], "final0")
    (FINAL / "final0_post.json").write_text(json.dumps(summary, indent=1))
    print({k: v for k, v in summary.items() if k not in ("net_caps", "placements", "per_output")})


def stage_refine(label, rounds="3", workers="4"):
    """Size with extraction's wire load, lay out again, and keep the best post-layout result."""
    d = json.loads((cfg.PART1 / "simulations" / "optimisation" / label / "summary.json").read_text())
    sizes, flips = d["sizes"], d["flips"]
    first = json.loads((FINAL / f"cmp_{label}.json").read_text())
    rows = [dict(design=label, round=0, note="sized on schematic only", post_worst_pin_ps=first["worst_pin_ps"],
                 post_worst_drv_ps=first["worst_drv_ps"], area_um2=first["area_um2"], wire_cap_ff=first["wire_cap_ff"],
                 total_width_lambda=d["total_width_lambda"])]
    best = (first["worst_drv_ps"], sizes, flips, f"cmp_{label}", first)
    summary = first
    log_path = RESULTS / f"phase7_layout_aware_{label}.csv"

    def save_log():
        with open(log_path, "w", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

    save_log()
    for k in range(1, int(rounds) + 1):
        caps_file = FINAL / f"caps_{label}_round{k}.json"
        caps_file.write_text(json.dumps(summary["net_caps"]))
        start = FINAL / f"start_{label}_round{k}.json"
        start.write_text(json.dumps(dict(sizes=sizes, flips=flips)))
        out = f"aware_{label}_round{k}"
        env = {**os.environ, "OMP_NUM_THREADS": "1"}
        subprocess.run([sys.executable, "optimize.py", label, workers, str(start), str(caps_file), out], check=True, env=env,
                       cwd=Path(__file__).parent, stdout=open(cfg.PART1 / "simulations" / "optimisation" / f"{out}.out", "w"))
        result = json.loads((cfg.PART1 / "simulations" / "optimisation" / out / "summary.json").read_text())
        sizes, flips = result["sizes"], result["flips"]
        tag = f"final_{label}_{k}"
        summary = layout_adder(label, sizes, flips, tag)
        (FINAL / f"{tag}_post.json").write_text(json.dumps(summary, indent=1))
        rows.append(dict(design=label, round=k, note="sized with extracted wire load", post_worst_pin_ps=summary["worst_pin_ps"],
                         post_worst_drv_ps=summary["worst_drv_ps"], area_um2=summary["area_um2"],
                         wire_cap_ff=summary["wire_cap_ff"], total_width_lambda=result["total_width_lambda"]))
        save_log()
        print(rows[-1], flush=True)
        if summary["worst_drv_ps"] < best[0] - 0.5:
            best = (summary["worst_drv_ps"], sizes, flips, tag, summary)
        else:
            break
    (FINAL / f"best_{label}.json").write_text(json.dumps(dict(label=label, sizes=best[1], flips=best[2], tag=best[3],
                                                              worst_pin_ps=best[4]["worst_pin_ps"], worst_drv_ps=best[0],
                                                              area_um2=best[4]["area_um2"]), indent=1))
    print("best", label, best[3], best[4]["worst_pin_ps"], best[0], flush=True)


def input_load_ff(adder, cgn=2.384, cgp=2.043):
    """Largest adder input capacitance at the pins from gate widths, with extraction wire load if present."""
    cap = {}
    for _, cell, pins in adder.instances:
        for dev in cell.devices:
            pin = dev.gate
            if pin in pins and pins[pin] in INPUTS:
                c = dev.w_lam * 0.09 * (cgn if dev.kind == "n" else cgp)
                cap[pins[pin]] = cap.get(pins[pin], 0.0) + c
    return cap


def final_design():
    d = json.loads((FINAL / "final_design.json").read_text())
    return d["label"], d["sizes"], d["flips"], d["tag"]


def stage_dff():
    """Size the flip-flop at the real pin load, then characterise schematic and extracted versions."""
    label, sizes, flips, tag = final_design()
    adder = build(label, sizes, flips, "cla_final")
    post = json.loads((FINAL / f"{tag}_post.json").read_text())
    pin_caps = input_load_ff(adder)
    total = {p: round(c + post["net_caps"].get(p, 0.0), 2) for p, c in pin_caps.items()}
    load = max(total.values())
    print("adder pin load fF", total, flush=True)
    subprocess.run([sys.executable, "dff_opt.py", f"{load}"], check=True, cwd=Path(__file__).parent,
                   stdout=open(FINAL / "dff_opt.out", "w"), env={**os.environ, "OMP_NUM_THREADS": "1"})
    rows = list(csv.DictReader(open(RESULTS / "phase5_dff_sizing.csv")))
    best = rows[0]
    params = {k: float(best[k]) for k in ("s1", "s2", "s3", "q")}
    cell = tspc(params["s1"], params["s2"], params["s3"], params["q"])
    sch = characterise(cell, load_ff=load)

    from run_layout_cells import layout_cell
    row = layout_cell(cell, work=cfg.PART1 / "layout" / "individual_blocks")
    if row["drc"] or not row["lvs"]:
        raise RuntimeError(f"flip-flop layout: {row}")
    ext = ExtractedCell(cfg.PART1 / "layout" / "individual_blocks" / cell.name / f"{cell.name}.spice", "dffx", ["d", "clk"], ["q"])
    post_row = characterise(ext, load_ff=load)
    out = dict(params=params, load_ff=load, pin_loads=total, schematic=_plain(sch), postlayout=_plain(post_row), layout=_plain(row))
    (FINAL / "dff.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out)[:700])


def _plain(d):
    return {k: (float(v) if isinstance(v, (np.floating,)) else v) for k, v in d.items()}


def _free_inputs(cell_inputs):
    """Inputs that move freely; an input named Xb with X present follows as its complement."""
    return [p for p in cell_inputs if not (p.endswith("b") and p[:-1] in cell_inputs)]


def block_delay(target, schematic_devices_flat, inputs, outputs, work, tag):
    """All single-input transitions of one block, through unit drivers, outputs loaded by the 20L/10L inverter."""
    from cellgen.bench import pwl_lines
    from cellgen.sim import run_ngspice
    from cellgen.switchlevel import evaluate
    from arcs import crossings, euler_walk
    work = Path(work)
    work.mkdir(parents=True, exist_ok=True)
    free = _free_inputs(inputs)
    walk = euler_walk(len(free)) if len(free) > 1 else [0, 1, 0]
    vectors = []
    for state in walk:
        vec = {p: (state >> k) & 1 for k, p in enumerate(free)}
        for p in inputs:
            if p not in vec:
                vec[p] = 1 - vec[p[:-1]]
        vectors.append(vec)
    period = 2.0e-9
    model = os.path.relpath(cfg.PART1 / "spice" / "models" / "TSMC_180nm.txt", work)
    net = (f"* block timing {tag}\n.include {model}\n.options reltol=1e-4\nVDD vdd gnd 1.8\n" + target.spice() +
           ".subckt tb_x1 a y vdd gnd\nmp y a vdd vdd CMOSP W=1.8e-06 L=1.8e-07 AS=9.72e-13 PS=4.68e-06 AD=9.72e-13 PD=4.68e-06\n"
           "mn y a gnd gnd CMOSN W=9.0e-07 L=1.8e-07 AS=4.86e-13 PS=2.88e-06 AD=4.86e-13 PD=2.88e-06\n.ends\n")
    for p in inputs:
        net += pwl_lines(f"V{p}", f"src_{p}", [v[p] for v in vectors], period, 20e-12)
        net += f"Xd_{p} src_{p} {p} vdd gnd tb_x1\n"
    for o in outputs:
        net += f"Xl_{o} {o} lo_{o} vdd gnd tb_x1\n"
    net += f"X0 {' '.join(target.ports[:-2])} vdd gnd {target.name}\n"
    probes = " ".join(f"v({n})" for n in inputs + outputs)
    total = len(vectors) * period
    maxstep = "20p" if total < 0.5e-6 else "200p"
    net += f".tran {maxstep} {total:.5e}\n.control\nset wr_singlescale\nset wr_vecnames\nrun\nwrdata {tag}.txt {probes}\nquit\n.endc\n.end\n"
    cir = work / f"{tag}.cir"
    cir.write_text(net)
    _, res = run_ngspice(cir, timeout=3000)
    wave = work / f"{tag}.txt"
    if not wave.exists() or "too small" in res.stderr:
        raise RuntimeError(f"{tag}: {res.stderr[-300:]}")
    names = wave.read_text().split("\n", 1)[0].split()
    data = np.loadtxt(wave, skiprows=1)
    wave.unlink()
    col = {n.lower(): i for i, n in enumerate(names)}
    t = data[:, 0]
    worst = dict(tplh_ps=0.0, tphl_ps=0.0)
    errors = 0
    for k in range(1, len(vectors)):
        changed = [p for p in free if vectors[k][p] != vectors[k - 1][p]]
        if not changed:
            continue
        lo, hi = np.searchsorted(t, [k * period, (k + 1) * period])
        tw = t[lo:hi + 1]
        tin = crossings(tw, data[lo:hi + 1, col[f"v({changed[0]})"]])
        old, _ = evaluate(schematic_devices_flat, vectors[k - 1])
        new, _ = evaluate(schematic_devices_flat, vectors[k])
        for o in outputs:
            v = data[lo:hi + 1, col[f"v({o})"]]
            if (new[o] and v[-1] < 1.62) or (not new[o] and v[-1] > 0.18):
                errors += 1
            if old[o] == new[o]:
                continue
            cr = crossings(tw, v)
            if len(cr):
                key = "tplh_ps" if new[o] else "tphl_ps"
                worst[key] = max(worst[key], (cr[-1] - tin[0]) * 1e12)
    worst["functional_errors"] = errors
    worst["transitions"] = len(vectors) - 1
    return {k: (round(v, 2) if isinstance(v, float) else v) for k, v in worst.items()}


def stage_blocks():
    """Task 5: each block's schematic delay against the extracted layout's delay."""
    from cellgen import Block, parse_flat
    from run_layout_cells import layout_cell
    label, sizes, flips, tag = final_design()
    adder = build(label, sizes, flips, "cla_final")
    ports = INPUTS + OUTPUTS
    rows_spec = adder_rows(adder)
    tiles = [t for row in partition(adder, rows_spec, ports) for t in row]
    driven = {}
    for _, cell, pins in adder.instances:
        for o in cell.outputs:
            driven[pins[o]] = True
    out_rows = []
    base = cfg.PART1 / "layout" / "individual_blocks"
    for tile in tiles:
        # a net made by an instance in the tile is one of its outputs
        made = {pins[o] for _, cell, pins in tile.instances for o in cell.outputs}
        outputs = sorted(n for n in tile.inputs if n in made)
        inputs = sorted(n for n in tile.inputs if n not in made)
        block = Block(tile.name + "_b", inputs, outputs, None, tile.instances, tile.description)
        lay = layout_cell(block, work=base)
        if lay["drc"] or not lay["lvs"]:
            raise RuntimeError(f"{tile.name}: {lay}")
        flat = parse_flat(block.spice(), block.name)
        sch = block_delay(block, flat, inputs, outputs, cfg.PART1 / "simulations" / "timing" / "blocks", f"{tile.name}_sch")
        ext = ExtractedCell(base / block.name / f"{block.name}.spice", f"{tile.name}x", inputs, outputs)
        post = block_delay(ext, flat, inputs, outputs, cfg.PART1 / "simulations" / "timing" / "blocks", f"{tile.name}_post")
        row = dict(block=tile.name, transistors=block.transistor_count, width_lambda=lay["width_lambda"],
                   height_lambda=lay["height_lambda"], area_um2=lay["area_um2"], drc=lay["drc"], lvs=lay["lvs"],
                   transitions=sch["transitions"], sch_tplh_ps=sch["tplh_ps"], sch_tphl_ps=sch["tphl_ps"],
                   post_tplh_ps=post["tplh_ps"], post_tphl_ps=post["tphl_ps"],
                   sch_errors=sch["functional_errors"], post_errors=post["functional_errors"])
        out_rows.append(row)
        print(row, flush=True)
    with open(RESULTS / "phase7_block_postlayout.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(out_rows[0].keys()))
        writer.writeheader()
        writer.writerows(out_rows)


def _critical_pairs(arcs_path, count=30):
    rows = list(csv.DictReader(open(arcs_path)))
    rows.sort(key=lambda r: -float(r["tpd_pin_ps"]))
    pairs, seen = [], set()
    for r in rows:
        key = (int(r["state"]), int(r["next_state"]) if r.get("next_state") else None)
        if key in seen or key[1] is None:
            continue
        seen.add(key)
        pairs.append(key)
        if len(pairs) == count:
            break
    return pairs


def stage_system():
    """Registered system, schematic and extracted: frequency search and power."""
    label, sizes, flips, tag = final_design()
    dff = json.loads((FINAL / "dff.json").read_text())
    p = dff["params"]
    ff = tspc(p["s1"], p["s2"], p["s3"], p["q"])
    adder = build(label, sizes, flips, "cla_final")
    top = registered_top(adder, ff, "reg_final")
    ports = REG_INPUTS + REG_OUTPUTS
    groups = [[(f"fi{q}", [f"fi_{q}"]) for q in ("a0", "b0", "a1", "b1", "a2", "b2", "a3", "b3", "c0")]] + adder_rows(adder) + \
             [[(f"fo{q}", [f"fo_{q}"]) for q in OUTPUTS]]
    tiles = partition(top, groups, ports)
    work = cfg.PART1 / "layout" / "integrated" / "registered"
    if work.exists():
        shutil.rmtree(work)
    res = assemble("reg_final_top", tiles, top, ports, work, align={3: 1, 4: 1})
    print({k: v for k, v in res.items() if k != "placements"}, flush=True)
    if res["drc"] or not res["lvs"]:
        raise RuntimeError(f"registered layout: {res['drc']} {res['lvs_message']} {res['drc_first'][:3]}")
    ext = ExtractedCell(work / "reg_final_top.spice", "reg_final", REG_INPUTS, REG_OUTPUTS)
    crit = _critical_pairs(cfg.PART1 / "simulations" / "timing" / f"post_{tag}" / "arcs.csv")
    states = vector_set(critical_states=crit, count=200)
    sim_dir = cfg.PART1 / "simulations" / "timing" / "registered"
    post = json.loads((FINAL / f"{tag}_post.json").read_text())

    out = dict(layout={k: v for k, v in res.items() if k != "placements"}, placements=res["placements"], vectors=len(states),
               wire_cap_ff=round(ext.cap_total_ff, 1))
    for name, circuit in (("schematic", top), ("postlayout", ext)):
        t_ok, good, history = find_failing_period(circuit, states, sim_dir / name, name, high=1.25e-9, low=0.5e-9)
        rerun = run_system(circuit, t_ok, states, sim_dir / name, f"{name}_at_limit", plot=True)
        out[name] = dict(min_period_ps=round(t_ok * 1e12, 1), fmax_ghz=round(1e-9 / t_ok * 1, 4), errors_at_limit=rerun["errors"],
                         pavg_mw_random=round(rerun["pavg_w"] * 1e3, 4), history=[(h["period_ps"], h["errors"]) for h in history])
        print(name, out[name], flush=True)
    # course formula, from post-layout values
    tpd = post["worst_pin_ps"]
    tsu = dff["postlayout"]["tsu_ps"]
    th = dff["postlayout"]["thold_ps"]
    tcq = dff["postlayout"]["tcq_ps"]
    t_course = tpd + tsu + th
    t_phys = tcq + tpd + tsu
    out["course"] = dict(tpd_max_ps=tpd, tsetup_ps=tsu, thold_ps=th, tcq_ps=tcq, T_course_ps=round(t_course, 1),
                         fmax_course_ghz=round(1e3 / t_course, 4), T_physical_ps=round(t_phys, 1),
                         fmax_physical_ghz=round(1e3 / t_phys, 4))
    check = run_system(ext, t_course * 1e-12, states, sim_dir / "postlayout", "at_course_formula", plot=True)
    out["course"]["errors_at_course_formula"] = check["errors"]
    out["course"]["note_at_course_formula"] = check.get("note", "")
    out["course"]["pavg_mw_at_course_formula"] = round(check.get("pavg_w", float("nan")) * 1e3, 4)
    # power at the verified limit, for two kinds of switching activity
    t_ok = out["postlayout"]["min_period_ps"] * 1e-12
    hint_seq = []
    a15 = 0b1111
    for _ in range(40):
        hint_seq += [a15, a15 | 1 << 8]
    hint = run_system(ext, t_ok, hint_seq, sim_dir / "postlayout", "power_hint")
    idle = run_system(ext, t_ok, [a15] * 40, sim_dir / "postlayout", "power_idle")
    tp = tpd * 1e-12
    random_p = out["postlayout"]["pavg_mw_random"] * 1e-3
    out["power"] = dict(period_ps=round(t_ok * 1e12, 1), vdd=cfg.VDD,
                        random=dict(cycles=len(states), pavg_mw=round(random_p * 1e3, 4), pdp_fj=round(random_p * tp * 1e15, 2)),
                        hint=dict(cycles=len(hint_seq), pavg_mw=round(hint["pavg_w"] * 1e3, 4), errors=hint["errors"],
                                  pdp_fj=round(hint["pavg_w"] * tp * 1e15, 2)),
                        idle_inputs=dict(cycles=40, pavg_mw=round(idle["pavg_w"] * 1e3, 4), errors=idle["errors"],
                                         note="inputs constant; clock and flip-flop power only"))
    area = out["layout"]["area_um2"]
    out["adp_um2_ps_adder"] = round(post["area_um2"] * tpd, 0)
    out["adp_um2_ps_registered"] = round(area * tpd, 0)
    (FINAL / "system.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out["course"]), json.dumps(out["power"]), flush=True)


def complete_digraph_walk(n=512):
    """Eulerian circuit visiting every ordered pair of distinct states once."""
    nxt = {v: 0 for v in range(n)}
    stack, path = [0], []
    while stack:
        v = stack[-1]
        if nxt[v] < n:
            w = nxt[v]
            nxt[v] += 1
            if w != v:
                stack.append(w)
        else:
            path.append(stack.pop())
    return path[::-1]


def stage_multi(stride="1"):
    """Ordered pairs of input states on the final adder, schematic. All pairs: 261,632 transitions.

    stride keeps every Nth segment of the walk, evenly spread, so that a sample is not biased
    towards the walk's start.

    Registers launch all inputs together, so several may change at once. Delay is from the
    earliest changing input. Arcs below 85 % of the single-input worst are not stored.
    """
    from concurrent.futures import ThreadPoolExecutor
    from arcs import PERIOD, run_segment
    label, sizes, flips, tag = final_design()
    adder = build(label, sizes, flips, "cla_final")
    if (FINAL / f"{tag}_post.json").exists():
        adder.net_caps = dict(json.loads((FINAL / f"{tag}_post.json").read_text())["net_caps"])
    baseline = json.loads((FINAL / f"{tag}_post.json").read_text())["worst_pin_ps"]
    walk = complete_digraph_walk()
    print("transitions", len(walk) - 1, flush=True)
    work = cfg.PART1 / "simulations" / "timing" / "multi_input"
    work.mkdir(parents=True, exist_ok=True)
    size = 240
    jobs = [(walk[s:s + size + 1], work / f"m{s // size:04d}.cir") for s in range(0, len(walk) - 1, size)]
    jobs = jobs[:: int(stride)]

    def run(job):
        arcs, functional = run_segment(adder, job[0], job[1], multi=True, keep_above=0.85 * baseline)
        for suffix in (".cir", ".log"):
            job[1].with_suffix(suffix).unlink(missing_ok=True)
        return arcs, functional

    with ThreadPoolExecutor(9) as ex:
        results = list(ex.map(run, jobs))
    arcs = [a for r in results for a in r[0]]
    functional = sum(r[1] for r in results)
    arcs.sort(key=lambda a: -a["tpd_pin_ps"])
    write_arcs(arcs[:2000], work / "slowest_arcs.csv")
    worst = arcs[0] if arcs else None
    out = dict(segments=len(jobs), stride=int(stride), all_transitions=len(walk) - 1,
               transitions=sum(len(j[0]) - 1 for j in jobs), functional_errors=functional,
               stored_arcs=len(arcs), threshold_ps=round(0.85 * baseline, 1),
               worst_ps=round(worst["tpd_pin_ps"], 2) if worst else None, worst=worst,
               note="schematic with extracted wire load annotated")
    (FINAL / "multi.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(out, default=float)[:500])


def stage_verify_multi():
    """Re-simulate the slowest multi-input transitions on the extracted layout."""
    from arcs import run_segment
    label, sizes, flips, tag = final_design()
    multi = cfg.PART1 / "simulations" / "timing" / "multi_input" / "slowest_arcs.csv"
    rows = list(csv.DictReader(open(multi)))
    states, seen = [], set()
    for r in rows:
        key = (int(r["state"]), int(r["next_state"]))
        if key not in seen:
            seen.add(key)
            states += [key[0], key[1]]
        if len(seen) == 100:
            break
    # add a neutral settling step between the chosen pairs
    work = cfg.PART1 / "simulations" / "timing" / "multi_verify"
    work.mkdir(parents=True, exist_ok=True)
    ext = ExtractedCell(cfg.PART1 / "layout" / "integrated" / tag / f"top_{tag}.spice", "post_verify", INPUTS, OUTPUTS)
    # pairs are not consecutive states: step through them so that only the chosen pair is measured
    sequence = []
    for i in range(0, len(states), 2):
        sequence += [states[i], states[i + 1]]
    arcs, functional = run_segment(ext, sequence, work / "verify.cir", multi=True)
    chosen = set(seen)
    arcs = [a for a in arcs if (a["state"], a["next_state"]) in chosen]
    arcs.sort(key=lambda a: -a["tpd_pin_ps"])
    write_arcs(arcs, work / "arcs.csv")
    out = dict(pairs=len(seen), functional_errors=functional, worst=arcs[0], worst_ps=round(arcs[0]["tpd_pin_ps"], 2))
    (FINAL / "multi_verify.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(out, default=float))


def stage_compare(*labels):
    """Lay out sized designs and measure post-layout delay, so choices rest on layout results."""
    rows = []
    for label in labels:
        d = json.loads((cfg.PART1 / "simulations" / "optimisation" / label / "summary.json").read_text())
        base = d.get("config", label).split("__")[0]
        s = layout_adder(base, d["sizes"], d["flips"], f"cmp_{label}")
        (FINAL / f"cmp_{label}.json").write_text(json.dumps(s, indent=1))
        row = dict(design=label, transistors=d["transistors"], total_width_lambda=d["total_width_lambda"],
                   sch_pin_ps=round(d["worst_pin_ps"], 1), sch_drv_ps=round(d["worst_drv_ps"], 1), post_pin_ps=s["worst_pin_ps"],
                   post_drv_ps=s["worst_drv_ps"], area_um2=s["area_um2"], wire_cap_ff=s["wire_cap_ff"],
                   adp_um2_ns=round(s["area_um2"] * s["worst_pin_ps"] * 1e-3, 1), worst_arc=s["worst_pin_arc"])
        rows.append(row)
        print(row, flush=True)
    path = RESULTS / "phase4_sized_comparison.csv"
    existing = list(csv.DictReader(open(path))) if path.exists() else []
    names = {r["design"] for r in rows}
    merged = [r for r in existing if r["design"] not in names] + rows
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(merged)


def adder_power(cell, work, tag, period=1.0e-9, count=200, seed=11):
    """Average adder supply power on random vectors at a fixed period, drivers and loads excluded."""
    import random
    from arcs import TB_CELLS
    from cellgen.bench import pwl_lines
    from cellgen.sim import run_ngspice
    work = Path(work)
    work.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    states = [rng.randrange(512) for _ in range(count)]
    model = os.path.relpath(cfg.PART1 / "spice" / "models" / "TSMC_180nm.txt", work)
    net = (f"* Adder power {tag}\n.include {model}\n.options reltol=1e-3\nVDD vdd gnd 1.8\nVdut vdut gnd 1.8\n" + cell.spice() + TB_CELLS)
    for k, pin in enumerate(INPUTS):
        levels = [(s >> k) & 1 for s in states]
        net += pwl_lines(f"V{pin}", f"src_{pin}", [1 - b for b in levels], period, 20e-12)
        net += f"Xs_{pin} src_{pin} drv_{pin} vdd gnd tb_x1\nXd_{pin} drv_{pin} {pin} vdd gnd tb_x2\n"
    for out in OUTPUTS:
        net += f"Xl_{out} {out} lo_{out} vdd gnd tb_x1\n"
    net += f"X0 {' '.join(cell.ports[:-2])} vdut gnd {cell.name}\n"
    total = count * period
    net += f".tran 50p {total:.5e}\n.meas tran iavg AVG i(Vdut) FROM={period:.5e} TO={total:.5e}\n.end\n"
    cir = work / f"{tag}.cir"
    cir.write_text(net)
    values, res = run_ngspice(cir, timeout=1500)
    if "iavg" not in values:
        raise RuntimeError(f"{tag}: no current measurement {res.stderr[-200:]}")
    return abs(values["iavg"]) * cfg.VDD


def stage_tradeoff(label, *factors):
    """Scale the final sizes uniformly, lay out each, and record delay, area, ADP, power and PDP."""
    best = json.loads((FINAL / f"best_{label}.json").read_text())
    rows = []
    for f in factors:
        factor = float(f)
        sizes = {k: round(max(0.34, v * factor), 3) for k, v in best["sizes"].items()}
        tag = f"scale_{label}_{str(f).replace('.', 'p')}"
        s = layout_adder(label, sizes, best["flips"], tag)
        ext = ExtractedCell(cfg.PART1 / "layout" / "integrated" / tag / f"top_{tag}.spice", f"p_{tag}", INPUTS, OUTPUTS)
        p = adder_power(ext, cfg.PART1 / "simulations" / "timing" / "tradeoff", tag)
        width = build(label, sizes, best["flips"], "x").total_width_lam
        rows.append(dict(design=label, scale=factor, total_width_lambda=width, post_pin_ps=s["worst_pin_ps"], post_drv_ps=s["worst_drv_ps"],
                         area_um2=s["area_um2"], adp_um2_ns=round(s["area_um2"] * s["worst_pin_ps"] * 1e-3, 1),
                         power_mw_1ns=round(p * 1e3, 4), pdp_fj=round(p * s["worst_pin_ps"] * 1e-12 * 1e15, 1), worst_arc=s["worst_pin_arc"]))
        print(rows[-1], flush=True)
    path = RESULTS / "phase4_tradeoff.csv"
    existing = list(csv.DictReader(open(path))) if path.exists() else []
    keep = [r for r in existing if not (r["design"] == label and float(r["scale"]) in [float(x) for x in factors])]
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(keep + rows)


def stage_course():
    """Course fmax from the true worst found: the larger of single-input and verified multi-input."""
    system = json.loads((FINAL / "system.json").read_text())
    dff = json.loads((FINAL / "dff.json").read_text())
    label, sizes, flips, tag = final_design()
    post = json.loads((FINAL / f"{tag}_post.json").read_text())
    verify = json.loads((FINAL / "multi_verify.json").read_text())
    tpd = max(post["worst_pin_ps"], verify["worst_ps"])
    tsu, th, tcq = dff["postlayout"]["tsu_ps"], dff["postlayout"]["thold_ps"], dff["postlayout"]["tcq_ps"]
    t_course, t_phys = tpd + tsu + th, tcq + tpd + tsu
    work = cfg.PART1 / "layout" / "integrated" / "registered"
    ext = ExtractedCell(work / "reg_final_top.spice", "reg_final", REG_INPUTS, REG_OUTPUTS)
    crit = _critical_pairs(cfg.PART1 / "simulations" / "timing" / f"post_{tag}" / "arcs.csv")
    states = vector_set(critical_states=crit, count=200)
    sim_dir = cfg.PART1 / "simulations" / "timing" / "registered" / "postlayout"
    check = run_system(ext, t_course * 1e-12, states, sim_dir, "at_course_formula", plot=True)
    system["course"] = dict(tpd_max_ps=round(tpd, 2), tpd_single_input_ps=post["worst_pin_ps"], tpd_multi_input_ps=verify["worst_ps"],
                            tsetup_ps=tsu, thold_ps=th, tcq_ps=tcq, T_course_ps=round(t_course, 1), fmax_course_ghz=round(1e3 / t_course, 4),
                            T_physical_ps=round(t_phys, 1), fmax_physical_ghz=round(1e3 / t_phys, 4),
                            errors_at_course_formula=check["errors"], note_at_course_formula=check.get("note", ""))
    (FINAL / "system.json").write_text(json.dumps(system, indent=1))
    print(system["course"])


def stage_power():
    """Pavg and PDP at the verified limit, circuit under test only, three kinds of activity."""
    system = json.loads((FINAL / "system.json").read_text())
    label, sizes, flips, tag = final_design()
    work = cfg.PART1 / "layout" / "integrated" / "registered"
    ext = ExtractedCell(work / "reg_final_top.spice", "reg_final", REG_INPUTS, REG_OUTPUTS)
    t_ok = system["postlayout"]["min_period_ps"] * 1e-12
    tpd = system["course"]["tpd_max_ps"] * 1e-12
    crit = _critical_pairs(cfg.PART1 / "simulations" / "timing" / f"post_{tag}" / "arcs.csv")
    states = vector_set(critical_states=crit, count=200)
    a15 = 0b1111
    hint_seq = [a15, a15 | 1 << 8] * 40
    sim_dir = cfg.PART1 / "simulations" / "timing" / "registered" / "power"
    out = dict(period_ps=round(t_ok * 1e12, 1), frequency_ghz=round(1e-9 / t_ok, 4), vdd=cfg.VDD)
    for name, seq in (("critical_and_random", states), ("hint_vector_toggling", hint_seq), ("inputs_constant", [a15] * 40)):
        r = run_system(ext, t_ok, seq, sim_dir, f"p_{name}")
        out[name] = dict(cycles=len(seq), errors=r["errors"], pavg_mw=round(r["pavg_w"] * 1e3, 4),
                         energy_per_cycle_pj=round(r["pavg_w"] * t_ok * 1e12, 3),
                         pdp_fj=round(r["pavg_w"] * tpd * 1e15, 2), interval_ns=[round(r["meas_from"] * 1e9, 3), round(r["meas_to"] * 1e9, 3)])
        print(name, out[name], flush=True)
    system["power"] = out
    (FINAL / "system.json").write_text(json.dumps(system, indent=1))


def stage_sch_final():
    """All transitions on the final adder's schematic, with no wire load, for the comparison table."""
    label, sizes, flips, tag = final_design()
    adder = build(label, sizes, flips, "cla_final")
    arcs, functional = all_arcs(adder, cfg.PART1 / "simulations" / "timing" / "final_schematic", workers=8)
    write_arcs(arcs, cfg.PART1 / "simulations" / "timing" / "final_schematic" / "arcs.csv")
    summary = arcs_summary(arcs)
    summary["functional_errors"] = functional
    summary["transistors"] = adder.transistor_count
    summary["total_width_lambda"] = adder.total_width_lam
    (FINAL / "final_schematic.json").write_text(json.dumps(summary, indent=1, default=float))
    print(summary)


def stage_functional():
    """All 512 input combinations on the final adder, twice, schematic and extracted."""
    from cellgen.bench import run_truth_table, write_results
    from itertools import product
    label, sizes, flips, tag = final_design()
    adder = build(label, sizes, flips, "cla_final")
    ext = ExtractedCell(cfg.PART1 / "layout" / "integrated" / tag / f"top_{tag}.spice", "final_post", INPUTS, OUTPUTS)
    ext.truth = adder_logic
    ext.vectors = lambda: [dict(zip(INPUTS, bits)) for bits in product([0, 1], repeat=9)]
    rows = []
    base = cfg.PART1 / "simulations" / "functional" / "final"
    for name, cell in (("schematic", adder), ("postlayout", ext)):
        res = run_truth_table(cell, base / name, cfg.plot_title("1.6", f"final-adder-{name}"), period=3e-9)
        row = res[0] if isinstance(res, tuple) else res
        row["netlist"] = name
        rows.append(row)
        print(row, flush=True)
    with open(RESULTS / "final_truth_table.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def stage_design_power(*tags):
    """Power and PDP at the same conditions for finished post-layout designs. Tag is a layout folder."""
    rows = []
    for tag in tags:
        ext = ExtractedCell(cfg.PART1 / "layout" / "integrated" / tag / f"top_{tag}.spice", f"p_{tag}", INPUTS, OUTPUTS)
        p = adder_power(ext, cfg.PART1 / "simulations" / "timing" / "tradeoff", f"pow_{tag}")
        rows.append(dict(tag=tag, power_mw_1ns=round(p * 1e3, 4)))
        print(rows[-1], flush=True)
    with open(RESULTS / "phase4_design_power.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["tag", "power_mw_1ns"])
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    FINAL.mkdir(parents=True, exist_ok=True)
    globals()[f"stage_{sys.argv[1]}"](*sys.argv[2:])
