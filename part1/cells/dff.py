#!/usr/bin/env python3
"""Phase 5: flip-flop cells and their timing characterisation.

Definitions, all in ps, measured at 50 % VDD:
  tcq    clock rising to Q, with data well before the clock
  tsu    smallest D-to-clock time for which clock-to-Q stays within 10 % of tcq and Q is correct
  thold  smallest clock-to-D time after which a data change no longer disturbs Q: Q must be
         correct, with any disturbance staying below 10 % of VDD
  tdq    data-to-Q delay; its minimum over D-to-clock time marks the optimal setup point
         (Stojanovic and Oklobdzija, IEEE JSSC 1999)
Each is found for both data values, and the larger is reported.
"""
import csv
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

from cellgen import D, GateStage, Pa, S, StagedCell, TGStage, config as cfg
from cellgen.sim import run_ngspice
from library import _fmt

OUT = cfg.PART1 / "simulations" / "timing" / "dff"
VDD = cfg.VDD
HALF = VDD / 2


def _dff_logic(_):
    raise NotImplementedError("sequential cell: checked by simulation")


def tspc(s1=1.0, s2=1.0, s3=1.0, q=2.0):
    """True single-phase clock flip-flop, 11T. Positive edge. Dynamic internal nodes."""
    return StagedCell(f"dff_tspc_x{_fmt(s1, s2, s3, q)}", ["d", "clk"], ["q"], _dff_logic, [
        GateStage(D("d"), "a", pun=S(D("d"), D("clk")), drive=s1),
        GateStage(S(D("a"), D("clk")), "b", pun=D("clk"), drive=s2),
        GateStage(S(D("clk"), D("b")), "qb", pun=D("b"), drive=s3),
        GateStage(D("qb"), "q", drive=q),
    ], "TSPC positive-edge flip-flop")


def tg_ms(core=1.0, q=2.0):
    """Static transmission-gate master-slave flip-flop, 22T, with weak feedback inverters."""
    weak = 0.35
    wn, wp = max(3, round(10 * core)), max(3, round(20 * core))
    fn, fp = max(3, round(10 * weak)), max(3, round(20 * weak))
    return StagedCell(f"dff_tgms_x{_fmt(core, q)}", ["d", "clk"], ["q"], _dff_logic, [
        GateStage(D("clk"), "clkb", drive=core),
        GateStage(D("d"), "dn", drive=core),
        TGStage("dn", "x", "clkb", "clk", wn, wp),
        GateStage(D("x"), "y", drive=core),
        GateStage(D("y"), "f", drive=weak),
        TGStage("f", "x", "clk", "clkb", fn, fp),
        TGStage("y", "z", "clk", "clkb", wn, wp),
        GateStage(D("z"), "w", drive=core),
        GateStage(D("w"), "g", drive=weak),
        TGStage("g", "z", "clkb", "clk", fn, fp),
        GateStage(D("w"), "q", drive=q),
    ], "static transmission-gate master-slave flip-flop")


TB = """.subckt tb_x1 a y vdd gnd
mp y a vdd vdd CMOSP W=1.8e-06 L=1.8e-07 AS=9.72e-13 PS=4.68e-06 AD=9.72e-13 PD=4.68e-06
mn y a gnd gnd CMOSN W=9.0e-07 L=1.8e-07 AS=4.86e-13 PS=2.88e-06 AD=4.86e-13 PD=2.88e-06
.ends
.subckt tb_x4 a y vdd gnd
mp y a vdd vdd CMOSP W=7.2e-06 L=1.8e-07 AS=3.888e-12 PS=1.548e-05 AD=3.888e-12 PD=1.548e-05
mn y a gnd gnd CMOSN W=3.6e-06 L=1.8e-07 AS=1.944e-12 PS=8.28e-06 AD=1.944e-12 PD=8.28e-06
.ends
"""


def _crossings(t, v, level=HALF):
    above = v >= level
    idx = np.nonzero(above[1:] != above[:-1])[0]
    return t[idx] + (level - v[idx]) * (t[idx + 1] - t[idx]) / (v[idx + 1] - v[idx])


class Bench:
    """One flip-flop event. The clock has rising edges at T_EDGE0 (loads the old value) and T_EDGE."""
    T_EDGE0, T_EDGE, T_END = 2.0e-9, 4.0e-9, 5.0e-9

    def __init__(self, cell, load_ff, work):
        self.cell, self.load_ff, self.work = cell, load_ff, Path(work)
        self.work.mkdir(parents=True, exist_ok=True)

    def run(self, tag, d_points):
        """d_points: list of (time, level at the D pin). Returns t, v(clk), v(d), v(q)."""
        cir = self.work / f"{tag}.cir"
        model = os.path.relpath(cfg.PART1 / "spice" / "models" / "TSMC_180nm.txt", self.work)
        # source polarity: one inverter (x4 driver) between source and pin, for finite edges
        src = [(t, VDD - v) for t, v in d_points]
        pwl = " ".join(f"{t:.5e} {v:.3f}" for t, v in src)
        net = (f"* {self.cell.name} timing\n.include {model}\n.options reltol=1e-4\nVDD vdd gnd 1.8\n"
               + self.cell.spice() + TB
               + f"Vd sd gnd PWL({pwl})\nXd sd d vdd gnd tb_x1\n"
               + f"Vc sc gnd PWL(0 1.8 1.0e-9 1.8 1.02e-9 0 {self.T_EDGE0 - 10e-12:.5e} 0 {self.T_EDGE0 + 10e-12:.5e} 1.8 "
                 f"3.0e-9 1.8 3.02e-9 0 {self.T_EDGE - 10e-12:.5e} 0 {self.T_EDGE + 10e-12:.5e} 1.8 "
                 f"{self.T_END:.5e} 1.8)\n"
               + "Xc sc clk vdd gnd tb_x4\n".replace("Xc sc", "Xci sc") .replace("clk vdd", "clkn vdd")
               + "Xc clkn clk vdd gnd tb_x4\n"
               + f"X0 d clk q vdd gnd {self.cell.name}\nXl q ql vdd gnd tb_x1\n"
               + (f"Cload q gnd {self.load_ff}f\n" if self.load_ff else "")
               + f".tran 1p {self.T_END:.5e}\n.control\nset wr_singlescale\nset wr_vecnames\nrun\n"
                 f"wrdata {tag}.txt v(clk) v(d) v(q)\nquit\n.endc\n.end\n")
        cir.write_text(net)
        _, res = run_ngspice(cir, timeout=300)
        wave = self.work / f"{tag}.txt"
        if not wave.exists():
            raise RuntimeError(res.stderr[-300:])
        data = np.loadtxt(wave, skiprows=1)
        wave.unlink()
        return data[:, 0], data[:, 1], data[:, 2], data[:, 3]

    def setup_case(self, value, skew):
        """D goes old to value at skew before the capturing edge. Returns (tcq, tdq, correct)."""
        old, new = (0 if value else VDD), (VDD if value else 0)
        t_d = self.T_EDGE - skew
        points = [(0, old), (t_d - 10e-12, old), (t_d + 10e-12, new), (self.T_END, new)]
        tag = f"su{int(value)}_{int(round(skew * 1e13)):+d}".replace("+", "p").replace("-", "m")
        t, clk, d, q = self.run(tag, points)
        win = t >= self.T_EDGE - 200e-12
        t_clk = _crossings(t[win], clk[win])
        t_clk_edge = t_clk[0]
        q_end = q[-1]
        correct = abs(q_end - new) < 0.1 * VDD
        cross = _crossings(t[win], q[win])
        after = cross[cross > t_clk_edge - 100e-12]
        if not correct or len(after) == 0:
            return None, None, correct
        t_q = after[-1]
        t_dd = _crossings(t, d)
        return t_q - t_clk_edge, t_q - t_dd[-1], correct

    def hold_case(self, value, delay):
        """D is correct before the edge, then flips delay after it. Returns (correct, disturbance)."""
        good, bad = (VDD if value else 0), (0 if value else VDD)
        t_d = self.T_EDGE + delay
        points = [(0, bad), (self.T_EDGE - 1.0e-9, bad), (self.T_EDGE - 1.0e-9 + 20e-12, good),
                  (t_d - 10e-12, good), (t_d + 10e-12, bad), (self.T_END, bad)]
        tag = f"h{int(value)}_{int(round(delay * 1e13)):+d}".replace("+", "p").replace("-", "m")
        t, clk, d, q = self.run(tag, points)
        # Q must make its one expected transition and then stay within 10 % of VDD
        settled = t >= self.T_EDGE + 600e-12
        worst = np.abs(q[settled] - good).max()
        moves = len(_crossings(t[t >= self.T_EDGE - 100e-12], q[t >= self.T_EDGE - 100e-12]))
        return worst < 0.1 * VDD and moves <= 1, worst


def characterise(cell, load_ff=0.0):
    bench = Bench(cell, load_ff, OUT / cell.name)
    tcq = {}
    skews = [s * 1e-12 for s in list(range(-60, 200, 10)) + [250, 300, 400, 600, 1000]]
    table = []

    def job(args):
        value, skew = args
        return value, skew, bench.setup_case(value, skew)

    with ThreadPoolExecutor(4) as ex:
        results = list(ex.map(job, [(v, s) for v in (0, 1) for s in skews]))
    summary = {}
    for value in (0, 1):
        rows = [(s, *r) for v, s, r in results if v == value]
        table += [dict(cell=cell.name, data=value, d_to_clk_ps=round(s * 1e12, 1),
                       tcq_ps=None if tc is None else round(tc * 1e12, 2),
                       tdq_ps=None if td is None else round(td * 1e12, 2), correct=ok) for s, tc, td, ok in rows]
        stable = next(tc for s, tc, _, ok in rows if abs(s - 1e-9) < 1e-13)
        tcq[value] = stable
        # setup: smallest skew such that all larger skews are correct and within 10 %
        tsu = None
        for s, tc, _, ok in sorted(rows, key=lambda r: -r[0]):
            if ok and tc is not None and tc <= 1.10 * stable:
                tsu = s
            else:
                break
        good_dq = [(td, s) for s, tc, td, ok in rows if ok and td is not None]
        min_dq, s_opt = min(good_dq)
        # refine setup with 2 ps steps below the coarse value
        fine = tsu
        for s in np.arange(tsu - 10e-12, tsu, 2e-12):
            _, _, r = job((value, float(s)))
            if r[2] and r[0] is not None and r[0] <= 1.10 * stable:
                fine = float(s)
                break
        summary[value] = dict(tcq=stable, tsu=fine, min_dq=min_dq, s_opt=s_opt)

    def hold_for(value):
        low, high = -300e-12, 300e-12
        ok_low = bench.hold_case(value, low)[0]
        if ok_low:
            return low
        for _ in range(9):
            mid = (low + high) / 2
            if bench.hold_case(value, mid)[0]:
                high = mid
            else:
                low = mid
        return high

    with ThreadPoolExecutor(2) as ex:
        holds = dict(zip((0, 1), ex.map(hold_for, (0, 1))))
    with open(bench.work / "setup_sweep.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(table[0].keys()))
        writer.writeheader()
        writer.writerows(table)
    return dict(cell=cell.name, transistors=cell.transistor_count, total_width_lambda=cell.total_width_lam,
                load_ff=load_ff,
                tcq_rise_ps=round(summary[1]["tcq"] * 1e12, 1), tcq_fall_ps=round(summary[0]["tcq"] * 1e12, 1),
                tsu_rise_ps=round(summary[1]["tsu"] * 1e12, 1), tsu_fall_ps=round(summary[0]["tsu"] * 1e12, 1),
                thold_rise_ps=round(holds[1] * 1e12, 1), thold_fall_ps=round(holds[0] * 1e12, 1),
                min_dq_rise_ps=round(summary[1]["min_dq"] * 1e12, 1), min_dq_fall_ps=round(summary[0]["min_dq"] * 1e12, 1),
                tcq_ps=round(max(summary[0]["tcq"], summary[1]["tcq"]) * 1e12, 1),
                tsu_ps=round(max(summary[0]["tsu"], summary[1]["tsu"]) * 1e12, 1),
                thold_ps=round(max(holds.values()) * 1e12, 1))


if __name__ == "__main__":
    rows = []
    for cell in (tspc(), tg_ms()):
        row = characterise(cell, load_ff=15.0)
        rows.append(row)
        print(row, flush=True)
    with open(cfg.PART1 / "results" / "phase5_dff_first_comparison.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
