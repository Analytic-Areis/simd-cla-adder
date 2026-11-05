* inv_x1: inverter
* GENERATED from part1/cells/library.py. Do not edit by hand.
.subckt inv_x1 a y vdd gnd
Mp1 y a vdd vdd CMOSP W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=9.7200e-13 PD=4.6800e-06
Mn1 y a gnd gnd CMOSN W=9.0000e-07 L=1.8000e-07 AS=4.8600e-13 PS=2.8800e-06 AD=4.8600e-13 PD=2.8800e-06
.ends inv_x1
* nand2_x1: 2-input NAND
* GENERATED from part1/cells/library.py. Do not edit by hand.
.subckt nand2_x1 i0 i1 y vdd gnd
Mp1 y i0 vdd vdd CMOSP W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=9.7200e-13 PD=4.6800e-06
Mp2 y i1 vdd vdd CMOSP W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=9.7200e-13 PD=4.6800e-06
Mn1 y i0 xn1 gnd CMOSN W=1.8000e-06 L=1.8000e-07 AS=4.8600e-13 PS=4.1400e-06 AD=9.7200e-13 PD=4.6800e-06
Mn2 xn1 i1 gnd gnd CMOSN W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=4.8600e-13 PD=4.1400e-06
.ends nand2_x1
* inv_x2: inverter
* GENERATED from part1/cells/library.py. Do not edit by hand.
.subckt inv_x2 a y vdd gnd
Mp1 y a vdd vdd CMOSP W=3.6000e-06 L=1.8000e-07 AS=1.9440e-12 PS=8.2800e-06 AD=1.9440e-12 PD=8.2800e-06
Mn1 y a gnd gnd CMOSN W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=9.7200e-13 PD=4.6800e-06
.ends inv_x2
* carry_gate_n1_i2: carry-gating cell: cin_hi = cout_lo AND NOT mode
* GENERATED from part1/cells/library.py. Do not edit by hand.
.subckt carry_gate_n1_i2 cout_lo mode cin_hi vdd gnd
Xinvm mode modeb vdd gnd inv_x1
Xnandg cout_lo modeb gn vdd gnd nand2_x1
Xinvg gn cin_hi vdd gnd inv_x2
.ends carry_gate_n1_i2
