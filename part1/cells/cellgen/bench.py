"""Exhaustive transistor-level truth-table bench.

Every input is driven through a unit inverter, so drive strength is finite. Every
output drives the assignment's 20L/10L inverter. Vectors run once in binary order and
once in a seeded random order, so a result that depends on stored charge would show.
"""
import csv
import os
import random
import re
from pathlib import Path

import numpy as np

from . import config as cfg
from .sim import run_ngspice

VOH_MIN = 0.9 * cfg.VDD
VOL_MAX = 0.1 * cfg.VDD
STATIC_LIMIT_A = 1e-6
TB_INV = (".subckt tb_inv a y vdd gnd\n"
          "mp y a vdd vdd CMOSP W=1.8e-06 L=1.8e-07 AS=9.72e-13 PS=4.68e-06 AD=9.72e-13 PD=4.68e-06\n"
          "mn y a gnd gnd CMOSN W=9.0e-07 L=1.8e-07 AS=4.86e-13 PS=2.88e-06 AD=4.86e-13 PD=2.88e-06\n.ends\n")
PERIOD = 1.0e-9
EDGE = 50e-12


def pwl_lines(name, node, levels, period=PERIOD, edge=EDGE):
    """PWL source for the inverted level: the driver inverter restores the polarity."""
    v = [(cfg.VDD if b == 0 else 0.0) for b in levels]
    pts = [(0.0, v[0])]
    for k in range(1, len(v)):
        if v[k] != v[k - 1]:
            t = k * period
            pts += [(t, v[k - 1]), (t + edge, v[k])]
    pts.append((len(v) * period, v[-1]))
    body = [f"{t:.5e} {x:.3f}" for t, x in pts]
    out = [f"{name} {node} gnd PWL("]
    for i in range(0, len(body), 6):
        out.append("+ " + " ".join(body[i:i + 6]))
    out.append("+ )")
    return "\n".join(out) + "\n"


def run_truth_table(cell, out_dir, plot_title, period=PERIOD):
    """Returns (result row, waveforms). Netlist, log and compressed waveforms stay in out_dir."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    base = cell.vectors()
    shuffled = base[:]
    random.Random(1).shuffle(shuffled)
    vectors = base + shuffled
    total = len(vectors) * period
    model = os.path.relpath(cfg.PART1 / "spice" / "models" / "TSMC_180nm.txt", out_dir)
    net = (f"* Truth table of {cell.name}: inputs through unit inverters, outputs load 20L/10L inverter\n"
           f".include {model}\n.options reltol=1e-3\nVDD vdd gnd 1.8\n")
    net += cell.spice()
    net += TB_INV
    for pin in cell.inputs:
        net += pwl_lines(f"V{pin}", f"src_{pin}", [v[pin] for v in vectors], period)
        net += f"Xd_{pin} src_{pin} {pin} vdd gnd tb_inv\n"
    for out in cell.outputs:
        net += f"Xl_{out} {out} lo_{out} vdd gnd tb_inv\n"
    pins = " ".join(cell.inputs + cell.outputs)
    net += f"X0 {pins} vdd gnd {cell.name}\n"
    probes = " ".join(f"v({n})" for n in cell.inputs + cell.outputs)
    # ngspice sets its minimum step to 1e-11 x the maximum step. With a 2 ps maximum, that
    # falls below double-precision time resolution near 0.5 us and the run aborts. Accuracy
    # is still held by the adaptive error control, and every edge is a breakpoint.
    net += (f".tran 200p {total:.5e}\n.control\nset wr_singlescale\nset wr_vecnames\nrun\n"
            f"set curplottitle={plot_title}\nwrdata wave.txt {probes} i(VDD)\nquit\n.endc\n.end\n")
    cir = out_dir / "truth.cir"
    cir.write_text(net)
    _, result = run_ngspice(cir, timeout=1800)
    wave = out_dir / "wave.txt"
    if not wave.exists():
        wave_alt = out_dir / "wave.txt.data"
        if wave_alt.exists():
            wave = wave_alt
        else:
            return dict(cell=cell.name, transistors=cell.transistor_count, vectors=len(vectors),
                        errors=-1, min_voh=None, max_vol=None, max_static_ua=None, passed=False,
                        note=result.stderr[-200:])
    data = np.loadtxt(wave, skiprows=1)
    names = wave.read_text().split("\n", 1)[0].split()
    col = {n.lower(): i for i, n in enumerate(names)}
    t = data[:, 0]
    if t[-1] < total * 0.9999 or "too small" in result.stderr:
        return dict(cell=cell.name, transistors=cell.transistor_count, vectors=len(vectors), errors=-1,
                    min_voh=None, max_vol=None, max_static_ua=None, passed=False,
                    note=f"simulation aborted at {t[-1]:.3e} s: {result.stderr.strip()[:120]}")
    sample_times = (np.arange(len(vectors)) + 1) * period - 20e-12
    errors, voh, vol = 0, cfg.VDD, 0.0
    first_error = ""
    samples = {}
    for out in cell.outputs:
        samples[out] = np.interp(sample_times, t, data[:, col[f"v({out})".lower()]])
    for k, vec in enumerate(vectors):
        expected = cell.truth(vec)
        for out in cell.outputs:
            v = samples[out][k]
            if expected[out]:
                voh = min(voh, v)
                ok = v >= VOH_MIN
            else:
                vol = max(vol, v)
                ok = v <= VOL_MAX
            if not ok:
                errors += 1
                first_error = first_error or f"{out}={v:.3f} at {vec}"
    max_static = static_current(cell, out_dir, base)
    passed = errors == 0 and max_static <= STATIC_LIMIT_A
    np.savez_compressed(out_dir / "wave.npz", names=np.array(names), data=data.astype(np.float32))
    wave.unlink()
    return dict(cell=cell.name, transistors=cell.transistor_count, vectors=len(vectors), errors=errors,
                min_voh=round(float(voh), 4), max_vol=round(float(vol), 4),
                max_static_ua=round(max_static * 1e6, 5), passed=passed, note=first_error), (t, data, col)


def static_current(cell, out_dir, vectors):
    """Largest DC supply current over all vectors, from true operating points.

    Transient samples are unsuitable: trapezoidal integration rings on the supply branch
    at large time steps, which gave tens of microamps regardless of settling time. Each
    vector is applied by alter, with drivers as in the truth-table bench, and solved by op.
    """
    model = os.path.relpath(cfg.PART1 / "spice" / "models" / "TSMC_180nm.txt", out_dir)
    net = (f"* DC supply current of {cell.name}\n.include {model}\nVDD vdd gnd 1.8\n" + cell.spice() + TB_INV)
    first = vectors[0]
    for pin in cell.inputs:
        net += f"V{pin} src_{pin} gnd {cfg.VDD if first[pin] == 0 else 0.0}\n"
        net += f"Xd_{pin} src_{pin} {pin} vdd gnd tb_inv\n"
    for out in cell.outputs:
        net += f"Xl_{out} {out} lo_{out} vdd gnd tb_inv\n"
    net += f"X0 {' '.join(cell.inputs + cell.outputs)} vdd gnd {cell.name}\n.control\n"
    for vec in vectors:
        for pin in cell.inputs:
            net += f"alter V{pin} = {cfg.VDD if vec[pin] == 0 else 0.0}\n"
        net += 'op\nprint i(VDD) > dc_current.txt\n'.replace(">", ">>")
    net += "quit\n.endc\n.end\n"
    cir = out_dir / "static.cir"
    target = out_dir / "dc_current.txt"
    target.unlink(missing_ok=True)
    cir.write_text(net)
    run_ngspice(cir, timeout=1800)
    text = target.read_text() if target.exists() else ""
    values = [abs(float(m)) for m in re.findall(r"=\s*([-+0-9.eE]+)", text)]
    target.unlink(missing_ok=True)
    if len(values) != len(vectors):
        raise RuntimeError(f"{cell.name}: {len(values)} DC points for {len(vectors)} vectors")
    return max(values)


def write_results(rows, path):
    keys = ["cell", "transistors", "vectors", "errors", "min_voh", "max_vol", "max_static_ua", "passed", "note"]
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=keys, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
