* inv_x1: inverter
* GENERATED from part1/cells/library.py. Do not edit by hand.
.subckt inv_x1 a y vdd gnd
Mp1 y a vdd vdd CMOSP W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=9.7200e-13 PD=4.6800e-06
Mn1 y a gnd gnd CMOSN W=9.0000e-07 L=1.8000e-07 AS=4.8600e-13 PS=2.8800e-06 AD=4.8600e-13 PD=2.8800e-06
.ends inv_x1
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
* c2_x1: C2 complex gate, stack 3
* GENERATED from part1/cells/library.py. Do not edit by hand.
.subckt c2_x1 g0b t0b g1b t1b c0b c2 vdd gnd
Mp1 c2 g1b vdd vdd CMOSP W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=9.7200e-13 PD=4.6800e-06
Mp2 xp1 t1b vdd vdd CMOSP W=5.4000e-06 L=1.8000e-07 AS=2.9160e-12 PS=1.1880e-05 AD=2.9160e-12 PD=1.1880e-05
Mp3 c2 g0b xp1 vdd CMOSP W=3.6000e-06 L=1.8000e-07 AS=1.9440e-12 PS=8.2800e-06 AD=1.9440e-12 PD=8.2800e-06
Mp4 xp2 t0b xp1 vdd CMOSP W=5.4000e-06 L=1.8000e-07 AS=2.9160e-12 PS=1.1880e-05 AD=1.4580e-12 PD=1.1340e-05
Mp5 c2 c0b xp2 vdd CMOSP W=5.4000e-06 L=1.8000e-07 AS=1.4580e-12 PS=1.1340e-05 AD=2.9160e-12 PD=1.1880e-05
Mn1 c2 g1b xn1 gnd CMOSN W=2.7000e-06 L=1.8000e-07 AS=1.4580e-12 PS=6.4800e-06 AD=1.4580e-12 PD=6.4800e-06
Mn2 xn1 t1b gnd gnd CMOSN W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=9.7200e-13 PD=4.6800e-06
Mn3 xn1 g0b xn2 gnd CMOSN W=2.7000e-06 L=1.8000e-07 AS=1.4580e-12 PS=6.4800e-06 AD=1.4580e-12 PD=6.4800e-06
Mn4 xn2 t0b gnd gnd CMOSN W=2.7000e-06 L=1.8000e-07 AS=1.4580e-12 PS=6.4800e-06 AD=1.4580e-12 PD=6.4800e-06
Mn5 xn2 c0b gnd gnd CMOSN W=2.7000e-06 L=1.8000e-07 AS=1.4580e-12 PS=6.4800e-06 AD=1.4580e-12 PD=6.4800e-06
.ends c2_x1
* c3_x1: C3 complex gate, stack 4
* GENERATED from part1/cells/library.py. Do not edit by hand.
.subckt c3_x1 g0b t0b g1b t1b g2b t2b c0b c3 vdd gnd
Mp1 c3 g2b vdd vdd CMOSP W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=9.7200e-13 PD=4.6800e-06
Mp2 xp1 t2b vdd vdd CMOSP W=7.2000e-06 L=1.8000e-07 AS=3.8880e-12 PS=1.5480e-05 AD=3.8880e-12 PD=1.5480e-05
Mp3 c3 g1b xp1 vdd CMOSP W=3.6000e-06 L=1.8000e-07 AS=1.9440e-12 PS=8.2800e-06 AD=1.9440e-12 PD=8.2800e-06
Mp4 xp2 t1b xp1 vdd CMOSP W=7.2000e-06 L=1.8000e-07 AS=3.8880e-12 PS=1.5480e-05 AD=3.8880e-12 PD=1.5480e-05
Mp5 c3 g0b xp2 vdd CMOSP W=5.4000e-06 L=1.8000e-07 AS=2.9160e-12 PS=1.1880e-05 AD=2.9160e-12 PD=1.1880e-05
Mp6 xp3 t0b xp2 vdd CMOSP W=7.2000e-06 L=1.8000e-07 AS=3.8880e-12 PS=1.5480e-05 AD=1.9440e-12 PD=1.4940e-05
Mp7 c3 c0b xp3 vdd CMOSP W=7.2000e-06 L=1.8000e-07 AS=1.9440e-12 PS=1.4940e-05 AD=3.8880e-12 PD=1.5480e-05
Mn1 c3 g2b xn1 gnd CMOSN W=3.6000e-06 L=1.8000e-07 AS=1.9440e-12 PS=8.2800e-06 AD=1.9440e-12 PD=8.2800e-06
Mn2 xn1 t2b gnd gnd CMOSN W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=9.7200e-13 PD=4.6800e-06
Mn3 xn1 g1b xn2 gnd CMOSN W=3.6000e-06 L=1.8000e-07 AS=1.9440e-12 PS=8.2800e-06 AD=1.9440e-12 PD=8.2800e-06
Mn4 xn2 t1b gnd gnd CMOSN W=2.7000e-06 L=1.8000e-07 AS=1.4580e-12 PS=6.4800e-06 AD=1.4580e-12 PD=6.4800e-06
Mn5 xn2 g0b xn3 gnd CMOSN W=3.6000e-06 L=1.8000e-07 AS=1.9440e-12 PS=8.2800e-06 AD=1.9440e-12 PD=8.2800e-06
Mn6 xn3 t0b gnd gnd CMOSN W=3.6000e-06 L=1.8000e-07 AS=1.9440e-12 PS=8.2800e-06 AD=1.9440e-12 PD=8.2800e-06
Mn7 xn3 c0b gnd gnd CMOSN W=3.6000e-06 L=1.8000e-07 AS=1.9440e-12 PS=8.2800e-06 AD=1.9440e-12 PD=8.2800e-06
.ends c3_x1
* c4b_mirror_x1: C4-bar mirror gate, stack 3
* GENERATED from part1/cells/library.py. Do not edit by hand.
.subckt c4b_mirror_x1 a3 b3 a2 b2 c2 c4b vdd gnd
Mp1 xp1 b3 vdd vdd CMOSP W=3.6000e-06 L=1.8000e-07 AS=1.9440e-12 PS=8.2800e-06 AD=9.7200e-13 PD=7.7400e-06
Mp2 c4b a3 xp1 vdd CMOSP W=3.6000e-06 L=1.8000e-07 AS=9.7200e-13 PS=7.7400e-06 AD=1.9440e-12 PD=8.2800e-06
Mp3 xp2 a3 vdd vdd CMOSP W=5.4000e-06 L=1.8000e-07 AS=2.9160e-12 PS=1.1880e-05 AD=2.9160e-12 PD=1.1880e-05
Mp4 xp2 b3 vdd vdd CMOSP W=5.4000e-06 L=1.8000e-07 AS=2.9160e-12 PS=1.1880e-05 AD=2.9160e-12 PD=1.1880e-05
Mp5 xp3 b2 xp2 vdd CMOSP W=5.4000e-06 L=1.8000e-07 AS=2.9160e-12 PS=1.1880e-05 AD=1.4580e-12 PD=1.1340e-05
Mp6 c4b a2 xp3 vdd CMOSP W=5.4000e-06 L=1.8000e-07 AS=1.4580e-12 PS=1.1340e-05 AD=2.9160e-12 PD=1.1880e-05
Mp7 xp4 a2 xp2 vdd CMOSP W=5.4000e-06 L=1.8000e-07 AS=2.9160e-12 PS=1.1880e-05 AD=2.9160e-12 PD=1.1880e-05
Mp8 xp4 b2 xp2 vdd CMOSP W=5.4000e-06 L=1.8000e-07 AS=2.9160e-12 PS=1.1880e-05 AD=2.9160e-12 PD=1.1880e-05
Mp9 c4b c2 xp4 vdd CMOSP W=5.4000e-06 L=1.8000e-07 AS=2.9160e-12 PS=1.1880e-05 AD=2.9160e-12 PD=1.1880e-05
Mn1 c4b a3 xn1 gnd CMOSN W=1.8000e-06 L=1.8000e-07 AS=4.8600e-13 PS=4.1400e-06 AD=9.7200e-13 PD=4.6800e-06
Mn2 xn1 b3 gnd gnd CMOSN W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=4.8600e-13 PD=4.1400e-06
Mn3 c4b a2 xn3 gnd CMOSN W=2.7000e-06 L=1.8000e-07 AS=7.2900e-13 PS=5.9400e-06 AD=1.4580e-12 PD=6.4800e-06
Mn4 xn3 b2 xn2 gnd CMOSN W=2.7000e-06 L=1.8000e-07 AS=1.4580e-12 PS=6.4800e-06 AD=7.2900e-13 PD=5.9400e-06
Mn5 c4b c2 xn4 gnd CMOSN W=2.7000e-06 L=1.8000e-07 AS=1.4580e-12 PS=6.4800e-06 AD=1.4580e-12 PD=6.4800e-06
Mn6 xn4 a2 xn2 gnd CMOSN W=2.7000e-06 L=1.8000e-07 AS=1.4580e-12 PS=6.4800e-06 AD=1.4580e-12 PD=6.4800e-06
Mn7 xn4 b2 xn2 gnd CMOSN W=2.7000e-06 L=1.8000e-07 AS=1.4580e-12 PS=6.4800e-06 AD=1.4580e-12 PD=6.4800e-06
Mn8 xn2 a3 gnd gnd CMOSN W=2.7000e-06 L=1.8000e-07 AS=1.4580e-12 PS=6.4800e-06 AD=1.4580e-12 PD=6.4800e-06
Mn9 xn2 b3 gnd gnd CMOSN W=2.7000e-06 L=1.8000e-07 AS=1.4580e-12 PS=6.4800e-06 AD=1.4580e-12 PD=6.4800e-06
.ends c4b_mirror_x1
* carry_r_x1: candidate R carry generator
* GENERATED from part1/cells/library.py. Do not edit by hand.
.subckt carry_r_x1 g0b t0b g1b t1b g2b t2b c0 a2 b2 a3 b3 c1 c2 c3 c4 vdd gnd
Xinvc0 c0 c0b vdd gnd inv_x1
Xc1 g0b t0b c0b c1 vdd gnd c1_x1
Xc2 g0b t0b g1b t1b c0b c2 vdd gnd c2_x1
Xc3 g0b t0b g1b t1b g2b t2b c0b c3 vdd gnd c3_x1
Xc4m a3 b3 a2 b2 c2 c4b vdd gnd c4b_mirror_x1
Xinvc4 c4b c4 vdd gnd inv_x1
.ends carry_r_x1
