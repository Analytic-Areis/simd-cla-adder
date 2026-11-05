* xor_static12_x1: static XOR, AOI22 with two inverters
* GENERATED from part1/cells/library.py. Do not edit by hand.
.subckt xor_static12_x1 p c s vdd gnd
Ms0p1 pb p vdd vdd CMOSP W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=9.7200e-13 PD=4.6800e-06
Ms0n1 pb p gnd gnd CMOSN W=9.0000e-07 L=1.8000e-07 AS=4.8600e-13 PS=2.8800e-06 AD=4.8600e-13 PD=2.8800e-06
Ms1p1 cb c vdd vdd CMOSP W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=9.7200e-13 PD=4.6800e-06
Ms1n1 cb c gnd gnd CMOSN W=9.0000e-07 L=1.8000e-07 AS=4.8600e-13 PS=2.8800e-06 AD=4.8600e-13 PD=2.8800e-06
Ms2p1 s2xp1 p vdd vdd CMOSP W=3.6000e-06 L=1.8000e-07 AS=1.9440e-12 PS=8.2800e-06 AD=1.9440e-12 PD=8.2800e-06
Ms2p2 s2xp1 c vdd vdd CMOSP W=3.6000e-06 L=1.8000e-07 AS=1.9440e-12 PS=8.2800e-06 AD=1.9440e-12 PD=8.2800e-06
Ms2p3 s pb s2xp1 vdd CMOSP W=3.6000e-06 L=1.8000e-07 AS=1.9440e-12 PS=8.2800e-06 AD=1.9440e-12 PD=8.2800e-06
Ms2p4 s cb s2xp1 vdd CMOSP W=3.6000e-06 L=1.8000e-07 AS=1.9440e-12 PS=8.2800e-06 AD=1.9440e-12 PD=8.2800e-06
Ms2n1 s p s2xn1 gnd CMOSN W=1.8000e-06 L=1.8000e-07 AS=4.8600e-13 PS=4.1400e-06 AD=9.7200e-13 PD=4.6800e-06
Ms2n2 s2xn1 c gnd gnd CMOSN W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=4.8600e-13 PD=4.1400e-06
Ms2n3 s pb s2xn2 gnd CMOSN W=1.8000e-06 L=1.8000e-07 AS=4.8600e-13 PS=4.1400e-06 AD=9.7200e-13 PD=4.6800e-06
Ms2n4 s2xn2 cb gnd gnd CMOSN W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=4.8600e-13 PD=4.1400e-06
.ends xor_static12_x1
* sum_xor_static12_x1: 4-bit sum block using xor_static12
* GENERATED from part1/cells/library.py. Do not edit by hand.
.subckt sum_xor_static12_x1 p0 p1 p2 p3 c0 c1 c2 c3 s0 s1 s2 s3 vdd gnd
Xsum0 p0 c0 s0 vdd gnd xor_static12_x1
Xsum1 p1 c1 s1 vdd gnd xor_static12_x1
Xsum2 p2 c2 s2 vdd gnd xor_static12_x1
Xsum3 p3 c3 s3 vdd gnd xor_static12_x1
.ends sum_xor_static12_x1
