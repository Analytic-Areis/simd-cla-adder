# Design decisions

Status values: **Proposed** (awaiting SPICE evidence), **Adopted** (evidence recorded), **Rejected**.

## D1. Logic family: static CMOS. Status: Adopted
- **Alternatives:** domino, compound domino, dual-mode logic, PTL, GDI, ratioed, adiabatic.
- **Why not domino as lead:** with inputs launched at the rising edge, dynamic gates would see non-monotonic inputs during evaluation if they evaluate in the high phase. Evaluating in the low phase gives static P/G the first half cycle and carries and sums only the second, so T is at least 2 x max(tcq + tPG, teval + tsum + tsu). The hint's measurement, C0 toggling with others stable, and the formula fmax = 1/(tpd,max + tsetup + thold) both assume combinational timing and do not map onto clocked carries. Keepers, charge sharing and clock power add cost.
- **Evidence:** the planned domino prototype was **not simulated**. This rejection rests on the timing argument above and on the course delay definition, not on a measurement. Zlatanovici et al. show dynamic logic winning at 64 bits, not 4.
- **Others:** DML and MT-CMOS need low-Vt devices; PTL/GDI have reduced swing or weak drive; ratioed gates draw static current; adiabatic targets power.

## D2. Carry architecture. Status: Adopted C4 prefix; candidate R rejected on measurement
**Outcome (2026-10-31):** C4 prefix won: 579.88 ps single-input and 2936.9 um2 post-layout, against R with TG sum at 645.59 ps and 3425.8 um2. The text below records the original proposal, which measurement overturned.

- **R:** C1, C2, C3 as single complex gates over g-bar, t-bar and c0-bar (stacks 2, 3, 4). C4 from a mirror gate over raw A3, B3, A2, B2 and C2 (stack 3), plus inverter.
- **Reason:** tied lowest estimated worst path (450 ps, 308 ps with textbook values). Avoids a 5-high PMOS stack, which measured 4.6 FO4 in its worst input position. Isolates the Cout load from the carry gate.
- **Caveat:** C2 has a faster estimated A0-to-C4 path (334 versus 375 ps), though this is not its worst path. SPICE decides between them.
- **Rejected on estimate alone:** none. C1 (baseline), C3 and C4 are all simulated. C1 gives the improvement reference.

## D3. Use OR-type propagate in carries; XOR only for sum. Status: Proposed
- **Why:** NOR2 is one stage and far lighter than XOR. Valid because OR and XOR differ only when G = 1 [33, p.2].
- **Alternative:** XOR propagate everywhere, which adds fan-out to a slow gate.

## D4. Input ordering: latest signal nearest the output. Status: Proposed
- **Why:** measured up to 33 % (NAND5) and 39 % (NOR5) difference by input position.
- **Note:** the critical signal differs by path, so ordering must be checked against the true worst arc.

## D5. Sum stage. Status: Adopted AOI22 dual-rail
AOI22 gave 579.88 ps against TG at 596.66 ps; TG has lower area and ADP.

Variants: AOI22 dual-rail XOR (10T with C-bar inverter), TG mux with output inverter, 12T static, 4-NAND baseline. P and P-bar from compound gates reusing NAND and NOR outputs.

## D6. Worst case found by search, not assumed. Status: Adopted as method
All 4608 single-input-change arcs for each candidate; a 25 % sample of 261,632 multi-input transitions on the final design, not the exhaustive sweep planned, because of run time. The A = 1111, B = 0000 C0 vector is always reported as the course requires. It needs both C0 edges: rising alone gives only S falling and C4 rising.

## D7. Realistic inputs. Status: Adopted as method
All inputs driven through finite inverter drivers, delay measured at the DUT pin. An ideal source would make upsizing look free.

## D8. Delay measured at the final 50 % crossing. Status: Adopted as method
False sums [15] can cross 50 % early.

## D9. Register Cin with a ninth input flip-flop. Status: Adopted, still to confirm on Moodle
Figure 1(i) shows registers for a and b only. A registered Cin keeps all launches on one clock and allows the C0 hint vector in the full system. Should be confirmed on Moodle.

## D10. Output load. Status: Adopted, still to confirm on Moodle
Standalone: inverter load on each S and on C4. C4 is not named in the course's load sentence; loading it is the conservative choice. Registered: inverter on each output flip-flop Q, CLA output drives D. Both results reported.

## D11. Timing. Status: Adopted as method
Report the course formula fmax = 1/(tpd,max + tsetup + thold), as required. It omits Clk-Q, so also report T >= tcq + tpd + tsu and the frequency at which the full registered circuit actually fails in simulation. Setup is defined at 10 % Clk-Q push-out and also at minimum D-Q delay [Stojanovic and Oklobdzija].

## D12. Flip-flop. Status: Adopted TSPC
Tcq + tsu 212.9 ps against 316.8 ps at 15 fF, with half the transistors.

Chosen by Clk-Q + setup at the actual load, with hold margin checked.

## D13. One source for netlist, schematic and layout. Status: Adopted
No schematic tool is installed, and the user requires drawings to match simulation. Cell descriptions in Python generate SPICE, drawings and MAGIC layouts, tested device by device.

## D14. LVS. Status: Adopted project script
netgen is missing and no Homebrew formula was found. A netgen source build was not attempted. `part1/cells/cellgen/lvs.py` compares devices and connectivity on the flat extracted netlist, is tested against injected faults, and is labelled as our own script.
