# Cell generator

One definition in `library.py` produces both the SPICE subcircuit and the transistor-level schematic, so a drawing cannot differ from the netlist it documents.

```bash
python3 generate.py
```

```bash
python3 -m unittest discover -s tests
```

```bash
python3 verify_phase0.py
```

| File | Purpose |
|---|---|
| `library.py` | Cell definitions. Edit cells here. |
| `generate.py` | Writes `../spice/modules/*.sp` and `../schematics/transistor_level/*`. |
| `cellgen/network.py` | Series and parallel networks, dual, mirror, path-based sizing. |
| `cellgen/cell.py` | Devices, junction estimates, SPICE output and parsing. |
| `cellgen/schematic.py` | Drawing. |
| `cellgen/sim.py` | Runs ngspice, reads `.meas`, converts hardcopies. |
| `cellgen/config.py` | Constants and the plot title. |
| `tests/test_cellgen.py` | Checks that need no simulator. |
| `verify_phase0.py` | Compares generated inverters with earlier measurements. |

## Conventions

- A network is written top to bottom: VDD to output for pull-up, output to ground for pull-down. Child order in `S()` is physical order, so it sets which input is nearest the output.
- Widths are whole lambda, minimum 3. A width given as `D("a", w=30)` overrides automatic sizing.
- Automatic sizing: width = drive x unit x the longest series path through that device. Unit is 10 lambda NMOS, 20 lambda PMOS.
- Junctions before layout: 6 lambda if contacted, 3 lambda on an uncontacted two-device series node.
- Pin names ending in `b` are active-low.

## Full flow

| Step | Command |
|---|---|
| Unit comparison | `python3 run_compare.py` |
| Size a design | `python3 optimize.py C4_aoi22 8` |
| Lay out sized designs | `python3 final_flow.py compare C4_aoi22` |
| Layout-aware loop | `python3 final_flow.py refine C4_aoi22 3 8` |
| Final measurements | `final_flow.py` stages: `dff`, `blocks`, `system`, `multi 4`, `verify_multi`, `course`, `power`, `sch_final`, `functional`, `tradeoff` |
| Resistance bound | `python3 resistance_bound.py final_C4_aoi22_1 7.7` |
| Report | `python3 make_figures.py`, then `python3 make_report.py` |

`final_design.json` in `../results/final/` selects the design the later stages use.

## Limits

- Static gates and transmission gates only.
- LVS is a project script, not an industry tool.
- MAGIC images are drawn from .mag data.
