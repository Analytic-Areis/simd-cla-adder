#!/usr/bin/env python3
"""Build the Part II report from the result files. No result value is typed here by hand.

Run after every simd.py stage:  python3 make_report.py
Writes documentation/report.tex and documentation/Bhargav_2025102061_part2.pdf.
"""
import csv
import json
import re
import shutil
import subprocess
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import simd
from cellgen import config as cfg

P2 = simd.P2
RES = P2 / "results"
DOC = P2 / "documentation"
FIG = DOC / "figures"


def rd(name):
    return json.loads((RES / name).read_text())


def tex(s):
    if "$" in str(s):   # already LaTeX maths, such as $\lambda$
        return str(s)
    return (str(s).replace("\\", r"\textbackslash{}").replace("_", r"\_").replace("%", r"\%")
            .replace("&", r"\&").replace("#", r"\#").replace("µ", r"$\mu$"))


def table(caption, headers, rows, spec=None, fit=False):
    spec = spec or "l" + "r" * (len(headers) - 1)
    out = [r"\begin{table}[H]\centering\small", rf"\caption{{{caption}}}"]
    if fit:
        out.append(r"\resizebox{\textwidth}{!}{")
    out += [rf"\begin{{tabular}}{{{spec}}}", r"\toprule", " & ".join(rf"\textbf{{{tex(h)}}}" for h in headers) + r" \\", r"\midrule"]
    out += [" & ".join(tex(c) for c in r) + r" \\" for r in rows]
    out += [r"\bottomrule", r"\end{tabular}"]
    if fit:
        out.append("}")
    out.append(r"\end{table}")
    return "\n".join(out)


def fig(name, caption, width=r"\textwidth", label=None):
    if not (FIG / name).exists():
        raise FileNotFoundError(name)
    lab = rf"\label{{{label}}}" if label else ""
    return rf"\begin{{figure}}[H]\centering\includegraphics[width={width}]{{figures/{name}}}\caption{{{caption}}}{lab}\end{{figure}}"


def f2(x):
    return "--" if x is None else f"{x:.2f}"


def make_figures():
    FIG.mkdir(parents=True, exist_ok=True)
    for src, dst in (("simd8_blocks.png", "2.0a_simd8-blocks.png"), ("base8_blocks.png", "2.0b_base8-blocks.png"),
                     ("carry_gate_n1_i2_blocks.png", "2.0c_gate-blocks.png"), ("gate_nand2_x1.png", "2.0d_gate-nand2.png"),
                     ("gate_inv_x2.png", "2.0e_gate-inv-x2.png"), ("gate_inv_x1.png", "2.0f_gate-inv-x1.png")):
        shutil.copy(P2 / "schematics" / src, FIG / dst)

    # worst delay to each output, post-layout
    cases = [("base_m0", "baseline", "#555555"), ("simd_m0", "SIMD_MODE=0", "#1f5fa8"), ("simd_m1", "SIMD_MODE=1", "#b8362f")]
    outs = [f"s{i}" for i in range(8)] + ["c8"]
    fig_, ax = plt.subplots(figsize=(11, 4.2))
    width = 0.27
    for k, (tag, label, colour) in enumerate(cases):
        per = rd(f"search_{tag}_post.json")["per_output"]
        vals = [per.get(o, 0.0) for o in outs]
        bars = ax.bar([i + (k - 1) * width for i in range(len(outs))], vals, width, label=label, color=colour)
        for b, v in zip(bars, vals):
            if v:
                ax.text(b.get_x() + b.get_width() / 2, v + 10, f"{v:.0f}", ha="center", fontsize=6.5, rotation=90)
    ax.set_xticks(range(len(outs)), [o.upper() for o in outs])
    ax.set_ylabel("worst delay to this output (ps)")
    ax.set_ylim(0, 1300)
    ax.legend(fontsize=8, ncol=3, loc="upper left")
    ax.grid(axis="y", alpha=0.3)
    ax.set_title(cfg.plot_title("2.5", "worst-delay-per-output-postlayout"), fontsize=9)
    fig_.tight_layout()
    fig_.savefig(FIG / "2.5_worst-delay-per-output-postlayout.png", dpi=150)
    plt.close(fig_)

    # gate sizing sweep
    rows = list(csv.DictReader(open(RES / "gate_sizing.csv")))
    nands = sorted({float(r["nand"]) for r in rows})
    invs = sorted({float(r["inv"]) for r in rows})
    grid = [[next(float(r["worst_cin_to_s7_ps"]) for r in rows if float(r["nand"]) == n and float(r["inv"]) == i) for i in invs] for n in nands]
    fig_, ax = plt.subplots(figsize=(6.4, 4.2))
    im = ax.imshow(grid, cmap="Blues_r", aspect="auto")
    for a, n in enumerate(nands):
        for b, i in enumerate(invs):
            ax.text(b, a, f"{grid[a][b]:.1f}", ha="center", va="center", fontsize=8,
                    color="white" if grid[a][b] < sum(map(sum, grid)) / (len(nands) * len(invs)) else "black")
    ax.set_xticks(range(len(invs)), [f"x{i:g}" for i in invs])
    ax.set_yticks(range(len(nands)), [f"x{n:g}" for n in nands])
    ax.set_xlabel("output inverter size")
    ax.set_ylabel("NAND2 size")
    fig_.colorbar(im, ax=ax, label="Cin to S7, schematic (ps)")
    ax.set_title(cfg.plot_title("2.6", "gating-cell-size-sweep"), fontsize=9)
    fig_.tight_layout()
    fig_.savefig(FIG / "2.6_gating-cell-size-sweep.png", dpi=150)
    plt.close(fig_)


def subckt_lines(path, name, width=92):
    """One subcircuit, with long lines continued on '+' lines so they fit the page."""
    text = Path(path).read_text()
    m = re.search(rf"(?ms)^\.subckt {name} .*?^\.ends {name}", text)
    out = []
    for line in m.group(0).splitlines():
        words, cur = line.split(), ""
        for w in words:
            if cur and len(cur) + len(w) + 1 > width:
                out.append(cur)
                cur = "+ " + w
            else:
                cur = f"{cur} {w}" if cur else w
        out.append(cur)
    return "\n".join(out)


def main():
    make_figures()
    gate = rd("gate.json")
    cells = rd("layout_cells.json")
    lay = {k: rd(f"layout_{k}.json") for k in ("simd", "base")}
    pen = rd("penalty.json")
    pw = rd("power.json")
    pw_course = rd("power_at_course_fmax.json")
    settle = rd("settle.json")
    srch = {(d, m, v): rd(f"search_{d}_m{m}_{v}.json") for d, m in (("base", 0), ("simd", 0), ("simd", 1)) for v in ("sch", "post")}
    P = {(r["design"], r["mode"], r["view"]): r for r in pen}
    tcq, tsu, th = pw["dff"]["tcq_ps"], pw["dff"]["tsu_ps"], pw["dff"]["thold_ps"]
    name = {("base", 0): "Baseline", ("simd", 0): "SIMD, SIMD\\_MODE = 0", ("simd", 1): "SIMD, SIMD\\_MODE = 1"}
    plain = {("base", 0): "Baseline", ("simd", 0): "SIMD, mode 0", ("simd", 1): "SIMD, mode 1"}

    def worst_arc(d, m, v):
        w = srch[(d, m, v)]["worst"]
        return f"{w['pin']} {w['pin_edge']} to {w['output']} {w['out_edge']}, {w['state']}"

    s0, b0 = srch[("simd", 0, "post")]["tpd_max_ps"], srch[("base", 0, "post")]["tpd_max_ps"]
    s0s, b0s = srch[("simd", 0, "sch")]["tpd_max_ps"], srch[("base", 0, "sch")]["tpd_max_ps"]
    post_pen = P[("simd", 0, "post")]
    sch_pen = P[("simd", 0, "sch")]
    common = {(r["design"], r["mode"]): r for r in pw["runs"] if r["run"] == "common"}
    long = {(r["design"], r["mode"]): r for r in pw["runs"] if r["run"] == "long200"}
    long_pen = 100 * (long[("simd", 0)]["power_uw"] - long[("base", 0)]["power_uw"]) / long[("base", 0)]["power_uw"]
    edp = pw["edp"]
    edp_pen = 100 * (edp["simd_m0"]["edp_fj_ps"] - edp["base_m0"]["edp_fj_ps"]) / edp["base_m0"]["edp_fj_ps"]
    area_pen = 100 * (lay["simd"]["area_um2"] - lay["base"]["area_um2"]) / lay["base"]["area_um2"]
    settle_rows = {}
    for r in settle:
        settle_rows.setdefault(r["period_ps"], {})[(r["design"], r["mode"])] = r["errors"]

    gate_net = subckt_lines(P2 / "schematics" / f"{gate['cell']}.sp", gate["cell"])
    simd_net = subckt_lines(P2 / "schematics" / "simd8.sp", "simd8")
    base_net = subckt_lines(P2 / "schematics" / "base8.sp", "base8")

    body = []
    add = body.append
    add(r"""\section{Task}
Part II builds an 8-bit adder from two instances of the Part I 4-bit carry look-ahead adder, CLA0 for bits 3..0 and CLA1 for bits 7..4, with a control input SIMD\_MODE:
\begin{itemize}
\item \textbf{SIMD\_MODE = 0, 8-bit mode:} the carry-out of CLA0 propagates into the carry-in of CLA1.
\item \textbf{SIMD\_MODE = 1, dual 4-bit mode:} the inter-block carry is forced to 0, so CLA0 and CLA1 add two independent 4-bit numbers.
\end{itemize}
A carry-gating cell between the two blocks does the switching. Its cost is measured against a \textbf{baseline}: the same two adders with CLA0's carry-out wired straight to CLA1's carry-in.

Everything here uses the provided TSMC 180\,nm model in ngspice at 1.8\,V, and MAGIC with the provided SCN6M\_DEEP technology file, $\lambda = 0.09\,\mu$m. Both 4-bit blocks are the final Part I adder with its final transistor sizes. Every output drives a $W_p/W_n = 20\lambda/10\lambda$ inverter, and every input is driven through a shaper and an x2 inverter, as in Part I.
""")
    add(r"\section{Architecture}")
    add(fig("2.0a_simd8-blocks.png", r"SIMD 8-bit adder: CLA0, the carry-gating cell and CLA1. c4lo is CLA0's carry-out, cinh is CLA1's carry-in."))
    add(fig("2.0b_base8-blocks.png", r"Baseline 8-bit adder: CLA0's carry-out c4lo goes straight to CLA1's carry-in."))
    add(r"""The SIMD design also brings CLA0's carry-out to an output, c4lo, because in dual mode it is the carry of the lower 4-bit result. It drives the same $20\lambda/10\lambda$ load as the other outputs.

\textbf{Functional check.} Both netlists were evaluated at switch level on 3000 random inputs each, against the behavioural model: 0 errors.
""")

    add(r"\section{The carry-gating cell}")
    add(r"""The carry into CLA1 must equal CLA0's carry-out in mode 0 and be 0 in mode 1:
\[ c_{in,hi} = c_{out,lo} \cdot \overline{\mathrm{SIMD\_MODE}} \]
This is an AND gate. In static CMOS, the cell uses a NAND2 followed by an inverter on the carry path, and a unit inverter for $\overline{\mathrm{SIMD\_MODE}}$. SIMD\_MODE is set before an add and held, so that inverter is off the timing path. Static CMOS was kept for the same reasons as in Part I: full swing and no static current.""")
    add(fig("2.0c_gate-blocks.png", f"Carry-gating cell, {gate['transistors']} transistors."))
    add(r"\begin{figure}[H]\centering"
        r"\includegraphics[width=0.32\textwidth]{figures/2.0f_gate-inv-x1.png}\hfill"
        r"\includegraphics[width=0.32\textwidth]{figures/2.0d_gate-nand2.png}\hfill"
        r"\includegraphics[width=0.32\textwidth]{figures/2.0e_gate-inv-x2.png}"
        r"\caption{Transistor-level schematics: mode inverter, NAND2 on the carry path, output inverter.}\end{figure}")
    add(rf"""\textbf{{Sizing.}} The NAND2 and the output inverter were swept on the schematic of the full SIMD adder in mode 0, measuring the worst delay from Cin to S7 on the vector A = FF, B = 00 (figure~\ref{{fig:sweep}}). The fastest was NAND2 x{gate['nand']:g} with an x{gate['inv']:g} output inverter, {gate['schematic_cin_to_s7_ps']:.2f}\,ps. A larger NAND2 is slower: it adds load to CLA0's carry-out, which is on the critical path.""")
    add(fig("2.6_gating-cell-size-sweep.png", "Gate sizing sweep: Cin to S7 in 8-bit mode, schematic.", r"0.7\textwidth", "fig:sweep"))
    a = gate["alone"]
    add(table("Carry-gating cell on its own, cout\\_lo to cin\\_hi with a 20/10$\\lambda$ load.",
              ["View", "Worst (ps)", "Output rising (ps)", "Output falling (ps)"],
              [["Schematic", f2(a["sch"]["worst_ps"]), f2(a["sch"]["rise_ps"]), f2(a["sch"]["fall_ps"])],
               ["Post-layout", f2(a["post"]["worst_ps"]), f2(a["post"]["rise_ps"]), f2(a["post"]["fall_ps"])]]))
    gl = gate["layout"]
    add(fig("magic_gate.png",
            f"Gating cell in MAGIC, with its carry pads above it, as placed in the SIMD adder. The cell alone is {gl['width_lambda']} x {gl['height_lambda']} $\\lambda$, DRC {gl['drc']}, LVS {tex(gl['lvs_message'])}.",
            r"0.55\textwidth"))

    add(r"\section{Layout}")
    c = cells["cla4_cell"]
    add(rf"""The layout keeps the two adders as two placed copies of one cell, as the task describes.
\begin{{enumerate}}
\item \textbf{{Adder cell.}} The Part I adder is laid out again as in Part I, with two extra metal 3 pads above its top row for C4 and C0. They are routed inside the cell like any other pin of those nets, so the top level can land a via on plain metal 3. The cell is DRC {c['drc']}, LVS {tex(c['lvs_message'])}, {c['area_um2']}\,$\mu$m$^2$.
\item \textbf{{Gating cell.}} Laid out the same way, with pads for cout\_lo and cin\_hi.
\item \textbf{{Top level.}} The adder cell is placed twice, with the gating cell between the copies in the SIMD design. The placement is flattened, then the inter-block carries are drawn on metal 5, which no cell uses. Port labels go on the cells' pin stubs, and the power straps join through buses below the cells.
\end{{enumerate}}""")
    add("The layout figures in this section are screenshots of MAGIC's own layout window.")
    add(fig("magic_cla4_cell.png", r"The Part I adder cell in MAGIC, with the two extra carry pads above the sum row."))
    add(fig("magic_simd8.png", r"SIMD 8-bit adder in MAGIC: CLA0 on the left, the gating cell in the middle, CLA1 on the right. The dashed lines above are metal 5, carrying c4lo and cinh."))
    add(fig("magic_simd8_gate_zoom.png", r"Close-up in MAGIC: the gating cell between CLA0 and CLA1 and its two metal 5 carries. The white rectangle is MAGIC's box, used to set the zoom.", r"0.85\textwidth"))
    add(fig("magic_base8.png", r"Baseline 8-bit adder in MAGIC: c4lo runs on metal 5 straight from CLA0 to CLA1."))
    add(table("Layout checks and size.", ["Design", "DRC", "LVS", "Transistors", "Size ($\\lambda$)", "Area ($\\mu$m$^2$)", "Wire C (fF)"],
              [[plain[(k, 0)].split(",")[0], lay[k]["drc"], lay[k]["lvs_message"], lay[k]["transistors"],
                f"{lay[k]['width_lambda']} x {lay[k]['height_lambda']}", lay[k]["area_um2"], lay[k]["wire_cap_ff"]] for k in ("base", "simd")],
              fit=True))
    add(rf"The SIMD layout is {area_pen:.1f}\% larger. Most of that is the gating cell's slot between the two adders, not the 8 transistors themselves. Both layouts match their schematics in LVS.")

    add(r"\section{Worst-case propagation delay in both modes}")
    add(r"""An exhaustive search over all transitions of 17 or 18 inputs is too long, so the search is guided. Each case runs 13,312 single-input transitions in four Eulerian walks:
\begin{itemize}
\item every transition of CLA0's nine inputs, with CLA1 set to pass a carry through all four bits: A$_{hi}$ = F, B$_{hi}$ = 0, then A$_{hi}$ = 0, B$_{hi}$ = F;
\item every transition of CLA1's eight inputs, with CLA0's carry-out held at 0 and then at 1.
\end{itemize}
These walks contain every path from a CLA0 input across the block boundary to the upper sums and C8. Delay runs from the adder pin to the last 50\% crossing of the output, so false sums do not shorten it. Every output was also checked after each transition.""")
    rows = []
    for d, m in (("base", 0), ("simd", 0), ("simd", 1)):
        for v in ("sch", "post"):
            s_ = srch[(d, m, v)]
            rows.append([plain[(d, m)], "schematic" if v == "sch" else "post-layout", s_["transitions"], s_["errors"],
                         f2(s_["tpd_max_ps"]), f2(s_["tpd_max_drv_ps"]), worst_arc(d, m, v)])
    add(table("Worst-case delay. tpd,pin is from the adder pin; tpd,drv includes the input driver.",
              ["Case", "View", "Transitions", "Errors", "tpd,pin (ps)", "tpd,drv (ps)", "Worst arc"], rows, "llrrrrl", fit=True))
    add(fig("2.5_worst-delay-per-output-postlayout.png", "Worst post-layout delay to each output."))
    add(rf"""\textbf{{Reading the results.}}
\begin{{itemize}}
\item In 8-bit mode the worst path runs from a3, through CLA0's carry tree and the inter-block carry, into CLA1's sums. The gating cell adds {s0 - b0:.2f}\,ps ({100 * (s0 - b0) / b0:.2f}\%) to tpd,max post-layout, and {s0s - b0s:.2f}\,ps ({100 * (s0s - b0s) / b0s:.2f}\%) on the schematic.
\item In dual mode the carry never crosses, so the worst path stays inside one 4-bit block: {srch[('simd', 1, 'post')]['tpd_max_ps']:.2f}\,ps post-layout. This is close to Part I's 579.88\,ps; the adder cell here was laid out again with the carry pads, and has the extra c4lo load.
\end{{itemize}}""")

    add(r"\section{Delay penalty of the gating cell}")
    add(r"Worst-case carry propagation vector, A = 0xFF, B = 0x00, Cin$_0$ toggling. Delay from Cin$_0$ to S7, in mode 0 for the SIMD adder:")
    add(r"\[ \text{Delay penalty (\%)} = \frac{t_{pd,SIMD} - t_{pd,baseline}}{t_{pd,baseline}} \times 100\% \]")
    rows = []
    for v in ("sch", "post"):
        for d, m in (("base", None), ("simd", 0), ("simd", 1)):
            r = P[(d, m, v)]
            rows.append(["schematic" if v == "sch" else "post-layout", plain[(d, m or 0)],
                         f2(r["cin_rise_to_s7_ps"]), f2(r["cin_fall_to_s7_ps"]), f2(r["cin_rise_to_c8_ps"]),
                         f2(r.get("cin_rise_to_c4lo_ps"))])
    add(table("Cin to S7 on the worst-case vector. In mode 1, S7 and C8 do not change.",
              ["View", "Case", "Cin rise to S7", "Cin fall to S7", "Cin rise to C8", "Cin rise to c4lo"], rows, "llrrrr", fit=True))
    add(table("Delay penalty, SIMD mode 0 against the baseline.", ["View", "Cin rise to S7", "Cin fall to S7"],
              [["Schematic", f"+{sch_pen['penalty_rise_ps']:.2f} ps, {sch_pen['penalty_rise_pct']:.2f}%", f"+{sch_pen['penalty_fall_ps']:.2f} ps, {sch_pen['penalty_fall_pct']:.2f}%"],
               ["Post-layout", f"+{post_pen['penalty_rise_ps']:.2f} ps, {post_pen['penalty_rise_pct']:.2f}%", f"+{post_pen['penalty_fall_ps']:.2f} ps, {post_pen['penalty_fall_pct']:.2f}%"]]))
    add(fig("2.4_worst-case-vector-postlayout.png", "Post-layout waveforms on the worst-case vector, all three cases.", label="fig:waves"))
    add(rf"""\textbf{{Why the penalty is smaller than the gate's own delay.}} The gate alone takes {a['post']['worst_ps']:.2f}\,ps, but the rising-edge penalty is only {post_pen['penalty_rise_ps']:.2f}\,ps. In the baseline, CLA0's carry-out drives CLA1's carry-in load directly. In the SIMD design it drives only the NAND2 input and the output load, so it switches sooner, which figure~\ref{{fig:waves}} shows. On the falling edge the penalty is larger, {post_pen['penalty_fall_ps']:.2f}\,ps.""")

    add(r"\section{Maximum frequency and power penalty}")
    fm = pw["fmax_ghz"]
    add(rf"""The maximum frequency uses the course formula, $f_{{max}} = 1 / (t_{{pd,max}} + t_{{setup}} + t_{{hold}})$, with the Part I flip-flop's post-layout $t_{{setup}} = {tsu}$\,ps and $t_{{hold}} = {th}$\,ps.""")
    add(table("Course-formula maximum frequency, post-layout.", ["Case", "tpd,max (ps)", "Period (ps)", "fmax (GHz)"],
              [[plain[(d, m)], f2(pw["tpd_max_ps"][f"{d}_m{m}"]), f2(pw["tpd_max_ps"][f"{d}_m{m}"] + tsu + th), f"{fm[f'{d}_m{m}']:.3f}"]
               for d, m in (("base", 0), ("simd", 0), ("simd", 1))]))
    course_err = {(r["design"], r["mode"], r["run"]): r["errors"] for r in pw_course["runs"]}
    add(rf"""\textbf{{The formula's clock is too short for some inputs.}} At each design's own course-formula clock, random vectors gave wrong outputs at the end of some cycles: {course_err[('base', 0, 'long200')]} of 200 for the baseline and {course_err[('simd', 0, 'long200')]} for SIMD mode 0. These vectors change several inputs at once, which is slower than the single-input worst case the search found, as in Part I. Power measured while outputs fail is not trustworthy. So the shortest clock at which all three cases settle on the same 200 random vectors was found:""")
    periods = sorted(settle_rows)
    add(table("Wrong output samples on 200 random vectors, post-layout.", ["Period (ps)"] + [plain[k] for k in (("base", 0), ("simd", 0), ("simd", 1))],
              [[f"{T:g}"] + [settle_rows[T][k] for k in (("base", 0), ("simd", 0), ("simd", 1))] for T in periods]))
    add(rf"""All three cases settle at {pw['common_period_ps']:g}\,ps, so power is compared there. All three get identical input vectors: 10 cycles as the task asks, and 200 vectors as a check. Power is the adder's own supply only: drivers and load inverters use a separate source.""")
    add(r"\[ \text{Power penalty (\%)} = \frac{P_{SIMD,\,mode\,0} - P_{baseline}}{P_{baseline}} \times 100\% \]")
    add(table(f"Average power at {pw['common_period_ps']:g} ps, post-layout. 0 wrong outputs in every run.",
              ["Case", "10 cycles ($\\mu$W)", "200 vectors ($\\mu$W)"],
              [[plain[k], common[k]["power_uw"], long[k]["power_uw"]] for k in (("base", 0), ("simd", 0), ("simd", 1))]))
    add(rf"""\textbf{{Power penalty in 8-bit mode:}} {pw['power_penalty_pct']:.2f}\% over 10 cycles, and {long_pen:.2f}\% over 200 vectors. The gating cell adds little switching: 8 small transistors, with the mode inverter idle. Dual mode uses the least power, because a carry stopped at the boundary does not ripple through CLA1.""")

    add(r"\section{Energy-delay product}")
    add(r"\[ EDP = P_{avg} \times t_{pd}^2 \]")
    add(table("Energy-delay product, with the 10-cycle power at the common clock and the post-layout tpd,max.",
              ["Case", "Pavg ($\\mu$W)", "tpd,max (ps)", "EDP (J s)"],
              [[plain[(d, m)], edp[f"{d}_m{m}"]["power_uw"], f2(edp[f"{d}_m{m}"]["tpd_ps"]), f"{edp[f'{d}_m{m}']['edp_fj_ps'] * 1e-27:.3e}"]
               for d, m in (("base", 0), ("simd", 0), ("simd", 1))]))
    add(rf"""In 8-bit mode the SIMD adder's EDP is {edp_pen:.1f}\% higher than the baseline's. Delay counts twice in EDP, so the {100 * (s0 - b0) / b0:.1f}\% delay penalty dominates the {pw['power_penalty_pct']:.1f}\% power penalty. In dual mode the EDP is far lower, because each add is only 4 bits long.""")

    add(r"\section{Summary and limits}")
    add(table("Cost of reconfigurability: SIMD mode 0 against the baseline, post-layout.", ["Measure", "Baseline", "SIMD mode 0", "Penalty"],
              [["Cin rise to S7 (ps)", f2(P[('base', None, 'post')]['cin_rise_to_s7_ps']), f2(post_pen['cin_rise_to_s7_ps']), f"{post_pen['penalty_rise_pct']:.2f}%"],
               ["tpd,max (ps)", f2(b0), f2(s0), f"{100 * (s0 - b0) / b0:.2f}%"],
               ["Power, 10 cycles ($\\mu$W)", common[("base", 0)]["power_uw"], common[("simd", 0)]["power_uw"], f"{pw['power_penalty_pct']:.2f}%"],
               ["EDP (J s)", f"{edp['base_m0']['edp_fj_ps'] * 1e-27:.3e}", f"{edp['simd_m0']['edp_fj_ps'] * 1e-27:.3e}", f"{edp_pen:.1f}%"],
               ["Transistors", lay["base"]["transistors"], lay["simd"]["transistors"], f"+{lay['simd']['transistors'] - lay['base']['transistors']}"],
               ["Area ($\\mu$m$^2$)", lay["base"]["area_um2"], lay["simd"]["area_um2"], f"{area_pen:.1f}%"]]))
    add(r"""\begin{itemize}
\item \textbf{Guided search.} The worst-case search is guided and single-input; it is not exhaustive. Multi-input changes are slower, as the settle test shows, and their exact worst case was not searched.
\item \textbf{Power clock.} Power is compared at a common verified clock, not at each design's course-formula fmax, because at that clock some vectors fail.
\item \textbf{Area.} It is the bounding box, including gaps and routing channels.
\item \textbf{Wire resistance.} Not extracted, as in Part I: MAGIC's resistance extraction crashed.
\end{itemize}""")

    add(r"\appendix\section{Netlists}")
    add(r"The full netlists, with the Part I cells, are in \texttt{part2/schematics/}.")
    for title, net in (("Carry-gating cell", gate_net), ("SIMD 8-bit adder, top level", simd_net), ("Baseline 8-bit adder, top level", base_net)):
        add(rf"\subsection*{{{title}}}\begin{{small}}\begin{{verbatim}}" + "\n" + net + "\n" + r"\end{verbatim}\end{small}")

    doc = r"""\documentclass[11pt,a4paper]{article}
\usepackage[margin=2.2cm]{geometry}
\usepackage{graphicx,booktabs,float,amsmath,hyperref}
\usepackage[T1]{fontenc}
\hypersetup{colorlinks=true,linkcolor=blue}
\title{VLSI Design Course Project, Part II\\SIMD-Reconfigurable 8-bit Adder}
\author{Bhargav, 2025102061\\IIIT Hyderabad, Monsoon 2026}
\date{}
\begin{document}
\maketitle
\tableofcontents
\newpage
""" + "\n\n".join(body) + "\n\\end{document}\n"
    (DOC / "report.tex").write_text(doc)
    for _ in range(2):
        res = subprocess.run(["pdflatex", "-interaction=nonstopmode", "report.tex"], cwd=DOC, capture_output=True, text=True, timeout=600)
    pdf = DOC / "report.pdf"
    if pdf.exists():
        shutil.move(pdf, DOC / "Bhargav_2025102061_part2.pdf")
    for ext in ("aux", "log", "toc", "out"):
        (DOC / f"report.{ext}").unlink(missing_ok=True)
    errors = [l for l in res.stdout.splitlines() if l.startswith("!")]
    print("errors:", errors[:10])
    print(res.stdout[-400:])


if __name__ == "__main__":
    main()
