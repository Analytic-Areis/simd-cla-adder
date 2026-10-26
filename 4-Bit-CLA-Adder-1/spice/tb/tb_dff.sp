* tb_dff.sp : TSPC D flip-flop function + clock-to-Q delay (Q3, Q4)
* clk 500 MHz (2 ns), D changes 500 ps before an edge.  Q drives the load inverter.
.include spice/common.inc
.include spice/cells/mos.lib
.include spice/cells/cells.lib
.include spice/cells/dff_tspc.lib

Vclk clk 0 PULSE(0 {SUPPLY} 1n {TR} {TR} {1n-TR} 2n)
Vd   d   0 PWL(0 0 2.5n 0 2.52n {SUPPLY} 6.5n {SUPPLY} 6.52n 0 11.2n 0 11.22n {SUPPLY} 11.7n {SUPPLY} 11.72n 0)
XFF d clk q DFF_TSPC
XL  q ql LOADINV

.tran 1p 16n
* edge #2 (3 ns) captures 1, edge #4 (7 ns) captures 0
.meas tran tcq_lh TRIG v(clk) VAL=0.9 RISE=2 TARG v(q) VAL=0.9 RISE=1
.meas tran tcq_hl TRIG v(clk) VAL=0.9 RISE=4 TARG v(q) VAL=0.9 FALL=1
* D pulse 11.2-11.7n lies inside the clock-high phase (11-12n) -> Q must stay 0
.meas tran q_at_13n FIND v(q) AT=12.9n

.control
run
wrdata results/logs/dff.dat v(clk) v(d) v(q)
set curplottitle=$myname-Q3-tspc-dff
hardcopy results/plots/q3_dff.eps v(clk)+4 v(d)+2 v(q)
.endc
.end
