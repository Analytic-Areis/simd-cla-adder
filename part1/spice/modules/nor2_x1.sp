* nor2_x1: 2-input NOR
* GENERATED from part1/cells/library.py. Do not edit by hand.
.subckt nor2_x1 i0 i1 y vdd gnd
Mp1 xp1 i0 vdd vdd CMOSP W=3.6000e-06 L=1.8000e-07 AS=1.9440e-12 PS=8.2800e-06 AD=9.7200e-13 PD=7.7400e-06
Mp2 y i1 xp1 vdd CMOSP W=3.6000e-06 L=1.8000e-07 AS=9.7200e-13 PS=7.7400e-06 AD=1.9440e-12 PD=8.2800e-06
Mn1 y i0 gnd gnd CMOSN W=9.0000e-07 L=1.8000e-07 AS=4.8600e-13 PS=2.8800e-06 AD=4.8600e-13 PD=2.8800e-06
Mn2 y i1 gnd gnd CMOSN W=9.0000e-07 L=1.8000e-07 AS=4.8600e-13 PS=2.8800e-06 AD=4.8600e-13 PD=2.8800e-06
.ends nor2_x1
