# Candidate architecture comparison

> **Outcome:** this file is the planning estimate. Measurement overturned its recommendation: C4 won, not R. Measured results are in `../results/phase3_unit_comparison.csv`, `../results/final/` and `../../explanation/research/research_log.md`.

Estimates come from `le_estimate.py`. Brackets use textbook parameters. They rank candidates for SPICE; they are not results. Transistor counts are for the adder alone, without flip-flops.

| ID | Architecture | A0→S3 ps | C0→S3 ps | A0→C4 ps | Max stack | Approx. devices | Status |
|---|---|---|---|---|---|---|---|
| C1 | XOR propagate, NAND-NAND carries | 654 (377) | 420 (266) | 570 (309) | 5 | 200 or more | Baseline in SPICE |
| C2 | NAND/NOR front end, single complex gate per carry | 450 (308) | 348 (278) | 334 (240) | 5 | About 170 | Rival in SPICE |
| **R** | C2, but C4 is a mirror gate over C2 | **450 (308)** | 338 (268) | 375 (311) | 4 | **172** | **Lead** |
| C3 | Stack limit 3, two carry levels | 470 (343) | 404 (315) | 317 (278) | 3 | About 170 | SPICE |
| C4 | Valency-2 prefix with late C0 | 510 (377) | 273 (197) | 335 (275) | 2 | About 180 | SPICE |
| E | Static Manchester TG chain | Needs SPICE | Needs SPICE | Needs SPICE | 4 TG in series | About 150 | SPICE |
| F | Domino Manchester | Timing model differs | Timing model differs | Timing model differs | 4 | About 130 | One prototype only |
| G | Ling-style [12] | Not estimated | Not estimated | Not estimated | 3 | Higher | Only if time allows |
| H | Ratioed generator [32] | n/a | n/a | n/a | n/a | n/a | Rejected |

## Expansion of carry equations

| Form | Example for C3 | Effect |
|---|---|---|
| Flat sum of products | G2 + P2G1 + P2P1G0 + P2P1P0C0 | Two levels with wide gates; high fan-in and fan-out |
| Nested single gate (R, C2) | G2 + T2(G1 + T1(G0 + T0C0)) | One stage with a 4-high stack |
| Grouped (C3) | G2 + T2C2 | Fewer stacked devices, one more stage |
| Prefix (C4) | G2:0 + T2:0C0 | C0 sees one gate; A0 sees several |

## R count

| Block | Composition | Devices |
|---|---|---|
| P/G, 4 bits | NAND2 4, NOR2 4, AOI21 6, OAI21 6 | 80 |
| C0 inverter | | 2 |
| C1, C2, C3 | 6 + 10 + 14 | 30 |
| C4 | Mirror 18, inverter 2 | 20 |
| Sum, 4 bits | AOI22 8, inverter 2 | 40 |
| **Total** | | **172** |

Sum variants change this count.

## Key conclusion

The lowest C0→S3 estimate belongs to C4, but its A0→S3 is among the slowest. If optimised only for the hint vector, it would look best while being slower in the true worst case. So every candidate is judged on all arcs, not on the hint vector alone.
