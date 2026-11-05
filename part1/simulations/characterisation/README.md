# Technology characterisation

Measures basic properties of the provided 180 nm model. This is not a CLA circuit.

Run with `python3 tech_char.py`. Netlists and ngspice logs go to `runs/`; CSV data goes to `results/`.

| Experiment | Output | Measures |
|---|---|---|
| E1 | `e1_capacitance.csv` | Load inverter input capacitance; gate capacitance per µm |
| E2 | `e2_beta_sweep.csv` | FO4 delay against Wp/Wn |
| E3 | `e3_inverter_fanout.csv`, `e3_fit.csv` | tau and effective parasitic |
| E4 | `e4_stack_raw.csv`, `e4_stack_summary.csv` | g and p for NAND and NOR, 1 to 5 inputs, input near and far from the output |

Results are summarised in `../../../explanation/research/research_log.md`.
