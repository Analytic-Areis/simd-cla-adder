# Part III explained: Verilog and FPGA

Full details: [`../part3/README.md`](../part3/README.md).

## The task

1. Describe the 4-bit CLA and the SIMD 8-bit adder in Verilog, and prove them correct by simulation in every mode.
2. Synthesise both and run them on the FPGA, a Boolean Board with a Spartan-7, with oscilloscope captures.

## What was written

| Part | Files | What it does |
|---|---|---|
| Adders | `rtl/cla4.v`, `rtl/simd8.v` | Same equations as the transistor designs: generate, transmit, look-ahead carries. The SIMD adder uses two `cla4` blocks and the gate `cin_hi = cout_lo & ~simd_mode` |
| Registered versions | `rtl/cla4_reg.v`, `rtl/simd8_reg.v` | Input flip-flops, the adder, output flip-flops, as in the transistor designs |
| Board tops | `board/fpga_cla4_top.v`, `board/fpga_simd8_top.v` | Switches, displays, LEDs, a built-in self-test and scope outputs |
| Testbenches | `tb/` | Exhaustive and directed tests |
| Constraints | `constraints/fpga_cla4_top.xdc`, `constraints/fpga_simd8_top.xdc` | One per board top, from the reference project's pins |

## How correctness was shown

| Testbench | Vectors | Result |
|---|---|---|
| 4-bit CLA, every input, plus the hint vector and corner cases | 524 | 0 errors |
| SIMD adder, every input in both modes, plus directed tests | 262,160 | 0 errors |
| Registered circuits, one-clock latency | 2,609 | 0 errors |
| Board tops: self-test, switch entry, a planted fault | 5 tests | All pass |

Every check compares with a model written using `+`, separate from the look-ahead equations. Annotated waveforms are in `part3/results/`.

## On the board: CLA4

| Control | Use |
|---|---|
| SW0 to SW3 | A |
| SW5 to SW8 | B |
| SW10 | Cin |
| Left display | A and B in decimal |
| Right display | S in decimal |
| LED0 | Cin |
| LED3 | Cout |
| SW15 | Runs the self-test |

## Still to do

- Vivado synthesis and bitstream: Vivado is not installed on this Mac. Use `part3/scripts/build.tcl` on a lab machine.
- Hardware test and oscilloscope captures on the board.
