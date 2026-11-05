# Part I explained: the 4-bit carry look-ahead adder

The illustrated version, with circuit diagrams, is [`guide/part1_build_guide.html`](guide/part1_build_guide.html). Open it in a browser. This page is the same story in short, with the numbers.

## The task

Add two 4-bit numbers A and B and a carry-in C0, giving a 4-bit sum S and a carry-out C4. Inputs are captured by flip-flops on one clock edge, and the result by flip-flops on the next edge. The goal is the smallest **post-layout worst-case delay**, measured on the real drawn layout with its wires. Area and power come second.

## The idea in one paragraph

A ripple adder passes the carry from bit to bit, so the top bit waits for all the others. A carry look-ahead adder works out every carry from two signals per bit: **generate**, g = a·b, where the bit makes a carry by itself, and **transmit**, t = a + b, where it passes one along. Written flat, C4 needs five transistors in series, which is slow. This design builds the carries as a **prefix tree**: bits are joined two at a time into group signals, and C0 is added last. No gate has more than 2 transistors in series.

## How it was built, phase by phase

| Phase | What was done | What closed it |
|---|---|---|
| Planning | Papers read, the transistor model measured: FO4 = 85.5 ps. Delays estimated with logical effort | Six candidate designs chosen |
| 0 | A Python generator: one description of each cell makes the SPICE netlist, the schematic drawing and the MAGIC layout | The generated inverter matched measurements |
| 1 | Gates and blocks: NAND, NOR, AOI/OAI compound gates, two XOR forms for the sum | Transistor-level truth tables pass |
| 2 | Six candidate adders, C1, C2, R, C3, C4 and E, each a different way to build the carries | All 512 input combinations correct |
| 3 | Every candidate searched over all 4608 single-input transitions | Candidate C4, the prefix tree, fastest: 658.9 ps at unit size |
| 4 | Transistor sizing by an optimiser, later fed with wire capacitance from the layout | Stable worst delay; trade-off data |
| 5 | Flip-flop: TSPC, 11 transistors, one clock | Faster than the master-slave flip-flop: 212.9 against 316.8 ps |
| 6 | The registered circuit and its clock limit | 264-vector frequency search |
| 7 | Block layouts in MAGIC: DRC, extraction, LVS | Every block clean |
| 8 | The full layout in rows, routed on metal 3 and 4 | DRC 0, LVS match |
| 9 | Post-layout measurements | Results below |
| 10 | The report | `part1/documentation/Bhargav_2025102061.pdf` |

## Final results, post-layout

| Measure | Value |
|---|---|
| Worst single-input delay | 579.88 ps, a1 rising to S3 rising |
| tpd,max with several inputs changing, sampled | 589.85 ps |
| Hint vector (A = 1111, B = 0000, C0 toggling) | 455.23 ps. It is not the worst case |
| Flip-flop tcq / tsetup / thold | 204.2 / 38.0 / 45.7 ps |
| Fastest working clock | 872.1 ps, 1.147 GHz |
| Course formula clock, tpd + tsu + thold | 673.6 ps. It fails in simulation: it leaves out Clk-Q |
| Power at 872.1 ps, random inputs | 3.39 mW |
| Area: adder / full registered circuit | 2937 / 7005.5 µm² |
| Transistors: adder / full circuit | 194 / 348 |

## Key decisions and why

- **Static CMOS** for every adder gate. A later check of other styles on one carry chain found only pseudo-NMOS faster, at 16 times the power and with a weak low level. Static CMOS was kept; see `research/research_log.md`.
- **Prefix carry tree**, candidate C4: fastest of six at unit size, and still fastest after sizing and layout.
- **OR-type transmit for the carries:** t = a + b differs from XOR only when both bits are 1, and then generate already sets the carry, so the lighter OR gate can be used. XOR is kept for the sum.
- **AOI22 sum gate:** 579.88 ps against 596.66 ps for the transmission-gate version, which is smaller.
- **Worst case found by search:** the hint vector looks like the longest path but is not.
- **Cin registered too:** a ninth flip-flop, so all inputs share one clock. To confirm on Moodle.

Full reasoning: [`research/design_decisions.md`](research/design_decisions.md).
