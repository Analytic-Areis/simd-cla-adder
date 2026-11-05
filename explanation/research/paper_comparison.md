# Provided paper comparison

Reported values only. "n/s" means not stated in the text extracted. Delays are not comparable across rows, because node, supply, load and tested transitions differ.

| # | Year | Style | Node, supply | Scope | Reported delay | Devices | Load stated? | Applicability to our goal |
|---|---|---|---|---|---|---|---|---|
| 33 | 2017 | NAND/NOR carries, alternating polarity | 0.25 um, 2.5 V | 4-bit CLA | 1.008 to 0.732 ns | n/s | No load | **High** |
| 05 | 2019 | Mirror nested gate | 90 nm | C4 only | 166 to 134 ps | 92 to 36 | n/s | **High** for C4 |
| 32 | 2014 | Ratioed, binary weighted | 0.18 um, 1.8 V | C4 only | 256 ps in Fig. 6, 500 ps in abstract | n/s | n/s | Benchmark only |
| 15 | 2017 | Static + delayed non-critical path | 90 nm | 4-bit CLA | Not the focus | 997 + 18 | n/s | Glitch method |
| 23 | 2010 | Subthreshold | 65/90 nm, 0.2 V | CRA, MCLA | ns range | n/s | 100 fF | Test method |
| 02 | 2026 | NAND-based static | 90 nm, 1.2 V | RCA, CLA, layout | 79.7 ps (Cin to Cout) | 332 | n/s | Report format |
| 12 | 2013 | Domino Manchester, Ling-style | 90 nm, 1 V | 8 to 64 bit | Improvement 4.73 to 35.08 % | n/s | n/s | Concepts |
| 03 | 2020 | GDI/PTL input gates | 90 nm, 1.2 V | 4-bit CLA | 0.162 to 0.143 / 0.135 ns | 176 to 106 / 142 | n/s | Low |
| 14 | 2020 | Hybrid XOR + GDI AND | 90 nm, 1.0 V | 4-bit CLA | 0.163 to 0.138 ns | 170 to 138 | n/s | Low |
| 19 | 2023 | GDI AND + XOR | 90 nm, 1.0 V | 4-bit CLA | 0.167 to 0.143 ns | 170 to 142 | n/s | Low |
| 13 | 2025 | Hybrid GDI + TG | 90 nm | 4-bit CLA | 0.150 to 0.093 ns | 80 to 56 | n/s | Low; inconsistent |
| 27 | 2025 | PTL versus TG | n/s | 4-bit CLA | 2.35 / 1.20 ns (CMOS 1.13 ns) | 56 / 136 / 512 | n/s | Evidence against PTL |
| 54 | 1997 | Bootstrapped pass transistor | n/s, 1.5 V | 4-bit carry | 70 % faster | n/s | n/s | Low |
| 24 | 2013 | MT-CMOS domino | 0.18 um | 4-bit Manchester | 55 % reduction claimed | n/s | n/s | Needs dual Vt |
| 16 | 2014 | Dual-mode logic | 45 nm | 4 to 32 bit | Faster, higher power | n/s | n/s | Needs low Vt and clock |
| 22 | 2016 | Adiabatic, stacking | 180 nm | 4-bit CLA | 24.362 / 27.176 / 23.447 ns | n/s | n/s | Power only |
| 26 | 2014 | Subthreshold static | 180 nm, 0.4 V | 4-bit CLA | Operation up to 5 MHz | n/s | n/s | Layout order only |
| 01 | 2024 | Five adder types | 90 nm | 4-bit | CLA 3.998 ns, CSkA 25.565 ps | 366 / 182 | n/s | Results not credible |
| 04 | 2023 | TG-based gates | 45 nm | 4-bit CLA | Roughly 5 times RCA | n/s | n/s | Errors in equations |
| Dhanjal | 2022 | Mirror logic | n/s | 4-bit CLA | None | n/s | n/s | Layout idea |

## Patterns

1. **Reduced transistor count is often presented as the source of speed.** Our requirement is worst-case delay with a defined load, so this needs testing rather than assuming.
2. **Static CMOS is usually treated as the slow baseline, but the baseline is rarely optimised.** A sized static design is the fair comparison.
3. **Worst-case delay is tested inconsistently.** Several test Cin only. Papers 33 and 23 look at inputs more widely, and paper 33 identifies a path from an operand bit.
4. **Dual threshold is unavailable to us.** Techniques relying on it cannot be reproduced with the provided model.
