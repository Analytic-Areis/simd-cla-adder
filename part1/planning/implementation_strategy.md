# Implementation and verification strategy

Proposed circuits. No W/L values yet; sizing follows the SPICE comparison.

## Proposed transistor-level design (candidate R)

**Front end, bit i**

| Output | Function | Gate | Devices |
|---|---|---|---|
| g-bar i | NOT(ai bi) | NAND2 | 4 |
| t-bar i | NOT(ai + bi) | NOR2 | 4 |
| Pi | NOT(ai bi + t-bar i) | AOI21 | 6 |
| P-bar i | NOT((ai + bi) g-bar i) | OAI21 | 6 |

Pi and P-bar i have matched depth and need no internal inverter. `check_logic.py` confirms the proposed functions over all 512 inputs (Boolean only).

**Carry gates**

| Carry | Function | Stack N / P | Devices |
|---|---|---|---|
| C1 | NOT[g̅0 (t̅0 + c̅0)] | 2 / 2 | 6 |
| C2 | NOT[g̅1 (t̅1 + g̅0 (t̅0 + c̅0))] | 3 / 3 | 10 |
| C3 | NOT[g̅2 (t̅2 + g̅1 (t̅1 + g̅0 (t̅0 + c̅0)))] | 4 / 4 | 14 |
| C̅4 | NOT[a3 b3 + (a3 + b3)(a2 b2 + (a2 + b2) C2)] | 3 / 3 | 18 |
| C4 | Inverter on C̅4 | 1 / 1 | 2 |

**Sum, variant to be chosen.** Si = NOT(Pi Ci + P̅i C̅i) as AOI22 plus an inverter making C̅i. Alternatives: TG mux with output inverter, 12T static XOR, 4-NAND.

**Sizing method.** Start from logical effort using measured g and p. Then iterate: simulate all arcs, find the slowest, adjust only devices on that path, keep a change only if worst-case delay falls. Limit input capacitance so the driver cost stays visible.

## Expected critical paths (hypotheses)

| Rank | Path | Why |
|---|---|---|
| 1 | A0 or B0 → t̅0 or g̅0 → C3 gate → XOR → S3 | Highest fan-out, 4-high stack, worst input position, then XOR |
| 2 | A0 or B0 → C2 → C̅4 → C4 | Two complex gates and an inverter |
| 3 | C0 → c̅0 → C3 → XOR → S3 | Course's hint path; skips the P/G stage |
| 4 | Ai → Pi → XOR → Si | Two XOR-depth stages, without carries |

Most likely slow edge: output transitions pulled up through a PMOS stack.

## Optimisation opportunities

1. Input order within stacks: up to 33 to 39 % measured on isolated gates.
2. Separate the XOR gate load from t̅0 and g̅0 if it dominates.
3. Skew stacks: favour the critical edge rather than equalising.
4. Reduce the fan-out on t̅0 and g̅0, the highest-branching nets.
5. Compare sum stages.
6. In layout: share diffusion in stacks; keep the C0, t̅0 and C3 routes short.

## Proposed schematics

Draft: `proposed_block_diagram.png`, `proposed_c2_gate.png`. For the report, generated from cell definitions, with W/L labels:
block level; NAND2 and NOR2; AOI21 and OAI21; C1, C2, C3; C̅4 mirror gate; sum stage; inverters and buffers; flip-flop.

## Simulation strategy

| Check | Method | Pass or output |
|---|---|---|
| Each block | Exhaustive truth table | All combinations match |
| Function | 512 vectors, each settled, compared with a Python golden model | Zero mismatches |
| Single-input arcs | 9 inputs x 256 states x 2 edges = 4608 | Worst arc, by output and edge |
| Multi-input arcs | Up to 261,632 ordered pairs. Run all if run time allows; otherwise sampling guided by slowest arcs, stated in the report | Worst vector |
| Hint vector | A = 1111, B = 0000, C0 both edges | Required table |
| Flip-flop | Sweep D-to-clock | Setup, hold, Clk-Q, D-Q curve |
| Full system | Registered circuit with a frequency search | Failing frequency, against the formula |
| Power | Post-layout at fmax over a stated interval: hint vector and random vectors | Pavg, PDP |
| Robustness (optional) | VDD ±10 %, temperature | Margins |

**Conventions.** Input from a pulse with 20 ps edges through finite inverter drivers. Delay from DUT input to final output crossing at 0.9 V. Junction areas 6λ contacted, 3λ shared, until extraction replaces them. `.meas` is used wherever possible. Logs and raw data are kept. `set curplottitle` is on every plot.

**Area for ADP.** Layout bounding box in µm², and total device width. ADP = area x tpd,max. PDP and ADP are never interchanged.

## Layout strategy

- Rows with shared VDD and ground rails; a common cell height.
- Metal 1 inside cells, metal 2 and 3 between them.
- MAGIC scripted by Tcl with DRC run for every cell.
- `ext2spice cthresh 0`; model names renamed on a copy from `nfet`, `pfet` to `CMOSN`, `CMOSP`.
- Ports defined with `port make`.
- Check LVS, then simulate extracted netlists with the same testbenches as the schematic.

## Tool gaps

| Gap | Plan |
|---|---|
| netgen | Build from source; fallback is a comparison script |
| Schematic capture | Python generation from cell definitions |
| schemdraw, scipy | Install in a project virtual environment if needed |
| Plot titles | Needs your name and roll number |
