# Research log: Part I, 4-bit CLA

Factual record. Append new dated entries; do not rewrite old ones.

## 2026-10-31: Planning milestone

### Inventory
- Read `Course_project.pdf` (3 pages), including Figure 1. Checklist: `part1/planning/requirements_checklist.md`.
- Tools present: ngspice-46, MAGIC 8.3.668, Python 3.14 with numpy, matplotlib, pypdf, pdfplumber, pymupdf, pdflatex.
- Tools absent: netgen (no Homebrew formula found), xschem, schemdraw, scipy.
- `TSMC_180nm.txt` and `ref/TSMC_180nm.txt` differ only in line endings (CRLF), confirmed by diff after stripping CR.

### Literature
- Read all 20 PDFs in `ref/papers/`, and rendered the figures of papers 05, 12, 32 and 33. Paper 32's text layer is garbled, so it was read from page images.
- Spot-checked archived papers 18 and 31. The screening stands: 18 is a parallel-prefix design simulated in Xilinx ISE; 31 is an incrementer/decrementer.
- External sources read in part: Zlatanovici et al. 2009; Stojanovic and Oklobdzija 1999. Others were checked at citation or abstract level only. See `literature_review.md`.
- A paper by Harris and Sutherland on logical effort of adders could not be located, so it is not cited.

### Measured: technology characterisation
Script: `part1/simulations/characterisation/tech_char.py`. Netlists and logs: `runs/`. Data: `results/`.

Conditions: VDD 1.8 V, 27 C, model as provided, junction areas estimated from tech-file rules (6 lambda contacted, 3 lambda shared).

| Quantity | Value |
|---|---|
| Input capacitance of the 20L/10L load inverter | 7.58 fF |
| Gate capacitance per um, NMOS / PMOS | 2.38 / 2.04 fF/um |
| FO4 inverter delay at Wp/Wn = 2 | 85.5 ps (tpHL 85.0, tpLH 86.0) |
| Wp/Wn giving minimum average delay | 1.5 (84.0 ps), very flat around it |
| tau from delay-versus-fanout fit | 11.90 ps |
| Effective inverter parasitic | 3.13 tau |

The effective parasitic is well above the textbook value of 1 because the fit includes the delay caused by a finite input slope. It should be read as a fitted value under these driving conditions, not as pure self-loading.

Series stacks, each device sized n times unit, delay at electrical effort 4:

| n | NAND near output | NAND near rail | NOR near output | NOR near rail |
|---|---|---|---|---|
| 2 | 108.7 ps | 114.6 ps | 130.0 ps | 145.7 ps |
| 3 | 131.1 ps | 154.5 ps | 169.7 ps | 215.6 ps |
| 4 | 153.1 ps | 203.6 ps | 206.0 ps | 297.2 ps |
| 5 | 174.1 ps | 260.6 ps | 238.7 ps | 389.0 ps |

Findings:
- Input position matters greatly: 33 % delay difference on NAND5 and 39 % on NOR5.
- PMOS stacks are the limiting case. NOR5 with the worst input position is 4.6 FO4.
- Fitted g agrees with textbook logical effort within about 10 % (NAND3 1.53 versus 5/3; NOR3 2.2 versus 7/3).

Failure recorded: the first run aborted with "Timestep too small". The shaper inverter had W = 0.056 um, below the 0.27 um (3 lambda) minimum. Widths are now clipped at 0.27 um.

### Measured: layout flow check
Files: `part1/layout/flow_check/`. Test inverter only, not a design cell.
- MAGIC runs in batch with the provided tech file. After two fixes (poly overhang 3 lambda, well overlap of contact 3 lambda), DRC count is 0.
- The provided tech file extracts device models as `nfet` and `pfet`, whereas the model file defines `CMOSN` and `CMOSP`. Extracted netlists need renaming on a copy.
- Ports must be created with `port make` for extracted subcircuits to have pins.
- Extracted versus schematic delay, driving one load inverter: tpHL 35.6 versus 34.8 ps; tpLH 37.1 versus 36.2 ps (about 2.5 % slower).

### Estimate: logical-effort ranking
Script: `part1/planning/le_estimate.py`. Output: `le_estimate_results.csv`. Not a simulation. Excludes wires. Input budget 15 fF per pin, load 7.58 fF.

| Candidate | A0 to S3 | C0 to S3 | A0 to C4 |
|---|---|---|---|
| C1 textbook XOR + NAND-NAND | 654 (377) | 420 (266) | 570 (309) |
| C2 flat complex gates | 450 (308) | 348 (278) | 334 (240) |
| C3 stack limit 3, two carry levels | 470 (343) | 404 (315) | 317 (278) |
| C4 valency-2 prefix, late C0 | 510 (377) | 273 (197) | 335 (275) |
| R flat C1 to C3, C4 mirror over C2 | 450 (308) | 338 (268) | 375 (311) |

Values in ps using measured stack data; in brackets, textbook g and p. Absolute values are only rough. The two parameter sets differ by up to about 1.7 times.

Findings:
- In all candidates the A0 path is estimated slower than the C0 path, so the hint vector may not be the true worst case. Paper 33 also names the path from B0 through C3 to S3 as the longest [33, p.2]. To be tested by simulation.
- Ranking by the C0 path puts the prefix design first; ranking by the A0 path puts it behind the flat designs. Optimising only the hint vector could choose the wrong architecture.
- C2 and R tie on the estimated worst path. C3 and C4 are close enough that SPICE must decide.

### Logic check of candidate R
`part1/planning/check_logic.py` compares the proposed compound P/P-bar, carry and sum functions with the CLA equations and integer addition over all 512 inputs: 0 mismatches. This is Boolean only, not a circuit simulation.

### Outcome
Recommended lead architecture R, direct rival C2, others kept as comparison. See `design_decisions.md`. No CLA circuit has been implemented or simulated yet.

## 2026-10-31: Phase 0, tooling

### Built
- Final folder layout. `technology/` links to the provided files, which were not moved.
- `part1/cells/`: one definition generates the SPICE subcircuit and the schematic. 16 cells generated at unit size: inverter, NAND2 to 5, NOR2 to 5, AOI21, OAI21, AOI22, C1, C2, C3, C4-bar mirror.

### Tests
`part1/cells/tests/test_cellgen.py`, 6 tests, all pass:
- Logic evaluated at switch level from the emitted SPICE text matches the intended function for every input, with neither a floating output nor a rail short.
- Widths are legal, on the lambda grid, with bodies tied.
- Each schematic's drawn devices equal the netlist's (name, type, terminals, W, L).
- Transistor counts are 6, 10, 14, 18 for C1, C2, C3, C4-bar.
- Stack heights are 2, 3, 4, 3.
- NAND3/5 and NOR3/5 geometry equals the characterisation netlists.

A separate one-off run confirmed the logic check flags a wrong function and a floating output. It was not saved as a test.

### Measured: generated inverter
`part1/results/phase0_generator_check.csv`, from `part1/cells/verify_phase0.py`:

| Check | Generated | Reference | Difference |
|---|---|---|---|
| FO4 tpHL | 85.028 ps | 85.028 ps | 0.000 % |
| FO4 tpLH | 85.972 ps | 85.972 ps | 0.000 % |
| Flow inverter tpHL | 34.725 ps | 34.725 ps | 0.000 % |
| Flow inverter tpLH | 36.150 ps | 36.150 ps | 0.000 % |

These show the generator reproduces hand-built netlists. They are not an independent check of the model.

### Problems found and resolved
- **Correction to the flow check entry above.** The hand-written driver in `flow_inv_tb.cir` had PS = PD = 9 um instead of 8.28 um. First seen as a 0.15 % offset in the generator comparison. Removing the extracted branch did not change the numbers, ruling out the first explanation. Fixing the perimeter removed the offset entirely. The bench and log were updated. Corrected results: extracted 35.57 / 37.07 ps, schematic 34.73 / 36.15 ps (tpHL / tpLH), or 2.44 % and 2.55 % slower. Superseded values were 35.6 / 37.1 and 34.8 / 36.2 ps.
- **Stack test.** When tightened to exact equality it failed with 6 against 3, because it counted paths doubling back through a node. This was a fault in the test, not the cells. Paths may no longer revisit a node.

### Observations
- `set curplottitle` reaches the ngspice hardcopy, in lower case. Earlier submissions show the same.
- Plot titles still have a NAME-ROLL placeholder.
- The waveform for the FO4 input shows slight undershoot just before the rising edge, as expected from coupling through the gate-drain capacitance.

### Not done in Phase 0
Transmission-gate cells, layout generation, sizing, input-order optimisation. No adder has been assembled.

## 2026-10-31: Phases 1 to 3, tooling and first comparison

The user asked for work to continue through all phases without pausing for approval.

### Phase 1: block cells
Added transmission-gate stages and hierarchical blocks to the generator. New cells: four XOR variants, Manchester stage, C3-bar mirror, P/G bit and block, candidate R carry block, four sum blocks.

`part1/results/phase1_block_functional.csv`: all 27 cells and blocks passed at transistor level, inputs through unit inverters and outputs loaded by the 20L/10L inverter, in binary and shuffled vector order. Worst VOH 1.7289 V, worst VOL 0.0124 V. Largest DC supply current below 1 nA.

Problems found:
- **Bench failure read as circuit failure.** Blocks showed identical error counts. ngspice had aborted with "Timestep too small": its minimum step is 1e-11 of the maximum step, which at 2 ps falls under double-precision time resolution near 0.5 us. The bench then scored missing data as errors. Benches now use a suitable maximum step and report any aborted run as a failure.
- **False static-current failures.** Transient samples of supply current gave about 40 uA regardless of settling time, which is integration ringing. Replaced by DC operating points for every vector. A deliberately contending cell gives 459 uA, so the check does detect contention.

### Phases 2 and 3: unit-size comparison
`part1/results/phase3_unit_comparison.csv`. All 4608 single-input transitions, with final-crossing delay. Driver: x2 inverter behind an x1 shaper. Pin delay is the course's measure; driver delay also charges for input capacitance.

| Candidate | Transistors | Width (lambda) | Worst pin ps | Worst from driver ps | Hint vector ps |
|---|---|---|---|---|---|
| C1 textbook | 208 | 5260 | 771.3 | 832.5 | 421.4 |
| C2 flat | 170 | 5470 | 764.0 | 840.6 | 577.2 |
| R | 172 | 5160 | 727.0 | 803.5 | 574.2 |
| C3 stack 3 | 170 | 4800 | 796.4 | 873.1 | 623.5 |
| C4 prefix | 194 | 4930 | 658.9 | 735.5 | 360.0 |
| E Manchester | 144 | 3480 | 799.8 | 882.2 | 629.1 |
| R with TG sum | 164 | 4560 | 698.8 | 787.0 | 542.1 |

Findings:
- **The logical-effort estimate was wrong about ranking.** It placed C4 behind C2 and R on the A0 path. At unit sizing C4 is fastest. This overturns the estimate at unit sizing; sized results decide.
- **The hint vector is not the worst case in any candidate.** The worst arcs start at operand bits a0, a1, b1, as predicted.

### Optimiser attempt 1, discarded
Tracked only 26 arcs. R_tg showed 672 ps on its working set but 1010 ps on the full check, because downsizing slowed untracked paths. Logs kept in `part1/simulations/optimisation/attempt1_overfit/`. Also found ngspice oversubscribing the CPU with its own threads (load average 75 on 10 cores); runs now use one thread each. The restart tracks the worst arc of every input-output class (114) and confirms each move on all of them.

### Phase 5: flip-flop
`part1/results/phase5_dff_first_comparison.csv`, 15 fF load plus inverter:

| Flip-flop | T | tcq ps | tsu ps | thold ps | tcq + tsu ps | tsu + thold ps |
|---|---|---|---|---|---|---|
| TSPC | 11 | 172.9 | 40.0 | 43.4 | 212.9 | 83.4 |
| TG master-slave | 22 | 200.8 | 116.0 | -42.2 | 316.8 | 73.8 |

The course formula slightly favours TG master-slave (73.8 ps, thanks to negative hold), but the real clock limit depends on clock-to-Q plus setup, where TSPC is about 100 ps better, with half the transistors. **TSPC chosen.** First hold result of 300 ps for TG was an artefact of checking Q before it settled, corrected.

### Layout flow
`part1/cells/cellgen/layout.py`, `lvs.py`, `part1/cells/top.py`. Rules were learned from MAGIC DRC reports: metal 2 via 5 lambda, poly to poly contact 4, metal 3 and 4 spacing 4, stacked vias must be in one cell. Results: all 30 cells DRC 0 and LVS match. Assembled unit-size adder: DRC 0, LVS match on 186 devices.

- LVS is our own script (netgen unavailable). Tests confirm it rejects a wrong width, swapped gate, missing device and shorted nets. It caught a real short from an over-eager metal 3 fill.
- MAGIC image export is blank in batch mode, so figures are drawn from saved .mag files.
- Unit-size C4 with TG sums, first floorplan: worst pin delay 718.3 ps post-layout. Total wire capacitance 342 fF, with g0b and c0 near 15 fF. Aligning sum cells to bit columns and ordering carry gates by bit gave 282 fF, 18 % less, and 5 % less area.
- Extraction here reports capacitance only. Resistance is still to be assessed.

Name and roll number supplied by the user: Bhargav, 2025102061.

## 2026-10-31: Phases 4 to 9, final design

The user provided name and roll number and said to continue with the design proposed, which at that point meant selecting by measured data rather than keeping candidate R. R stayed in the comparison.

### Phase 4: sizing and choice
Second optimiser (`part1/cells/optimize.py`): objective is a soft maximum of delay from the driver input, tracked on the worst arc of each input-output class, with moves screened on the 36 slowest classes and confirmed on all, then a full 4608-transition check. Logs in `part1/simulations/optimisation/`.

A further flaw was found: within a class, the slowest input state can change as sizes change, so a full check could still exceed the tracked worst. The working set is now rebuilt from each full check.

Layout-aware loop: extracted wire capacitance per net is back-annotated, sizes refined, layout rebuilt, all transitions re-simulated.

| Design | Schematic pin ps | Post, schematic sizes ps | Post, final ps | Area um2 | Status |
|---|---|---|---|---|---|
| C4 + AOI22 sum | 489.9 | 597.61 | 579.88 | 2936.9 | Chosen |
| C4 + TG sum | 487.3 | 601.45 | 596.66 | 2498.5 | Lower area and ADP |
| R + TG sum | 559.1 | 645.59 | not refined | 3425.8 | Slower and larger |
| R + AOI22 sum | 586.1 | none | none | | Layout failed LVS after routing relaxation; not pursued |
| C2 + TG sum | 663.5 at last full check | none | none | | Stopped early at about 36 % behind C4 |

Round 2 of the loop was worse in both C4 designs (594.85 and 597.38 ps), so round 1 was kept. **Engineering conclusion: the prefix design is faster than flat complex gates here, which is the opposite of the first estimate.** R and C2 were not refined with wire load; C4's margin is much larger than the refinement gain seen on C4 itself (about 18 ps).

### Phase 5: flip-flop
TSPC at the real pin load, 47.76 fF including wire, drives x0.6, x1, x1, x2. Schematic tcq 208.5, tsu 34.0, thold 55.1 ps. Post-layout tcq 204.2, tsu 38.0, thold 45.7 ps.

### Phases 6 to 8: registered system and layout
`part1/results/final/system.json`. Registered adder: 348 transistors, DRC 0, LVS match on 348 merged devices and 207 nets, area 7005.5 um2, 624.5 fF wire capacitance. 264 vectors: hint vector, 30 slowest arcs, 200 random. Shortest working period by binary search: schematic 740.2 ps (1.351 GHz), extracted 872.1 ps (1.147 GHz).

Final adder truth table, all 512 inputs twice: 0 errors on schematic and on extracted netlist. All nine tiles and the flip-flop: DRC 0, LVS match, 0 functional errors in their single-input transitions.

### Phase 9: worst case, fmax, power
- Schematic worst single-input 516.3 ps; extracted 579.88 ps, a1 rising to S3 rising, A=0001 B=0101 C0=0.
- Hint vector, extracted: worst 455.23 ps. **The hint vector understates the true worst case.**
- **Correction of an assumption:** multi-input transitions were expected to matter little, and the 65,520-transition sample on the annotated schematic peaked at 577.64 ps, under the single-input worst. Re-simulating its 100 slowest pairs on the extracted netlist gave **589.85 ps**, four inputs changing, which exceeds 579.88 ps. tpd,max is therefore 589.85 ps. It is from a 25 % sample, so an unsampled transition could be slower.
- Course formula: 589.85 + 38.0 + 45.7 = 673.6 ps, 1.485 GHz. **At that period the extracted circuit produced 264 wrong samples.** The formula omits clock-to-Q. tcq + tpd + tsu gives 832.0 ps; simulation gives 872.1 ps. The 40 ps further gap is not fully explained; likely contributors are real input slopes, and that tcq and tsu were measured in isolation.
- Power at 872.1 ps, extracted, circuit under test only (a first version included the bench's drivers and buffers, corrected): 3.39 mW on random and critical vectors, PDP 2000 fJ. 2.50 mW for hint vector toggling. 0.887 mW with inputs constant.

### Resistance
MAGIC `extresist` crashed with a segmentation fault; log in `part1/results/final/resistance/`. Bound: longest poly run 152 lambda, 585 ohm at 7.7 ohm/square, placed in series with all 194 gates. Worst single-input delay rose from 579.88 to 600.83 ps, 3.61 %. This over-estimates poly resistance on purpose and excludes metal and vias.

### Tool note
A user-suggested MAGIC bridge (github.com/EkanshWadhwa39/magic-agent-bridge) was read but not used; batch scripts already covered DRC and extraction.

### Precision note
Re-running the worst single-input arc from a settled state gave 583.77 ps, against 579.88 ps in the all-transition walk. Hint-vector worst was 454.2 ps in a short run and 455.23 ps in the walk. Delay therefore depends slightly on preceding state. Charge on internal stack nodes is the likely reason; not investigated further.

### Trade-off and router limitation
`part1/results/phase4_tradeoff.csv`, uniform scaling of the final sizes, post-layout single-input worst: x0.7 602.38 ps, 2574.0 um2, 0.983 mW; x0.85 601.39 ps, 2743.7 um2, 1.116 mW; x1.0 579.88 ps, 2936.9 um2, 1.270 mW, reproducing the earlier layout exactly; x1.2 590.99 ps, 3293.8 um2, 1.482 mW. Power is adder only at 1 ns per vector. x1.3 and x1.4 were DRC clean but failed LVS after routing, as did R with AOI22 sums. The cause was not found. LVS stops these cases from being reported, but the router is not proven reliable at higher congestion.

### Report
`part1/documentation/Bhargav_2025102061.pdf`, Part I only, built from result files by `part1/cells/make_report.py`. Review of the PDF found one failing row in the block truth table: the unit-size 5-high C4 gate reached 1.604 V at the 980 ps sample, under the 1.62 V limit. At 3 ns per vector it passed with 0 errors. The gate is used only by rejected candidate C2.

Planned items not done: domino prototype, exhaustive multi-input sweep, netgen source build, layout-aware sizing of R and C2, true resistance extraction.

### Schematic power, added after the report
`part1/results/final/schematic_power.json`, schematic registered circuit, circuit under test only, 264 vectors, 0 errors: 3.0883 mW at 872.1 ps, the same clock as the extracted result (3.3899 mW), and 3.6208 mW at its own 740.2 ps limit. Not yet in the report PDF.

## 31 Oct 2026: check of part1_agy

Checked the separate design in `part1_agy` without writing to it. Details in `part1/results/agy_comparison/comparison.md`.

- Valid: logic 0 errors on 512 inputs, DRC 0, full LVS match, fresh extraction agrees, stored results reproduced by rerunning its flow on a copy.
- Common bench, post-layout, Q to output with the same load: part1_agy 664.51 ps, this design 615.68 ps. Schematic: 491.70 ps and 536.71 ps. Hint vector, post-layout: 371.93 ps and 472.73 ps.
- Area, drawn extent: 13437 and 6960 um2.
- First-Q multi-input figure on this design is 673.42 ps with added inverters, against 589.85 ps reported from simultaneous pin edges without them. The first-Q figure includes flip-flop rise and fall skew.
- Clock limit, power and flip-flop stages on the common bench were not run: the user asked to stop computing.

## 3 Nov 2026: logic-style check, pre-layout

Script `part1/cells/logic_styles.py`, results `part1/results/logic_styles.json`. One 4-stage ripple carry chain C0 to C4, all bits propagating, same C0 driver and carry loads for every style, sizing swept per style, 409 versions. Correct means C4 within 10 % of each rail.

- Best C0 to C4 delay: pseudo-NMOS 235.8 ps at 6056 uW, footless domino 328.6 ps (rising only) at 1417 uW, static CMOS mirror 349.7 ps at 371 uW, footed domino 377.2 ps, TG mux 422.5 ps, DCVSL 578.8 ps, CPL 603.7 ps.
- Pseudo-NMOS best has VOL 0.175 V. With VOL at most 0.12 V its best is 290.6 ps, and at most 0.09 V it is 401.8 ps.
- Not tested: GDI, dual-mode logic, MT-CMOS, adiabatic logic.
- Pre-layout only, ripple chain only. The final design is unchanged.
- Decision, 3 Nov 2026: the user chose to keep static CMOS. No pseudo-NMOS carry tree will be built.

## 3 Nov 2026: folder cleanup

On the user's request, moved to the Trash (folder `temp_vlsi_cleanup_2026-11-03`): `part1_agy` (the user keeps a backup), `part1/simulations/agy_check`, `part1/layout/via_probe`, the empty `part1/schematics/block_level`, LaTeX build files and the duplicate `report.pdf`, and `.DS_Store` files. Comparison results stay in `part1/results/agy_comparison/`. READMEs rewritten.

## 3 Nov 2026: project moved up one level

At the user's request, everything in `temp_vlsi/` was moved into `VLSI_CP/` and the empty `temp_vlsi/` removed. Earlier entries that name `temp_vlsi` refer to this same project root.

## 3 Nov 2026: CMOS and FPGA split

At the user's request, the project root was split into `cmos_layout/` (Part I, research, technology files, references) and `fpga/` (Part III, empty). The assignment PDF and the top README stay in `VLSI_CP/`.

## 3 Nov 2026: Part III Verilog started

In `fpga/`: behavioural RTL for the 4-bit CLA and the SIMD 8-bit adder, registered versions, two Boolean Board tops with a built-in self-test, one constraints file from the reference project's pins, and a Vivado build script. Icarus Verilog: all four testbenches pass, 0 errors over 524 + 262,160 + 2,609 checks and 5 board-level tests. Vivado synthesis and hardware testing not done yet; Vivado is not installed on this machine.

## 5 Nov 2026: Part II, SIMD-reconfigurable 8-bit adder

Code: `part2/cells/simd.py`. Two instances of the final Part I adder with a carry-gating cell, `cin_hi = cout_lo · ¬SIMD_MODE`, as NAND2 ×1 and inverter ×2 with a unit mode inverter, 8 transistors. Sizes from a 25-point schematic sweep on Cin to S7.

- Logic: 3000 random inputs at switch level, 0 errors, SIMD and baseline.
- Layout: a flat 8-bit row layout failed to route. Replaced by two placed copies of the adder cell, laid out again with extra metal 3 pads for C4 and C0, plus the gating cell, flattened, inter-block carries on metal 5. Fixes on the way: a via over a pin via cut a metal 2 to 3 link (LVS caught it); stacked separate vias not allowed, so `m345c`; one pad too close to a metal 4 track, so pads moved between tracks. Final: DRC 0 and LVS match for both, 396 and 388 devices.
- Worst-case search, 13,312 single-input transitions per case, 0 errors. Schematic: baseline 855.22 ps, SIMD mode 0 920.09 ps, mode 1 516.31 ps. Post-layout: 1030.86, 1109.77 and 570.22 ps.
- Cin to S7, A = FF, B = 00, post-layout: baseline 816.11 ps rise, SIMD 877.83 ps, penalty +61.72 ps, 7.56%. Falling edge +114.44 ps, 14.49%.
- Course-formula fmax: 0.897, 0.838 and 1.529 GHz. At those clocks some random multi-input vectors did not settle. All three settle on 200 random vectors at 1400 ps, and power is compared there: 1695.2, 1720.7 and 1592.4 µW over 10 cycles, power penalty 1.50% (2.30% on 200 vectors). EDP penalty 17.6%.

## 5 Nov 2026: folders reorganised

At the user's request: `part1/`, `part2/` and `part3/` (was `fpga/`) at the top level, `technology/` holds the provided model and tech file as real files, and `explanation/` holds this research folder, the references and the guides. All three parts were rerun after the move: Part I tests pass, a Part II post-layout check gives the same delay, and all Part III testbenches pass.

## 5 Nov 2026: Part II report

`part2/documentation/Bhargav_2025102061_part2.pdf`, 10 pages, built by `part2/cells/make_report.py` from the result files: task, architecture, gating cell and its sizing, layout, worst-case delay in both modes, delay penalty, fmax and power penalty, EDP, limits, netlists. While checking it, an EDP unit slip in the Part II README was found and fixed: EDP is about 1.8 × 10⁻²¹ J·s, not 10⁻²⁴. The JSON results were right.

## 5 Nov 2026: MAGIC screenshots in both reports

`part1/cells/magic_shot.py` opens a cell in MAGIC's own X11 window on the XQuartz display, fits it, dumps the window with `xwd`, and converts the dump to PNG unchanged, cropped to the cell outline. The layout figures in both reports are now these screenshots. Part I: P/G, sum, carry and flip-flop tiles, the final adder and the registered circuit. Part II: the adder cell with pads, the gating cell, the SIMD adder, a close-up of the gate between the blocks, and the baseline. MAGIC's Cairo display mode failed on XQuartz with a BadAccess error, so the plain X11 mode is used. Reports: Part I 26 pages, Part II 12 pages.

## 5 Nov 2026: submission report, draft 1

`submission/Bhargav_2025102061.pdf`, 17 pages, IEEE two-column style after the reference report the user gave (a 5-bit CLA report): contents page, numbered sections, gate-by-gate pre- and post-layout plots, MAGIC screenshots of every gate and block, Part II as section XI, placeholders for Verilog and FPGA. New in this draft: per-gate waveforms and delays (`submission/figures.py sims`, 0 errors, for example NAND2 tpLH 66.02 ps pre-layout and 66.14 ps post-layout), full registered circuit plots pre- and post-layout on eight additions (0 wrong samples), and MAGIC screenshots of each gate and block.

## 2026-11-05: full-circuit transistor-level schematic

Added `submission/full_schematic.py`. It draws all 194 adder transistors with their final W/L from the same cell objects that write the netlist, split into three full-page figures by signal flow: P/G front end (80 T), prefix tree (50 T), final carries and sums (64 T), plus the TSPC flip-flop. Gates connect by net name; group nets print as G(i:j) and T(i:j) with bars for active-low. A check confirms the drawn devices equal the netlist devices, 194 of 194. The figures are vector PDF and sit at the end of Section III of the submission report (Figs. 6 to 8); the report is now 21 pages.

## 2026-11-07: course container configuration

Added `docker-compose.yml` from the course toolchain guide (iic-osic-tools, container iiith_vlsid_env, noVNC 6080, `~/designs` at `/foss/designs`), with one extra volume mounting this project at `/foss/designs/VLSI_CP`. `magic_shot.py` now finds `xwd` on PATH and takes the display from `$DISPLAY` when it is an X display name, so it works in the container; on the Mac it still uses XQuartz on :1. Docker is not installed on this Mac, so the container run is not yet tested. The project's results were all produced on the Mac.

## 2026-11-07: unused designs moved out; Euler paths and stick diagrams

Moved the layouts, post-layout simulations and result files of designs not used in the final adder into `test_dump/`, keeping their original paths. That covers C4 with TG sums, the R designs, the other layouts of C4/AOI22 (before sizing, the second sizing round, uniform scaling), router trials, and cells not in the final adder. `test_dump/README.md` lists them all.

Both reports no longer include post-layout results of those designs. Part I lost its finalists table and its area-delay trade-off section; the submission report lost its trade-off subsection. The schematic unit-size comparison of the six architectures stays, because it explains why C4 was chosen.

Added `submission/stick_euler.py`. For each gate it captures the row order the layout generator chose and checks that the regenerated layout matches the saved MAGIC layout script, which all 7 cells do. It then draws the PUN/PDN Euler graphs and a centre-line stick diagram of the layout. All five logic gates and the AOI22 XOR have unbroken Euler paths with a common P/N order; the TSPC flip-flop has one break per row. This is a new report section, before the MAGIC layouts; the MAGIC screenshots are kept.

## 2026-11-10: reports trimmed to netlists, MAGIC and cited papers

The evaluator asked that the reports show netlists, MAGIC layouts and only the papers actually used, with no mention of the scripts. Changes, in `submission/build_report.py`, `part1/cells/make_report.py` and `part2/cells/make_report.py`:
- Removed every mention of scripts, the layout generator, the "automated" search, the LVS comparison script and netgen, the Part II "Reproducing the results" appendix and the `simd.py` source line, the Part II router remark, and the Part I limitation about the LVS tool. Results and numbers are unchanged.
- References: only cited works remain. Submission: removed Zlatanovici et al., Weste and Harris, and Mano. Part I: removed Yuan and Svensson, Weste and Harris, and Mano (none cited), and added entries for Hasan et al. (2019), Efstathiou et al. (2013) and Nyathi and Mutumba (2017), which the text already named.
- The submission still has no netlist appendix, as the user chose.

## 2026-11-10: Part III folder renamed to fpga/

At the user's request, `part3/` is now `fpga/`, so it can go into the user's own git repo on its own and be used from a laptop with Vivado. Added `fpga/scripts/create_project.tcl`, which makes a Vivado project with every source, both constraint files and the four testbenches (not run yet: no Vivado on this Mac), and `fpga/.gitignore`. Updated the README's Vivado steps. All four Icarus testbenches pass from `fpga/` and from a copy made outside the project. Earlier entries that say `part3/` refer to this folder.
