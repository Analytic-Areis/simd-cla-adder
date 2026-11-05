* xor_aoi22_x1: dual-rail XOR, AOI22 with c-bar inverter
* GENERATED from part1/cells/library.py. Do not edit by hand.
.subckt xor_aoi22_x1 p pb c s vdd gnd
Ms0p1 cb c vdd vdd CMOSP W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=9.7200e-13 PD=4.6800e-06
Ms0n1 cb c gnd gnd CMOSN W=9.0000e-07 L=1.8000e-07 AS=4.8600e-13 PS=2.8800e-06 AD=4.8600e-13 PD=2.8800e-06
Ms1p1 s1xp1 p vdd vdd CMOSP W=3.6000e-06 L=1.8000e-07 AS=1.9440e-12 PS=8.2800e-06 AD=1.9440e-12 PD=8.2800e-06
Ms1p2 s1xp1 c vdd vdd CMOSP W=3.6000e-06 L=1.8000e-07 AS=1.9440e-12 PS=8.2800e-06 AD=1.9440e-12 PD=8.2800e-06
Ms1p3 s pb s1xp1 vdd CMOSP W=3.6000e-06 L=1.8000e-07 AS=1.9440e-12 PS=8.2800e-06 AD=1.9440e-12 PD=8.2800e-06
Ms1p4 s cb s1xp1 vdd CMOSP W=3.6000e-06 L=1.8000e-07 AS=1.9440e-12 PS=8.2800e-06 AD=1.9440e-12 PD=8.2800e-06
Ms1n1 s p s1xn1 gnd CMOSN W=1.8000e-06 L=1.8000e-07 AS=4.8600e-13 PS=4.1400e-06 AD=9.7200e-13 PD=4.6800e-06
Ms1n2 s1xn1 c gnd gnd CMOSN W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=4.8600e-13 PD=4.1400e-06
Ms1n3 s pb s1xn2 gnd CMOSN W=1.8000e-06 L=1.8000e-07 AS=4.8600e-13 PS=4.1400e-06 AD=9.7200e-13 PD=4.6800e-06
Ms1n4 s1xn2 cb gnd gnd CMOSN W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=4.8600e-13 PD=4.1400e-06
.ends xor_aoi22_x1
* sum_xor_aoi22_x1: 4-bit sum block using xor_aoi22
* GENERATED from part1/cells/library.py. Do not edit by hand.
.subckt sum_xor_aoi22_x1 p0 p1 p2 p3 p0b p1b p2b p3b c0 c1 c2 c3 s0 s1 s2 s3 vdd gnd
Xsum0 p0 p0b c0 s0 vdd gnd xor_aoi22_x1
Xsum1 p1 p1b c1 s1 vdd gnd xor_aoi22_x1
Xsum2 p2 p2b c2 s2 vdd gnd xor_aoi22_x1
Xsum3 p3 p3b c3 s3 vdd gnd xor_aoi22_x1
.ends sum_xor_aoi22_x1
