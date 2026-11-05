# Part I: 4-bit carry look-ahead adder

Status: complete. Report: [`documentation/Bhargav_2025102061.pdf`](documentation/Bhargav_2025102061.pdf).

## Where things are

| Folder | Contents |
|---|---|
| `documentation/` | Report PDF, LaTeX source `report.tex`, and `figures/` |
| `results/` | Summary CSVs by phase. `final/` holds the final measurements |
| `results/agy_comparison/` | Check of the separate `part1_agy` design against this one. Read `comparison.md` |
| `results/logic_styles.json` | Pre-layout check of seven logic styles on one carry chain |
| `layout/integrated/` | Assembled layouts. `final_C4_aoi22_1` is the final adder and `registered` is the full circuit. The rest are trials and sizing variants |
| `layout/individual_blocks/` | Each block's MAGIC layout and extraction |
| `layout/flow_check/` | First MAGIC to ngspice flow test |
| `extraction/` | Extracted netlists of the final adder and the registered circuit |
| `schematics/transistor_level/` | Generated schematic drawings. `final/` has the final sizes |
| `simulations/` | Netlists, logs and waveforms of every run, by kind |
| `cells/` | Generators, test benches, optimiser, layout flow and report builder |
| `spice/` | Generated netlists and a link to the model |
| `planning/` | Requirements, planning estimates, strategy and roadmap |

`project_config.json` holds the name and roll number used in plot titles.

## Rebuild

Commands run from `cells/`. See [`cells/README.md`](cells/README.md).

## Notes

- Layout figures in the report are screenshots of MAGIC's own window, taken by `cells/magic_shot.py` with XQuartz running.

- `part1_agy` was removed on 3 Nov 2026. A backup is kept outside this folder. Its comparison results stay in `results/agy_comparison/`, but `cells/agy_check.py` cannot be rerun without it.
- The provided model and tech file are in `../technology/`. Research notes are in `../explanation/research/`.
