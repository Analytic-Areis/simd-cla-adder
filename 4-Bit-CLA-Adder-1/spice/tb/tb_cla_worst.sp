* tb_cla_worst.sp : CLA core, worst-case vector A=1111 B=0000, C0 toggling
* (the Q9 vector, here pre-layout). S: 1111 -> 0000, C4: 0 -> 1 and back.
* C0 is driven through a 2-inverter buffer (like a flip-flop output) so the
* edge is realistic; delays are measured from the buffered c0 node.
* Every s_i and c4 drives the project load inverter (20L/10L).
.include spice/common.inc
.include spice/cells/mos.lib
.include spice/cells/cells.lib
.include spice/cells/sumcell.inc
.include spice/blocks/cla4.lib

Va0 a0 0 {SUPPLY}
Va1 a1 0 {SUPPLY}
Va2 a2 0 {SUPPLY}
Va3 a3 0 {SUPPLY}
Vb0 b0 0 0
Vb1 b1 0 0
Vb2 b2 0 0
Vb3 b3 0 0
Vc0 c0i 0 PULSE(0 {SUPPLY} 1n {TR} {TR} {2n-TR} 4n)
XD1 c0i c0x INV s=2
XD2 c0x c0  INV s=4

XDUT a0 a1 a2 a3 b0 b1 b2 b3 c0 s0 s1 s2 s3 c4 c4b CLA4
XL0 s0 l0 LOADINV
XL1 s1 l1 LOADINV
XL2 s2 l2 LOADINV
XL3 s3 l3 LOADINV
XL4 c4 l4 LOADINV

.tran 1p 9n
* C0 rise (1n): sums fall, c4 rises
.meas tran tphl_s0 TRIG v(c0) VAL=0.9 RISE=1 TARG v(s0) VAL=0.9 FALL=1
.meas tran tphl_s1 TRIG v(c0) VAL=0.9 RISE=1 TARG v(s1) VAL=0.9 FALL=1
.meas tran tphl_s2 TRIG v(c0) VAL=0.9 RISE=1 TARG v(s2) VAL=0.9 FALL=1
.meas tran tphl_s3 TRIG v(c0) VAL=0.9 RISE=1 TARG v(s3) VAL=0.9 FALL=1
.meas tran tplh_c4 TRIG v(c0) VAL=0.9 RISE=1 TARG v(c4) VAL=0.9 RISE=1
* C0 fall (3n): sums rise, c4 falls
.meas tran tplh_s0 TRIG v(c0) VAL=0.9 FALL=1 TARG v(s0) VAL=0.9 RISE=1
.meas tran tplh_s1 TRIG v(c0) VAL=0.9 FALL=1 TARG v(s1) VAL=0.9 RISE=1
.meas tran tplh_s2 TRIG v(c0) VAL=0.9 FALL=1 TARG v(s2) VAL=0.9 RISE=1
.meas tran tplh_s3 TRIG v(c0) VAL=0.9 FALL=1 TARG v(s3) VAL=0.9 RISE=1
.meas tran tphl_c4 TRIG v(c0) VAL=0.9 FALL=1 TARG v(c4) VAL=0.9 FALL=1
* average supply power over 2 full C0 periods (includes buffer + loads)
.meas tran iavg AVG i(Vdd) FROM=1n TO=9n

.control
run
compose tall values $&tphl_s0 $&tphl_s1 $&tphl_s2 $&tphl_s3 $&tplh_c4 $&tplh_s0 $&tplh_s1 $&tplh_s2 $&tplh_s3 $&tphl_c4
let tpd_max = vecmax(tall)
let pavg = -iavg*1.8
let pdp = pavg*tpd_max
echo "RESULT tpd_max $&tpd_max"
echo "RESULT pavg $&pavg"
echo "RESULT pdp $&pdp"
wrdata results/logs/cla_worst.dat v(c0) v(s0) v(s1) v(s2) v(s3) v(c4)
set curplottitle=$myname-Q9-prelayout-core-worstcase
hardcopy results/plots/q9_core_worst.eps v(c0)+10 v(c4)+8 v(s3)+6 v(s2)+4 v(s1)+2 v(s0)
.endc
.end
