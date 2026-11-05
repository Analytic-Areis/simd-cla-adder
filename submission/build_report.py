#!/usr/bin/env python3
"""Submission report, IEEE two-column style. Every number is read from a result file at build time.

Run figures.py sims and figures.py shots first, then:  python3 build_report.py
Writes report.tex and Bhargav_2025102061.pdf in this folder.
Draft 1 holds Parts I and II. Sections XIII and XIV are placeholders for Part III.
"""
import csv
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "part1" / "cells"))

from cellgen import config as cfg   # noqa: E402
from dff import tspc   # noqa: E402
from final_flow import build, final_design   # noqa: E402
from figures import GATES   # noqa: E402

P1R, P2R = ROOT / "part1" / "results", ROOT / "part2" / "results"
FIN = P1R / "final"
FIG = HERE / "figures"


def j(path):
    return json.loads(Path(path).read_text())


def rows(path):
    return list(csv.DictReader(open(path)))


def tex(s):
    s = str(s)
    if "$" in s:
        return s
    return s.replace("\\", r"\textbackslash{}").replace("_", r"\_").replace("%", r"\%").replace("&", r"\&").replace("#", r"\#")


def table(caption, head, body, spec=None, label=None, star=False, size=r"\footnotesize"):
    spec = spec or "|" + "|".join("c" * len(head)) + "|"
    env = "table*" if star else "table"
    out = [rf"\begin{{{env}}}[{'!t' if star else 'H'}]\centering{size}", rf"\caption{{{caption}}}"]
    if label:
        out.append(rf"\label{{{label}}}")
    out += [rf"\begin{{tabular}}{{{spec}}}\hline", " & ".join(tex(h) for h in head) + r" \\ \hline"]
    out += [" & ".join(tex(c) for c in r) + r" \\ \hline" for r in body]
    out += [r"\end{tabular}", rf"\end{{{env}}}"]
    return "\n".join(out)


def fig(path, caption, width=r"\columnwidth", star=False, label=None):
    src = Path(path)
    if not src.exists():
        raise FileNotFoundError(path)
    name = src.name if src.parent == FIG else f"{src.parent.name}_{src.name}"
    if src.parent != FIG:
        shutil.copy(src, FIG / name)
    env = "figure*" if star else "figure"
    lab = rf"\label{{{label}}}" if label else ""
    place = "!t" if star else "H"   # single-column floats stay under their heading, as in the reference
    return rf"\begin{{{env}}}[{place}]\centering\includegraphics[width={width}]{{figures/{name}}}\caption{{{caption}}}{lab}\end{{{env}}}"


def widths(cell):
    n = sorted({d.w_lam for d in cell.devices if d.kind == "n"})
    p = sorted({d.w_lam for d in cell.devices if d.kind == "p"})
    return "/".join(f"{x:g}" for x in n), "/".join(f"{x:g}" for x in p)


def subckt(path, name, width=60):
    text = Path(path).read_text()
    m = re.search(rf"(?ms)^\.subckt {name} .*?^\.ends {name}", text)
    out = []
    for line in m.group(0).splitlines():
        cur = ""
        for w in line.split():
            if cur and len(cur) + len(w) + 1 > width:
                out.append(cur)
                cur = "+ " + w
            else:
                cur = f"{cur} {w}" if cur else w
        out.append(cur)
    return "\n".join(out)


def main():
    FIG.mkdir(exist_ok=True)
    P1F, P2F = ROOT / "part1" / "documentation" / "figures", ROOT / "part2" / "documentation" / "figures"
    SCH = ROOT / "part1" / "schematics" / "transistor_level" / "final"
    label, sizes, flips, tag = final_design()
    adder = build(label, sizes, flips, "cla_final")
    post, sch = j(FIN / f"{tag}_post.json"), j(FIN / "final_schematic.json")
    system, dff, verify, multi = j(FIN / "system.json"), j(FIN / "dff.json"), j(FIN / "multi_verify.json"), j(FIN / "multi.json")
    bound = j(FIN / "resistance" / f"{tag}_bound.json")
    sch_power = j(FIN / "schematic_power.json")
    unit, blocks, tradeoff = rows(P1R / "phase3_unit_comparison.csv"), rows(P1R / "phase7_block_postlayout.csv"), rows(P1R / "phase4_tradeoff.csv")
    hint = rows(FIN / "hint_vector_postlayout.csv")
    truth = rows(P1R / "final_truth_table.csv")
    gd = j(HERE / "gate_delays.json")
    course, power, lay = system["course"], system["power"], system["layout"]
    ff = tspc(**dff["params"])
    sic, tpd = post["worst_pin_ps"], course["tpd_max_ps"]

    # Part II
    gate2, cells2 = j(P2R / "gate.json"), j(P2R / "layout_cells.json")
    lay2 = {k: j(P2R / f"layout_{k}.json") for k in ("simd", "base")}
    pen, pw, settle = j(P2R / "penalty.json"), j(P2R / "power.json"), j(P2R / "settle.json")
    pwc = j(P2R / "power_at_course_fmax.json")
    srch = {(d, m, v): j(P2R / f"search_{d}_m{m}_{v}.json") for d, m in (("base", 0), ("simd", 0), ("simd", 1)) for v in ("sch", "post")}
    PEN = {(r["design"], r["mode"], r["view"]): r for r in pen}
    common = {(r["design"], r["mode"]): r for r in pw["runs"] if r["run"] == "common"}
    long = {(r["design"], r["mode"]): r for r in pw["runs"] if r["run"] == "long200"}
    case = {("base", 0): "Baseline", ("simd", 0): "SIMD, mode 0", ("simd", 1): "SIMD, mode 1"}
    s0, b0 = srch[("simd", 0, "post")]["tpd_max_ps"], srch[("base", 0, "post")]["tpd_max_ps"]
    pp = PEN[("simd", 0, "post")]
    edp = pw["edp"]
    edp_pen = 100 * (edp["simd_m0"]["edp_fj_ps"] / edp["base_m0"]["edp_fj_ps"] - 1)
    long_pen = 100 * (long[("simd", 0)]["power_uw"] / long[("base", 0)]["power_uw"] - 1)
    area_pen = 100 * (lay2["simd"]["area_um2"] / lay2["base"]["area_um2"] - 1)

    B = []
    add = B.append

    # ---------------------------------------------------------------- I
    add(r"""\section{Introduction}
Addition is the core of every datapath. A ripple-carry adder passes the carry from bit to bit, so the top sum bit waits for every lower bit and the delay grows with word length. A carry look-ahead adder (CLA) computes every carry from generate and propagate signals in parallel, so no carry waits for the one below it.

This project designs a registered 4-bit CLA in TSMC 180\,nm (Part I), then joins two copies into an 8-bit adder that can be reconfigured into two independent 4-bit adders with one control signal (Part II). The primary objective throughout is the smallest \emph{post-layout worst-case delay}; area and power are reported as trade-offs. Inputs are captured by D flip-flops on a rising clock edge and the result is captured on the next rising edge. Every output drives a $W_p/W_n = 20\lambda/10\lambda$ inverter, $\lambda = 0.09\,\mu$m, $V_{DD} = 1.8$\,V.

All simulations use NGSPICE with the provided model; all layouts use MAGIC with the provided SCN6M\_DEEP technology file. Every plot carries the title format \texttt{Name-Roll-question-part}, as the course asks.""")

    # ---------------------------------------------------------------- II
    add(r"""\section{Design Proposal}
\begin{itemize}
\item $V_{DD} = 1.8$\,V, technology TSMC 180\,nm, $L_n = L_p = 2\lambda$.
\item Logic style: static CMOS for every adder gate; TSPC dynamic flip-flops.
\end{itemize}
\subsection{Generate, Propagate, Carry and Sum}
For bits $a_i$ and $b_i$:
\[ g_i = a_i b_i, \qquad p_i = a_i \oplus b_i, \]
\[ c_{i+1} = g_i + p_i c_i, \qquad s_i = p_i \oplus c_i . \]
Expanding the carry rule removes the ripple:
\begin{align*}
c_1 &= g_0 + p_0 c_0\\
c_2 &= g_1 + p_1 g_0 + p_1 p_0 c_0\\
c_3 &= g_2 + p_2 g_1 + p_2 p_1 g_0 + p_2 p_1 p_0 c_0\\
c_4 &= g_3 + p_3 g_2 + p_3 p_2 g_1 + p_3 p_2 p_1 g_0 + p_3 p_2 p_1 p_0 c_0
\end{align*}
Built directly, $c_4$ needs a five-input AND term, so a five-transistor stack, and $c_0$ fans out to every carry gate. Both make the circuit slow.

\subsection{Optimization}
\textbf{OR-type transmit.} In the carry terms, $p_i$ can be replaced by $t_i = a_i + b_i$. The two differ only when $a_i = b_i = 1$, and then $g_i = 1$ already sets the carry. A NOR2 gives $\overline{t_i}$ in one light stage, and XOR is kept only for the sum. The idea follows Miao and Li~\cite{miao}.

\textbf{Prefix carry tree.} Bits are merged two at a time into group signals, and $c_0$ is added last:
\[ G_{1:0} = g_1 + t_1 g_0, \quad T_{1:0} = t_1 t_0, \]
\[ G_{3:0} = G_{3:2} + T_{3:2}\,G_{1:0}, \quad G_{2:0} = g_2 + t_2\,G_{1:0}, \]
\[ c_k = G_{k-1:0} + T_{k-1:0}\, c_0 . \]
No gate has more than two transistors in series, and $c_0$ reaches each carry through one inverter and one gate.""")
    add(table("Unit-size comparison of six candidate architectures, schematic, worst over all 4608 single-input transitions",
              ["Candidate", "T", "Worst (ps)", "Hint vector (ps)"],
              [(r["candidate"], r["transistors"], r["worst_pin_ps"], r["hint_vector_pin_ps"]) for r in unit if "/" not in r["candidate"]]))
    add(r"""C1 is the textbook XOR and NAND-NAND design, C2 one complex gate per carry, R C2 with a mirror gate for $c_4$, C3 a design with stacks limited to 3, C4 the prefix tree, and E a static Manchester chain. C4 was fastest, and remained fastest after sizing and layout, so it was chosen. The six designs differ only in their carry logic.""")

    # ---------------------------------------------------------------- III
    add(r"\section{Design Details}")
    add(fig(P1F / "block_diagram.png", "Block-level architecture of the 4-bit CLA.", star=True, width=r"0.92\textwidth"))
    add(r"""\textbf{Blocks.} Each bit has a P/G front end: NAND2 gives $\overline{g_i}$, NOR2 gives $\overline{t_i}$, and two compound gates reuse them to make $p_i$ (AOI21) and $\overline{p_i}$ (OAI21). The carry block is the prefix tree: OAI21 and NOR2 for pairs, AOI21 and NAND2 for groups down to bit 0, then one OAI21 per carry with $\overline{c_0}$. The sum is a dual-rail AOI22 XOR, $s_i = \overline{p_i c_i + \overline{p_i}\,\overline{c_i}}$, with an inverter for $\overline{c_i}$.

\textbf{Sizing.} The reference inverter is $W_n = 10\lambda$, $W_p = 20\lambda$. A unit-size gate matches its worst-case pull-up and pull-down resistance to that inverter. The final sizes were found by an automated search that minimised the worst delay over all transitions, then repeated with wire capacitance taken from the extracted layout. Table~\ref{tab:gatesize} lists the unit cells used in Sections IV and VI; Table~\ref{tab:sizing} lists every instance of the final adder.""")
    add(table("Unit cell sizes (widths in $\\lambda$; several values are different stack positions)", ["Cell", "T", "NMOS W", "PMOS W"],
              [(n, c.transistor_count, *widths(c)) for n, c, _, _, _ in GATES], label="tab:gatesize"))
    srows = []
    for inst, cell, pins in adder.instances:
        n, p = widths(cell)
        srows.append((inst, cell.name.split("_x")[0], pins[cell.outputs[0]], n, p))
    add(table("Final adder sizing, every instance (widths in $\\lambda$)", ["Inst.", "Cell", "Output", "NMOS W", "PMOS W"], srows, label="tab:sizing", size=r"\scriptsize"))
    add(r"""\textbf{D flip-flop.} A true single-phase clock (TSPC) flip-flop~\cite{yuan} needs one clock and 11 transistors. At a 15\,fF load it gave clock-to-Q plus setup of 212.9\,ps, against 316.8\,ps for a 22-transistor transmission-gate master-slave flip-flop, so TSPC was chosen.""")
    add(fig(SCH / "dff_final.png", f"TSPC flip-flop, stage drives x{dff['params']['s1']:g}, x{dff['params']['s2']:g}, x{dff['params']['s3']:g}, x{dff['params']['q']:g}, sized at the largest adder input load of {dff['load_ff']:.2f} fF.", star=True, width=r"0.85\textwidth"))
    for c, cap in (("nand2_x1", "NAND2"), ("aoi21_x1", "AOI21, used for $p_i$ and the group generates"), ("oai21_x1", "OAI21, used for $\\overline{p_i}$ and the final carries")):
        add(fig(SCH / f"{c}.png", f"Transistor schematic: {cap}.", r"0.8\columnwidth"))

    # ---------------------------------------------------------------- IV
    add(r"""\section{NGSPICE Simulation (Pre-Layout)}
Each gate is driven through two inverters, so its inputs have realistic edges, and its output drives the $20\lambda/10\lambda$ inverter. Inputs follow an Eulerian walk, which applies every single-input change from every state. Delay is measured from the 50\% point of the changing input to the last 50\% crossing of the output.""")
    order = [("Inverter", "inv_x1"), ("NAND2", "nand2_x1"), ("NOR2", "nor2_x1"), ("AOI21", "aoi21_x1"), ("OAI21", "oai21_x1"), ("AOI22 XOR (sum)", "xor_aoi22_x1")]
    for nice, c in order:
        add(rf"\subsection{{{tex(nice)}}}")
        add(fig(FIG / f"gate_{c}_schematic.png", f"{tex(nice)} plot: pre-layout."))
    add(r"\subsection{D Flip-Flop}")
    add(fig(FIG / "dff_schematic.png", "TSPC D flip-flop plot: pre-layout. Q takes D at each rising clock edge."))
    for name, nice in (("pg0", "P/G Block"), ("carry", "Carry Block"), ("sum0", "Sum Block")):
        add(rf"\subsection{{{nice}}}")
        add(fig(FIG / f"block_{name}_schematic.png", f"{nice} plot: pre-layout."))
    add(table("Gate delays, pre-layout, worst over all single-input changes", ["Gate", "tpLH (ps)", "tpHL (ps)", "Errors"],
              [(n, gd[n]["schematic"]["tplh_ps"], gd[n]["schematic"]["tphl_ps"], gd[n]["schematic"]["errors"]) for n, _ in order]))

    # ---------------------------------------------------------------- V
    S, Q = dff["schematic"], dff["postlayout"]
    add(rf"""\section{{D Flip-Flop Characterization from NGSPICE}}
\subsection{{TSPC Flip-Flop}}
The flip-flop is characterised at its real load, {dff['load_ff']:.2f}\,fF, with both data values. Definitions follow Stojanovi\'c and Oklobd\v{{z}}ija~\cite{{stoj}}.
\subsection{{Clock to Q Delay $t_{{cq}}$}}
Time from the 50\% point of the rising clock to the 50\% point of Q, with data set up long before the edge.""")
    add(table("Clock to Q delay, pre-layout", ["Parameter", "Time (ps)"],
              [("$t_{cq}$, Q rising", S["tcq_rise_ps"]), ("$t_{cq}$, Q falling", S["tcq_fall_ps"]), ("$t_{cq}$ (worst)", S["tcq_ps"])]))
    add(r"""\subsection{Set Up Time $t_{su}$}
The shortest D-to-clock time for which clock-to-Q stays within 10\% of its long-setup value.""")
    add(table("Set up time, pre-layout", ["Parameter", "Time (ps)"],
              [("$t_{su}$, D rising", S["tsu_rise_ps"]), ("$t_{su}$, D falling", S["tsu_fall_ps"]), ("$t_{su}$ (worst)", S["tsu_ps"])]))
    add(r"""\subsection{Hold Time $t_{hold}$}
The shortest clock-to-D time for which a later data change leaves Q correct, with no disturbance above 10\% of $V_{DD}$.""")
    add(table("Hold time, pre-layout", ["Parameter", "Time (ps)"],
              [("$t_{hold}$, D rising", S["thold_rise_ps"]), ("$t_{hold}$, D falling", S["thold_fall_ps"]), ("$t_{hold}$ (worst)", S["thold_ps"])]))
    add(fig(P1F / "dff_sweep.png", "Clock-to-Q and D-to-Q delay against D-to-clock time, schematic."))

    # ---------------------------------------------------------------- VI
    add(r"""\section{MAGIC Layouts}
Every layout below is a screenshot of MAGIC's own layout window. Each cell passes MAGIC's DRC with zero errors, and each extracted netlist matches the schematic in LVS, using a comparison script written for this project because netgen was not available. Post-layout plots use the netlist MAGIC extracted, with all parasitic capacitance.""")
    for (nice, c) in order:
        add(rf"\subsection{{{tex(nice)}}}")
        add(fig(FIG / f"magic_gate_{c}.png", f"MAGIC layout of {tex(nice)}.", r"0.36\columnwidth"))
        add(fig(FIG / f"gate_{c}_post-layout.png", f"{tex(nice)} plot: post-layout."))
    add(r"\subsection{D Flip-Flop}")
    add(fig(FIG / "magic_gate_dff.png", "MAGIC layout of the TSPC D flip-flop.", r"0.45\columnwidth"))
    add(fig(FIG / "dff_post-layout.png", "TSPC D flip-flop plot: post-layout."))
    add(r"\subsection{Clock to Q, Set Up and Hold Time of the Flip-Flop}")
    add(table("Flip-flop timing, pre- and post-layout", ["Parameter (ps)", "Pre-layout", "Post-layout"],
              [("$t_{cq}$", S["tcq_ps"], Q["tcq_ps"]), ("$t_{su}$", S["tsu_ps"], Q["tsu_ps"]), ("$t_{hold}$", S["thold_ps"], Q["thold_ps"])]))
    for name, cell, nice in (("pg0", "pg0_b", "P/G Block"), ("carry", "carry_b", "Carry Block"), ("sum0", "sum0_b", "Sum Block")):
        add(rf"\subsection{{{nice}}}")
        add(fig(FIG / f"magic_block_{cell}.png", f"MAGIC layout of the {nice}.", r"0.95\columnwidth" if name == "carry" else r"0.45\columnwidth"))
        add(fig(FIG / f"block_{name}_post-layout.png", f"{nice} plot: post-layout."))
    add(table("Gates and blocks: pre-layout against post-layout. Block delays are worst over all their single-input transitions.",
              ["Cell", "Pre tpLH", "Pre tpHL", "Post tpLH", "Post tpHL"],
              [(n, gd[n]["schematic"]["tplh_ps"], gd[n]["schematic"]["tphl_ps"], gd[n]["post-layout"]["tplh_ps"], gd[n]["post-layout"]["tphl_ps"]) for n, _ in order]
              + [(f"block {b['block']}", b["sch_tplh_ps"], b["sch_tphl_ps"], b["post_tplh_ps"], b["post_tphl_ps"]) for b in blocks],
              size=r"\scriptsize"))
    add(r"Pre- and post-layout plots match for every gate and block. Delays change little at cell level, because a single cell has short wires; the difference grows once the cells are wired together (Section XI).")

    # ---------------------------------------------------------------- VII
    add(rf"""\section{{NGSPICE Circuit (Pre-Layout)}}
The full circuit of the course's Figure 1(i) has 9 input flip-flops ($a$, $b$ and $c_0$), the adder and 5 output flip-flops. A ninth flip-flop on $c_0$ keeps every input on the same clock. Inputs change before a rising edge; the sum appears at the output flip-flops one clock later.""")
    add(fig(FIG / "system_schematic.png", "Registered adder plot: pre-layout. Each sum appears one clock after its inputs.", star=True, width=r"0.9\textwidth"))
    add(rf"""\textbf{{Worst-case delay.}} The worst case was found by search, not assumed: all 4608 single-input transitions, each timed to the last 50\% crossing so false sums cannot shorten it. Pre-layout worst: \textbf{{{sch['worst_pin_ps']:.2f}\,ps}}, {tex(sch['worst_pin_arc'])}. The course hint vector, $A = 1111$, $B = 0000$ with $c_0$ toggling, gives only {sch['hint_worst_ps']:.2f}\,ps, because $c_0$ enters the prefix tree last.

\textbf{{Clock.}} The shortest clock at which the pre-layout registered circuit gave no wrong outputs on {system['vectors']} vectors is {system['schematic']['min_period_ps']}\,ps, {system['schematic']['fmax_ghz']:.3f}\,GHz.""")

    # ---------------------------------------------------------------- VIII
    places = system["placements"]
    pg_x = sorted({q[1] for q in places if q[0].startswith("pg")})
    bit_pitch = sorted({b - a for a, b in zip(pg_x, pg_x[1:])})
    row_y = sorted({q[2] for q in places})
    row_pitch = [b - a for a, b in zip(row_y, row_y[1:])]
    add(r"\section{MAGIC Layout Plan}")
    add(fig(P1F / "floorplan.png", "MAGIC layout floor plan. Rows from the bottom: input flip-flops, P/G bits, carry block, sum bits, output flip-flops."))
    add(r"Signals flow upward through the rows. The P/G and sum cells sit on one bit pitch, so each sum bit lines up with its own P/G bit.")
    add(table("Pitches", ["Pitch", "Value ($\\lambda$)", "Value ($\\mu$m)"],
              [("Horizontal, bit pitch", "/".join(map(str, bit_pitch)), "/".join(f"{x * 0.09:.2f}" for x in bit_pitch)),
               ("Vertical, row pitches", ", ".join(map(str, row_pitch)), ", ".join(f"{x * 0.09:.2f}" for x in row_pitch)),
               ("Routing grid, metal 3 and 4", "9", "0.81")]))

    # ---------------------------------------------------------------- IX
    add(r"\section{Final MAGIC Layout}")
    add(fig(P1F / "magic_adder.png", "Final 4-bit adder layout in MAGIC."))
    add(fig(P1F / "magic_registered.png", "Full registered circuit layout in MAGIC, with input and output flip-flops."))
    add(table("Layout results", ["Layout", "DRC", "LVS", "Size ($\\lambda$)", "Area ($\\mu$m$^2$)"],
              [("Adder", post["drc"], "match", f"{post['width_lambda']}x{post['height_lambda']}", post["area_um2"]),
               ("Registered", lay["drc"], "match", f"{lay['width_lambda']}x{lay['height_lambda']}", lay["area_um2"])]))
    add(rf"The adder has {post['transistors']} transistors and the registered circuit {post['transistors'] + 14 * ff.transistor_count}. Extracted wire capacitance is {post['wire_cap_ff']}\,fF for the adder and {system['wire_cap_ff']}\,fF for the registered circuit.")

    # ---------------------------------------------------------------- X
    hw = max(float(r["delay_ps"]) for r in hint)
    add(r"\section{Post-Layout Simulations and Delays}")
    add(fig(FIG / "system_post-layout.png", "Registered adder plot: post-layout. The outputs match the pre-layout run.", star=True, width=r"0.9\textwidth"))
    add(r"\subsection{Critical Path Delay}")
    add(table("Course hint vector, $A = 1111$, $B = 0000$, $c_0$ toggling, post-layout", ["$c_0$ edge", "Output", "Type", "Delay (ps)"],
              [(r["c0_edge"], r["output"].upper(), r["kind"], r["delay_ps"]) for r in hint], size=r"\scriptsize"))
    add(fig(P1F / "hint_postlayout.png", "Hint vector, extracted netlist, 50\\% crossings marked."))
    add(rf"""The slowest hint-vector output takes {hw:.1f}\,ps, but the search over all transitions finds a slower one: \textbf{{{sic:.2f}\,ps}}, {tex(post['worst_pin_arc'])}. When several inputs change together, a sample of {multi['transitions']} transitions re-simulated on the extracted netlist gives \textbf{{{verify['worst_ps']}\,ps}}. This is taken as $t_{{pd,max}}$.""")
    add(fig(P1F / "worst_arc_postlayout.png", "Worst single-input transition, extracted netlist."))
    add(rf"""\subsection{{Maximum Clock Frequency}}
The course formula gives
\[ T = t_{{pd,max}} + t_{{su}} + t_{{hold}} = {course['tpd_max_ps']} + {course['tsetup_ps']} + {course['thold_ps']} = {course['T_course_ps']}\,\text{{ps}}, \]
$f_{{max}} = {course['fmax_course_ghz']}$\,GHz. At that clock the extracted registered circuit gave {course['errors_at_course_formula']} wrong output samples, because the formula leaves out clock-to-Q. Using $T \ge t_{{cq}} + t_{{pd,max}} + t_{{su}} = {course['T_physical_ps']}$\,ps instead, and checking by simulation, the shortest clock that works is \textbf{{{system['postlayout']['min_period_ps']}\,ps, {system['postlayout']['fmax_ghz']:.3f}\,GHz}}.""")
    add(rf"""\subsection{{Power}}
\[ P_{{avg}} = \frac{{V_{{DD}}}}{{T_2 - T_1}} \int_{{T_1}}^{{T_2}} I_{{VDD}}(t)\,dt \]
At the verified clock of {power['period_ps']}\,ps, over {power['critical_and_random']['cycles']} cycles of random and critical vectors, the circuit's own supply gives $P_{{avg}} = {power['critical_and_random']['pavg_mw']}$\,mW, so $PDP = P_{{avg}} \times t_{{pd,max}} = {power['critical_and_random']['pdp_fj']}$\,fJ. Input drivers, clock buffers and load inverters use a separate supply.""")
    add(table("Comparison of pre- and post-layout", ["Parameter", "Pre-Layout", "Post-Layout"], [
        ("Worst single-input delay", f"{sch['worst_pin_ps']:.2f} ps", f"{sic:.2f} ps"),
        ("Hint vector delay", f"{sch['hint_worst_ps']:.2f} ps", f"{post['hint_worst_ps']:.2f} ps"),
        ("$t_{cq}$", f"{S['tcq_ps']} ps", f"{Q['tcq_ps']} ps"),
        ("$t_{su}$", f"{S['tsu_ps']} ps", f"{Q['tsu_ps']} ps"),
        ("$t_{hold}$", f"{S['thold_ps']} ps", f"{Q['thold_ps']} ps"),
        ("$T_{clk}(min)$, verified", f"{system['schematic']['min_period_ps']} ps", f"{system['postlayout']['min_period_ps']} ps"),
        ("$f_{clk}(max)$, verified", f"{system['schematic']['fmax_ghz']:.3f} GHz", f"{system['postlayout']['fmax_ghz']:.3f} GHz"),
        ("$P_{avg}$ at the post-layout clock", f"{sch_power['same_clock']['pavg_mw']} mW", f"{power['critical_and_random']['pavg_mw']} mW"),
    ], label="tab:prepost"))
    add(rf"""Post-layout delays are longer, by {100 * (sic / sch['worst_pin_ps'] - 1):.1f}\% for the worst single-input delay, because the extracted netlist adds the capacitance of every wire and junction. Flip-flop clock-to-Q drops slightly after layout, because shared diffusion in the layout has less capacitance than the schematic's estimate.""")
    add(r"\subsection{Area-Delay Trade-off}")
    add(table("Uniform scaling of the final sizes, post-layout", ["Scale", "Delay (ps)", "Area ($\\mu$m$^2$)", "P (mW)"],
              [(r["scale"], r["post_pin_ps"], r["area_um2"], r["power_mw_1ns"]) for r in sorted(tradeoff, key=lambda r: float(r["scale"]))]))
    add(rf"Bigger is not always faster: scaling up by 1.2 makes the extra load outweigh the extra drive. MAGIC's resistance extraction crashed on this layout, so resistance was bounded instead: with the longest poly run's resistance in series with every gate, the worst delay rises by at most {bound['increase_pct']}\%.")

    # ---------------------------------------------------------------- XI Part II
    add(r"""\section{Part II: SIMD-Reconfigurable 8-bit Adder}
GPUs often split one wide datapath into narrower sub-words~\cite{hp}. Here two copies of the Part I adder, CLA0 for bits 3..0 and CLA1 for bits 7..4, form an 8-bit adder with a control input SIMD\_MODE:
\begin{itemize}
\item SIMD\_MODE $= 0$: CLA0's carry-out goes into CLA1's carry-in, one 8-bit add.
\item SIMD\_MODE $= 1$: the inter-block carry is forced to 0, two independent 4-bit adds.
\end{itemize}
The cost of this is measured against a \emph{baseline}: the same two adders wired directly, with no gating.""")
    add(r"\subsection{Architecture}")
    add(r"The block diagram below shows the two Part I adders and the carry-gating cell between them. CLA0's carry-out, c4lo, is also an output, because in dual mode it is the carry of the lower 4-bit result; it drives the same 20$\lambda$/10$\lambda$ load as the other outputs. The baseline is the same diagram without the gate, with c4lo wired straight to CLA1's carry-in.")
    add(fig(P2F / "2.0a_simd8-blocks.png", "SIMD 8-bit adder: CLA0, the carry-gating cell and CLA1. c4lo is CLA0's carry-out and cinh CLA1's carry-in.", star=True, width=r"0.95\textwidth"))
    add(r"""\subsection{Carry-Gating Cell}
\[ c_{in,hi} = c_{out,lo} \cdot \overline{\mathrm{SIMD\_MODE}} \]
This is an AND gate. In static CMOS the cell is a NAND2 followed by an inverter on the carry path, with a unit inverter making $\overline{\mathrm{SIMD\_MODE}}$; the mode is held during an add, so that inverter is off the timing path. The cell has 8 transistors.""")
    add(fig(P2F / "2.6_gating-cell-size-sweep.png", f"Gate sizing sweep, Cin to S7 in mode 0, schematic. Best: NAND2 x{gate2['nand']:g}, inverter x{gate2['inv']:g}."))
    add(fig(P2F / "magic_gate.png", "MAGIC layout of the carry-gating cell, with carry pads above it.", r"0.6\columnwidth"))
    a2 = gate2["alone"]
    add(table("Carry-gating cell alone, cout\\_lo to cin\\_hi with the 20/10$\\lambda$ load", ["View", "Worst", "Rising", "Falling"],
              [("Pre-layout", a2["sch"]["worst_ps"], a2["sch"]["rise_ps"], a2["sch"]["fall_ps"]), ("Post-layout", a2["post"]["worst_ps"], a2["post"]["rise_ps"], a2["post"]["fall_ps"])]))
    c = cells2["cla4_cell"]
    add(rf"""\subsection{{Layout}}
The Part I adder was laid out again with two extra metal 3 pads above its top row, for $c_4$ and $c_0$. The 8-bit layout places this cell twice, with the gating cell between the copies in the SIMD design, and joins the inter-block carries on metal 5, which no cell uses. A first attempt that placed all gates of both adders in one set of rows ran out of routing tracks.""")
    add(fig(P2F / "magic_simd8.png", "SIMD 8-bit adder in MAGIC: CLA0, the gating cell and CLA1. The dashed lines at the top are metal 5.", star=True, width=r"0.95\textwidth"))
    add(fig(P2F / "magic_simd8_gate_zoom.png", "Close-up in MAGIC: the gating cell between the two adders, with its two metal 5 carries."))
    add(fig(P2F / "magic_base8.png", "Baseline 8-bit adder in MAGIC: c4lo runs on metal 5 straight from CLA0 to CLA1."))
    add(table("Part II layout results", ["Design", "DRC", "Devices (LVS)", "Area ($\\mu$m$^2$)"],
              [("Baseline", lay2["base"]["drc"], f"{lay2['base']['transistors']}, match", lay2["base"]["area_um2"]),
               ("SIMD", lay2["simd"]["drc"], f"{lay2['simd']['transistors']}, match", lay2["simd"]["area_um2"])]))
    add(r"""\subsection{Worst-Case Delay in Both Modes}
The search runs 13,312 single-input transitions per case: every transition of CLA0's nine inputs with CLA1 set to pass a carry through all four bits, and every transition of CLA1's eight inputs with CLA0's carry-out held at 0 and at 1.""")
    add(table("Worst-case propagation delay", ["Case", "Pre-layout (ps)", "Post-layout (ps)"],
              [(case[(d, m)], srch[(d, m, "sch")]["tpd_max_ps"], srch[(d, m, "post")]["tpd_max_ps"]) for d, m in (("base", 0), ("simd", 0), ("simd", 1))]))
    add(fig(P2F / "2.5_worst-delay-per-output-postlayout.png", "Worst post-layout delay to each output.", star=True, width=r"0.85\textwidth"))
    w = srch[("simd", 0, "post")]["worst"]
    add(rf"In mode 0 the worst path is {w['pin']} {w['pin_edge']} to {w['output'].upper()}, through CLA0's carry tree and the gating cell into CLA1. In mode 1 the carry never crosses, so the worst path stays inside one 4-bit block.")
    add(r"""\subsection{Delay Penalty}
Worst-case carry vector $A = $ 0xFF, $B = $ 0x00, $c_{in,0}$ toggling, delay from $c_{in,0}$ to $S_7$:
\[ \text{Delay penalty} = \frac{t_{pd,SIMD} - t_{pd,baseline}}{t_{pd,baseline}} \times 100\% \]""")
    add(table("Cin to S7 on the worst-case vector", ["View", "Baseline (ps)", "SIMD m0 (ps)", "Penalty"],
              [(v, f"{PEN[('base', None, k)]['cin_rise_to_s7_ps']:.2f}", f"{PEN[('simd', 0, k)]['cin_rise_to_s7_ps']:.2f}",
                f"+{PEN[('simd', 0, k)]['penalty_rise_ps']:.2f} ps, {PEN[('simd', 0, k)]['penalty_rise_pct']:.2f}%") for v, k in (("Pre-layout", "sch"), ("Post-layout", "post"))]))
    add(fig(P2F / "2.4_worst-case-vector-postlayout.png", "Post-layout waveforms on the worst-case vector. In mode 1 CLA1's carry-in stays at 0.", star=True, width=r"0.8\textwidth"))
    add(rf"The gate alone takes {a2['post']['worst_ps']:.2f}\,ps, but the penalty is only {pp['penalty_rise_ps']:.2f}\,ps: in the baseline, CLA0's carry-out drives CLA1's carry-in load directly, while in the SIMD design the gate isolates that load, so CLA0's carry-out switches sooner.")
    fm = pw["fmax_ghz"]
    sr = {}
    for r in settle:
        sr.setdefault(r["period_ps"], {})[(r["design"], r["mode"])] = r["errors"]
    add(rf"""\subsection{{Power Penalty}}
Course-formula $f_{{max}}$, with the Part I flip-flop's post-layout $t_{{su}}$ and $t_{{hold}}$: baseline {fm['base_m0']:.3f}\,GHz, SIMD mode 0 {fm['simd_m0']:.3f}\,GHz, mode 1 {fm['simd_m1']:.3f}\,GHz. At those clocks some random vectors that change several inputs at once did not settle, so the shortest clock at which all three cases settle on the same 200 random vectors was found: {pw['common_period_ps']:g}\,ps. Power is compared there, with identical inputs for all three.
\[ \text{{Power penalty}} = \frac{{P_{{SIMD,0}} - P_{{baseline}}}}{{P_{{baseline}}}} \times 100\% \]""")
    add(table(f"Average power at {pw['common_period_ps']:g} ps, post-layout", ["Case", "10 cycles ($\\mu$W)", "200 vectors ($\\mu$W)"],
              [(case[k], common[k]["power_uw"], long[k]["power_uw"]) for k in (("base", 0), ("simd", 0), ("simd", 1))]))
    add(rf"Power penalty in 8-bit mode: \textbf{{{pw['power_penalty_pct']:.2f}\%}} over 10 cycles, and {long_pen:.2f}\% over 200 vectors.")
    add(r"""\subsection{Energy-Delay Product}
\[ EDP = P_{avg} \times t_{pd}^2 \]""")
    add(table("Energy-delay product, post-layout", ["Case", "$P_{avg}$ ($\\mu$W)", "$t_{pd,max}$ (ps)", "EDP (J s)"],
              [(case[(d, m)], edp[f"{d}_m{m}"]["power_uw"], edp[f"{d}_m{m}"]["tpd_ps"], f"{edp[f'{d}_m{m}']['edp_fj_ps'] * 1e-27:.3e}") for d, m in (("base", 0), ("simd", 0), ("simd", 1))]))
    add(table("Cost of reconfigurability, SIMD mode 0 against the baseline, post-layout", ["Measure", "Penalty"], [
        ("Cin to S7 delay", f"{pp['penalty_rise_pct']:.2f}%"), ("$t_{pd,max}$", f"{100 * (s0 / b0 - 1):.2f}%"),
        ("Power, 10 cycles", f"{pw['power_penalty_pct']:.2f}%"), ("EDP", f"{edp_pen:.1f}%"),
        ("Transistors", f"+{lay2['simd']['transistors'] - lay2['base']['transistors']}"), ("Area", f"{area_pen:.1f}%")]))
    add(r"Delay counts twice in EDP, so the delay penalty dominates the small power penalty. In dual mode each add is only 4 bits long, so its EDP is far lower.")

    # ---------------------------------------------------------------- XII, XIII placeholders
    add(r"""\section{Verilog HDL}
\emph{To be completed in the next draft, with Part III: behavioural Verilog of the 4-bit CLA and the SIMD adder, test vectors for every mode, and annotated simulation waveforms.}

\section{FPGA Implementation}
\emph{To be completed in the next draft, with Part III: synthesis and implementation on the Boolean Board, test scenarios, and oscilloscope captures.}""")

    add(r"""\section*{Acknowledgment}
I thank Prof. Abhishek Srivastava for the course and this project, and the teaching assistants for their guidance.""")
    add(r"""\begin{thebibliography}{9}
\bibitem{miao} J. Miao and S. Li, ``A novel implementation of 4-bit carry look-ahead adder,'' in \emph{Proc. IEEE EDSSC}, 2017.
\bibitem{yuan} J. Yuan and C. Svensson, ``High-speed CMOS circuit technique,'' \emph{IEEE J. Solid-State Circuits}, vol. 24, no. 1, pp. 62--70, 1989.
\bibitem{stoj} V. Stojanovi\'c and V. G. Oklobd\v{z}ija, ``Comparative analysis of master-slave latches and flip-flops for high-performance and low-power systems,'' \emph{IEEE J. Solid-State Circuits}, vol. 34, no. 4, pp. 536--548, 1999.
\bibitem{zlat} R. Zlatanovici, S. Kao and B. Nikoli\'c, ``Energy-delay optimization of 64-bit carry-lookahead adders with a 240 ps 90 nm CMOS design example,'' \emph{IEEE J. Solid-State Circuits}, vol. 44, no. 2, pp. 569--583, 2009.
\bibitem{hp} J. L. Hennessy and D. A. Patterson, \emph{Computer Architecture: A Quantitative Approach}.
\bibitem{wh} N. Weste and D. Harris, \emph{CMOS VLSI Design}, 4th ed.
\bibitem{mano} M. Morris Mano, \emph{Digital Logic and Computer Design}.
\end{thebibliography}""")

    # ---------------------------------------------------------------- appendix netlists
    add(r"\section*{Appendix: Netlists}\addcontentsline{toc}{section}{Appendix: Netlists}")
    add(r"Generated netlists; widths and lengths in metres. All files are in the project folders \texttt{part1/spice/} and \texttt{part2/schematics/}.")
    gate_net = subckt(ROOT / "part2" / "schematics" / f"{gate2['cell']}.sp", gate2["cell"])
    simd_net = subckt(ROOT / "part2" / "schematics" / "simd8.sp", "simd8")
    adder_net = subckt_from_text(adder.spice(), "cla_final")
    for title, net in (("4-bit CLA, top level", adder_net), ("Carry-gating cell", gate_net), ("SIMD 8-bit adder, top level", simd_net)):
        add(rf"\subsection*{{{title}}}{{\scriptsize\begin{{verbatim}}" + "\n" + net + "\n" + r"\end{verbatim}}")

    doc = r"""\documentclass[conference,a4paper]{IEEEtran}
\usepackage{graphicx,amsmath,amssymb,array,cite,float}
\usepackage[hidelinks]{hyperref}
\raggedbottom   % no stretched gaps between pinned figures
\begin{document}
\onecolumn
{\small\tableofcontents}
\clearpage
\twocolumn
\title{VLSI Design Course Project\\Designing and Implementing a 4-bit CLA and a SIMD-Reconfigurable 8-bit Adder}
\author{\IEEEauthorblockN{Bhargav}
\IEEEauthorblockA{2025102061\\IIIT Hyderabad\\Draft 1: Parts I and II}}
\maketitle
\begin{abstract}
This project designs a 4-bit carry look-ahead adder (CLA) in TSMC 180\,nm, then joins two copies into a SIMD-reconfigurable 8-bit adder. The 4-bit adder uses a static CMOS prefix carry tree with OR-type transmit and dual-rail AOI22 sums, registered by TSPC flip-flops. Every gate, block and full circuit is simulated in NGSPICE before and after layout in MAGIC. The worst case is found by searching all single-input transitions rather than assumed: post-layout, the 4-bit adder's worst delay is """ + f"{sic:.2f}" + r""" ps and the registered circuit works up to """ + f"{system['postlayout']['fmax_ghz']:.3f}" + r""" GHz. In the 8-bit adder, a NAND2-and-inverter carry-gating cell switches between one 8-bit and two 4-bit additions, at a post-layout cost of """ + f"{pp['penalty_rise_pct']:.2f}" + r"""\% in carry delay and """ + f"{pw['power_penalty_pct']:.2f}" + r"""\% in power.
\end{abstract}
""" + "\n\n".join(B) + "\n\\end{document}\n"
    (HERE / "report.tex").write_text(doc)
    for _ in range(3):
        res = subprocess.run(["pdflatex", "-interaction=nonstopmode", "report.tex"], cwd=HERE, capture_output=True, text=True, timeout=900)
    pdf = HERE / "report.pdf"
    if pdf.exists():
        shutil.move(pdf, HERE / "Bhargav_2025102061.pdf")
    for ext in ("aux", "log", "toc", "out"):
        (HERE / f"report.{ext}").unlink(missing_ok=True)
    print("errors:", [l for l in res.stdout.splitlines() if l.startswith("!")][:10])
    print(res.stdout[-300:])


def subckt_from_text(text, name, width=60):
    m = re.search(rf"(?ms)^\.subckt {name} .*?^\.ends {name}", text)
    out = []
    for line in m.group(0).splitlines():
        cur = ""
        for w in line.split():
            if cur and len(cur) + len(w) + 1 > width:
                out.append(cur)
                cur = "+ " + w
            else:
                cur = f"{cur} {w}" if cur else w
        out.append(cur)
    return "\n".join(out)


if __name__ == "__main__":
    main()
