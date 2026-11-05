# Part II explained: the SIMD-reconfigurable 8-bit adder

Full results and file list: [`../part2/README.md`](../part2/README.md).

## The task

GPUs often split one wide adder into several narrow ones, for example one 8-bit add or two 4-bit adds, under a control signal. Part II builds this from two copies of the Part I adder:

| `SIMD_MODE` | What the circuit does |
|---|---|
| 0 | CLA0's carry-out goes into CLA1: one 8-bit add |
| 1 | CLA1's carry-in is forced to 0: two separate 4-bit adds |

The cost of this flexibility is measured against a **baseline**: the same two adders wired directly, with no gating.

## The carry-gating cell

The carry into CLA1 must be CLA0's carry-out when `SIMD_MODE` = 0, and 0 when it is 1:

```text
cin_hi = cout_lo AND (NOT SIMD_MODE)
```

In static CMOS this is a **NAND2 followed by an inverter**, with ¬SIMD_MODE from a small inverter. The mode is set once and does not change during an add, so that inverter is not on the timing path. The cell has 8 transistors.

Sizes were chosen by simulation: a NAND2 of unit size and an output inverter of twice unit size gave the fastest Cin to S7. A larger NAND made CLA0's carry-out slower, because it loads it more.

## How it was built

1. **Netlists:** a hierarchical netlist with two instances of the Part I adder, CLA0 and CLA1, plus the gate. A flat version of the same circuit is used to check the logic.
2. **Logic check:** 3000 random inputs at switch level, 0 errors, for both designs.
3. **Gate sizing and layout:** 25 size pairs simulated, then the cell laid out alone. DRC 0, LVS match.
4. **Adder cell with pads:** the Part I adder laid out again with two extra metal 3 pads above it, for C4 and C0.
5. **Top layout:** the adder cell placed twice, the gate between them, everything flattened, and the inter-block carries drawn on metal 5. DRC 0 and LVS match, for both the SIMD design and the baseline.
6. **Worst-case search:** 13,312 single-input transitions per case, on the schematic and on the extracted layout.
7. **Delay penalty:** A = FF, B = 00, Cin toggling, Cin to S7.
8. **fmax and power:** fmax from the course formula, then power over 10 cycles with identical inputs for all three cases.

## Results, post-layout

| | Baseline | SIMD, mode 0 | SIMD, mode 1 |
|---|---|---|---|
| Worst-case delay | 1030.86 ps | 1109.77 ps | 570.22 ps |
| Cin rise to S7, A = FF, B = 00 | 816.11 ps | 877.83 ps | S7 stays put |
| Power at 1400 ps, 10 cycles | 1695.2 µW | 1720.7 µW | 1592.4 µW |
| EDP, P × tpd² | 1.80 × 10⁻²¹ J·s | 2.12 × 10⁻²¹ J·s | 0.52 × 10⁻²¹ J·s |
| Area | 7749.0 µm² | 8858.7 µm² | |

- **Delay penalty**, Cin rise to S7: +61.72 ps, **7.56%**. On the falling edge: +114.44 ps, 14.49%.
- **Power penalty** in 8-bit mode: **+1.50%** over 10 cycles, +2.30% over 200 vectors.
- **EDP penalty:** +17.6%, because delay counts twice in EDP.

## What the results mean

- **The gate costs about 60 ps, not its full 110 ps.** On its own, the gate takes about 110 ps. In the baseline, CLA0's carry-out drives CLA1's carry-in load directly and is slowed by it; the gate isolates that load, so CLA0's carry-out gets faster. Figure 2.4 in `part2/documentation/figures/` shows this.
- **Dual mode is as fast as Part I:** each half is a 4-bit add, 570 ps against 580 ps in Part I. The SIMD design adds about 1.5% power and about 14% area for this choice.
- **The worst path is not the hint vector:** the worst path starts at a3, crosses the block boundary, and ends at S5.

## Problems met

| Problem | Fix |
|---|---|
| Laying out all 8 bits flat in rows, the router ran out of tracks in the carry row | Two placed copies of the adder cell, joined on metal 5, which no cell uses |
| A via in the top cell over the cell's own pin via cut the metal 2 to metal 3 link: LVS caught it | Extra metal 3 pads above each cell, routed inside the cell, for the top level to land on |
| Two separate vias stacked at one spot are not allowed | One stacked metal 3 to metal 5 via (`m345c`) |
| One pad sat 3 λ from a metal 4 track | Pads moved midway between routing tracks |
| At the course-formula clock, random multi-input vectors did not all settle | Power measured at 1400 ps, the shortest clock at which all three cases settle on 200 random vectors |

## Limits

- **Guided search:** the worst-case search is targeted, not exhaustive. It covers every single-input transition of each block with the other block set to its slowest state.
- **Multi-input delay:** changes of several inputs at once are slower than tpd,max, as the settle test shows; the exact multi-input worst case was not searched.
- **Area:** the bounding box includes the gaps between cells and the routing channels, so it overstates the gate's own area.
