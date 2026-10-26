* tb_cla_func.sp : exhaustive functional test of the CLA core (Q3)
* 9 inputs counted in binary, one vector per 1 ns slot (512 vectors):
*   a0..a3 = bits 0..3, b0..b3 = bits 4..7, c0 = bit 8.
* Outputs sampled by scripts/check_cla.py at the end of each slot.
.include spice/common.inc
.include spice/cells/mos.lib
.include spice/cells/cells.lib
.include spice/cells/sumcell.inc
.include spice/blocks/cla4.lib

Va0 a0 0 PULSE(0 {SUPPLY} 1n   {TR} {TR} {1n-TR}   2n)
Va1 a1 0 PULSE(0 {SUPPLY} 2n   {TR} {TR} {2n-TR}   4n)
Va2 a2 0 PULSE(0 {SUPPLY} 4n   {TR} {TR} {4n-TR}   8n)
Va3 a3 0 PULSE(0 {SUPPLY} 8n   {TR} {TR} {8n-TR}   16n)
Vb0 b0 0 PULSE(0 {SUPPLY} 16n  {TR} {TR} {16n-TR}  32n)
Vb1 b1 0 PULSE(0 {SUPPLY} 32n  {TR} {TR} {32n-TR}  64n)
Vb2 b2 0 PULSE(0 {SUPPLY} 64n  {TR} {TR} {64n-TR}  128n)
Vb3 b3 0 PULSE(0 {SUPPLY} 128n {TR} {TR} {128n-TR} 256n)
Vc0 c0 0 PULSE(0 {SUPPLY} 256n {TR} {TR} {256n-TR} 512n)

XDUT a0 a1 a2 a3 b0 b1 b2 b3 c0 s0 s1 s2 s3 c4 c4b CLA4
XL0 s0 l0 LOADINV
XL1 s1 l1 LOADINV
XL2 s2 l2 LOADINV
XL3 s3 l3 LOADINV
XL4 c4 l4 LOADINV

.options interp
.tran 50p 512n

.control
run
wrdata results/logs/cla_func.dat v(s0) v(s1) v(s2) v(s3) v(c4)
set curplottitle=$myname-Q3-cla-core-exhaustive
hardcopy results/plots/q3_cla_func.eps v(c0)+12 v(c4)+10 v(s3)+8 v(s2)+6 v(s1)+4 v(s0)+2
.endc
.end
