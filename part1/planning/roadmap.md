# Part I roadmap

Due 1 Dec 2026. Each phase ends only with its check passed. Target dates allow time for the report and for Parts II and III.

**Status: Phases 0 to 10 of Part I complete on 31 Oct. Planned items not done: domino prototype, exhaustive multi-input sweep, netgen source build, refinement of R and C2.**

| Phase | Work | Done when | Target |
|---|---|---|---|
| 0 (done) | Move to the final folder layout; cell description format; netlist and schematic generators | Generated inverter matches measured results | 2 Nov |
| 1 | Add transmission-gate support; block cells and transistor-level truth-table tests in ngspice | All blocks pass | 4 Nov |
| 2 | Build candidates C1, C2, R, C3, C4, E; domino prototype; 512-vector checks | All functional | 7 Nov |
| 3 | Same sizing budget for all; 4608 arcs on each; choose architecture and sum stage | Comparison table recorded | 9 Nov |
| 4 | Sizing iterations with log; ADP and PDP comparisons; broader multi-input search | Stable worst-case delay; design frozen | 12 Nov |
| 5 | TSPC versus TG master-slave; setup, hold, Clk-Q | Flip-flop chosen and characterised | 14 Nov |
| 6 | Full registered circuit; waveforms; frequency search | Pre-layout system verified | 15 Nov |
| 7 | Solve LVS method; block layouts; DRC, extraction, per-block comparison | Every block clean and compared | 20 Nov |
| 8 | Floor plan and pitches; top layout; extraction | DRC clean, LVS match | 24 Nov |
| 9 | Post-layout tpd,max, fmax, Pavg, PDP, ADP; schematic versus post-layout table | All tasks 8 to 11 answered | 26 Nov |
| 10 | Report with generated figures, plot titles, netlists; demo notes | PDF complete | 29 Nov |

## Proposed folder layout

```text
VLSI_CP/
├── Course_project.pdf
├── README.md
├── ref/                    untouched
├── technology/             provided files, moved only after your approval
├── explanation/research/  decisions, literature, log
└── part1/
    ├── planning/
    ├── cells/              single-source cell definitions and generators
    ├── schematics/{block_level,transistor_level}/
    ├── spice/{models,modules,testbenches,integration}/
    ├── simulations/{characterisation,functional,timing,optimisation}/
    ├── layout/{flow_check,individual_blocks,integrated}/
    ├── extraction/
    ├── results/
    └── documentation/
```

The provided model and tech file are in `technology/`.

## Main risks

| Risk | Response |
|---|---|
| Layout parasitics reorder paths | Rerun all-arc search on the extracted netlist |
| Full multi-input search too slow | Guided sampling, stated openly |
| netgen build fails | Comparison script |
| Scripted layout of complex gates takes longer than planned | Begin block layouts early and reuse common cells |
| Interpretation of Cin and load differs from the instructor's | Confirm on Moodle; report both cases |
