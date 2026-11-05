* xor_nand4_x1: four-NAND XOR baseline
* GENERATED from part1/cells/library.py. Do not edit by hand.
.subckt xor_nand4_x1 p c s vdd gnd
Ms0p1 n1 p vdd vdd CMOSP W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=9.7200e-13 PD=4.6800e-06
Ms0p2 n1 c vdd vdd CMOSP W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=9.7200e-13 PD=4.6800e-06
Ms0n1 n1 p s0xn1 gnd CMOSN W=1.8000e-06 L=1.8000e-07 AS=4.8600e-13 PS=4.1400e-06 AD=9.7200e-13 PD=4.6800e-06
Ms0n2 s0xn1 c gnd gnd CMOSN W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=4.8600e-13 PD=4.1400e-06
Ms1p1 n2 p vdd vdd CMOSP W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=9.7200e-13 PD=4.6800e-06
Ms1p2 n2 n1 vdd vdd CMOSP W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=9.7200e-13 PD=4.6800e-06
Ms1n1 n2 p s1xn1 gnd CMOSN W=1.8000e-06 L=1.8000e-07 AS=4.8600e-13 PS=4.1400e-06 AD=9.7200e-13 PD=4.6800e-06
Ms1n2 s1xn1 n1 gnd gnd CMOSN W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=4.8600e-13 PD=4.1400e-06
Ms2p1 n3 c vdd vdd CMOSP W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=9.7200e-13 PD=4.6800e-06
Ms2p2 n3 n1 vdd vdd CMOSP W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=9.7200e-13 PD=4.6800e-06
Ms2n1 n3 c s2xn1 gnd CMOSN W=1.8000e-06 L=1.8000e-07 AS=4.8600e-13 PS=4.1400e-06 AD=9.7200e-13 PD=4.6800e-06
Ms2n2 s2xn1 n1 gnd gnd CMOSN W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=4.8600e-13 PD=4.1400e-06
Ms3p1 s n2 vdd vdd CMOSP W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=9.7200e-13 PD=4.6800e-06
Ms3p2 s n3 vdd vdd CMOSP W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=9.7200e-13 PD=4.6800e-06
Ms3n1 s n2 s3xn1 gnd CMOSN W=1.8000e-06 L=1.8000e-07 AS=4.8600e-13 PS=4.1400e-06 AD=9.7200e-13 PD=4.6800e-06
Ms3n2 s3xn1 n3 gnd gnd CMOSN W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=4.8600e-13 PD=4.1400e-06
.ends xor_nand4_x1
* sum_xor_nand4_x1: 4-bit sum block using xor_nand4
* GENERATED from part1/cells/library.py. Do not edit by hand.
.subckt sum_xor_nand4_x1 p0 p1 p2 p3 c0 c1 c2 c3 s0 s1 s2 s3 vdd gnd
Xsum0 p0 c0 s0 vdd gnd xor_nand4_x1
Xsum1 p1 c1 s1 vdd gnd xor_nand4_x1
Xsum2 p2 c2 s2 vdd gnd xor_nand4_x1
Xsum3 p3 c3 s3 vdd gnd xor_nand4_x1
.ends sum_xor_nand4_x1
