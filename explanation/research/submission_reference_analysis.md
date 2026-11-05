# Previous submission analysis

Used for presentation and methodology only. No design, number or file from these goes into our results.

| Item | `Carry-Lookahead-Adder` (2021) | `4-Bit-CLA-Adder_ref` (2025) | `5-Bit-CLA-Adder_ref` (2026) |
|---|---|---|---|
| Report | `Report.md`, screenshots | 8-page `Report.pdf` | README; only the problem statement is in `Report/` |
| Architecture | NAND/NOR with OR-type propagate, citing paper 33 | XOR, AND, OR gates | AND, OR, XOR gates up to 5 inputs |
| DFF | NAND-based, plus C2MOS and TSPC trials | TSPC, 12T | D flip-flop with separate setup, hold and Clk-Q decks |
| Schematic form | Screenshots and drawn | Hand-drawn | Not in the repository's documents |
| Reported timing | No summary figures found in the report | 180 ps; setup 130, hold 150, Clk-Q 300 ps; 1739.13 MHz | No figures; "Optimized through CLA architecture" |
| Layout | Hierarchical, initial and revised floor plans | Block and top layout; pitches 93.69 and 122.22 um | Blocks and top |
| Extraction | Present | 376 MOS, only 32 capacitors in the top netlist | Present |
| LVS | No evidence | No evidence | Claimed in README; no LVS files found |

## Worth adopting

- Module-by-module order: gates, flip-flop, adder, full circuit, each with its own deck and post-layout deck (all three).
- Floor plan iteration shown with before and after (2021).
- Separate decks for setup, hold and Clk-Q (2026).
- Explicit pitches in the report, as the course requires (2025).
- Derivation from equations to gate structure before showing the circuit (2021).

## Weaknesses to avoid

1. **Timing arithmetic.** In the 2025 report, the course formula with its own numbers gives 1/(180+130+150 ps) = 2174 MHz, not the reported 1739.13 MHz, and the derivation is not shown. We must show each calculation.
2. **Near-ideal input edges.** 10 ps edges from ideal sources appear in 2021 decks. These hide input-loading cost, so wide devices look free.
3. **Junction estimates.** The 2021 decks use a constant 5 lambda diffusion length. Tech-file rules give 6 lambda when contacted and 3 lambda when shared.
4. **Extraction threshold.** Only 32 capacitors in a 376-device 2025 netlist suggests small coupling was dropped. We set `cthresh 0`.
5. **Limited vector coverage.** Decks focus on selected pulse patterns. We test all arcs and report the method.
6. **Unsupported claims.** "Post-layout matches pre-layout" and "100 % coverage" appear in the 2026 README without data.
7. **Hand-drawn schematics** can differ from the netlist. Ours are to be generated from the source that creates the netlist.

## Practical notes

- 2021 registers Cin with its own flip-flop (`x109` in `top.sp`), though Figure 1(i) of the course PDF does not show it.
- `.measure` statements in the 2021 full-circuit deck are commented out, so its top-level delay cannot be reproduced directly from that file.
- Tech-file copies in these folders differ from ours at least in line endings. We use only the provided root copy.
