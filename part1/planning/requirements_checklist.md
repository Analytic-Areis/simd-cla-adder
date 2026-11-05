# Part I requirements checklist

Source: `Course_project.pdf` (40 marks). Due 1 Dec 2026, 18:00. Demo and viva 3 and 4 Dec 2026.

## Global conditions
- [x] Part I PDF: `part1/documentation/Bhargav_2025102061.pdf` (final submission must also add Parts II and III)
- [x] Use the given 180 nm model for NGSPICE and `SCN6M_DEEP.09.tech27` for MAGIC
- [x] Ln = Lp, VDD = 1.8 V
- [x] Every plot carries `Bhargav-2025102061-question-part`; ngspice lowers its case in its own plots
- [x] Answers include explanation, plots, annotations, netlists

## Circuit
- [x] 4-bit CLA between input and output registers, Figure 1(i)
- [x] P/G, carry and sum blocks, Figure 1(ii)
- [x] Each sum bit drives an inverter, Wp/Wn = 20λ/10λ, L = 2λ, λ = 0.09 µm
- [x] Inputs available before a rising edge; output present at the next rising edge, Figure 1(iii)
- [x] Logic style is free: static, dynamic or mixed

## Numbered tasks
- [x] 1. Discuss proposed structure
- [x] 2. Topology and sizing of every block, including the D flip-flop
- [x] 3. Simulate each block and verify functionality
- [x] 4. D flip-flop setup, hold, clock-to-Q from NGSPICE
- [x] 5. Layout each block in MAGIC; extract; compare with schematic simulation
- [x] 6. Integrate; full netlist; annotated waveforms; worst-case delay; maximum clock speed
- [x] 7. Floor plan; horizontal and vertical pitches of regular structures
- [x] 8. Full layout and extraction; repeat simulations; schematic versus post-layout table
- [x] 9. Post-layout worst-case vector and tpd,max. Check tpLH and tpHL on S0 to S3 and C4
- [x] 10. Post-layout fmax = 1/(tpd,max + tsetup + thold), with plots
- [x] 11. Post-layout Pavg at fmax and PDP = Pavg x tpd,max

## Added by project brief
- [x] Exhaustive functional check, 512 input combinations
- [x] tpLH, tpHL, per-output delays
- [x] Optimisation log and ADP alongside PDP
- [x] Block-level and transistor-level schematics matching the netlists
- [x] Preserve netlists, logs and waveform data
- [x] Part I only: no Part II, SIMD, Verilog or FPGA work

## Points to confirm
| Point | Working decision |
|---|---|
| Figure 1(i) shows no register on Cin | Add a ninth input flip-flop (D9) |
| The load sentence names sum bits only | Also load C4 (D10) |
| "Output" could mean the CLA or the flip-flop output | Report both (D10) |
| The fmax formula omits clock-to-Q | Report the course value and the physical limit (D11) |
| C0 rising alone cannot give tpLH on S | Test both edges (D6) |
