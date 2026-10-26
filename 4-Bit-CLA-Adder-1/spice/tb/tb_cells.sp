* tb_cells.sp : functional check of every logic cell (Q3)
* Inputs count in binary: A = bit0 (1 ns slots), B = bit1, C = bit2.
* Every output drives the project load inverter (20L/10L).
.include spice/common.inc
.include spice/cells/mos.lib
.include spice/cells/cells.lib
.include spice/cells/sumcell.inc

VA A 0 PULSE(0 {SUPPLY} 1n {TR} {TR} {1n-TR} 2n)
VB B 0 PULSE(0 {SUPPLY} 2n {TR} {TR} {2n-TR} 4n)
VC C 0 PULSE(0 {SUPPLY} 4n {TR} {TR} {4n-TR} 8n)

XINV   A    y_inv   INV
XNAND  A B  y_nand  NAND2
XNOR   A B  y_nor   NOR2
XAOI   A B C y_aoi  AOI21
XOAI   A B C y_oai  OAI21
XAB    A Ab INV
XSUM   A Ab B y_sum SUMCELL

XL1 y_inv  l1 LOADINV
XL2 y_nand l2 LOADINV
XL3 y_nor  l3 LOADINV
XL4 y_aoi  l4 LOADINV
XL5 y_oai  l5 LOADINV
XL6 y_sum  l6 LOADINV

.tran 1p 8n

* sample propagation delays of the INV (rise/fall) as a sanity check
.meas tran inv_tphl TRIG v(A) VAL=0.9 RISE=1 TARG v(y_inv) VAL=0.9 FALL=1
.meas tran inv_tplh TRIG v(A) VAL=0.9 FALL=1 TARG v(y_inv) VAL=0.9 RISE=1

.control
run
wrdata results/logs/cells.dat v(A) v(B) v(C) v(y_inv) v(y_nand) v(y_nor) v(y_aoi) v(y_oai) v(y_sum)
set curplottitle=$myname-Q3-cells-inv-nand-nor
hardcopy results/plots/q3_cells_1.eps v(A)+8 v(B)+6 v(y_inv)+4 v(y_nand)+2 v(y_nor)
set curplottitle=$myname-Q3-cells-aoi21-oai21-sum
hardcopy results/plots/q3_cells_2.eps v(A)+10 v(B)+8 v(C)+6 v(y_aoi)+4 v(y_oai)+2 v(y_sum)
.endc
.end
