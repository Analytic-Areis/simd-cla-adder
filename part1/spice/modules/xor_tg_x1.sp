* xor_tg_x1: transmission-gate mux XOR with output inverter
* GENERATED from part1/cells/library.py. Do not edit by hand.
.subckt xor_tg_x1 p pb c s vdd gnd
Ms0p1 cb c vdd vdd CMOSP W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=9.7200e-13 PD=4.6800e-06
Ms0n1 cb c gnd gnd CMOSN W=9.0000e-07 L=1.8000e-07 AS=4.8600e-13 PS=2.8800e-06 AD=4.8600e-13 PD=2.8800e-06
Ms1n p c m gnd CMOSN W=9.0000e-07 L=1.8000e-07 AS=4.8600e-13 PS=2.8800e-06 AD=4.8600e-13 PD=2.8800e-06
Ms1p p cb m vdd CMOSP W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=9.7200e-13 PD=4.6800e-06
Ms2n pb cb m gnd CMOSN W=9.0000e-07 L=1.8000e-07 AS=4.8600e-13 PS=2.8800e-06 AD=4.8600e-13 PD=2.8800e-06
Ms2p pb c m vdd CMOSP W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=9.7200e-13 PD=4.6800e-06
Ms3p1 s m vdd vdd CMOSP W=1.8000e-06 L=1.8000e-07 AS=9.7200e-13 PS=4.6800e-06 AD=9.7200e-13 PD=4.6800e-06
Ms3n1 s m gnd gnd CMOSN W=9.0000e-07 L=1.8000e-07 AS=4.8600e-13 PS=2.8800e-06 AD=4.8600e-13 PD=2.8800e-06
.ends xor_tg_x1
