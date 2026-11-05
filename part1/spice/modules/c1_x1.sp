* c1_x1: C1 complex gate, stack 2
* GENERATED from part1/cells/library.py. Do not edit by hand.
.subckt c1_x1 g0b t0b c0b c1 vdd gnd
Mp1 c1 g0b vdd vdd CMOSP W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=9.7200e-13 PD=4.6800e-06
Mp2 xp1 t0b vdd vdd CMOSP W=3.6000e-06 L=1.8000e-07 AS=1.9440e-12 PS=8.2800e-06 AD=9.7200e-13 PD=7.7400e-06
Mp3 c1 c0b xp1 vdd CMOSP W=3.6000e-06 L=1.8000e-07 AS=9.7200e-13 PS=7.7400e-06 AD=1.9440e-12 PD=8.2800e-06
Mn1 c1 g0b xn1 gnd CMOSN W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=9.7200e-13 PD=4.6800e-06
Mn2 xn1 t0b gnd gnd CMOSN W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=9.7200e-13 PD=4.6800e-06
Mn3 xn1 c0b gnd gnd CMOSN W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=9.7200e-13 PD=4.6800e-06
.ends c1_x1
