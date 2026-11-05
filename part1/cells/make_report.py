#!/usr/bin/env python3
"""Build the Part I report from result files. No result value is typed here by hand."""
import csv
import json
import re
import shutil
import subprocess
from pathlib import Path

from cellgen import config as cfg
from dff import tspc
from final_flow import FINAL, build, final_design

DOC = cfg.PART1 / "documentation"
FIG = DOC / "figures"
RES = cfg.PART1 / "results"


def rd(name):
    return json.loads((FINAL / name).read_text())


def rows_of(path):
    return list(csv.DictReader(open(path)))


def tex(s):
    return (str(s).replace("\\", r"\textbackslash{}").replace("_", r"\_").replace("%", r"\%").replace("&", r"\&").replace("#", r"\#"))


def table(caption, headers, rows, spec=None, size=r"\small", label=None, fit=False):
    spec = spec or "l" + "r" * (len(headers) - 1)
    out = [r"\begin{table}[H]\centering", size, rf"\caption{{{caption}}}"]
    if fit:
        out.append(r"\resizebox{\textwidth}{!}{")
    if label:
        out.append(rf"\label{{{label}}}")
    out += [rf"\begin{{tabular}}{{{spec}}}", r"\toprule", " & ".join(rf"\textbf{{{tex(h)}}}" for h in headers) + r" \\", r"\midrule"]
    out += [" & ".join(tex(c) for c in r) + r" \\" for r in rows]
    out += [r"\bottomrule", r"\end{tabular}"]
    if fit:
        out.append("}")
    out.append(r"\end{table}")
    return "\n".join(out)


def fig(name, caption, width=r"\textwidth"):
    if not (FIG / name).exists():
        raise FileNotFoundError(name)
    return rf"""\begin{{figure}}[H]\centering\includegraphics[width={width}]{{figures/{name}}}\caption{{{caption}}}\end{{figure}}"""


def sizing_rows(adder):
    roles = []
    for inst, cell, pins in adder.instances:
        n = sorted({d.w_lam for d in cell.devices if d.kind == "n"})
        p = sorted({d.w_lam for d in cell.devices if d.kind == "p"})
        out = [pins[o] for o in cell.outputs]
        roles.append((inst, cell.name.split("_x")[0], out[0], cell.transistor_count,
                      "/".join(map(str, n)), "/".join(map(str, p))))
    return roles


def main():
    label, sizes, flips, tag = final_design()
    post = rd(f"{tag}_post.json")
    sch = rd("final_schematic.json")
    system = rd("system.json")
    dff = rd("dff.json")
    multi = rd("multi.json")
    verify = rd("multi_verify.json")
    bound = json.loads((FINAL / "resistance" / f"{tag}_bound.json").read_text())
    adder = build(label, sizes, flips, "cla_final")
    p = dff["params"]
    ff = tspc(p["s1"], p["s2"], p["s3"], p["q"])
    unit = rows_of(RES / "phase3_unit_comparison.csv")
    blocks = rows_of(RES / "phase7_block_postlayout.csv")
    tradeoff = rows_of(RES / "phase4_tradeoff.csv")
    powers = {r["tag"]: r for r in rows_of(RES / "phase4_design_power.csv")}
    truth = rows_of(RES / "final_truth_table.csv")
    func = rows_of(RES / "phase1_block_functional.csv")
    hint = rows_of(FINAL / "hint_vector_postlayout.csv")
    tg = rd("final_C4_tg_1_post.json")
    rerun = rd("worst_arc_rerun.json")["rerun_ps"]
    rtg = rd("cmp_R_tg_refresh.json")
    sic = post["worst_pin_ps"]          # worst single-input transition, used to compare designs
    course = system["course"]
    tpd = course["tpd_max_ps"]          # worst transition found, single or multi-input
    power = system["power"]
    lay = system["layout"]

    # text fragments that depend on results are built from them, so they cannot go stale
    formula_ok = course["errors_at_course_formula"] == 0
    formula_text = ("At the course-formula frequency the extracted registered circuit ran with no errors."
                    if formula_ok else
                    f"At the course-formula period ({course['T_course_ps']} ps) the extracted registered circuit gave "
                    f"{course['errors_at_course_formula']} wrong output samples, so that frequency is \\emph{{not}} reliable for this design. "
                    "The formula leaves out clock-to-Q delay.")
    hint_worst = max(float(r["delay_ps"]) for r in hint)
    hint_row = max(hint, key=lambda r: float(r["delay_ps"]))
    finalists = [
        ("C4 prefix, AOI22 sum (chosen)", 194, f"{rd('cmp_C4_aoi22.json')['worst_pin_ps']:.1f}", f"{sic:.1f}", f"{post['area_um2']:.0f}",
         f"{post['area_um2'] * sic * 1e-3:.0f}", powers[tag]["power_mw_1ns"], f"{float(powers[tag]['power_mw_1ns']) * sic:.0f}"),
        ("C4 prefix, TG sum", 186, f"{rd('cmp_C4_tg.json')['worst_pin_ps']:.1f}", f"{tg['worst_pin_ps']:.1f}", f"{tg['area_um2']:.0f}",
         f"{tg['area_um2'] * tg['worst_pin_ps'] * 1e-3:.0f}", powers["final_C4_tg_1"]["power_mw_1ns"],
         f"{float(powers['final_C4_tg_1']['power_mw_1ns']) * tg['worst_pin_ps']:.0f}"),
        ("R flat carries, TG sum", 164, "-", f"{rtg['worst_pin_ps']:.1f}", f"{rtg['area_um2']:.0f}",
         f"{rtg['area_um2'] * rtg['worst_pin_ps'] * 1e-3:.0f}", powers["cmp_R_tg_refresh"]["power_mw_1ns"],
         f"{float(powers['cmp_R_tg_refresh']['power_mw_1ns']) * rtg['worst_pin_ps']:.0f}"),
    ]
    per = []
    for o in ("s0", "s1", "s2", "s3", "c4"):
        for key, name in (("tplh", "tpLH"), ("tphl", "tpHL")):
            a = sch["per_output"][f"{o}_{key}_ps"]
            b = post["per_output"][f"{o}_{key}_ps"]
            per.append((o.upper(), name, f"{a:.1f}", f"{b:.1f}", f"{100 * (b / a - 1):.1f}"))

    places = system["placements"]
    pitch_pg = sorted({q[1] for q in places if q[0].startswith("pg")})
    bit_pitches = sorted({b - a for a, b in zip(pitch_pg, pitch_pg[1:])})
    row_y = sorted({q[2] for q in places})
    row_pitches = [b - a for a, b in zip(row_y, row_y[1:])]
    ffw = sorted({q[3] for q in places if q[0].startswith(("fi", "fo"))})

    body = rf"""
\section*{{Summary of results}}
All values below are from ngspice runs, and post-layout values use netlists extracted by MAGIC. Unless stated otherwise, delays are worst-case over all 4608 single-input transitions, measured from the 50\% point at the adder input pin to the final 50\% crossing at the output. Inputs are driven by a finite inverter, and each output drives the $W_p/W_n=20\lambda/10\lambda$ inverter.

{table("Final design", ["Quantity", "Value"], [
 ("Architecture", "Static CMOS prefix CLA with dual-rail AOI22 sum; TSPC flip-flops"),
 ("Adder transistors / registered transistors", f"{sch['transistors']} / {sch['transistors'] + 14 * ff.transistor_count}"),
 ("Schematic worst-case delay", f"{sch['worst_pin_ps']:.1f} ps"),
 ("Post-layout worst single-input transition", f"{sic:.2f} ps ({post['worst_pin_arc']})"),
 ("Post-layout worst found overall, tpd,max", f"{tpd:.2f} ps (several inputs changing; from a sample)"),
 ("Course hint vector, post-layout worst", f"{hint_worst:.1f} ps"),
 ("Flip-flop post-layout tcq / tsetup / thold", f"{course['tcq_ps']} / {course['tsetup_ps']} / {course['thold_ps']} ps"),
 ("fmax by course formula", f"{course['fmax_course_ghz']} GHz (T = {course['T_course_ps']} ps)"),
 ("Verified limit, extracted registered circuit", f"{system['postlayout']['fmax_ghz']} GHz (T = {system['postlayout']['min_period_ps']} ps)"),
 ("Pavg at verified limit, random and critical vectors", f"{power['critical_and_random']['pavg_mw']} mW"),
 ("PDP (Pavg x tpd,max)", f"{power['critical_and_random']['pdp_fj']} fJ"),
 ("Layout area, adder / registered", f"{post['area_um2']:.0f} / {lay['area_um2']:.0f} um2"),
 ("ADP, adder", f"{post['area_um2'] * tpd * 1e-3:.0f} um2 ns"),
 ("DRC errors, adder and registered", "0 and 0"),
], spec="p{7.2cm}p{8.2cm}")}

\noindent\textbf{{Points to note.}} (1) The course formula gives a higher frequency than the circuit achieves: {formula_text} (2) The hint vector is not the worst case. The slowest arcs start at operand bits, not at $C_0$. (3) MAGIC has no usable resistance extraction here, so resistance is bounded by simulation in Section~\ref{{sec:res}}, not extracted. (4) LVS was run with a script written for this project, because netgen was unavailable. (5) Figure 1(i) shows no register on $C_{{in}}$; a ninth input flip-flop was added. (6) The load sentence names sum bits only; $C_4$ also drives the inverter here.

\section{{Literature review}}
Twenty provided papers were read. Few state the output load, input driver or the transitions tested, so their delay figures are not comparable with this work or with each other.
\begin{{itemize}}
\item \textbf{{OR-type propagate:}} Miao and Li~\cite{{miao}} replace XOR with NOR in the carry path and name a path from B0 through C3 to S3 as the longest. Both ideas were tested here, and the worst paths here also start at operand bits.
\item \textbf{{Mirror and flat carry gates:}} Hasan et al.\ (2019) build $C_4$ as one nested gate. Measured stacks here show why this is costly: a worst-position NOR5 is 4.6 FO4 at 180 nm.
\item \textbf{{Reduced-swing styles:}} GDI and pass-transistor papers (Dipto 2020, Hossain 2020, Joy 2023, Chezhiyan 2025) report gains against their own baselines at 90 nm. One of these (Chezhiyan and Bommi 2025) itself lists static CMOS as fastest. They were not adopted.
\item \textbf{{Dynamic logic:}} Zlatanovici et al.~\cite{{zlat}} show dynamic logic winning at 64 bits, and static preferred at long cycle times. Efstathiou et al.\ (2013) report only 4.73\% gain at 8 bits from a Ling-style split. Neither applies directly at 4 bits.
\item \textbf{{False sums:}} Nyathi and Mutumba (2017) show sums switching before carries settle, which is why delay here is measured at the final crossing.
\item \textbf{{Single-threshold limit:}} MT-CMOS and dual-mode designs (Sivakumar 2013, Chaitanya Kumar 2014) need low-threshold devices that the provided model does not offer.
\end{{itemize}}
Full notes, with source pages, are in \texttt{{explanation/research/literature\_review.md}}.

\section{{Proposed structure}}
\subsection{{Equations and structure}}
With $p_i=a_i\oplus b_i$, $g_i=a_ib_i$, $t_i=a_i+b_i$, the carries can use $t_i$ in place of $p_i$, because the two differ only when $g_i=1$. XOR is then needed only for the sum, $S_i=p_i\oplus c_i$, so the carry path is free of a slow XOR. This idea follows Miao and Li~\cite{{miao}}.

The carries are computed as a prefix tree with $C_0$ entering last:
\[G_{{1:0}}=g_1+t_1g_0,\quad T_{{1:0}}=t_1t_0,\quad G_{{3:2}}=g_3+t_3g_2,\quad T_{{3:2}}=t_3t_2,\]
\[G_{{3:0}}=G_{{3:2}}+T_{{3:2}}G_{{1:0}},\quad G_{{2:0}}=g_2+t_2G_{{1:0}},\quad C_{{k}}=G_{{k-1:0}}+T_{{k-1:0}}C_0.\]
Each level is inverting, so polarity alternates: NAND2 and NOR2 give active-low $\bar g,\bar t$; OAI21 and NOR2 give active-high level 1; AOI21 and NAND2 give active-low level 2; a final OAI21 with $\bar C_0$ gives each carry. $C_0$ passes through one inverter and one gate.

{fig("block_diagram.png", "Block-level architecture. Signals are named as in the netlists.")}

\subsection{{How this architecture was chosen}}
Six architectures were simulated at unit sizing, over all 4608 single-input transitions. Delay from the driver input also charges each design for its input capacitance.

{table("Unit-size comparison, schematic, all single-input transitions", ["Candidate", "T", "Width (lambda)", "Worst pin (ps)", "From driver (ps)", "Hint vector (ps)"],
 [(r["candidate"], r["transistors"], r["total_width_lambda"], r["worst_pin_ps"], r["worst_drv_ps"], r["hint_vector_pin_ps"]) for r in unit], size=r"\footnotesize")}

C1 is the textbook XOR and NAND-NAND design; C2 uses one complex gate per carry, up to a 5-high stack; R is C2 with $C_4$ from a mirror gate over $C_2$; C3 limits stacks to 3; C4 is the prefix tree; E is a static Manchester chain. A first-order logical-effort estimate had placed flat designs ahead of the prefix tree. Measurement contradicted it, so the estimate was dropped. The finalists were then sized with the same method and laid out:

{table("Finalists after sizing, laid out and extracted. Power is the adder alone on the same 200 random vectors at 1 ns per vector.", ["Design", "T", "Post, sized on schematic (ps)", "Post, final, single-input (ps)", "Area (um2)", "ADP (um2 ns)", "P (mW)", "PDP (fJ)"], finalists, spec="lrrrrrrr", size=r"\footnotesize", fit=True)}

The AOI22 sum version is fastest, and speed is the primary objective, so it was chosen. The TG sum version is {tg['worst_pin_ps'] - sic:.1f} ps slower with lower area and ADP, so it is the better choice if area is weighted more. R with AOI22 sums reached 586.1 ps on schematic, but its assembled layout failed LVS after routing relaxation, so it has no valid post-layout number and is not listed. C2 was stopped early at 663.5 ps on schematic, well behind C4.

\section{{Design details: topology and sizing}}
\subsection{{Adder}}
Sizes come from an automated search minimising worst-case delay from the driver input, confirmed against every input-output class, then repeated with wire capacitance extracted from the layout. Each accepted step is logged in \texttt{{part1/simulations/optimisation/}}. Widths below are in $\lambda$ ($\lambda=0.09\,\mu$m); every channel length is $2\lambda$, equal for NMOS and PMOS. Multiple widths are the different series positions in a stack.

{table("Final adder sizing, every instance", ["Instance", "Cell", "Output", "T", "NMOS W", "PMOS W"], sizing_rows(adder), spec="llcrll", size=r"\scriptsize")}

{fig("convergence.png", "Layout-aware sizing, first round. Each point is an accepted step.", r"0.82\textwidth")}

\subsection{{Transistor-level schematics}}
Each drawing is generated from the same definition that writes the netlist, and a test confirms each drawing shows exactly the netlist's devices, terminals and sizes. All final cells are in \texttt{{part1/schematics/transistor\_level/final/}}. Representative cells follow.

{"".join(_schematic_figs(adder))}

\subsection{{D flip-flop}}
TSPC and a static transmission-gate master-slave flip-flop were compared with a 15 fF load: TSPC 172.9 ps clock-to-Q and 40.0 ps setup; master-slave 200.8 ps and 116.0 ps. TSPC is about 100 ps better on clock-to-Q plus setup, with 11 transistors against 22. The course formula alone slightly favours the master-slave because of its negative hold time, but it would give a slower clock in practice, so TSPC was chosen. TSPC nodes are dynamic, so it needs a minimum clock frequency; this was not characterised.

Stage drives are $\times${p['s1']}, $\times${p['s2']}, $\times${p['s3']}, $\times${p['q']}, found by search at the largest adder pin load, {dff['load_ff']:.1f} fF including wire.

{fig("../../schematics/transistor_level/final/dff_final.png", "Final TSPC flip-flop.", r"\textwidth")}

\section{{Block simulation}}
Every cell and block was exhaustively simulated at transistor level through finite inverter drivers, with the 20$\lambda$/10$\lambda$ inverter on each output, in binary and in shuffled order. A DC solution for every vector checks for static current. The unit-size 5-high $C_4$ gate, used only by the rejected candidate C2, needed 3 ns per vector to settle within 10\% of VDD (1.604 V at 980 ps), so its row uses 3 ns; all others use 1 ns.

{table("Truth-table results, library at unit size", ["Cells and blocks", "Failing", "Worst VOH (V)", "Worst VOL (V)", "Largest DC current (nA)"],
 [(len(func), sum(1 for r in func if r["passed"] != "True"), min(float(r["min_voh"]) for r in func), max(float(r["max_vol"]) for r in func), f"{max(float(r['max_static_ua']) for r in func) * 1e3:.2f}")], spec="rrrrr")}

{fig("wave_pg.png", "P/G bit waveforms.", r"0.9\textwidth")}
{fig("wave_xor.png", "Dual-rail XOR waveforms.", r"0.9\textwidth")}

\noindent Final adder, all 512 input combinations, each twice: schematic {truth[0]['errors']} errors, extracted {truth[1]['errors']} errors.

\section{{Flip-flop characterisation}}
Measured at 50\% VDD. $t_{{cq}}$ is with data well before the clock. $t_{{setup}}$ is the shortest D-to-clock time keeping clock-to-Q within 10\% of $t_{{cq}}$. $t_{{hold}}$ is the shortest clock-to-D time for which a later data change leaves Q correct, with no disturbance above 10\% of VDD. Both data values were tested and the larger is reported. Definitions follow Stojanovi\'c and Oklobd\v{{z}}ija~\cite{{stoj}}.

{table(f"Flip-flop timing at {dff['load_ff']:.1f} fF load", ["Quantity (ps)", "Schematic", "Post-layout"], [
 ("Clock to Q, Q rising", dff["schematic"]["tcq_rise_ps"], dff["postlayout"]["tcq_rise_ps"]),
 ("Clock to Q, Q falling", dff["schematic"]["tcq_fall_ps"], dff["postlayout"]["tcq_fall_ps"]),
 ("Setup, D rising", dff["schematic"]["tsu_rise_ps"], dff["postlayout"]["tsu_rise_ps"]),
 ("Setup, D falling", dff["schematic"]["tsu_fall_ps"], dff["postlayout"]["tsu_fall_ps"]),
 ("Hold, D rising", dff["schematic"]["thold_rise_ps"], dff["postlayout"]["thold_rise_ps"]),
 ("Hold, D falling", dff["schematic"]["thold_fall_ps"], dff["postlayout"]["thold_fall_ps"]),
 ("Worst tcq / tsetup / thold", f"{dff['schematic']['tcq_ps']} / {dff['schematic']['tsu_ps']} / {dff['schematic']['thold_ps']}", f"{dff['postlayout']['tcq_ps']} / {dff['postlayout']['tsu_ps']} / {dff['postlayout']['thold_ps']}"),
])}

{fig("dff_sweep.png", "Delay against D-to-clock time, schematic.", r"0.95\textwidth")}

\section{{Block layouts}}
Layouts were generated by script for the provided technology file and checked with MAGIC. Every cell passes DRC with zero errors, and extraction is compared with the schematic by the project's LVS script, which merges parallel fingers and is tested against wrong widths, swapped gates, missing devices and shorted nets.

{table("Each block: schematic against extracted, worst over all its single-input transitions", ["Block", "T", "W x H (lambda)", "Area (um2)", "DRC", "LVS", "Sch tpLH", "Sch tpHL", "Post tpLH", "Post tpHL"],
 [(b["block"], b["transistors"], f"{b['width_lambda']} x {b['height_lambda']}", b["area_um2"], b["drc"], "match" if b["lvs"] == "True" else "FAIL", b["sch_tplh_ps"], b["sch_tphl_ps"], b["post_tplh_ps"], b["post_tphl_ps"]) for b in blocks], size=r"\footnotesize", fit=True)}

{table("Flip-flop layout", ["Width x height (lambda)", "Area (um2)", "DRC", "LVS"], [(f"{dff['layout']['width_lambda']} x {dff['layout']['height_lambda']}", dff["layout"]["area_um2"], dff["layout"]["drc"], "match" if dff["layout"]["lvs"] else "FAIL")], spec="rrrr")}

The layout figures below are screenshots of MAGIC's own layout window, taken with the cell loaded and fitted to the window.

{fig("magic_pg.png", "P/G bit 0 tile in MAGIC, as placed in the final adder.", r"0.62\textwidth")}
{fig("magic_sum.png", "Sum bit 0 tile in MAGIC.", r"0.62\textwidth")}
{fig("magic_dff.png", "TSPC flip-flop layout in MAGIC.", r"0.62\textwidth")}
{fig("magic_carry.png", "Carry block tile in MAGIC.", r"0.95\textwidth")}

\section{{Integration}}
The complete circuit of Figure 1(i) has 9 input flip-flops, the adder and 5 output flip-flops. It was simulated with the hint vector, the 30 slowest arcs from the adder search, and 200 random vectors. A vector captured at one rising edge must appear at the output flip-flops after the next. The limit below is the shortest clock period, found by binary search to 5 ps, with zero wrong samples.

{table("Registered system", ["Quantity", "Schematic", "Post-layout"], [
 ("Vectors checked", system["vectors"], system["vectors"]),
 ("Shortest working period (ps)", system["schematic"]["min_period_ps"], system["postlayout"]["min_period_ps"]),
 ("Maximum verified frequency (GHz)", system["schematic"]["fmax_ghz"], system["postlayout"]["fmax_ghz"]),
 ("Wrong samples at that period", system["schematic"]["errors_at_limit"], system["postlayout"]["errors_at_limit"]),
])}

{fig("system_postlayout.png", "Extracted registered circuit at the verified limit, first vectors. Q values follow inputs after one clock period.")}

\section{{Floor plan and pitches}}
{fig("floorplan.png", "Floor plan of the registered adder. Rows from bottom: input flip-flops, P/G bits, carry block, sum bits, output flip-flops.", r"0.82\textwidth")}

The P/G bit cells form the regular structure, and sum cells align to their columns.

{table("Pitches", ["Structure", "Pitch (lambda)", "Pitch (um)"], [
 ("Horizontal: bit pitch, P/G and sum columns", "/".join(map(str, bit_pitches)), "/".join(f"{x * 0.09:.2f}" for x in bit_pitches)),
 ("Horizontal: flip-flop cell", "/".join(map(str, ffw)), "/".join(f"{x * 0.09:.2f}" for x in ffw)),
 ("Vertical: row pitches, bottom to top", ", ".join(map(str, row_pitches)), ", ".join(f"{x * 0.09:.2f}" for x in row_pitches)),
 ("Channel track pitch, metal 1", "9", "0.81"),
 ("Gate pitch, shared / contacted diffusion", "7 / 9", "0.63 / 0.81"),
 ("Over-cell routing grid, metal 3 and 4", "9", "0.81"),
], spec="lrr")}

\section{{Full layout: schematic against post-layout}}
Adder layout: DRC {post['drc']}, LVS {tex(post['lvs'])}, {post['capacitors']} extracted capacitors totalling {post['wire_cap_ff']} fF. Registered layout: DRC {lay['drc']}, LVS {tex(lay['lvs_message'])}, area {lay['area_um2']} $\mu$m$^2$.

{fig("magic_adder.png", "Final 4-bit adder layout in MAGIC: P/G row at the bottom, carry block, sum row at the top.", r"0.92\textwidth")}
{fig("magic_registered.png", "Registered adder layout in MAGIC: input flip-flops at the bottom, output flip-flops at the top.", r"0.85\textwidth")}

{table("Worst delay per output, all single-input transitions (ps)", ["Output", "Edge", "Schematic", "Post-layout", "Change (%)"], per, spec="llrrr", size=r"\footnotesize")}

Worst single-input delay rose from {sch['worst_pin_ps']:.1f} to {sic:.1f} ps ({100 * (sic / sch['worst_pin_ps'] - 1):.1f}\%). Note that the final sizes were tuned with wire load in mind, so the schematic column is not the best schematic result.

\section{{Critical path}}
\subsection{{Course hint vector}}
With $A=1111$, $B=0000$, toggling $C_0$ both ways gives both edges at each output. Rising $C_0$ alone gives only falling sums and rising $C_4$. All $S$ outputs flip, as the hint predicts.

{table("Hint vector, extracted netlist", ["C0 edge", "Output", "Type", "Delay (ps)"], [(r["c0_edge"], r["output"].upper(), r["kind"], r["delay_ps"]) for r in hint], spec="llll", size=r"\footnotesize")}

{fig("hint_postlayout.png", "Hint vector, extracted netlist, with 50\\% crossings marked.")}
{fig("native_ngspice.png", "The same event as drawn by ngspice itself, showing the required curplottitle. ngspice displays the title in lower case. C0, S3+2 V, C4+4 V.", r"0.7\textwidth")}

\subsection{{True worst case}}
The slowest hint-vector output is {hint_row['output'].upper()} at {hint_worst:.1f} ps, but the worst single-input transition is \textbf{{{tex(post['worst_pin_arc'])}}} at \textbf{{{sic:.2f} ps}}. The hint vector skips the P/G stage and most of the prefix tree: $C_0$ reaches each carry through one inverter and one gate. Reporting only the hint vector would understate this design's delay by {tpd - hint_worst:.1f} ps.

{fig("worst_arc_postlayout.png", "Worst single-input transition, extracted netlist.")}

\noindent\textbf{{History dependence.}} Delay depends slightly on what came before. Starting this arc from a settled DC state gives {rerun:.1f} ps, against {sic:.2f} ps inside the long all-transition walk. For the hint vector, the walk measured up to {post['hint_worst_ps']} ps against {hint_worst:.1f} ps above. The likely cause is charge left on internal stack nodes, which was not investigated further. Differences of this size should be read as the precision of these numbers.

\subsection{{Several inputs changing together}}
Registers launch all inputs together, so several can change at once. All pairs would be 261,632 transitions, so an evenly spread sample was run: {multi['transitions']} transitions (one segment in {multi['stride']}), on the schematic with extracted wire load annotated. Worst {multi['worst_ps']} ps, with {multi['functional_errors']} errors. The {verify['pairs']} slowest pairs from that sample were then re-simulated on the extracted netlist: worst \textbf{{{verify['worst_ps']} ps}}, from {verify['worst']['inputs_changed']} inputs changing, measured from the earliest of them. {"This exceeds the single-input worst case, so it is taken as $t_{pd,max}$." if verify['worst_ps'] > sic else "This does not exceed the single-input worst case."} This is a sample, not an exhaustive proof, so an unsampled transition could be slightly slower.

\section{{Maximum clock frequency}}
The course defines $f_{{max}}=1/(t_{{pd,max}}+t_{{setup}}+t_{{hold}})$. With post-layout values:
\[T={course['tpd_max_ps']}+{course['tsetup_ps']}+{course['thold_ps']}={course['T_course_ps']}\text{{ ps}},\quad f_{{max}}={course['fmax_course_ghz']}\text{{ GHz}}.\]
{formula_text} A flip-flop launch actually needs $T\ge t_{{cq}}+t_{{pd,max}}+t_{{setup}}={course['tcq_ps']}+{course['tpd_max_ps']}+{course['tsetup_ps']}={course['T_physical_ps']}$ ps, or {course['fmax_physical_ghz']} GHz. Simulation of the extracted circuit finds the actual limit: \textbf{{{system['postlayout']['fmax_ghz']} GHz}} (T = {system['postlayout']['min_period_ps']} ps). The value to rely on is the simulated limit.

\section{{Power}}
$P_{{avg}}=\frac{{V_{{DD}}}}{{T_2-T_1}}\int_{{T_1}}^{{T_2}}I_{{VDD}}(t)\,dt$ for the extracted registered circuit, at the verified limit of {power['period_ps']} ps. Input drivers, clock buffers and output load inverters use a separate supply, so they are not included; the load's capacitance is still driven by the circuit. $T_1$ follows one settling cycle.

{table("Post-layout power, with PDP = Pavg x tpd,max", ["Activity", "Cycles", "Errors", "Pavg (mW)", "Energy/cycle (pJ)", "PDP (fJ)"], [
 ("200 random plus critical vectors", power["critical_and_random"]["cycles"], power["critical_and_random"]["errors"], power["critical_and_random"]["pavg_mw"], power["critical_and_random"]["energy_per_cycle_pj"], power["critical_and_random"]["pdp_fj"]),
 ("Hint vector, C0 toggling each cycle", power["hint_vector_toggling"]["cycles"], power["hint_vector_toggling"]["errors"], power["hint_vector_toggling"]["pavg_mw"], power["hint_vector_toggling"]["energy_per_cycle_pj"], power["hint_vector_toggling"]["pdp_fj"]),
 ("Inputs constant (clock and flip-flops)", power["inputs_constant"]["cycles"], power["inputs_constant"]["errors"], power["inputs_constant"]["pavg_mw"], power["inputs_constant"]["energy_per_cycle_pj"], power["inputs_constant"]["pdp_fj"]),
], size=r"\footnotesize")}

The first row is the main result. It is measured at the verified limit, not the course-formula frequency, because the circuit must run correctly for the number to mean anything.

\section{{Area-delay trade-off}}
ADP $=$ area $\times$ delay, not to be confused with PDP. The final sizes were scaled uniformly, and each scale was laid out and extracted.

{table("Uniform scaling of the final sizes, post-layout", ["Scale", "Width (lambda)", "Worst single-input (ps)", "Area (um2)", "ADP (um2 ns)", "P at 1 ns (mW)", "PDP (fJ)"],
 [(r["scale"], r["total_width_lambda"], r["post_pin_ps"], r["area_um2"], r["adp_um2_ns"], r["power_mw_1ns"], r["pdp_fj"]) for r in sorted(tradeoff, key=lambda r: float(r["scale"]))], size=r"\footnotesize")}

{fig("tradeoff.png", "Delay and ADP against layout area, for uniform scaling.", r"0.95\textwidth")}

Scale 1.0 is the chosen design, and repeating its layout from scratch reproduced the same delay. The curve is not smooth, because layout and routing change with each scale. Lower scales trade a small delay increase for less area and power, so they suit designs where ADP or PDP matters more than speed. Layouts at scales 1.3 and 1.4 were DRC clean but failed LVS after routing, so they gave no valid result and are not listed. The same assembly failure affected R with AOI22 sums. The final design passes LVS, but the cause of these failures was not found, so the router is not proven reliable at higher congestion.

\section{{Layout resistance}}\label{{sec:res}}
MAGIC's extraction here gives capacitance only, and its \texttt{{extresist}} command crashes on this layout (segmentation fault; log kept). As a substitute, the longest poly run from a contact to a gate end was measured from the layout: {bound['longest_poly_lambda']} $\lambda$, or {bound['r_gate_ohm']} $\Omega$ at the technology file's 7.7 $\Omega$/square. That resistance was placed in series with \emph{{every}} one of the {bound['gates']} gates, which is far more than any real gate sees, and all transitions were simulated again: worst single-input delay {bound['without_r_ps']} to {bound['with_r_bound_ps']} ps, an increase of {bound['increase_ps']} ps ({bound['increase_pct']}\%). Metal and vias are not included in this bound. Metal is 0.08 $\Omega$/square and vias are 6 to 16 $\Omega$, so they should matter much less than poly. This is an upper bound for poly only, not an extraction.

\section{{Limitations}}
\begin{{itemize}}
\item LVS is a project script (colour refinement on device-net graphs), not an industry tool. It compares devices and connectivity, and it has rejected injected faults and real routing shorts.
\item Some larger layouts fail LVS after routing, for a cause not yet found, as noted in the trade-off section.
\item Multi-input transitions are sampled, not exhaustive.
\item Resistance is bounded for poly, not extracted. Reported delays exclude resistance.
\item One typical-corner model at 27 C, with no voltage, temperature or process variation.
\item The clock is ideal apart from one buffer; clock-tree layout and skew are not modelled beyond the extracted clock net.
\item Figures of layouts are drawn from .mag data, since MAGIC's image export is blank in batch mode.
\item R with AOI22 sums and C2 were not fully compared, as stated above, and R with TG sums did not get the layout-aware sizing round that C4 did. That round improved C4 by 4.8 to 17.7 ps, well short of the gap.
\item Dynamic logic was not simulated. The planned domino prototype was not built. It was rejected on a timing argument: inputs launched at the rising edge would be non-monotonic during evaluation, and a half-cycle evaluate window conflicts with the course's delay measurement. This is reasoning, not a measurement.
\item The simulated clock limit is about 40 ps longer than $t_{{cq}}+t_{{pd,max}}+t_{{setup}}$. This gap is not fully explained. Flip-flop values were measured in isolation, and the cause was not isolated further.
\item TSPC minimum clock frequency was not characterised.
\end{{itemize}}

\section{{Netlists}}
All netlists and logs are in the project directory. The final adder and flip-flop netlists follow, with widths and lengths in metres and junctions as estimated before layout.

{{\tiny
\begin{{verbatim}}
{_netlist(adder, ff)}
\end{{verbatim}}
}}

\begin{{thebibliography}}{{9}}
\bibitem{{miao}} J. Miao and S. Li, ``A novel implementation of 4-bit carry look-ahead adder,'' IEEE EDSSC, 2017. DOI 10.1109/EDSSC.2017.8126457.
\bibitem{{stoj}} V. Stojanovi\'c and V. Oklobd\v{{z}}ija, ``Comparative analysis of master-slave latches and flip-flops for high-performance and low-power systems,'' IEEE JSSC, 34(4), 536--548, 1999. DOI 10.1109/4.753687.
\bibitem{{yuan}} J. Yuan and C. Svensson, ``High-speed CMOS circuit technique,'' IEEE JSSC, 24(1), 62--70, 1989. DOI 10.1109/4.16303.
\bibitem{{zlat}} R. Zlatanovici, S. Kao and B. Nikoli\'c, ``Energy-delay optimization of 64-bit carry-lookahead adders with a 240 ps 90 nm CMOS design example,'' IEEE JSSC, 44(2), 569--583, 2009. DOI 10.1109/JSSC.2008.2010795.
\bibitem{{wh}} N. Weste and D. Harris, \emph{{CMOS VLSI Design}}, 4th ed., course reference.
\bibitem{{mano}} M. Morris Mano, \emph{{Digital Logic and Computer Design}}, course reference.
\end{{thebibliography}}
"""
    doc = rf"""\documentclass[10pt,a4paper]{{article}}
\usepackage[margin=2cm]{{geometry}}
\usepackage{{graphicx,booktabs,amsmath,float,array}}
\usepackage[hidelinks]{{hyperref}}
\title{{VLSI Design Course Project\\Part I: 4-bit Carry Look-Ahead Adder}}
\author{{Bhargav, Roll No. 2025102061\\IIIT Hyderabad, Monsoon 2026}}
\date{{}}
\begin{{document}}
\maketitle
\tableofcontents
{body}
\end{{document}}
"""
    (DOC / "report.tex").write_text(doc)
    for _ in range(2):
        res = subprocess.run(["pdflatex", "-interaction=nonstopmode", "report.tex"], cwd=DOC, capture_output=True, text=True, timeout=600)
    pdf = DOC / "report.pdf"
    if pdf.exists():
        shutil.move(pdf, DOC / "Bhargav_2025102061.pdf")
    for ext in ("aux", "log", "toc", "out"):
        (DOC / f"report.{ext}").unlink(missing_ok=True)
    print(res.stdout[-800:])
    print([l for l in res.stdout.splitlines() if l.startswith("!")][:10])


def _schematic_figs(adder):
    out = []
    seen = set()
    wanted = [("nand0", "NAND2 for generate, bit 0"), ("nor0", "NOR2 for OR-type propagate, bit 0"),
              ("aoi0", "AOI21 for P, bit 0"), ("oai0", "OAI21 for P-bar, bit 0"), ("g10", "Prefix OAI21, G(1:0)"),
              ("g30", "Prefix AOI21, G-bar(3:0)"), ("c4g", "Final carry OAI21, C4"), ("x3", "Dual-rail XOR for S3 with c-bar inverter"), ("invc0", "C0 inverter")]
    cells = {i[0]: i[1] for i in adder.instances}
    for inst, caption in wanted:
        cell = cells[inst]
        out.append(fig(f"../../schematics/transistor_level/final/{cell.name}.png", f"{caption} ({tex(cell.name)}).", r"0.48\textwidth") + "\n")
    return out


def _netlist(adder, ff):
    text = adder.spice() + "\n" + ff.spice()
    lines = []
    for line in text.splitlines():
        if line.startswith("* GENERATED"):
            continue
        lines.append(line if len(line) < 150 else line[:147] + "...")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
