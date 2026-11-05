# FPGA, Part III

Verilog for the 4-bit CLA (Part I) and the SIMD-reconfigurable 8-bit adder (Part II), testbenches, Boolean Board tops and constraints.

| Item | Status |
|---|---|
| Behavioural RTL, both designs | Written |
| Simulation, Icarus Verilog | All four testbenches pass. 264,000+ vectors checked, 0 errors |
| Annotated waveforms | `results/3.1` to `3.3` |
| Synthesis, implementation, bitstream | **Not run yet.** Vivado is not installed on this machine. Use `scripts/build.tcl` on a machine with Vivado |
| Hardware test and oscilloscope captures | Not done yet |

**Board:** Real Digital Boolean Board, Spartan-7 `xc7s50csga324-1`, 100 MHz clock. The part and pins come from the reference project in `reference_constraints/`.

## Folders

| Path | Contents |
|---|---|
| `rtl/` | `cla4.v` and `simd8.v`, the adders. `cla4_reg.v` and `simd8_reg.v`, the registered circuits with input and output flip-flops |
| `board/` | Board tops `fpga_cla4_top.v` and `fpga_simd8_top.v`, plus shared helpers in `board_common.v`: reset, step clock, random generator, displays |
| `tb/` | Testbenches |
| `constraints/` | One constraint file per top, `fpga_cla4_top.xdc` and `fpga_simd8_top.xdc`. Every pin is commented with what it does in that design |
| `scripts/` | `run_sim.sh` runs every testbench. `plot_waves.py` draws the figures. `build.tcl` builds a bitstream in Vivado |
| `sim/` | Simulation logs and VCD waveforms, written by `run_sim.sh` |
| `results/` | Annotated waveform figures |
| `reference/`, `reference_constraints/` | The reference code and constraints this was based on, unchanged |

## Run

```bash
bash scripts/run_sim.sh
```

```bash
python3 scripts/plot_waves.py
```

On a machine with Vivado, from this folder:

```bash
vivado -mode batch -source scripts/build.tcl -tclargs fpga_cla4_top
```

```bash
vivado -mode batch -source scripts/build.tcl -tclargs fpga_simd8_top
```

Outputs go to `build/<top>/`: the bitstream, synthesised netlist, and utilisation, timing and power reports.

## The designs

- **`cla4`:** generate `g = a·b`, transmit `t = a + b` for the carries, propagate `p = a ⊕ b` for the sums. Every carry is computed directly from g, t and Cin, as in Part I.
- **`simd8`:** two `cla4` blocks. The carry-gating cell is `cin_hi = cout_lo · ¬SIMD_MODE`. In mode 0 the lower carry passes to the upper block; in mode 1 it is forced to 0. `cout_lo` keeps the lower block's carry visible in both modes.
- **Registered versions:** inputs are captured on one clock edge and the result is registered on the next, as in Part I Figure 1(i).

## Simulation test vectors

| Testbench | What it checks | Vectors |
|---|---|---|
| `tb_cla4` | TEST 1: every input combination against a + b + Cin | 512 |
| | TEST 2: hint vector A = 1111, B = 0000, Cin toggling | 4 |
| | TEST 3: corner cases: zero, all ones, generate at bit 0, generate at bit 3, all propagate with and without Cin | 8 |
| `tb_simd8` | TEST 1: 8-bit mode, every combination of A, B, Cin against A + B + Cin | 131,072 |
| | TEST 2: dual 4-bit mode, every combination against two separate 4-bit sums | 131,072 |
| | TEST 3: worst carry path A = 0xFF, B = 0x00, Cin toggling, both modes | 6 |
| | TEST 4: same operands with the mode switched, to show the carry passed or blocked | 6 |
| | TEST 5: the gating cell, all four combinations of lower carry and mode | 4 |
| `tb_registered` | One-clock latency through the registers, with the enable always on and every third clock | 2,609 |
| `tb_fpga_tops` | Both board tops: self-test through all phases, manual switch entry, and a deliberate fault the self-check must catch | 5 tests |

Every check compares against a model written with `+`, separate from the look-ahead equations. In the SIMD model, dual mode is two 4-bit sums with the upper carry-in forced to 0.

## Using the board

### CLA4 board

| Control | Use |
|---|---|
| SW0 to SW3 | A, SW0 is the lowest bit |
| SW4 | Not used, a gap |
| SW5 to SW8 | B, SW5 is the lowest bit |
| SW9 | Not used, a gap |
| SW10 | Cin |
| SW12, SW13 | Step rate: 1.49 Hz, 95.4 Hz, 6.10 kHz, 781 kHz |
| SW15 | 0 = manual, 1 = automatic self-test |
| Left display D0 | A on the two left digits and B on the two right digits, in decimal: A = 7, B = 12 shows `0712` |
| Right display D1 | S on the two right digits, in decimal. The two left digits are off |
| LED0 | Cin |
| LED3 | Cout (C4) |
| LED5, LED6 | Self-test running, self-test error |
| LED12, LED13 | Self-test phase |

### SIMD8 board

| Control | Use |
|---|---|
| SW0 to SW7 | Operand value |
| SW14 | 0 = the switches set A, 1 = they set B. The other operand keeps its last value |
| SW8 | Cin |
| SW9 | SIMD_MODE |
| SW12, SW13 | Step rate, as above |
| SW15 | 0 = manual, 1 = automatic self-test |
| Left display D0 | A and B, in hex |
| Right display D1 | Cout, lower carry-out, S[7:4], S[3:0], in hex |
| LEDs | LED0 Cin, LED1 mode, LED2 lower carry-out, LED3 gated carry, LED4 Cout, LED5 self-test running, LED6 error, LED12, LED13 phase, LED14 step clock, LED15 pass |

The board resets itself at power-up, because the reference gives no button pins. LED7 to LED11 and the buttons are not used for the same reason.

## Hardware test scenarios

The self-test checks every result against a `+` model on the chip itself. A mismatch lights the error LED until the board is switched back to manual.

| Phase | CLA4 board | SIMD8 board |
|---|---|---|
| 0 | A = 1111, B = 0000, Cin toggling: the hint vector | 8-bit mode, A = 0xFF, B = 0x00, Cin toggling: the Part II worst case |
| 1 | A = 0000, B = 1111, Cin toggling | Dual mode, same vector: the carry must stop at bit 4 |
| 2 | Pseudo-random A, B, Cin | 8-bit mode, pseudo-random |
| 3 | All 512 inputs in order | Pseudo-random with the mode switching every step |

**Oscilloscope probes**, on the GPIO header pins used for SPI in the reference project. Check each against the header labels before connecting.

| Probe | Pin | CLA4 board | SIMD8 board |
|---|---|---|---|
| `probe[0]` | B13 | Step clock | Step clock |
| `probe[1]` | E12 | Cin at the adder input | Cin at the adder input |
| `probe[2]` | A13 | S3 at the adder output | S7 at the adder output |
| `probe[3]` | C14 | C4 at the adder output | Cout at the adder output |
| `probe[4]` | A14 | Error flag | Gated carry into the upper block |

Suggested captures:
1. Phase 0 at the 781 kHz rate: Cin against S3, or S7, and Cout. Every Cin edge flips the sum and carry.
2. SIMD8 in phases 0 and 1: the gated carry, probe 4, follows Cin in 8-bit mode and stays low in dual mode.
3. Any phase: the error flag, probe 4 on the CLA4 board, stays low.

The probes show the adder's inputs and outputs between the two register stages. The time from Cin to the sum edge includes the FPGA's logic and routing plus two output buffers, so it is not the same as the transistor-level delay of Part I.
