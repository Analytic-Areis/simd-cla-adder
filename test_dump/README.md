# test_dump

Layouts, post-layout simulations and result files of designs that were tried and **not used** in the final adder. They were moved here on 2026-11-07 so the project folders hold only the final design. Nothing was deleted, and each item keeps its original path under this folder. For example, `test_dump/part1/layout/integrated/cmp_C4_tg` was `part1/layout/integrated/cmp_C4_tg`.

The final design is `final_C4_aoi22_1`: the C4 prefix tree with AOI22 sums, after one layout-aware sizing round. Its layout, the registered layout, and the gate and block layouts it uses remain in `part1/layout/`.

| What | Moved here |
|---|---|
| Other full adders | `cmp_C4_tg` and `final_C4_tg_1`/`_2` (C4 with transmission-gate sums), `cmp_R_aoi22_refresh` and `cmp_R_tg_refresh` (flat carries, mirror C4) |
| Other layouts of the chosen design | `cmp_C4_aoi22` (before layout-aware sizing), `final_C4_aoi22_2` (second sizing round, not kept), `scale_C4_aoi22_*` (uniform scaling, 0.7 to 1.4) |
| Router and flow trials | `trial`, `trial_reg`, `flow_check` |
| Cells not in the final adder | NAND3 to NAND5, NOR3 to NOR5, AOI22 alone, carry gates c1 to c4 and their mirrors, Manchester bit, flat carry cell, older P/G and sum cells, TG, NAND4 and 12-transistor XORs |
| Post-layout simulations of the above | `part1/simulations/timing/post_cmp_*`, `post_final_C4_aoi22_2`, `post_final_C4_tg_*`, `post_scale_*`, `trial_post`, `reg_trial`, `tradeoff` |
| Result files of the above | `part1/results/final/cmp_*.json`, `final_C4_aoi22_2_post.json`, `final_C4_tg_*`, the TG-sum sizing files, `phase4_tradeoff.csv`, `phase7_layout_aware_C4_tg.csv` |

Schematic-level comparisons of the six candidate architectures stay in `part1/results/phase3_unit_comparison.csv`, because the reports use them to explain why C4 was chosen.

`final_flow.py` and `top.py` can still re-create these items. They would write to the original paths, not here.
