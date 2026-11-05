# Literature review

Numbers are as reported by each paper, under its own conditions. They are not comparable across papers. See `paper_comparison.md`.

## Overall assessment

- Very few of the provided papers state output load, input driver or slope, or the set of input transitions tested. Without those, a delay figure cannot be transferred to our design.
- Most report improvement in comparison with their own baseline, usually at 90 nm.
- Only papers 22, 24, 26 and 32 use 180 nm, and only 32 targets speed at 1.8 V with a stated worst-case number.
- Most useful for our design: 33, 05, 32 (as a benchmark), 15, 23 (method), 02 (reporting format), 12 (concepts).

## Directly useful

**[33] Miao and Li, 2017. 4-bit CLA, 0.25 um, 2.5 V.**
Replaces XOR with NOR in the carry path, using NAND/NOR terms with alternating polarity carries. Reduces fan-in and fan-out and removes a series device from the critical path.
States the longest path runs from B0 through C3 to S3 [p.2]. Delay 1.008 to 0.732 ns; area and energy also lower [p.2]. Minimum sizing, no output load [p.2]. The text calls the gates dynamic, though Fig. 2 draws complementary networks.
*Use:* OR-type propagate in carries; alternating polarity; the A/B path as critical path hypothesis.
*Limit:* unloaded, older node; an improvement measured without load may shrink under ours.

**[05] Hasan et al., 2019. C4 only, 90 nm.**
Builds C4 as one nested mirror gate from raw inputs using C(i+1) = Ci(Ai+Bi) + AiBi, with an output inverter [p.2]. 36 versus 92 transistors, 134 versus 166 ps [p.2].
*Use:* mirror nesting, no separate P/G stage. Basis of our C4 gate.
*Limit:* gives C4 only; S needs C1 to C3 as well. Stack is 5 high, which our measurements show is expensive in PMOS. The abstract's delay improvement (19.69 %) differs from the table's (19.277 %).

**[32] Ghasemzadeh et al., 2014. C4 generator, 0.18 um, 1.8 V.**
Ratioed, binary-weighted branches from raw inputs, with a weak PMOS for the all-propagate case [p.2]. Worst-case figure shows 256 ps [p.3 Fig. 6]; the abstract says 500 ps [p.1]. Same node and supply as ours, so useful as a benchmark.
*Limit:* ratioed node means static current whenever pull-up and pull-down fight, reduced noise margin, and sensitivity to device ratios. Widths reach 16 times unit, loading high-order inputs. Gives C4 only. Rejected as architecture.

**[15] Nyathi and Mutumba, 2017. False sums, 90 nm post-layout.**
P arrives before C, so S can switch to a wrong value and then correct [p.2-3]. Latches hide this but the energy is still spent. Slowing the non-critical path with a reduced rail saves 40 % power for 18 extra transistors on 997 [p.4].
*Use:* measure delay at the final 50 % crossing, not the first. Include glitch energy in power results.
*Limit:* the fix deliberately delays paths; it conflicts with our primary objective, and the extra rail is outside our plan. Noted for the power trade-off only.

**[23] Ghobadi et al., 2010. Subthreshold, 65/90 nm.**
Operating regime not relevant. Method is useful: measures all paths (a0, b0, c0 to outputs) and reports the largest [p.3]; drives inputs through buffers [p.3].
*Use:* our testbench method.

**[02] Khalid et al., 2026. RCA versus CLA, 90 nm.**
Full flow with DRC, LVS and RCX, reporting PDP and ADP [p.5]. CLA 79.7 ps, 332 transistors, 797 um2.
*Use:* reporting format.
*Limit:* worst case tests only the Cin path to Cout [p.3-4]. Power is labelled in uJ.

**[12] Efstathiou et al., 2013. Domino Manchester, 90 nm, 1 V.**
Ling-style split into even and odd chains of 8-bit modules. Improvement 4.73 % at 8 bits, rising to 35.08 % at 64 [p.4], with 43.4 % more energy and 49.9 % more area [p.4]. Sum uses a mux selected by the Ling carry [p.3].
*Use:* Ling and sum mux concepts; static XOR topology (Fig. 3).
*Limit:* the gain at 8 bits is small and grows with width, so little is expected at 4 bits.

## Logic-style papers reviewed and not adopted

**[03] Dipto et al., 2020; [14] Hossain and Arifin, 2020; [19] Joy et al., 2023; [13] Chezhiyan et al., 2025. GDI, PTL and hybrid input gates, 90 nm.**
Replace input XOR/AND with reduced-transistor gates and keep static carries and sums. Reported delay reductions of about 12 to 17 % for 03, 14, 19, and 38 % for 13. They attribute improvement to reduced "input impedance", which appears to mean input capacitance. Loads and drivers are not stated. Paper 13 also contradicts itself on which style is in the critical path [p.1 versus p.3-4], and its 80 and 56 transistor counts look low for a full 4-bit CLA.
*Assessment:* weak drive and reduced swing need restoring stages, and these changes do not touch the C0 path. Standard GDI cells also need body connections not available in ordinary twin-well layout. Low input capacitance is a valid aim; our NAND/NOR front end pursues it with full swing.

**[27] Chezhiyan and Bommi, 2025. PTL versus TG.**
PTL 56T, 2.35 ns; TG 136T, 1.20 ns; static CMOS from another reference 512T, 1.13 ns [p.4]. Threshold drop and signal spikes reported for PTL. Node not stated in the extracted text.
*Use:* evidence against PTL for speed. TG stays a candidate for the sum mux.

**[04] Divya et al., 2023.** Transmission-gate gates at 45 nm. Equations are incorrect, such as S1 using G1 in place of a carry [p.2]. No reusable data.

**[01] Sarker et al., 2024.** Compares five adders at 90 nm. Reports 3.998 ns for CLA but 25.565 ps for carry-skip [p.5]. That ratio is not physically credible in one node, so these results are not used.

**[22] Mangla and Kumar, 2016.** Adiabatic and stacking at 180 nm. Average delays around 24 ns [p.5], far beyond what FO4 of 85 ps would predict. Power-oriented. Not useful for speed.

**[16] Chaitanya Kumar and Selva Kumar, 2014.** Dual-mode logic at 45 nm. Adds clocked devices and decision logic; trades power and area for speed. Uses low-Vth devices [p.2], which our model does not provide.

**[24] Sivakumar et al., 2013.** MT-CMOS domino Manchester at 0.18 um. Claims 40 % power and 55 % delay gains over standard domino, without absolute figures. Needs multiple thresholds; we have one model per device type. States that reducing width increases parasitics, which is questionable.

**[54] Lou and Kuo, 1997.** Bootstrapped pass-transistor CLA at 1.5 V, 70 % faster than Manchester at 4 bits [p.1]. Gate overdrive above VDD stresses oxide and adds complexity. Benefit is aimed at low supply. Not adopted.

**[26] Gupta et al., 2014.** Subthreshold CLA in 180 nm at 0.4 V, 5 MHz, area 60 x 92.5 um2 [p.1]. Useful only for its bottom-up layout order.

**Dhanjal, 2022.** One-page survey of CMOS mirror-logic CLA. Confirms mirror symmetry as a layout benefit. No data.

## External references

| Source | How read | Used for |
|---|---|---|
| R. Zlatanovici, S. Kao, B. Nikolic, "Energy-Delay Optimization of 64-Bit Carry-Lookahead Adders With a 240 ps 90 nm CMOS Design Example," IEEE JSSC 44(2), 569-583, 2009. DOI 10.1109/JSSC.2008.2010795 | Sections on logic families and tree choices | For their 64-bit case: dynamic needed below 12.5 FO4; static preferred at long cycle times; Ling helps by reducing first-stage stack. Applies to 64 bits, not automatically to 4. |
| V. Stojanovic, V. Oklobdzija, "Comparative analysis of master-slave latches and flip-flops...," IEEE JSSC 34(4), 536-548, 1999. DOI 10.1109/4.753687 | Definitions and methodology | Setup and hold definitions; D-Q delay minimum as the real measure of flip-flop time cost. |
| R. Zimmermann, W. Fichtner, "Low-power logic styles: CMOS versus pass-transistor logic," IEEE JSSC 32(7), 1079-1090, 1997. DOI 10.1109/4.597298 | Index summaries only | Complementary CMOS superior to CPL in most cases. Full text to be read before citing in the report. |
| J. Yuan, C. Svensson, "High-speed CMOS circuit technique," IEEE JSSC 24(1), 62-70, 1989. DOI 10.1109/4.16303 | Abstract only | Origin of TSPC. |
| D. Harris, "A taxonomy of parallel prefix networks," Asilomar 2003, 2213-2217. DOI 10.1109/ACSC.2003.1292373 | Citation only, fetch failed | Prefix terminology. Full text to be read before citing. |
| K. Goel, A. Kumar, M. Bayoumi, "Design of robust, energy-efficient full adders...," IEEE TVLSI 14(12), 1309-1321, 2006. DOI 10.1109/TVLSI.2006.887807 | Abstract level | Hybrid-CMOS context. |
| H. Ling, "High-Speed Binary Adder," IBM J. Res. Dev. 25(3), 156-166, 1981. DOI 10.1147/rd.252.0156 | Citation only | Ling equations. |
| A. Weinberger, J. L. Smith, "A logic for high-speed addition," NBS Circular 591, 3-12, 1958 | Citation only | Origin of CLA. |
| N. Weste, D. Harris, *CMOS VLSI Design*, 4th ed. (course reference); I. Sutherland, B. Sproull, D. Harris, *Logical Effort*, 1999 | Not available locally; standard results used | Logical effort method and textbook g, p. Page references to be checked before the report. |

Unverified: the GDI paper by Morgenshtein et al. (IEEE TVLSI, 2002) did not appear in search. Its DOI must be checked before any citation.
