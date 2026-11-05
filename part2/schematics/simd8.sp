* nand2_x1p25: 2-input NAND
* GENERATED from part1/cells/library.py. Do not edit by hand.
.subckt nand2_x1p25 i0 i1 y vdd gnd
Mp1 y i0 vdd vdd CMOSP W=2.2500e-06 L=1.8000e-07 AS=1.2150e-12 PS=5.5800e-06 AD=1.2150e-12 PD=5.5800e-06
Mp2 y i1 vdd vdd CMOSP W=2.2500e-06 L=1.8000e-07 AS=1.2150e-12 PS=5.5800e-06 AD=1.2150e-12 PD=5.5800e-06
Mn1 y i0 xn1 gnd CMOSN W=2.2500e-06 L=1.8000e-07 AS=6.0750e-13 PS=5.0400e-06 AD=1.2150e-12 PD=5.5800e-06
Mn2 xn1 i1 gnd gnd CMOSN W=2.2500e-06 L=1.8000e-07 AS=1.2150e-12 PS=5.5800e-06 AD=6.0750e-13 PD=5.0400e-06
.ends nand2_x1p25
* nor2_x1p56: 2-input NOR
* GENERATED from part1/cells/library.py. Do not edit by hand.
.subckt nor2_x1p56 i0 i1 y vdd gnd
Mp1 xp1 i0 vdd vdd CMOSP W=5.5800e-06 L=1.8000e-07 AS=3.0132e-12 PS=1.2240e-05 AD=1.5066e-12 PD=1.1700e-05
Mp2 y i1 xp1 vdd CMOSP W=5.5800e-06 L=1.8000e-07 AS=1.5066e-12 PS=1.1700e-05 AD=3.0132e-12 PD=1.2240e-05
Mn1 y i0 gnd gnd CMOSN W=1.4400e-06 L=1.8000e-07 AS=7.7760e-13 PS=3.9600e-06 AD=7.7760e-13 PD=3.9600e-06
Mn2 y i1 gnd gnd CMOSN W=1.4400e-06 L=1.8000e-07 AS=7.7760e-13 PS=3.9600e-06 AD=7.7760e-13 PD=3.9600e-06
.ends nor2_x1p56
* aoi21_x0p41: NOT(a b + c)
* GENERATED from part1/cells/library.py. Do not edit by hand.
.subckt aoi21_x0p41 a b c y vdd gnd
Mp1 xp1 a vdd vdd CMOSP W=1.4400e-06 L=1.8000e-07 AS=7.7760e-13 PS=3.9600e-06 AD=7.7760e-13 PD=3.9600e-06
Mp2 xp1 b vdd vdd CMOSP W=1.4400e-06 L=1.8000e-07 AS=7.7760e-13 PS=3.9600e-06 AD=7.7760e-13 PD=3.9600e-06
Mp3 y c xp1 vdd CMOSP W=1.4400e-06 L=1.8000e-07 AS=7.7760e-13 PS=3.9600e-06 AD=7.7760e-13 PD=3.9600e-06
Mn1 y a xn1 gnd CMOSN W=7.2000e-07 L=1.8000e-07 AS=1.9440e-13 PS=1.9800e-06 AD=3.8880e-13 PD=2.5200e-06
Mn2 xn1 b gnd gnd CMOSN W=7.2000e-07 L=1.8000e-07 AS=3.8880e-13 PS=2.5200e-06 AD=1.9440e-13 PD=1.9800e-06
Mn3 y c gnd gnd CMOSN W=3.6000e-07 L=1.8000e-07 AS=1.9440e-13 PS=1.8000e-06 AD=1.9440e-13 PD=1.8000e-06
.ends aoi21_x0p41
* oai21_x0p41: NOT((a + b) c)
* GENERATED from part1/cells/library.py. Do not edit by hand.
.subckt oai21_x0p41 a b c y vdd gnd
Mp1 xp1 a vdd vdd CMOSP W=1.4400e-06 L=1.8000e-07 AS=7.7760e-13 PS=3.9600e-06 AD=3.8880e-13 PD=3.4200e-06
Mp2 y b xp1 vdd CMOSP W=1.4400e-06 L=1.8000e-07 AS=3.8880e-13 PS=3.4200e-06 AD=7.7760e-13 PD=3.9600e-06
Mp3 y c vdd vdd CMOSP W=7.2000e-07 L=1.8000e-07 AS=3.8880e-13 PS=2.5200e-06 AD=3.8880e-13 PD=2.5200e-06
Mn1 y a xn1 gnd CMOSN W=7.2000e-07 L=1.8000e-07 AS=3.8880e-13 PS=2.5200e-06 AD=3.8880e-13 PD=2.5200e-06
Mn2 y b xn1 gnd CMOSN W=7.2000e-07 L=1.8000e-07 AS=3.8880e-13 PS=2.5200e-06 AD=3.8880e-13 PD=2.5200e-06
Mn3 xn1 c gnd gnd CMOSN W=7.2000e-07 L=1.8000e-07 AS=3.8880e-13 PS=2.5200e-06 AD=3.8880e-13 PD=2.5200e-06
.ends oai21_x0p41
* nor2_x1p95: 2-input NOR
* GENERATED from part1/cells/library.py. Do not edit by hand.
.subckt nor2_x1p95 i0 i1 y vdd gnd
Mp1 xp1 i0 vdd vdd CMOSP W=7.0200e-06 L=1.8000e-07 AS=3.7908e-12 PS=1.5120e-05 AD=1.8954e-12 PD=1.4580e-05
Mp2 y i1 xp1 vdd CMOSP W=7.0200e-06 L=1.8000e-07 AS=1.8954e-12 PS=1.4580e-05 AD=3.7908e-12 PD=1.5120e-05
Mn1 y i0 gnd gnd CMOSN W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=9.7200e-13 PD=4.6800e-06
Mn2 y i1 gnd gnd CMOSN W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=9.7200e-13 PD=4.6800e-06
.ends nor2_x1p95
* nor2_x1p25: 2-input NOR
* GENERATED from part1/cells/library.py. Do not edit by hand.
.subckt nor2_x1p25 i0 i1 y vdd gnd
Mp1 xp1 i0 vdd vdd CMOSP W=4.5000e-06 L=1.8000e-07 AS=2.4300e-12 PS=1.0080e-05 AD=1.2150e-12 PD=9.5400e-06
Mp2 y i1 xp1 vdd CMOSP W=4.5000e-06 L=1.8000e-07 AS=1.2150e-12 PS=9.5400e-06 AD=2.4300e-12 PD=1.0080e-05
Mn1 y i0 gnd gnd CMOSN W=1.0800e-06 L=1.8000e-07 AS=5.8320e-13 PS=3.2400e-06 AD=5.8320e-13 PD=3.2400e-06
Mn2 y i1 gnd gnd CMOSN W=1.0800e-06 L=1.8000e-07 AS=5.8320e-13 PS=3.2400e-06 AD=5.8320e-13 PD=3.2400e-06
.ends nor2_x1p25
* aoi21_x0p8: NOT(a b + c)
* GENERATED from part1/cells/library.py. Do not edit by hand.
.subckt aoi21_x0p8 a b c y vdd gnd
Mp1 xp1 a vdd vdd CMOSP W=2.8800e-06 L=1.8000e-07 AS=1.5552e-12 PS=6.8400e-06 AD=1.5552e-12 PD=6.8400e-06
Mp2 xp1 b vdd vdd CMOSP W=2.8800e-06 L=1.8000e-07 AS=1.5552e-12 PS=6.8400e-06 AD=1.5552e-12 PD=6.8400e-06
Mp3 y c xp1 vdd CMOSP W=2.8800e-06 L=1.8000e-07 AS=1.5552e-12 PS=6.8400e-06 AD=1.5552e-12 PD=6.8400e-06
Mn1 y a xn1 gnd CMOSN W=1.4400e-06 L=1.8000e-07 AS=3.8880e-13 PS=3.4200e-06 AD=7.7760e-13 PD=3.9600e-06
Mn2 xn1 b gnd gnd CMOSN W=1.4400e-06 L=1.8000e-07 AS=7.7760e-13 PS=3.9600e-06 AD=3.8880e-13 PD=3.4200e-06
Mn3 y c gnd gnd CMOSN W=7.2000e-07 L=1.8000e-07 AS=3.8880e-13 PS=2.5200e-06 AD=3.8880e-13 PD=2.5200e-06
.ends aoi21_x0p8
* oai21_x0p8: NOT((a + b) c)
* GENERATED from part1/cells/library.py. Do not edit by hand.
.subckt oai21_x0p8 a b c y vdd gnd
Mp1 xp1 a vdd vdd CMOSP W=2.8800e-06 L=1.8000e-07 AS=1.5552e-12 PS=6.8400e-06 AD=7.7760e-13 PD=6.3000e-06
Mp2 y b xp1 vdd CMOSP W=2.8800e-06 L=1.8000e-07 AS=7.7760e-13 PS=6.3000e-06 AD=1.5552e-12 PD=6.8400e-06
Mp3 y c vdd vdd CMOSP W=1.4400e-06 L=1.8000e-07 AS=7.7760e-13 PS=3.9600e-06 AD=7.7760e-13 PD=3.9600e-06
Mn1 y a xn1 gnd CMOSN W=1.4400e-06 L=1.8000e-07 AS=7.7760e-13 PS=3.9600e-06 AD=7.7760e-13 PD=3.9600e-06
Mn2 y b xn1 gnd CMOSN W=1.4400e-06 L=1.8000e-07 AS=7.7760e-13 PS=3.9600e-06 AD=7.7760e-13 PD=3.9600e-06
Mn3 xn1 c gnd gnd CMOSN W=1.4400e-06 L=1.8000e-07 AS=7.7760e-13 PS=3.9600e-06 AD=7.7760e-13 PD=3.9600e-06
.ends oai21_x0p8
* nand2_x1: 2-input NAND
* GENERATED from part1/cells/library.py. Do not edit by hand.
.subckt nand2_x1 i0 i1 y vdd gnd
Mp1 y i0 vdd vdd CMOSP W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=9.7200e-13 PD=4.6800e-06
Mp2 y i1 vdd vdd CMOSP W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=9.7200e-13 PD=4.6800e-06
Mn1 y i0 xn1 gnd CMOSN W=1.8000e-06 L=1.8000e-07 AS=4.8600e-13 PS=4.1400e-06 AD=9.7200e-13 PD=4.6800e-06
Mn2 xn1 i1 gnd gnd CMOSN W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=4.8600e-13 PD=4.1400e-06
.ends nand2_x1
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
* inv_x1: inverter
* GENERATED from part1/cells/library.py. Do not edit by hand.
.subckt inv_x1 a y vdd gnd
Mp1 y a vdd vdd CMOSP W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=9.7200e-13 PD=4.6800e-06
Mn1 y a gnd gnd CMOSN W=9.0000e-07 L=1.8000e-07 AS=4.8600e-13 PS=2.8800e-06 AD=4.8600e-13 PD=2.8800e-06
.ends inv_x1
* oai21_fn_x1p25: NOT((a + b) c)
* GENERATED from part1/cells/library.py. Do not edit by hand.
.subckt oai21_fn_x1p25 a b c y vdd gnd
Mp1 xp1 a vdd vdd CMOSP W=4.5000e-06 L=1.8000e-07 AS=2.4300e-12 PS=1.0080e-05 AD=1.2150e-12 PD=9.5400e-06
Mp2 y b xp1 vdd CMOSP W=4.5000e-06 L=1.8000e-07 AS=1.2150e-12 PS=9.5400e-06 AD=2.4300e-12 PD=1.0080e-05
Mp3 y c vdd vdd CMOSP W=2.2500e-06 L=1.8000e-07 AS=1.2150e-12 PS=5.5800e-06 AD=1.2150e-12 PD=5.5800e-06
Mn1 y c xn1 gnd CMOSN W=2.2500e-06 L=1.8000e-07 AS=1.2150e-12 PS=5.5800e-06 AD=1.2150e-12 PD=5.5800e-06
Mn2 xn1 a gnd gnd CMOSN W=2.2500e-06 L=1.8000e-07 AS=1.2150e-12 PS=5.5800e-06 AD=1.2150e-12 PD=5.5800e-06
Mn3 xn1 b gnd gnd CMOSN W=2.2500e-06 L=1.8000e-07 AS=1.2150e-12 PS=5.5800e-06 AD=1.2150e-12 PD=5.5800e-06
.ends oai21_fn_x1p25
* nor2_x0p8: 2-input NOR
* GENERATED from part1/cells/library.py. Do not edit by hand.
.subckt nor2_x0p8 i0 i1 y vdd gnd
Mp1 xp1 i0 vdd vdd CMOSP W=2.8800e-06 L=1.8000e-07 AS=1.5552e-12 PS=6.8400e-06 AD=7.7760e-13 PD=6.3000e-06
Mp2 y i1 xp1 vdd CMOSP W=2.8800e-06 L=1.8000e-07 AS=7.7760e-13 PS=6.3000e-06 AD=1.5552e-12 PD=6.8400e-06
Mn1 y i0 gnd gnd CMOSN W=7.2000e-07 L=1.8000e-07 AS=3.8880e-13 PS=2.5200e-06 AD=3.8880e-13 PD=2.5200e-06
Mn2 y i1 gnd gnd CMOSN W=7.2000e-07 L=1.8000e-07 AS=3.8880e-13 PS=2.5200e-06 AD=3.8880e-13 PD=2.5200e-06
.ends nor2_x0p8
* inv_x1p25: inverter
* GENERATED from part1/cells/library.py. Do not edit by hand.
.subckt inv_x1p25 a y vdd gnd
Mp1 y a vdd vdd CMOSP W=2.2500e-06 L=1.8000e-07 AS=1.2150e-12 PS=5.5800e-06 AD=1.2150e-12 PD=5.5800e-06
Mn1 y a gnd gnd CMOSN W=1.0800e-06 L=1.8000e-07 AS=5.8320e-13 PS=3.2400e-06 AD=5.8320e-13 PD=3.2400e-06
.ends inv_x1p25
* inv_x1p95: inverter
* GENERATED from part1/cells/library.py. Do not edit by hand.
.subckt inv_x1p95 a y vdd gnd
Mp1 y a vdd vdd CMOSP W=3.5100e-06 L=1.8000e-07 AS=1.8954e-12 PS=8.1000e-06 AD=1.8954e-12 PD=8.1000e-06
Mn1 y a gnd gnd CMOSN W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=9.7200e-13 PD=4.6800e-06
.ends inv_x1p95
* aoi21_fnp_x0p41: NOT(a b + c)
* GENERATED from part1/cells/library.py. Do not edit by hand.
.subckt aoi21_fnp_x0p41 a b c y vdd gnd
Mp1 xp1 c vdd vdd CMOSP W=1.4400e-06 L=1.8000e-07 AS=7.7760e-13 PS=3.9600e-06 AD=7.7760e-13 PD=3.9600e-06
Mp2 y a xp1 vdd CMOSP W=1.4400e-06 L=1.8000e-07 AS=7.7760e-13 PS=3.9600e-06 AD=7.7760e-13 PD=3.9600e-06
Mp3 y b xp1 vdd CMOSP W=1.4400e-06 L=1.8000e-07 AS=7.7760e-13 PS=3.9600e-06 AD=7.7760e-13 PD=3.9600e-06
Mn1 y b xn1 gnd CMOSN W=7.2000e-07 L=1.8000e-07 AS=1.9440e-13 PS=1.9800e-06 AD=3.8880e-13 PD=2.5200e-06
Mn2 xn1 a gnd gnd CMOSN W=7.2000e-07 L=1.8000e-07 AS=3.8880e-13 PS=2.5200e-06 AD=1.9440e-13 PD=1.9800e-06
Mn3 y c gnd gnd CMOSN W=3.6000e-07 L=1.8000e-07 AS=1.9440e-13 PS=1.8000e-06 AD=1.9440e-13 PD=1.8000e-06
.ends aoi21_fnp_x0p41
* nand2_x0p41: 2-input NAND
* GENERATED from part1/cells/library.py. Do not edit by hand.
.subckt nand2_x0p41 i0 i1 y vdd gnd
Mp1 y i0 vdd vdd CMOSP W=7.2000e-07 L=1.8000e-07 AS=3.8880e-13 PS=2.5200e-06 AD=3.8880e-13 PD=2.5200e-06
Mp2 y i1 vdd vdd CMOSP W=7.2000e-07 L=1.8000e-07 AS=3.8880e-13 PS=2.5200e-06 AD=3.8880e-13 PD=2.5200e-06
Mn1 y i0 xn1 gnd CMOSN W=7.2000e-07 L=1.8000e-07 AS=1.9440e-13 PS=1.9800e-06 AD=3.8880e-13 PD=2.5200e-06
Mn2 xn1 i1 gnd gnd CMOSN W=7.2000e-07 L=1.8000e-07 AS=3.8880e-13 PS=2.5200e-06 AD=1.9440e-13 PD=1.9800e-06
.ends nand2_x0p41
* aoi21_fnp_x1: NOT(a b + c)
* GENERATED from part1/cells/library.py. Do not edit by hand.
.subckt aoi21_fnp_x1 a b c y vdd gnd
Mp1 xp1 c vdd vdd CMOSP W=3.6000e-06 L=1.8000e-07 AS=1.9440e-12 PS=8.2800e-06 AD=1.9440e-12 PD=8.2800e-06
Mp2 y a xp1 vdd CMOSP W=3.6000e-06 L=1.8000e-07 AS=1.9440e-12 PS=8.2800e-06 AD=1.9440e-12 PD=8.2800e-06
Mp3 y b xp1 vdd CMOSP W=3.6000e-06 L=1.8000e-07 AS=1.9440e-12 PS=8.2800e-06 AD=1.9440e-12 PD=8.2800e-06
Mn1 y b xn1 gnd CMOSN W=1.8000e-06 L=1.8000e-07 AS=4.8600e-13 PS=4.1400e-06 AD=9.7200e-13 PD=4.6800e-06
Mn2 xn1 a gnd gnd CMOSN W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=4.8600e-13 PD=4.1400e-06
Mn3 y c gnd gnd CMOSN W=9.0000e-07 L=1.8000e-07 AS=4.8600e-13 PS=2.8800e-06 AD=4.8600e-13 PD=2.8800e-06
.ends aoi21_fnp_x1
* inv_x1p56: inverter
* GENERATED from part1/cells/library.py. Do not edit by hand.
.subckt inv_x1p56 a y vdd gnd
Mp1 y a vdd vdd CMOSP W=2.7900e-06 L=1.8000e-07 AS=1.5066e-12 PS=6.6600e-06 AD=1.5066e-12 PD=6.6600e-06
Mn1 y a gnd gnd CMOSN W=1.4400e-06 L=1.8000e-07 AS=7.7760e-13 PS=3.9600e-06 AD=7.7760e-13 PD=3.9600e-06
.ends inv_x1p56
* oai21_x0p51: NOT((a + b) c)
* GENERATED from part1/cells/library.py. Do not edit by hand.
.subckt oai21_x0p51 a b c y vdd gnd
Mp1 xp1 a vdd vdd CMOSP W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=4.8600e-13 PD=4.1400e-06
Mp2 y b xp1 vdd CMOSP W=1.8000e-06 L=1.8000e-07 AS=4.8600e-13 PS=4.1400e-06 AD=9.7200e-13 PD=4.6800e-06
Mp3 y c vdd vdd CMOSP W=9.0000e-07 L=1.8000e-07 AS=4.8600e-13 PS=2.8800e-06 AD=4.8600e-13 PD=2.8800e-06
Mn1 y a xn1 gnd CMOSN W=9.0000e-07 L=1.8000e-07 AS=4.8600e-13 PS=2.8800e-06 AD=4.8600e-13 PD=2.8800e-06
Mn2 y b xn1 gnd CMOSN W=9.0000e-07 L=1.8000e-07 AS=4.8600e-13 PS=2.8800e-06 AD=4.8600e-13 PD=2.8800e-06
Mn3 xn1 c gnd gnd CMOSN W=9.0000e-07 L=1.8000e-07 AS=4.8600e-13 PS=2.8800e-06 AD=4.8600e-13 PD=2.8800e-06
.ends oai21_x0p51
* oai21_fnp_x0p8: NOT((a + b) c)
* GENERATED from part1/cells/library.py. Do not edit by hand.
.subckt oai21_fnp_x0p8 a b c y vdd gnd
Mp1 xp1 b vdd vdd CMOSP W=2.8800e-06 L=1.8000e-07 AS=1.5552e-12 PS=6.8400e-06 AD=7.7760e-13 PD=6.3000e-06
Mp2 y a xp1 vdd CMOSP W=2.8800e-06 L=1.8000e-07 AS=7.7760e-13 PS=6.3000e-06 AD=1.5552e-12 PD=6.8400e-06
Mp3 y c vdd vdd CMOSP W=1.4400e-06 L=1.8000e-07 AS=7.7760e-13 PS=3.9600e-06 AD=7.7760e-13 PD=3.9600e-06
Mn1 y c xn1 gnd CMOSN W=1.4400e-06 L=1.8000e-07 AS=7.7760e-13 PS=3.9600e-06 AD=7.7760e-13 PD=3.9600e-06
Mn2 xn1 a gnd gnd CMOSN W=1.4400e-06 L=1.8000e-07 AS=7.7760e-13 PS=3.9600e-06 AD=7.7760e-13 PD=3.9600e-06
Mn3 xn1 b gnd gnd CMOSN W=1.4400e-06 L=1.8000e-07 AS=7.7760e-13 PS=3.9600e-06 AD=7.7760e-13 PD=3.9600e-06
.ends oai21_fnp_x0p8
* xor_aoi22_x1p25_0p51: dual-rail XOR, AOI22 with c-bar inverter
* GENERATED from part1/cells/library.py. Do not edit by hand.
.subckt xor_aoi22_x1p25_0p51 p pb c s vdd gnd
Ms0p1 cb c vdd vdd CMOSP W=9.0000e-07 L=1.8000e-07 AS=4.8600e-13 PS=2.8800e-06 AD=4.8600e-13 PD=2.8800e-06
Ms0n1 cb c gnd gnd CMOSN W=4.5000e-07 L=1.8000e-07 AS=2.4300e-13 PS=1.9800e-06 AD=2.4300e-13 PD=1.9800e-06
Ms1p1 s1xp1 p vdd vdd CMOSP W=4.5000e-06 L=1.8000e-07 AS=2.4300e-12 PS=1.0080e-05 AD=2.4300e-12 PD=1.0080e-05
Ms1p2 s1xp1 c vdd vdd CMOSP W=4.5000e-06 L=1.8000e-07 AS=2.4300e-12 PS=1.0080e-05 AD=2.4300e-12 PD=1.0080e-05
Ms1p3 s pb s1xp1 vdd CMOSP W=4.5000e-06 L=1.8000e-07 AS=2.4300e-12 PS=1.0080e-05 AD=2.4300e-12 PD=1.0080e-05
Ms1p4 s cb s1xp1 vdd CMOSP W=4.5000e-06 L=1.8000e-07 AS=2.4300e-12 PS=1.0080e-05 AD=2.4300e-12 PD=1.0080e-05
Ms1n1 s p s1xn1 gnd CMOSN W=2.2500e-06 L=1.8000e-07 AS=6.0750e-13 PS=5.0400e-06 AD=1.2150e-12 PD=5.5800e-06
Ms1n2 s1xn1 c gnd gnd CMOSN W=2.2500e-06 L=1.8000e-07 AS=1.2150e-12 PS=5.5800e-06 AD=6.0750e-13 PD=5.0400e-06
Ms1n3 s pb s1xn2 gnd CMOSN W=2.2500e-06 L=1.8000e-07 AS=6.0750e-13 PS=5.0400e-06 AD=1.2150e-12 PD=5.5800e-06
Ms1n4 s1xn2 cb gnd gnd CMOSN W=2.2500e-06 L=1.8000e-07 AS=1.2150e-12 PS=5.5800e-06 AD=6.0750e-13 PD=5.0400e-06
.ends xor_aoi22_x1p25_0p51
* xor_aoi22_x1_0p64: dual-rail XOR, AOI22 with c-bar inverter
* GENERATED from part1/cells/library.py. Do not edit by hand.
.subckt xor_aoi22_x1_0p64 p pb c s vdd gnd
Ms0p1 cb c vdd vdd CMOSP W=1.1700e-06 L=1.8000e-07 AS=6.3180e-13 PS=3.4200e-06 AD=6.3180e-13 PD=3.4200e-06
Ms0n1 cb c gnd gnd CMOSN W=5.4000e-07 L=1.8000e-07 AS=2.9160e-13 PS=2.1600e-06 AD=2.9160e-13 PD=2.1600e-06
Ms1p1 s1xp1 p vdd vdd CMOSP W=3.6000e-06 L=1.8000e-07 AS=1.9440e-12 PS=8.2800e-06 AD=1.9440e-12 PD=8.2800e-06
Ms1p2 s1xp1 c vdd vdd CMOSP W=3.6000e-06 L=1.8000e-07 AS=1.9440e-12 PS=8.2800e-06 AD=1.9440e-12 PD=8.2800e-06
Ms1p3 s pb s1xp1 vdd CMOSP W=3.6000e-06 L=1.8000e-07 AS=1.9440e-12 PS=8.2800e-06 AD=1.9440e-12 PD=8.2800e-06
Ms1p4 s cb s1xp1 vdd CMOSP W=3.6000e-06 L=1.8000e-07 AS=1.9440e-12 PS=8.2800e-06 AD=1.9440e-12 PD=8.2800e-06
Ms1n1 s p s1xn1 gnd CMOSN W=1.8000e-06 L=1.8000e-07 AS=4.8600e-13 PS=4.1400e-06 AD=9.7200e-13 PD=4.6800e-06
Ms1n2 s1xn1 c gnd gnd CMOSN W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=4.8600e-13 PD=4.1400e-06
Ms1n3 s pb s1xn2 gnd CMOSN W=1.8000e-06 L=1.8000e-07 AS=4.8600e-13 PS=4.1400e-06 AD=9.7200e-13 PD=4.6800e-06
Ms1n4 s1xn2 cb gnd gnd CMOSN W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=4.8600e-13 PD=4.1400e-06
.ends xor_aoi22_x1_0p64
* xor_aoi22_x0p8_1p25: dual-rail XOR, AOI22 with c-bar inverter
* GENERATED from part1/cells/library.py. Do not edit by hand.
.subckt xor_aoi22_x0p8_1p25 p pb c s vdd gnd
Ms0p1 cb c vdd vdd CMOSP W=2.2500e-06 L=1.8000e-07 AS=1.2150e-12 PS=5.5800e-06 AD=1.2150e-12 PD=5.5800e-06
Ms0n1 cb c gnd gnd CMOSN W=1.0800e-06 L=1.8000e-07 AS=5.8320e-13 PS=3.2400e-06 AD=5.8320e-13 PD=3.2400e-06
Ms1p1 s1xp1 p vdd vdd CMOSP W=2.8800e-06 L=1.8000e-07 AS=1.5552e-12 PS=6.8400e-06 AD=1.5552e-12 PD=6.8400e-06
Ms1p2 s1xp1 c vdd vdd CMOSP W=2.8800e-06 L=1.8000e-07 AS=1.5552e-12 PS=6.8400e-06 AD=1.5552e-12 PD=6.8400e-06
Ms1p3 s pb s1xp1 vdd CMOSP W=2.8800e-06 L=1.8000e-07 AS=1.5552e-12 PS=6.8400e-06 AD=1.5552e-12 PD=6.8400e-06
Ms1p4 s cb s1xp1 vdd CMOSP W=2.8800e-06 L=1.8000e-07 AS=1.5552e-12 PS=6.8400e-06 AD=1.5552e-12 PD=6.8400e-06
Ms1n1 s p s1xn1 gnd CMOSN W=1.4400e-06 L=1.8000e-07 AS=3.8880e-13 PS=3.4200e-06 AD=7.7760e-13 PD=3.9600e-06
Ms1n2 s1xn1 c gnd gnd CMOSN W=1.4400e-06 L=1.8000e-07 AS=7.7760e-13 PS=3.9600e-06 AD=3.8880e-13 PD=3.4200e-06
Ms1n3 s pb s1xn2 gnd CMOSN W=1.4400e-06 L=1.8000e-07 AS=3.8880e-13 PS=3.4200e-06 AD=7.7760e-13 PD=3.9600e-06
Ms1n4 s1xn2 cb gnd gnd CMOSN W=1.4400e-06 L=1.8000e-07 AS=7.7760e-13 PS=3.9600e-06 AD=3.8880e-13 PD=3.4200e-06
.ends xor_aoi22_x0p8_1p25
* xor_aoi22_x0p51_1: dual-rail XOR, AOI22 with c-bar inverter
* GENERATED from part1/cells/library.py. Do not edit by hand.
.subckt xor_aoi22_x0p51_1 p pb c s vdd gnd
Ms0p1 cb c vdd vdd CMOSP W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=9.7200e-13 PD=4.6800e-06
Ms0n1 cb c gnd gnd CMOSN W=9.0000e-07 L=1.8000e-07 AS=4.8600e-13 PS=2.8800e-06 AD=4.8600e-13 PD=2.8800e-06
Ms1p1 s1xp1 p vdd vdd CMOSP W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=9.7200e-13 PD=4.6800e-06
Ms1p2 s1xp1 c vdd vdd CMOSP W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=9.7200e-13 PD=4.6800e-06
Ms1p3 s pb s1xp1 vdd CMOSP W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=9.7200e-13 PD=4.6800e-06
Ms1p4 s cb s1xp1 vdd CMOSP W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=9.7200e-13 PD=4.6800e-06
Ms1n1 s p s1xn1 gnd CMOSN W=9.0000e-07 L=1.8000e-07 AS=2.4300e-13 PS=2.3400e-06 AD=4.8600e-13 PD=2.8800e-06
Ms1n2 s1xn1 c gnd gnd CMOSN W=9.0000e-07 L=1.8000e-07 AS=4.8600e-13 PS=2.8800e-06 AD=2.4300e-13 PD=2.3400e-06
Ms1n3 s pb s1xn2 gnd CMOSN W=9.0000e-07 L=1.8000e-07 AS=2.4300e-13 PS=2.3400e-06 AD=4.8600e-13 PD=2.8800e-06
Ms1n4 s1xn2 cb gnd gnd CMOSN W=9.0000e-07 L=1.8000e-07 AS=4.8600e-13 PS=2.8800e-06 AD=2.4300e-13 PD=2.3400e-06
.ends xor_aoi22_x0p51_1
* cla4_final: Candidate C4: valency-2 prefix, late C0
* GENERATED from part1/cells/library.py. Do not edit by hand.
.subckt cla4_final a0 a1 a2 a3 b0 b1 b2 b3 c0 s0 s1 s2 s3 c4 vdd gnd
Xnand0 a0 b0 g0b vdd gnd nand2_x1p25
Xnor0 a0 b0 t0b vdd gnd nor2_x1p56
Xaoi0 a0 b0 t0b p0 vdd gnd aoi21_x0p41
Xoai0 a0 b0 g0b p0b vdd gnd oai21_x0p41
Xnand1 a1 b1 g1b vdd gnd nand2_x1p25
Xnor1 a1 b1 t1b vdd gnd nor2_x1p95
Xaoi1 a1 b1 t1b p1 vdd gnd aoi21_x0p41
Xoai1 a1 b1 g1b p1b vdd gnd oai21_x0p41
Xnand2 a2 b2 g2b vdd gnd nand2_x1p25
Xnor2 a2 b2 t2b vdd gnd nor2_x1p25
Xaoi2 a2 b2 t2b p2 vdd gnd aoi21_x0p8
Xoai2 a2 b2 g2b p2b vdd gnd oai21_x0p8
Xnand3 a3 b3 g3b vdd gnd nand2_x1
Xnor3 a3 b3 t3b vdd gnd nor2_x1p25
Xaoi3 a3 b3 t3b p3 vdd gnd aoi21_x1
Xoai3 a3 b3 g3b p3b vdd gnd oai21_x1
Xinvc0 c0 c0b vdd gnd inv_x1
Xg10 t1b g0b g1b g1_0 vdd gnd oai21_fn_x1p25
Xt10 t1b t0b t1_0 vdd gnd nor2_x1p56
Xg32 t3b g2b g3b g3_2 vdd gnd oai21_x0p8
Xt32 t3b t2b t3_2 vdd gnd nor2_x0p8
Xig2 g2b g2 vdd gnd inv_x1p25
Xit2 t2b t2 vdd gnd inv_x1p95
Xg30 t3_2 g1_0 g3_2 g3_0b vdd gnd aoi21_fnp_x0p41
Xt30 t3_2 t1_0 t3_0b vdd gnd nand2_x0p41
Xg20 t2 g1_0 g2 g2_0b vdd gnd aoi21_fnp_x1
Xt20 t2 t1_0 t2_0b vdd gnd nand2_x1p25
Xig10 g1_0 g1_0b vdd gnd inv_x1
Xit10 t1_0 t1_0b vdd gnd inv_x1p56
Xc1 t0b c0b g0b c1 vdd gnd oai21_x0p51
Xc2 t1_0b c0b g1_0b c2 vdd gnd oai21_fn_x1p25
Xc3 t2_0b c0b g2_0b c3 vdd gnd oai21_fn_x1p25
Xc4g t3_0b c0b g3_0b c4 vdd gnd oai21_fnp_x0p8
Xx0 p0 p0b c0 s0 vdd gnd xor_aoi22_x1p25_0p51
Xx1 p1 p1b c1 s1 vdd gnd xor_aoi22_x1_0p64
Xx2 p2 p2b c2 s2 vdd gnd xor_aoi22_x0p8_1p25
Xx3 p3 p3b c3 s3 vdd gnd xor_aoi22_x0p51_1
.ends cla4_final
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
* simd8: SIMD-reconfigurable 8-bit adder: CLA0, carry-gating cell, CLA1
* GENERATED from part1/cells/library.py. Do not edit by hand.
.subckt simd8 a0 a1 a2 a3 a4 a5 a6 a7 b0 b1 b2 b3 b4 b5 b6 b7 c0 mode s0 s1 s2 s3 s4 s5 s6 s7 c8 c4lo vdd gnd
Xcla0 a0 a1 a2 a3 b0 b1 b2 b3 c0 s0 s1 s2 s3 c4lo vdd gnd cla4_final
Xgate c4lo mode cinh vdd gnd carry_gate_n1_i2
Xcla1 a4 a5 a6 a7 b4 b5 b6 b7 cinh s4 s5 s6 s7 c8 vdd gnd cla4_final
.ends simd8
