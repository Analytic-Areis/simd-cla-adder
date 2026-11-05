* nand2_x1: 2-input NAND
* GENERATED from part1/cells/library.py. Do not edit by hand.
.subckt nand2_x1 i0 i1 y vdd gnd
Mp1 y i0 vdd vdd CMOSP W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=9.7200e-13 PD=4.6800e-06
Mp2 y i1 vdd vdd CMOSP W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=9.7200e-13 PD=4.6800e-06
Mn1 y i0 xn1 gnd CMOSN W=1.8000e-06 L=1.8000e-07 AS=4.8600e-13 PS=4.1400e-06 AD=9.7200e-13 PD=4.6800e-06
Mn2 xn1 i1 gnd gnd CMOSN W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=4.8600e-13 PD=4.1400e-06
.ends nand2_x1
* nor2_x1: 2-input NOR
* GENERATED from part1/cells/library.py. Do not edit by hand.
.subckt nor2_x1 i0 i1 y vdd gnd
Mp1 xp1 i0 vdd vdd CMOSP W=3.6000e-06 L=1.8000e-07 AS=1.9440e-12 PS=8.2800e-06 AD=9.7200e-13 PD=7.7400e-06
Mp2 y i1 xp1 vdd CMOSP W=3.6000e-06 L=1.8000e-07 AS=9.7200e-13 PS=7.7400e-06 AD=1.9440e-12 PD=8.2800e-06
Mn1 y i0 gnd gnd CMOSN W=9.0000e-07 L=1.8000e-07 AS=4.8600e-13 PS=2.8800e-06 AD=4.8600e-13 PD=2.8800e-06
Mn2 y i1 gnd gnd CMOSN W=9.0000e-07 L=1.8000e-07 AS=4.8600e-13 PS=2.8800e-06 AD=4.8600e-13 PD=2.8800e-06
.ends nor2_x1
* aoi21_x1: NOT(a b + c)
* GENERATED from part1/cells/library.py. Do not edit by hand.
.subckt aoi21_x1 a b c y vdd gnd
Mp1 xp1 a vdd vdd CMOSP W=3.6000e-06 L=1.8000e-07 AS=1.9440e-12 PS=8.2800e-06 AD=1.9440e-12 PD=8.2800e-06
Mp2 xp1 b vdd vdd CMOSP W=3.6000e-06 L=1.8000e-07 AS=1.9440e-12 PS=8.2800e-06 AD=1.9440e-12 PD=8.2800e-06
Mp3 y c xp1 vdd CMOSP W=3.6000e-06 L=1.8000e-07 AS=1.9440e-12 PS=8.2800e-06 AD=1.9440e-12 PD=8.2800e-06
Mn1 y a xn1 gnd CMOSN W=1.8000e-06 L=1.8000e-07 AS=4.8600e-13 PS=4.1400e-06 AD=9.7200e-13 PD=4.6800e-06
Mn2 xn1 b gnd gnd CMOSN W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=4.8600e-13 PD=4.1400e-06
Mn3 y c gnd gnd CMOSN W=9.0000e-07 L=1.8000e-07 AS=4.8600e-13 PS=2.8800e-06 AD=4.8600e-13 PD=2.8800e-06
.ends aoi21_x1
* oai21_x1: NOT((a + b) c)
* GENERATED from part1/cells/library.py. Do not edit by hand.
.subckt oai21_x1 a b c y vdd gnd
Mp1 xp1 a vdd vdd CMOSP W=3.6000e-06 L=1.8000e-07 AS=1.9440e-12 PS=8.2800e-06 AD=9.7200e-13 PD=7.7400e-06
Mp2 y b xp1 vdd CMOSP W=3.6000e-06 L=1.8000e-07 AS=9.7200e-13 PS=7.7400e-06 AD=1.9440e-12 PD=8.2800e-06
Mp3 y c vdd vdd CMOSP W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=9.7200e-13 PD=4.6800e-06
Mn1 y a xn1 gnd CMOSN W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=9.7200e-13 PD=4.6800e-06
Mn2 y b xn1 gnd CMOSN W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=9.7200e-13 PD=4.6800e-06
Mn3 xn1 c gnd gnd CMOSN W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=9.7200e-13 PD=4.6800e-06
.ends oai21_x1
* pg_bit_x1: P/G bit: NAND2, NOR2, compound AOI21 and OAI21
* GENERATED from part1/cells/library.py. Do not edit by hand.
.subckt pg_bit_x1 a b gb tb p pb vdd gnd
Xnand a b gb vdd gnd nand2_x1
Xnor a b tb vdd gnd nor2_x1
Xaoi a b tb p vdd gnd aoi21_x1
Xoai a b gb pb vdd gnd oai21_x1
.ends pg_bit_x1
