#!/usr/bin/env python3
"""Technology characterisation of the provided TSMC 180 nm BSIM3 model.

This is NOT the CLA. It measures the numbers the architecture comparison needs:
gate capacitance per micron, inverter beta for minimum delay, FO4, the logical
effort time constant tau, and g/p of series stacks of 2-5 devices.

Every netlist and ngspice log is kept under runs/ and every number written to
results/*.csv is parsed from an ngspice .meas line. Nothing is typed in by hand.

Usage: python3 tech_char.py
"""
import csv
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNS = HERE / "runs"
RESULTS = HERE / "results"
MODEL = "../../../../TSMC_180nm.txt"  # relative to runs/, original file untouched
LAM = 0.09e-6
VDD = 1.8
WN0, WP0 = 0.9e-6, 1.8e-6  # the assignment's load inverter: 10 lambda / 20 lambda
L = 0.18e-6


def mos(name, d, g, s, b, kind, w, sd="ext", dd="ext"):
    """One MOSFET with layout-aware junction estimates.

    From the tech file DRC: a contacted source/drain is 6 lambda long (2 lambda
    gate-to-contact + 4 lambda contact). An uncontacted node shared by two series
    gates is 3 lambda long (poly-to-poly spacing).
    """
    def ap(style):
        ln = (6 if style == "ext" else 3) * LAM
        return w * ln, 2 * (w + ln)
    a_s, p_s = ap(sd)
    a_d, p_d = ap(dd)
    model = "CMOSN" if kind == "n" else "CMOSP"
    return (f"{name} {d} {g} {s} {b} {model} W={w:.4e} L={L:.4e} "
            f"AS={a_s:.4e} PS={p_s:.4e} AD={a_d:.4e} PD={p_d:.4e}\n")


def inv_cell(name, a, beta=2.0):
    # 0.27 um is the 3-lambda minimum diffusion width. An unclipped W of 0.056 um in
    # the shaper stage made ngspice abort with "Timestep too small" (see journal).
    a = max(a, 0.3)
    wn, wp = a * WN0, a * WN0 * beta
    return (f".subckt {name} in out vdd gnd\n"
            + mos("mp", "out", "in", "vdd", "vdd", "p", wp)
            + mos("mn", "out", "in", "gnd", "gnd", "n", wn)
            + ".ends\n")


def run(tag, netlist):
    """Write netlist, run ngspice in batch, keep the log, return .meas values."""
    RUNS.mkdir(parents=True, exist_ok=True)
    cir, log = RUNS / f"{tag}.cir", RUNS / f"{tag}.log"
    cir.write_text(netlist)
    out = subprocess.run(["ngspice", "-b", cir.name], cwd=RUNS, capture_output=True,
                         text=True, timeout=300)
    log.write_text(out.stdout + "\n--- STDERR ---\n" + out.stderr)
    vals = {}
    for line in out.stdout.splitlines():
        m = re.match(r"\s*(\w+)\s*=\s*([-+0-9.eE]+)\s", line + " ")
        if m:
            try:
                vals[m.group(1).lower()] = float(m.group(2))
            except ValueError:
                pass
    return vals


HEADER = f"* {{}}\n.include {MODEL}\n.options reltol=1e-4\nVDD vdd gnd {VDD}\n"
PULSE = f"Vin in0 gnd PULSE(0 {VDD} 1n 20p 20p 2n 4n)\n"


def tp_meas(innode, outnode, in_rise_is_out_fall=True):
    """tpHL / tpLH at the 50 % points, on the second period so the state is settled."""
    fall, rise = ("rise", "fall") if in_rise_is_out_fall else ("fall", "rise")
    h = VDD / 2
    return (f".meas tran tphl TRIG v({innode}) VAL={h} {fall.upper()}=2 "
            f"TARG v({outnode}) VAL={h} FALL=2\n"
            f".meas tran tplh TRIG v({innode}) VAL={h} {rise.upper()}=2 "
            f"TARG v({outnode}) VAL={h} RISE=2\n")


def gate_cap_per_um():
    """E1: input charge on inverter gates, by integrating the source current.

    The Vin ramp is slow, so no short-circuit-free approximation is needed: we use
    ground-referenced C-V by holding the rails and integrating current in the gate
    source only.
    """
    rows = []
    for label, wn, wp in [("load_inverter_1.8_0.9", WN0, WP0)]:
        nl = HEADER.format("E1 input capacitance of inverter") + inv_cell("inv", 1.0)
        nl += f"Vg g gnd PWL(0 0 1n 0 2n {VDD} 3n {VDD})\nX1 g o vdd gnd inv\n"
        nl += inv_cell("invload", 1.0) + "X2 o o2 vdd gnd invload\n"
        nl += (".tran 1p 3n\n.meas tran q INTEG i(Vg) FROM=1n TO=3n\n.end\n")
        v = run("e1_cin_inv", nl)
        rows.append(dict(cell=label, qin=v.get("q"), cin_f=abs(v.get("q", 0)) / VDD))
    # Separate n and p gate cap per micron (device alone, S=D=B at the rail that
    # keeps the channel in its normal digital-off-to-on sweep).
    nl = HEADER.format("E1b Cg per um, single devices")
    nl += "Vgn gn gnd PWL(0 0 1n 0 2n 1.8 3n 1.8)\nVgp gp gnd PWL(0 1.8 1n 1.8 2n 0 3n 0)\n"
    nl += mos("mn", "gnd", "gn", "gnd", "gnd", "n", WN0)
    nl += mos("mp", "vdd", "gp", "vdd", "vdd", "p", WP0)
    nl += ".tran 1p 3n\n.meas tran qn INTEG i(Vgn) FROM=1n TO=3n\n"
    nl += ".meas tran qp INTEG i(Vgp) FROM=1n TO=3n\n.end\n"
    v = run("e1b_cg_per_um", nl)
    cgn = abs(v["qn"]) / VDD / (WN0 * 1e6)
    cgp = abs(v["qp"]) / VDD / (WP0 * 1e6)
    rows.append(dict(cell="cg_n_per_um", qin=v["qn"], cin_f=cgn))
    rows.append(dict(cell="cg_p_per_um", qin=v["qp"], cin_f=cgp))
    return rows, cgn, cgp


def fanout_inverter(a_dut, h, beta):
    """Shaper, driver, DUT, load, and a further load so the load sees realistic Miller."""
    drv = a_dut / 4
    nl = PULSE
    cells = {"sh": drv / 4, "dr": drv, "du": a_dut, "lo": a_dut * h, "ll": a_dut * h * 4}
    for n, a in cells.items():
        nl += inv_cell(n, a, beta)
    nl += ("X0 in0 n1 vdd gnd sh\nX1 n1 ndut vdd gnd dr\nX2 ndut nout vdd gnd du\n"
           "X3 nout n3 vdd gnd lo\nX4 n3 n4 vdd gnd ll\n")
    return nl


def e2_beta_sweep():
    jobs = {}
    for beta in [1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 3.0, 3.5]:
        nl = HEADER.format(f"E2 FO4 inverter beta={beta}") + fanout_inverter(1.0, 4, beta)
        nl += ".tran 0.5p 11n\n" + tp_meas("ndut", "nout") + ".end\n"
        jobs[beta] = (f"e2_beta_{beta}", nl)
    rows = []
    with ThreadPoolExecutor(8) as ex:
        res = {b: ex.submit(run, *j) for b, j in jobs.items()}
    for b, f in res.items():
        v = f.result()
        rows.append(dict(beta=b, tphl_ps=v["tphl"] * 1e12, tplh_ps=v["tplh"] * 1e12,
                         tp_avg_ps=(v["tphl"] + v["tplh"]) / 2 * 1e12))
    return rows


def linfit(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    return slope, my - slope * mx


def e3_tau(beta=2.0):
    fan = [1, 2, 3, 4, 5, 6, 8]
    rows = []
    with ThreadPoolExecutor(8) as ex:
        res = {}
        for h in fan:
            nl = HEADER.format(f"E3 inverter FO{h}") + fanout_inverter(1.0, h, beta)
            nl += ".tran 0.5p 11n\n" + tp_meas("ndut", "nout") + ".end\n"
            res[h] = ex.submit(run, f"e3_fo{h}", nl)
    for h in fan:
        v = res[h].result()
        rows.append(dict(h=h, tphl_ps=v["tphl"] * 1e12, tplh_ps=v["tplh"] * 1e12,
                         tp_avg_ps=(v["tphl"] + v["tplh"]) / 2 * 1e12))
    slope, inter = linfit([r["h"] for r in rows], [r["tp_avg_ps"] for r in rows])
    return rows, slope, inter


def stack_gate(kind, n):
    """NAND-n or NOR-n sized for unit drive. Series devices are n x unit width."""
    pins = [f"i{k}" for k in range(n)]
    s = f".subckt g{kind}{n} {' '.join(pins)} out vdd gnd\n"
    if kind == "nand":
        wn, wp = n * WN0, WP0
        for k in range(n):
            s += mos(f"mp{k}", "out", pins[k], "vdd", "vdd", "p", wp)
            d = "out" if k == 0 else f"x{k}"
            so = "gnd" if k == n - 1 else f"x{k + 1}"
            s += mos(f"mn{k}", d, pins[k], so, "gnd", "n", wn,
                     sd="ext" if k == n - 1 else "int", dd="ext" if k == 0 else "int")
    else:
        wn, wp = WN0, n * WP0
        for k in range(n):
            s += mos(f"mn{k}", "out", pins[k], "gnd", "gnd", "n", wn)
            d = "out" if k == 0 else f"x{k}"
            so = "vdd" if k == n - 1 else f"x{k + 1}"
            s += mos(f"mp{k}", d, pins[k], so, "vdd", "p", wp,
                     sd="ext" if k == n - 1 else "int", dd="ext" if k == 0 else "int")
    return s + ".ends\n", wn, wp


def e4_stack(cgn, cgp):
    """g and p of series stacks, input nearest the output vs nearest the rail."""
    inv_cin = cgn * WN0 * 1e6 + cgp * WP0 * 1e6
    fan = [1, 2, 4, 6]
    res = {}
    with ThreadPoolExecutor(8) as ex:
        for kind in ("nand", "nor"):
            for n in (1, 2, 3, 4, 5):
                sub, wn, wp = stack_gate(kind, n)
                cin = cgn * wn * 1e6 + cgp * wp * 1e6
                a_eq = cin / inv_cin
                positions = ["near"] if n == 1 else ["near", "far"]
                for pos in positions:
                    idx = 0 if pos == "near" else n - 1
                    for h in fan:
                        nl = HEADER.format(f"E4 {kind}{n} {pos}-rail input FO{h}") + PULSE + sub
                        for tag, a in (("sh", a_eq / 16), ("dr", a_eq / 4),
                                       ("lo", a_eq * h), ("ll", a_eq * h * 4)):
                            nl += inv_cell(tag, a)
                        nl += "X0 in0 n1 vdd gnd sh\nX1 n1 ndut vdd gnd dr\n"
                        conn = []
                        for k in range(n):
                            if k == idx:
                                conn.append("ndut")
                            else:
                                conn.append("vdd" if kind == "nand" else "gnd")
                        nl += f"X2 {' '.join(conn)} nout vdd gnd g{kind}{n}\n"
                        nl += "X3 nout n3 vdd gnd lo\nX4 n3 n4 vdd gnd ll\n"
                        nl += ".tran 0.5p 11n\n" + tp_meas("ndut", "nout") + ".end\n"
                        res[(kind, n, pos, h)] = ex.submit(run, f"e4_{kind}{n}_{pos}_fo{h}", nl)
    rows = []
    for (kind, n, pos, h), f in res.items():
        v = f.result()
        rows.append(dict(kind=kind, n=n, pos=pos, h=h, tphl_ps=v["tphl"] * 1e12,
                         tplh_ps=v["tplh"] * 1e12,
                         tp_avg_ps=(v["tphl"] + v["tplh"]) / 2 * 1e12))
    return rows


def write_csv(name, rows):
    RESULTS.mkdir(parents=True, exist_ok=True)
    with open(RESULTS / name, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def main():
    cap_rows, cgn, cgp = gate_cap_per_um()
    write_csv("e1_capacitance.csv", cap_rows)
    for r in cap_rows:
        print("E1", r)

    beta_rows = e2_beta_sweep()
    write_csv("e2_beta_sweep.csv", beta_rows)
    for r in beta_rows:
        print("E2", {k: round(v, 2) for k, v in r.items()})

    tau_rows, tau, pinv_ps = e3_tau()
    write_csv("e3_inverter_fanout.csv", tau_rows)
    for r in tau_rows:
        print("E3", {k: round(v, 2) for k, v in r.items()})
    print(f"E3 fit: tau={tau:.2f} ps  parasitic intercept={pinv_ps:.2f} ps  "
          f"pinv={pinv_ps / tau:.2f}  FO4(fit)={4 * tau + pinv_ps:.1f} ps")

    stack = e4_stack(cgn, cgp)
    write_csv("e4_stack_raw.csv", stack)
    summary = []
    keys = sorted({(r["kind"], r["n"], r["pos"]) for r in stack})
    for kind, n, pos in keys:
        sel = sorted([r for r in stack if (r["kind"], r["n"], r["pos"]) == (kind, n, pos)],
                     key=lambda r: r["h"])
        hs = [r["h"] for r in sel]
        s, i = linfit(hs, [r["tp_avg_ps"] for r in sel])
        sl, il = linfit(hs, [r["tplh_ps"] for r in sel])
        sf, if_ = linfit(hs, [r["tphl_ps"] for r in sel])
        summary.append(dict(kind=kind, n=n, input=pos, g=s / tau, p=i / tau,
                            g_lh=sl / tau, p_lh=il / tau, g_hl=sf / tau, p_hl=if_ / tau,
                            fo4_equiv_ps=4 * s + i))
        print("E4", kind, n, pos, f"g={s / tau:.2f} p={i / tau:.2f} "
              f"gLH={sl / tau:.2f} pLH={il / tau:.2f} gHL={sf / tau:.2f} pHL={if_ / tau:.2f} "
              f"d(h=4)={4 * s + i:.1f}ps")
    write_csv("e4_stack_summary.csv", summary)
    write_csv("e3_fit.csv", [dict(tau_ps=tau, parasitic_ps=pinv_ps, pinv=pinv_ps / tau,
                                  fo4_fit_ps=4 * tau + pinv_ps)])


if __name__ == "__main__":
    main()
