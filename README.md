# VLSI Design Course Project: CLA & SIMD Reconfigurable Adder

Implementation, layout, and FPGA validation of a 4-bit Carry Lookahead Adder (CLA) and an 8-bit SIMD-reconfigurable adder datapath.

---

## Project Overview

* **Course**: VLSI Design (Monsoon 2026), CVEST, IIIT Hyderabad


* **Instructor**: Prof. Abhishek Srivastava


* **Target Technology**: 180 nm CMOS Process (`SCN6M_DEEP.09.tech27` technology rules for MAGIC)


* **Operating Conditions**: $V_{DD} = 1.8\text{ V}$, equal gate lengths $L_n = L_p = 2\lambda$ ($\lambda = 0.09\ \mu\text{m}$)


* **Load Requirement**: Output sum bits drive an inverter load of size $W_p / W_n = 20\lambda / 10\lambda$



---

## Project Architecture & Modules

```
                    +------------------------------------+
Inputs (A, B) ----->| Input D-Flip-Flops                 |
                    +-----------------+------------------+
                                      |
                                      v
                    +------------------------------------+
                    | 4-bit Carry Lookahead Adder (CLA)  |
                    |  - Propagate & Generate (P/G) Unit |
                    |  - Carry Lookahead Generator (CLG) |
                    |  - Sum Generation Logic            |
                    +-----------------+------------------+
                                      |
                                      v
                    +------------------------------------+
Outputs (Sum, Cout)>| Output D-Flip-Flops & Inv Loads    |
                    +------------------------------------+

```



1. **Part I: Pipelined 4-bit Carry Look Ahead Adder (40 Marks)**


* Module decomposition: Propagate/Generate ($P/G$), Carry Look Ahead unit, and Sum block.


* Static/dynamic CMOS schematic entry and NGSPICE characterization.


* Sequential characterization: D-Flip-Flop setup time ($t_{\text{setup}}$), hold time ($t_{\text{hold}}$), and clock-to-Q delay ($t_{c\text{-}q}$).


* MAGIC physical layout, design rule checking (DRC), and parasitic extraction (`ext2spice`).


* Post-layout validation: Critical path delay under worst-case transitions, maximum clock frequency ($f_{\max}$), dynamic power, and Power-Delay Product (PDP).




2. **Part II: SIMD-Reconfigurable 8-bit Adder (30 Marks)**


* Dual-mode datapath using two 4-bit CLA blocks (`CLA0` and `CLA1`):


* **8-bit Mode (`SIMD_MODE = 0`)**: $C_{\text{out}}$ of `CLA0` passes to $C_{\text{in}}$ of `CLA1`.


* **Dual 4-bit Mode (`SIMD_MODE = 1`)**: Inter-block carry is gated to `0`, executing two concurrent 4-bit additions.




* Carry-gating cell implementation (schematic + layout).


* Overhead and penalty characterization vs. baseline direct 8-bit CLA: Delay Penalty ($\Delta t_{pd}$), Power Penalty ($\Delta P_{\text{avg}}$), and Energy-Delay Product (EDP).




3. **Part III: HDL & FPGA Implementation (30 Marks)**
* Behavioral Verilog modeling and simulation testbenches for both architectures.
* FPGA logic synthesis and on-board hardware validation with oscilloscope waveform capture.



---

## Repository Directory Structure

```text
├── hdl/
│   ├── sim/                    # Simulation testbenches and test vectors
│   └── src/                    # Verilog RTL files (4-bit CLA, SIMD 8-bit Adder)
├── layout/
│   ├── magic/                  # MAGIC layout files (.mag) using SCN6M_DEEP.09
│   └── extracted/              # Extracted SPICE netlists (.ext, .spice)
├── ngspice/
│   ├── blocks/                 # Sub-circuit netlists (DFF, PG_logic, CLA_logic, Sum)
│   ├── sim_schematic/          # Pre-layout test fixtures and transient decks
│   ├── sim_postlayout/         # Post-layout delay, power, and PDP verification
│   └── tech/                   # 180nm TSMC/MOSIS model cards
├── fpga/
│   ├── constraints/            # Pin constraints (.xdc / .ucf)
│   └── scope_captures/         # Oscilloscope measurements and hardware validation
└── docs/
    └── report/                 # Final PDF deliverable and plot figures

```

---

## Toolchain & Dependencies

* **Circuit Simulator**: NGSPICE (v30+)


* **Layout Editor**: MAGIC VLSI (v8.3+) with technology file `SCN6M_DEEP.09.tech27`


* **HDL Simulation & Synthesis**: Vivado / ModelSim / Icarus Verilog
* **Hardware**: Target FPGA board and Digital Storage Oscilloscope (DSO)

---

## Key Simulation Guidelines

* **Plot Titles**: Set the plot title in every NGSPICE control script for traceability:


```spice
set curplottitle="<Name>-<RollNo>-<QuestionNo>-<Part>"

```





* **Worst-Case Delay Vector**: Set $A = 1111_2$, $B = 0000_2$, with $C_0$ toggling $0 \rightarrow 1$. Measure 50% $V_{DD}$ to 50% $V_{DD}$ delay using `.meas` commands across all output bits ($S_0 \dots S_3, C_4$).


* **Maximum Reliable Clock Frequency**:

$$f_{\max} = \frac{1}{t_{pd,\max} + t_{\text{setup}} + t_{\text{hold}}}$$





* **SIMD Delay & Power Penalties**:

$$\text{Delay Penalty (\%)} = \left(\frac{t_{pd,\text{SIMD}} - t_{pd,\text{baseline}}}{t_{pd,\text{baseline}}}\right) \times 100\%$$


$$\text{Power Penalty (\%)} = \left(\frac{P_{\text{SIMD, mode 0}} - P_{\text{baseline}}}{P_{\text{baseline}}}\right) \times 100\%$$
