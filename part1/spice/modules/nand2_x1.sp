* nand2_x1: 2-input NAND
* GENERATED from part1/cells/library.py. Do not edit by hand.
.subckt nand2_x1 i0 i1 y vdd gnd
Mp1 y i0 vdd vdd CMOSP W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=9.7200e-13 PD=4.6800e-06
Mp2 y i1 vdd vdd CMOSP W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=9.7200e-13 PD=4.6800e-06
Mn1 y i0 xn1 gnd CMOSN W=1.8000e-06 L=1.8000e-07 AS=4.8600e-13 PS=4.1400e-06 AD=9.7200e-13 PD=4.6800e-06
Mn2 xn1 i1 gnd gnd CMOSN W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=4.8600e-13 PD=4.1400e-06
.ends nand2_x1
