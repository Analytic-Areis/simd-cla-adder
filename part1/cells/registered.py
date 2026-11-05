#!/usr/bin/env python3
"""Phase 6: the registered system of Figure 1(i), and its frequency search.

Nine input flip-flops (a, b and Cin), the adder, five output flip-flops. Each output Q
drives the assignment's inverter. Works on schematic and extracted netlists alike.
"""
import os
import random
from pathlib import Path

import numpy as np

from candidates import INPUTS, OUTPUTS, adder_logic
from cellgen import Block, config as cfg
from cellgen.sim import run_ngspice

REG_INPUTS = [f"d_{p}" for p in INPUTS] + ["clk"]
REG_OUTPUTS = [f"q_{p}" for p in OUTPUTS]


def registered_top(adder, dff, name=None):
    """Block with all flip-flops and adder instances at one level, ready for layout rows."""
    instances = []
    for pin in INPUTS:
        instances.append((f"fi_{pin}", dff, {"d": f"d_{pin}", "clk": "clk", "q": pin}))
    instances += list(adder.instances)
    for pin in OUTPUTS:
        instances.append((f"fo_{pin}", dff, {"d": pin, "clk": "clk", "q": f"q_{pin}"}))
    return Block(name or f"reg_{adder.name}", REG_INPUTS, REG_OUTPUTS, None, instances, "registered 4-bit adder, Figure 1(i)")


TB = """.subckt tb_x1 a y vdd gnd
mp y a vdd vdd CMOSP W=1.8e-06 L=1.8e-07 AS=9.72e-13 PS=4.68e-06 AD=9.72e-13 PD=4.68e-06
mn y a gnd gnd CMOSN W=9.0e-07 L=1.8e-07 AS=4.86e-13 PS=2.88e-06 AD=4.86e-13 PD=2.88e-06
.ends
.subckt tb_x8 a y vdd gnd
mp y a vdd vdd CMOSP W=14.4e-06 L=1.8e-07 AS=7.776e-12 PS=3.0e-05 AD=7.776e-12 PD=3.0e-05
mn y a gnd gnd CMOSN W=7.2e-06 L=1.8e-07 AS=3.888e-12 PS=1.548e-05 AD=3.888e-12 PD=1.548e-05
.ends
"""


def state_vec(state):
    return {pin: (state >> k) & 1 for k, pin in enumerate(INPUTS)}


def vector_set(critical_states=(), count=256, seed=7):
    """Sequence of 9-bit input states: hint vector first, then critical arcs, then random."""
    hint_a = 0b1111
    hint0, hint1 = hint_a, hint_a | (1 << 8)
    seq = [hint0, hint1, hint0, hint1]
    for pair in critical_states:
        seq += list(pair)
    rng = random.Random(seed)
    seq += [rng.randrange(512) for _ in range(count)]
    return seq


def run_system(top, period, states, work, tag, plot=None, setup_margin=0.25, extra_probes=(), on_wave=None, tstep="5p"):
    """Simulate at one clock period.

    Each input changes setup_margin x T before a rising edge, through a finite driver. An
    input captured at edge k must appear at the output flip-flops after edge k + 1.
    Returns dict with errors and Pavg. Pavg is the supply of the circuit under test only: input
    drivers, clock buffers and the load inverters' own supply current are on a separate source.
    """
    work = Path(work)
    work.mkdir(parents=True, exist_ok=True)
    model = os.path.relpath(cfg.PART1 / "spice" / "models" / "TSMC_180nm.txt", work)
    n = len(states)
    t0 = 2 * period
    edges = t0 + np.arange(n + 3) * period
    net = (f"* Registered system at T={period * 1e12:.1f} ps\n.include {model}\n.options reltol=1e-4\n"
           "VDD vdd_core gnd 1.8\nVsense vdd_core vdd 0\nVTB vtb gnd 1.8\n" + top.spice() + TB)
    edge = 15e-12
    for pin_index, pin in enumerate(INPUTS):
        pts = []
        first = 1.8 if (states[0] >> pin_index) & 1 == 0 else 0.0
        pts.append((0.0, first))
        current = first
        for k, st in enumerate(states):
            level = 1.8 if (st >> pin_index) & 1 == 0 else 0.0
            if level != current:
                tc = edges[k] - setup_margin * period
                if pts[-1][0] < tc:
                    pts += [(tc, current), (tc + edge, level)]
                current = level
        pts.append((edges[-1] + period, current))
        body = [f"{t:.5e} {v:.2f}" for t, v in pts]
        net += f"Vd_{pin} sd_{pin} gnd PWL(\n"
        for i in range(0, len(body), 6):
            net += "+ " + " ".join(body[i:i + 6]) + "\n"
        net += "+ )\n"
        net += f"Xdrv_{pin} sd_{pin} d_{pin} vtb gnd tb_x1\n"
    # clock: square wave through a strong buffer chain
    half = period / 2
    clock_pts = ["0 0"]
    for e in edges:
        clock_pts += [f"{e - 10e-12:.5e} 0", f"{e + 10e-12:.5e} 1.8", f"{e + half - 10e-12:.5e} 1.8", f"{e + half + 10e-12:.5e} 0"]
    # invert twice: a source with 1.8 means clock high after two inverters
    net += "Vclk sc gnd PWL(\n"
    for i in range(0, len(clock_pts), 6):
        net += "+ " + " ".join(clock_pts[i:i + 6]) + "\n"
    net += "+ )\nXc1 sc c1 vtb gnd tb_x1\nXc2 c1 clk vtb gnd tb_x8\n"
    pins = " ".join(top.ports[:-2])
    net += f"X0 {pins} vdd gnd {top.name}\n"
    for q in REG_OUTPUTS:
        net += f"Xl_{q} {q} lo_{q} vtb gnd tb_x1\n"
    total = edges[-1] + period
    probes = " ".join(f"v({p})" for p in REG_OUTPUTS + ["clk"] + [f"d_{q}" for q in INPUTS] + list(extra_probes))
    meas_from = edges[1]
    net += (f".tran {tstep} {total:.5e}\n"
            f".meas tran iavg AVG i(Vsense) FROM={meas_from:.5e} TO={edges[-1]:.5e}\n"
            ".control\nset wr_singlescale\nset wr_vecnames\nrun\n"
            f"set curplottitle={cfg.plot_title('1.6', tag)}\n"
            f"wrdata {tag}.txt {probes}\nquit\n.endc\n.end\n")
    cir = work / f"{tag}.cir"
    cir.write_text(net)
    values, res = run_ngspice(cir, timeout=3000)
    wave = work / f"{tag}.txt"
    if not wave.exists() or "too small" in res.stderr:
        return dict(period_ps=period * 1e12, errors=-1, note=res.stderr[-200:])
    names = wave.read_text().split("\n", 1)[0].split()
    col = {x.lower(): i for i, x in enumerate(names)}
    data = np.loadtxt(wave, skiprows=1)
    t = data[:, 0]
    errors, first_error = 0, ""
    expected_list = [adder_logic(state_vec(s)) for s in states]
    # state captured at edge k is at the input flip-flop outputs after edge k,
    # the sum is captured at edge k+1, and is valid just before edge k+2
    for k in range(n):
        sample = edges[k + 2] - 15e-12
        for out in OUTPUTS:
            v = np.interp(sample, t, data[:, col[f"v(q_{out})"]])
            want = expected_list[k][out]
            if (want and v < 0.9) or (not want and v > 0.9):
                errors += 1
                first_error = first_error or f"vector {k}: q_{out}={v:.2f}, wanted {want}"
    result = dict(period_ps=round(period * 1e12, 2), errors=errors, note=first_error,
                  iavg_a=abs(values.get("iavg", float("nan"))), pavg_w=abs(values.get("iavg", float("nan"))) * cfg.VDD,
                  vectors=n, meas_from=meas_from, meas_to=float(edges[-1]))
    if on_wave is not None:
        result["measured"] = on_wave(t, data, col, edges)
    if plot:
        np.savez_compressed(work / f"{tag}.npz", names=np.array(names), data=data.astype(np.float32))
    wave.unlink()
    return result


def find_failing_period(top, states, work, label, high=2.0e-9, low=0.2e-9, resolution=5e-12):
    """Binary search on period for correct operation. Assumes monotonic behaviour near the limit."""
    history = []
    good = None
    while high - low > resolution:
        mid = (high + low) / 2
        r = run_system(top, mid, states, work, f"{label}_T{int(mid * 1e13)}")
        history.append(r)
        print(label, "T", round(mid * 1e12, 1), "ps errors", r["errors"], r.get("note", "")[:70], flush=True)
        if r["errors"] == 0:
            high = mid
            good = r
        else:
            low = mid
    return high, good, history
