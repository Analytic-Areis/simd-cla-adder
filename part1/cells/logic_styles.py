#!/usr/bin/env python3
"""Logic-style check, pre-layout: one 4-stage carry chain C0 -> C4 built in each style.

All stages propagate (a = 1, b = 0, so g = 0, t = P = 1), the classic carry path. Every style gets the same
C0 driver, the same load on each carry (one unit inverter per rail as a sum-gate stand-in, four on C4), and a
small sizing sweep; the fastest correct sizing of each style is reported. Correct means full swing on C4,
within 10 % of each rail. Power is the circuit's own supply, C0 toggling every 2 ns; the domino clock buffer
is on that supply, input drivers and load inverters are not.

Run: python3 logic_styles.py
"""
import csv
import json
import os
from concurrent.futures import ThreadPoolExecutor
from itertools import product

from cellgen import config as cfg
from cellgen.sim import run_ngspice

WORK = cfg.PART1 / "simulations" / "logic_styles"
OUT = cfg.PART1 / "results" / "logic_styles.json"
WN, WP, WMIN, DIFF = 0.9, 1.8, 0.27, 0.45   # um: unit NMOS, unit PMOS, minimum width, diffusion length


class Net:
    def __init__(self, prefix="M"):
        self.prefix, self.lines, self.count, self.width = prefix, [], 0, 0.0

    def m(self, d, g, s, kind, w, b=None, l=0.18, count=True):
        w = max(WMIN, w)
        b = b or ("gnd" if kind == "n" else "vdd")
        model = "CMOSN" if kind == "n" else "CMOSP"
        self.lines.append(f"{self.prefix}{len(self.lines)} {d} {g} {s} {b} {model} W={w:.3f}u L={l:.2f}u "
                          f"AS={w * DIFF:.4f}p AD={w * DIFF:.4f}p PS={2 * (w + DIFF):.3f}u PD={2 * (w + DIFF):.3f}u")
        if count:
            self.count += 1
            self.width += w

    def inv(self, a, y, k, vdd="vdd"):
        self.m(y, a, vdd, "p", WP * k, b=vdd)
        self.m(y, a, "gnd", "n", WN * k)


# each builder adds 4 stages from c0 (and c0b) to c4 (and c4b) and returns the true-rail names
def static_mirror(n, k, beta):
    wn, wp = WN * k, WN * k * beta
    c = "c0"
    for i in range(4):
        y = f"c{i + 1}"
        if i % 2 == 0:   # y = not(g + t.c): inputs g = 0, t = 1
            n.m(y, "g", "gnd", "n", wn)
            n.m(y, c, f"x{i}", "n", 2 * wn)
            n.m(f"x{i}", "t", "gnd", "n", 2 * wn)
            n.m(f"z{i}", "g", "vdd", "p", 2 * wp)
            n.m(y, c, f"z{i}", "p", 2 * wp)
            n.m(y, "t", f"z{i}", "p", 2 * wp)
        else:            # y = not(gb . (tb + c)): inputs gb = 1, tb = 0
            n.m(y, c, f"x{i}", "n", 2 * wn)
            n.m(y, "tb", f"x{i}", "n", 2 * wn)
            n.m(f"x{i}", "gb", "gnd", "n", 2 * wn)
            n.m(y, "gb", "vdd", "p", wp)
            n.m(f"z{i}", "tb", "vdd", "p", 2 * wp)
            n.m(y, c, f"z{i}", "p", 2 * wp)
        c = y
    return ["c1", "c2", "c3", "c4"]


def pseudo_nmos(n, k, r):
    wn = WN * k
    c = "c0"
    for i in range(4):
        y = f"c{i + 1}"
        if i % 2 == 0:
            n.m(y, "g", "gnd", "n", wn)
            n.m(y, c, f"x{i}", "n", 2 * wn)
            n.m(f"x{i}", "t", "gnd", "n", 2 * wn)
        else:
            n.m(y, c, f"x{i}", "n", 2 * wn)
            n.m(y, "tb", f"x{i}", "n", 2 * wn)
            n.m(f"x{i}", "gb", "gnd", "n", 2 * wn)
        n.m(y, "gnd", "vdd", "p", r * WP * k)   # always-on load
        c = y
    return ["c1", "c2", "c3", "c4"]


def dcvsl(n, k, r, buf):
    wn = WN * k
    c, cb = "c0", "c0b"
    for i in range(4):
        y, yb = (f"d{i + 1}", f"d{i + 1}b") if buf else (f"c{i + 1}", f"c{i + 1}b")
        # yb pulled low by f = g + t.c ; y pulled low by fbar = gb.(tb + cb)
        n.m(yb, "g", "gnd", "n", wn)
        n.m(yb, c, f"x{i}", "n", 2 * wn)
        n.m(f"x{i}", "t", "gnd", "n", 2 * wn)
        n.m(y, cb, f"w{i}", "n", 2 * wn)
        n.m(y, "tb", f"w{i}", "n", 2 * wn)
        n.m(f"w{i}", "gb", "gnd", "n", 2 * wn)
        n.m(y, yb, "vdd", "p", r * WP * k)
        n.m(yb, y, "vdd", "p", r * WP * k)
        if buf:   # inverters restore drive; swapping rails keeps the polarity
            n.inv(yb, f"c{i + 1}", buf)
            n.inv(y, f"c{i + 1}b", buf)
        c, cb = f"c{i + 1}", f"c{i + 1}b"
    return ["c1", "c2", "c3", "c4"]


def cpl(n, k, m, restore):
    wn = WN * k
    c, cb = "c0", "c0b"
    for i in range(4):
        x, xb = f"x{i}", f"xb{i}"
        n.m(x, "p", c, "n", wn, b="gnd")
        n.m(x, "pb", "a", "n", wn, b="gnd")
        n.m(xb, "p", cb, "n", wn, b="gnd")
        n.m(xb, "pb", "ab", "n", wn, b="gnd")
        if restore:
            n.m(x, xb, "vdd", "p", WMIN)
            n.m(xb, x, "vdd", "p", WMIN)
        n.inv(xb, f"c{i + 1}", m)
        n.inv(x, f"c{i + 1}b", m)
        c, cb = f"c{i + 1}", f"c{i + 1}b"
    return ["c1", "c2", "c3", "c4"]


def tg_mux(n, k, m):
    wn, wp = WN * k, WP * k
    c = "c0"
    for i in range(4):
        x, y = f"x{i}", f"c{i + 1}"
        other = "a" if i % 2 == 0 else "ab"
        n.m(x, "p", c, "n", wn, b="gnd")
        n.m(x, "pb", c, "p", wp, b="vdd")
        n.m(x, "pb", other, "n", wn, b="gnd")
        n.m(x, "p", other, "p", wp, b="vdd")
        n.inv(x, y, m)
        c = y
    return ["c1", "c2", "c3", "c4"]


def domino(n, k, m, foot=1):
    wn = WN * k
    c = "c0"
    for i in range(4):
        dn, y = f"dn{i}", f"c{i + 1}"
        n.m(dn, "clk", "vdd", "p", WP * k)              # precharge
        bottom = f"f{i}" if foot else "gnd"
        n.m(dn, "g", bottom, "n", wn)
        n.m(dn, c, f"x{i}", "n", 2 * wn)
        n.m(f"x{i}", "t", bottom, "n", 2 * wn)
        if foot:
            n.m(bottom, "clk", "gnd", "n", 2 * wn)       # foot
        n.m(dn, y, "vdd", "p", WMIN, l=0.36)             # keeper
        n.inv(dn, y, m)
        c = y
    return ["c1", "c2", "c3", "c4"]


STYLES = {
    "Static CMOS (mirror carry, used)": (static_mirror, dict(k=[1, 2, 3, 4, 5, 6, 8, 10, 12, 16], beta=[1, 1.25, 1.5, 2, 2.5])),
    "Pseudo-NMOS": (pseudo_nmos, dict(k=[1, 2, 3, 4, 5, 6, 8, 10, 12, 16], r=[0.15, 0.25, 0.3, 0.35, 0.45, 0.5])),
    "DCVSL": (dcvsl, dict(k=[1, 2, 3, 4, 6, 8], r=[0.15, 0.25, 0.5, 1], buf=[0, 1, 2, 3, 4])),
    "CPL": (cpl, dict(k=[0.5, 1, 1.5, 2, 3, 4], m=[0.5, 1, 1.5, 2, 3], restore=[0, 1])),
    "Transmission-gate mux": (tg_mux, dict(k=[0.5, 1, 1.5, 2, 3, 4, 6], m=[1, 2, 3, 4, 6])),
    "Domino (footed, keeper)": (domino, dict(k=[1, 2, 3, 4, 6, 8, 12], m=[0.5, 1, 2, 3, 4, 6], foot=[1])),
    "Domino (footless, keeper)": (domino, dict(k=[1, 2, 3, 4, 6, 8, 12], m=[0.5, 1, 2, 3, 4, 6], foot=[0])),
}
DUAL = {"DCVSL", "CPL"}


def deck(style, params, tag):
    builder, _ = STYLES[style]
    n = Net()
    rails = builder(n, **params)
    is_domino = builder is domino
    dual = style in DUAL
    model = os.path.relpath(cfg.PART1 / "spice" / "models" / "TSMC_180nm.txt", WORK)
    lines = [f"* {style} {params}", f".include {model}", ".options reltol=1e-4",
             "VDD vdd_core gnd 1.8", "Vsense vdd_core vdd 0", "VTB vtb gnd 1.8",
             # static inputs for a = 1, b = 0 on every bit
             "Vg g gnd 0", "Vt t gnd 1.8", "Vgb gb gnd 1.8", "Vtbar tb gnd 0",
             "Vp p gnd 1.8", "Vpb pb gnd 0", "Va a gnd 1.8", "Vab ab gnd 0"]
    if is_domino:   # evaluate 0.5-2.5 ns and 4.5-6.5 ns; C0 low again during precharge
        edges = [1, 2.7, 5, 6.7]
        clk = "PWL(0 0 0.5n 0 0.515n 1.8 2.5n 1.8 2.515n 0 4.5n 0 4.515n 1.8 6.5n 1.8 6.515n 0 9n 0)"
        lines += [f"Vck sck gnd {clk}"]
        tb = Net("MK")
        tb.inv("sck", "ck1", 1, vdd="vtb")
        lines += tb.lines
        n.inv("ck1", "clk", max(2, 2 * params["k"]))
    else:
        edges = [1, 3, 5, 7]
    # C0 and its complement through the same two-inverter driver (input inverted twice)
    def pwl(lo, hi):
        pts, level = [f"0 {lo}"], lo
        for e in edges:
            nxt = hi if level == lo else lo
            pts += [f"{e}n {level}", f"{e + 0.015:.3f}n {nxt}"]
            level = nxt
        return "PWL(" + " ".join(pts + [f"9n {level}"]) + ")"
    lines += [f"Vs s gnd {pwl(0, 1.8)}", f"Vsb sb gnd {pwl(1.8, 0)}"]
    drv = Net("MD")
    drv.inv("s", "s1", 1, vdd="vtb"); drv.inv("s1", "c0", 2, vdd="vtb")
    drv.inv("sb", "sb1", 1, vdd="vtb"); drv.inv("sb1", "c0b", 2, vdd="vtb")
    for i, r in enumerate(rails):   # sum-gate stand-in on every carry rail, FO4 on C4
        for j in range(4 if r == "c4" else 1):
            drv.inv(r, f"ld{i}_{j}", 1, vdd="vtb")
            if dual:
                drv.inv(f"{r}b", f"ldb{i}_{j}", 1, vdd="vtb")
    lines += drv.lines + n.lines
    meas = [".meas tran tpr TRIG v(c0) VAL=0.9 RISE=1 TARG v(c4) VAL=0.9 RISE=1",
            ".meas tran pavg AVG i(Vsense) FROM=0.5n TO=8.5n"]
    if is_domino:
        meas += [".meas tran vlo FIND v(c4) AT=0.45n", ".meas tran vhi FIND v(c4) AT=2.45n",
                 ".meas tran tpre TRIG v(clk) VAL=0.9 FALL=1 TARG v(c4) VAL=0.9 FALL=1"]
    else:
        meas += [".meas tran tpf TRIG v(c0) VAL=0.9 FALL=1 TARG v(c4) VAL=0.9 FALL=1",
                 ".meas tran vlo FIND v(c4) AT=0.95n", ".meas tran vhi FIND v(c4) AT=2.95n",
                 ".meas tran vlo2 FIND v(c4) AT=4.95n"]
    lines += [".tran 2p 9n"] + meas + [".end"]
    cir = WORK / f"{tag}.cir"
    cir.write_text("\n".join(lines) + "\n")
    return cir, n


def run(job):
    style, params, tag = job
    cir, n = deck(style, params, tag)
    v, _ = run_ngspice(cir, timeout=300)
    domino_style = STYLES[style][0] is domino
    tpr, tpf = v.get("tpr"), (None if domino_style else v.get("tpf"))
    vlo, vhi = v.get("vlo"), v.get("vhi")
    ok = all(x is not None for x in (tpr, vlo, vhi)) and vlo < 0.18 and vhi > 1.62 and (domino_style or tpf is not None)
    if not domino_style and v.get("vlo2") is not None:
        ok = ok and v["vlo2"] < 0.18
    delays = [x for x in (tpr, tpf) if x is not None]
    return dict(style=style, params=params, ok=ok, tpr_ps=tpr and tpr * 1e12, tpf_ps=tpf and tpf * 1e12,
                worst_ps=max(delays) * 1e12 if delays else None, vlo=vlo, vhi=vhi,
                precharge_ps=v.get("tpre") and v["tpre"] * 1e12,
                power_uw=abs(v["pavg"]) * 1.8e6 if "pavg" in v else None,
                transistors=n.count, width_um=round(n.width, 2))


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    jobs = []
    for style, (_, grid) in STYLES.items():
        keys = list(grid)
        for i, values in enumerate(product(*grid.values())):
            jobs.append((style, dict(zip(keys, values)), f"{STYLES[style][0].__name__}{'' if style.find('footless') < 0 else '_nf'}_{i:02d}"))
    with ThreadPoolExecutor(8) as ex:
        rows = list(ex.map(run, jobs))
    with open(WORK / "sweep.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    best = {}
    for style in STYLES:
        good = [r for r in rows if r["style"] == style and r["ok"]]
        best[style] = min(good, key=lambda r: r["worst_ps"]) if good else None
        tried = sum(r["style"] == style for r in rows)
        b = best[style]
        print(f"{style:34s} tried {tried:3d} correct {len(good):3d} "
              + (f"best {b['worst_ps']:.1f} ps (rise {b['tpr_ps']:.1f}, fall {b['tpf_ps'] and round(b['tpf_ps'], 1)}) "
                 f"P {b['power_uw']:.0f} uW, {b['transistors']} T, {b['width_um']} um, {b['params']}" if b else "none correct"),
              flush=True)
    OUT.write_text(json.dumps(dict(best=best, all=rows), indent=1, default=str))


if __name__ == "__main__":
    main()
