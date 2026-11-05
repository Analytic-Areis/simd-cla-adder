# Part II: SIMD-reconfigurable 8-bit adder

Report: [`documentation/Bhargav_2025102061_part2.pdf`](documentation/Bhargav_2025102061_part2.pdf), 10 pages, built by `cells/make_report.py` from the result files.

Two copies of the Part I 4-bit carry look-ahead adder with a carry-gating cell between them. All results are from ngspice with the provided TSMC 180 nm model, on layouts drawn and checked in MAGIC.

| `SIMD_MODE` | Behaviour |
|---|---|
| 0 | One 8-bit add. CLA0's carry-out reaches CLA1's carry-in through the gating cell |
| 1 | Two 4-bit adds. The carry into CLA1 is forced to 0 |

The **baseline** for comparison is the same two adders wired directly, CLA0's carry-out to CLA1's carry-in, with no gating cell.

## Results, post-layout

| Measure | Baseline | SIMD, mode 0 | SIMD, mode 1 |
|---|---|---|---|
| Worst-case delay tpd,max | 1030.86 ps | 1109.77 ps | 570.22 ps |
| Worst path | a3 rise to S5 | a3 fall to S5 | a1 rise to S3 |
| Cin rise to S7, A = FF, B = 00 | 816.11 ps | 877.83 ps | S7 does not change |
| Cin fall to S7, same vector | 789.50 ps | 903.93 ps | S7 does not change |
| Course-formula fmax | 0.897 GHz | 0.838 GHz | 1.529 GHz |
| Power, 10 cycles at 1400 ps | 1695.2 µW | 1720.7 µW | 1592.4 µW |
| Power, 200 vectors at 1400 ps | 1876.3 µW | 1919.5 µW | 1713.7 µW |
| EDP, P × tpd,max² | 1.80 × 10⁻²¹ J·s | 2.12 × 10⁻²¹ J·s | 0.52 × 10⁻²¹ J·s |
| Transistors | 388 | 396 | |
| Layout area | 7749.0 µm² | 8858.7 µm² | |
| DRC / LVS | 0 / match, 388 devices | 0 / match, 396 devices | |

**Penalties of the gating cell, in 8-bit mode against the baseline:**

| | Schematic | Post-layout |
|---|---|---|
| Delay penalty, Cin rise to S7 | +58.28 ps, 9.20% | **+61.72 ps, 7.56%** |
| Delay penalty, Cin fall to S7 | +96.30 ps, 16.04% | +114.44 ps, 14.49% |
| tpd,max penalty | +64.87 ps, 7.59% | +78.91 ps, 7.65% |
| Power penalty, 10 cycles | | **+1.50%** |
| Power penalty, 200 vectors | | +2.30% |
| EDP penalty | | +17.6% |

Schematic worst-case delays: baseline 855.22 ps, SIMD mode 0 920.09 ps, SIMD mode 1 516.31 ps. All searches gave 0 functional errors.

## The carry-gating cell

`cin_hi = cout_lo · ¬SIMD_MODE`, in static CMOS: a NAND2 and an inverter on the carry path, and a unit inverter making ¬SIMD_MODE. The mode is a static control, so its inverter is off the timing path. 8 transistors.

- **Sizing:** sizes were swept on the schematic to minimise Cin to S7 in mode 0 (`results/gate_sizing.csv`). The best is NAND2 ×1 with output inverter ×2. A larger NAND loads CLA0's carry-out more and is slower.
- **Alone, with a 20/10 λ inverter load:** cout_lo to cin_hi is 104.27 ps on the schematic and 110.46 ps post-layout.
- **Layout:** 93 × 133 λ, DRC 0, LVS match.
- **Why it costs about 60 ps and not 110 ps:** the gate isolates CLA1's carry-in load from CLA0's carry-out, so CLA0's carry-out switches faster than in the baseline (figure 2.4).

## How the layout is built

1. **The adder cell:** the Part I adder with its final sizes, laid out again by the Part I flow with two extra metal 3 pads above its top row for C4 and C0. The parent connects to these pads, so its vias never land on the cell's own pin vias. The cell is DRC clean and matches LVS; with the pads it is 3083.1 µm² against 2936.9 µm² in Part I.
2. **The gating cell:** laid out by the same flow with the same kind of pads.
3. **The top level:** places the adder cell twice, CLA0 and CLA1, with the gating cell between them in the SIMD design. It is flattened, then the inter-block carries are drawn on metal 5, which no cell uses. Port labels go on the cells' pin stubs, and power straps join through buses below the cells.

The first attempt laid out the whole 8-bit adder flat in rows. Its router ran out of tracks in the carry row, so the two-instance layout above replaced it.

## Method and limits

- **Delay:** every input goes through a shaper and an x2 driver, and every output, including CLA0's carry-out in the SIMD design, drives a 20/10 λ inverter. Delay runs from the adder pin to the last 50% crossing of the output, as in Part I.
- **Worst-case search:** guided, not exhaustive: 13,312 single-input transitions per case.
  - Every transition of CLA0's 9 inputs, with CLA1 set to pass a carry through all 4 bits, A_hi = F, B_hi = 0 and then A_hi = 0, B_hi = F.
  - Every transition of CLA1's 8 inputs, with CLA0's carry-out held at 0 and then at 1.
- **fmax:** the course formula, 1 / (tpd,max + tsetup + thold), with the Part I flip-flop's post-layout tsetup = 38.0 ps and thold = 45.7 ps.
- **Multi-input changes are slower:** at the course-formula clock, random vectors that change several inputs at once did not always settle (`results/power_at_course_fmax.json`). The search changes one input at a time, so tpd,max is a single-input figure. The shortest clock at which all three cases settled on 200 random vectors was 1400 ps (`results/settle.json`), so power is compared there, with identical vectors for all three.
- **Area:** the top-level bounding box, including the gaps between cells, the metal 5 channels and the power buses. Most of the 1109.7 µm² difference is the gating cell plus the extra gap it needs; the cell itself is 181.1 µm² with its pads and straps.

## Files

| Path | Contents |
|---|---|
| `cells/simd.py` | Every stage: netlists, gate sizing, cells, layout, search, penalty, power, figures, summary |
| `schematics/` | Hierarchical netlists `simd8.sp`, `base8.sp`, `carry_gate_*.sp`, and block and transistor drawings |
| `layout/cells/` | Adder cell `cla4_cell` and gating cell `gate_top`, with tiles |
| `layout/simd/`, `layout/base/` | Top layouts: `*8_top.mag` with the cells placed, `*8_flat.mag` the flattened layout that is checked and extracted |
| `extraction/` | Extracted netlists of both 8-bit adders |
| `simulations/` | Decks and logs: gate sizing, search, penalty, power, settle, waves |
| `results/` | `part2_summary.csv`, `penalty.json`, `power.json`, `gate.json`, layout and search results |
| `documentation/` | The report PDF, its LaTeX source, and `figures/`: MAGIC screenshots `magic_*.png`, block and transistor drawings, layout drawings 2.1 to 2.3, waveforms 2.4, delay per output 2.5, gate sizing 2.6 |

## Rerun

From `cells/`:

```bash
python3 simd.py gate
```

```bash
python3 simd.py cells
```

```bash
python3 simd.py layout_h simd base
```

```bash
python3 simd.py search simd 0 post
```

```bash
python3 simd.py penalty
```

```bash
python3 simd.py power 1400
```

```bash
python3 simd.py waves
```

```bash
python3 simd.py summary
```

```bash
python3 make_report.py
```

The MAGIC screenshots come from `part1/cells/magic_shot.py`, which needs XQuartz running. It opens each cell in MAGIC's window and captures that window.

The search takes about 8 minutes per case. `search` takes `base 0`, `simd 0` or `simd 1`, then `sch` or `post`.
