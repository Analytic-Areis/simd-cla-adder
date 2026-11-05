"""All-arc timing: every single-input-change transition of a 9-input adder.

The 4608 directed transitions form an Eulerian circuit of the 9-cube, so one continuous
walk covers each exactly once. The walk is split into segments, each run separately:
this keeps time values small enough for fine time steps and allows parallel runs.

Each input is driven: ideal source, shaper inverter x1, driver inverter x2, adder pin.
Two delays are reported:
  tpd_pin  from the adder pin to the output, as the course defines delay
  tpd_drv  from the driver's input to the output, which includes the driver's own delay
           and so charges each design for its input capacitance
Delay uses the final 50 % crossing of the output, so false sums do not shorten it.
"""
import csv
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

from cellgen import config as cfg
from cellgen.bench import pwl_lines
from cellgen.sim import run_ngspice
from candidates import INPUTS, OUTPUTS, adder_logic

HALF = cfg.VDD / 2
PERIOD = 2.0e-9
SEGMENT = 240

TB_CELLS = """.subckt tb_x1 a y vdd gnd
mp y a vdd vdd CMOSP W=1.8e-06 L=1.8e-07 AS=9.72e-13 PS=4.68e-06 AD=9.72e-13 PD=4.68e-06
mn y a gnd gnd CMOSN W=9.0e-07 L=1.8e-07 AS=4.86e-13 PS=2.88e-06 AD=4.86e-13 PD=2.88e-06
.ends
.subckt tb_x2 a y vdd gnd
mp y a vdd vdd CMOSP W=3.6e-06 L=1.8e-07 AS=1.944e-12 PS=8.28e-06 AD=1.944e-12 PD=8.28e-06
mn y a gnd gnd CMOSN W=1.8e-06 L=1.8e-07 AS=9.72e-13 PS=4.68e-06 AD=9.72e-13 PD=4.68e-06
.ends
"""


def euler_walk(n=9):
    """Hierholzer on the directed n-cube. Returns the visited states, length 2**n * n + 1."""
    next_bit = {v: 0 for v in range(2 ** n)}
    stack, path = [0], []
    while stack:
        v = stack[-1]
        if next_bit[v] < n:
            bit = next_bit[v]
            next_bit[v] += 1
            stack.append(v ^ (1 << bit))
        else:
            path.append(stack.pop())
    return path[::-1]


def state_to_vec(state):
    return {pin: (state >> k) & 1 for k, pin in enumerate(INPUTS)}


def build_bench(adder, states, path, period=PERIOD, reltol="1e-4"):
    model = os.path.relpath(cfg.PART1 / "spice" / "models" / "TSMC_180nm.txt", path.parent)
    vectors = [state_to_vec(s) for s in states]
    total = len(states) * period
    net = (f"* All-arc segment for {adder.name}\n.include {model}\n.options reltol={reltol}\nVDD vdd gnd 1.8\n"
           + adder.spice() + TB_CELLS)
    for pin in INPUTS:
        # the source is inverted once more by the bench: two inverters give the true level at the pin
        levels = [v[pin] for v in vectors]
        net += pwl_lines(f"V{pin}", f"src_{pin}", [1 - b for b in levels], period, 20e-12)
        net += f"Xs_{pin} src_{pin} drv_{pin} vdd gnd tb_x1\nXd_{pin} drv_{pin} {pin} vdd gnd tb_x2\n"
    for out in OUTPUTS:
        net += f"Xl_{out} {out} lo_{out} vdd gnd tb_x1\n"
    net += f"X0 {' '.join(adder.ports[:-2])} vdd gnd {adder.name}\n"
    probes = " ".join(f"v({n})" for n in INPUTS + [f"drv_{p}" for p in INPUTS] + OUTPUTS)
    net += (f".tran 20p {total:.5e}\n.control\nset wr_singlescale\nset wr_vecnames\nrun\n"
            f"wrdata {path.stem}.txt {probes}\nquit\n.endc\n.end\n")
    path.write_text(net)
    return vectors


def crossings(t, v, level=HALF):
    """All times v crosses level, with linear interpolation."""
    above = v >= level
    idx = np.nonzero(above[1:] != above[:-1])[0]
    return t[idx] + (level - v[idx]) * (t[idx + 1] - t[idx]) / (v[idx + 1] - v[idx])


def run_segment(adder, states, path, first_step=0, period=PERIOD, reltol="1e-4", multi=False, keep_above=0.0):
    """multi: also measure transitions where several inputs change, from the earliest input.
    keep_above: discard arcs faster than this many ps, so very long sweeps stay small."""
    vectors = build_bench(adder, states, path, period, reltol)
    _, result = run_ngspice(path, timeout=3000)
    wave = path.with_suffix(".txt")
    if not wave.exists() or "too small" in result.stderr:
        raise RuntimeError(f"{path.name}: simulation failed: {result.stderr[-200:]}")
    names = wave.read_text().split("\n", 1)[0].split()
    data = np.loadtxt(wave, skiprows=1)
    wave.unlink()
    col = {n.lower(): i for i, n in enumerate(names)}
    t = data[:, 0]
    total = len(states) * period
    if t[-1] < total * 0.9999:
        raise RuntimeError(f"{path.name}: stopped at {t[-1]:.3e}")
    arcs, functional = [], 0
    series = {n: data[:, col[f"v({n})"]] for n in INPUTS + OUTPUTS}
    drv = {p: data[:, col[f"v(drv_{p})"]] for p in INPUTS}
    for k in range(1, len(states)):
        lo, hi = np.searchsorted(t, [k * period, (k + 1) * period])
        tw = t[lo:hi + 1]
        changed = [p for p in INPUTS if vectors[k][p] != vectors[k - 1][p]]
        if not changed or (len(changed) != 1 and not multi):  # a set-up step, or a repeated state
            continue
        first_pin, first_drv = None, None
        for candidate in changed:
            t_pin = crossings(tw, series[candidate][lo:hi + 1])
            t_drv = crossings(tw, drv[candidate][lo:hi + 1])
            if len(t_pin) < 1 or len(t_drv) < 1:
                raise RuntimeError(f"no input crossing at step {k}")
            if first_pin is None or t_pin[0] < first_pin:
                first_pin, pin = t_pin[0], candidate
            if first_drv is None or t_drv[0] < first_drv:
                first_drv = t_drv[0]
        old, new = adder_logic(vectors[k - 1]), adder_logic(vectors[k])
        for out in OUTPUTS:
            v = series[out][lo:hi + 1]
            settled = v[-1]
            if (new[out] and settled < 0.9 * cfg.VDD) or (not new[out] and settled > 0.1 * cfg.VDD):
                functional += 1
            if old[out] == new[out]:
                continue
            cross = crossings(tw, v)
            if len(cross) == 0:
                functional += 1
                continue
            tout = cross[-1]
            tpd_pin = (tout - first_pin) * 1e12
            if tpd_pin < keep_above:
                continue
            arcs.append(dict(pin=pin, pin_edge="rise" if vectors[k][pin] else "fall",
                             state=sum(vectors[k - 1][q] << n for n, q in enumerate(INPUTS)),
                             next_state=sum(vectors[k][q] << n for n, q in enumerate(INPUTS)),
                             inputs_changed=len(changed),
                             output=out, out_edge="rise" if new[out] else "fall",
                             tpd_pin_ps=tpd_pin, tpd_drv_ps=(tout - first_drv) * 1e12,
                             extra_crossings=len(cross) - 1))
    return arcs, functional


def all_arcs(adder, out_dir, workers=8):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    walk = euler_walk()
    jobs = []
    for start in range(0, len(walk) - 1, SEGMENT):
        states = walk[start:start + SEGMENT + 1]
        jobs.append((states, out_dir / f"seg{start // SEGMENT:02d}.cir", start))
    with ThreadPoolExecutor(workers) as ex:
        results = list(ex.map(lambda j: run_segment(adder, *j), jobs))
    arcs = [a for r in results for a in r[0]]
    functional = sum(r[1] for r in results)
    return arcs, functional


def write_arcs(arcs, path):
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(arcs[0].keys()))
        writer.writeheader()
        writer.writerows(arcs)


def describe_state(state):
    bits = {pin: (state >> k) & 1 for k, pin in enumerate(INPUTS)}
    a = "".join(str(bits[f"a{i}"]) for i in range(3, -1, -1))
    b = "".join(str(bits[f"b{i}"]) for i in range(3, -1, -1))
    return f"A={a} B={b} C0={bits['c0']}"
