* tb_dff_setup_hold.sp : setup & hold time of the TSPC DFF (Q4)
*  Clock edges at 1n, 3n (edge under test), 5n.
*  SETUP : D makes its transition TSU before the 3n edge.  tcq is recorded
*          vs TSU; setup time = smallest TSU with tcq <= 1.1 x tcq(nominal).
*  HOLD  : D takes the new value 2n, and keeps it until 3n + TH, then reverts.
*          hold time = smallest TH for which Q still captures correctly.
*  Both rising (0->1) and falling (1->0) data are swept. Needs ngspice >= 32
*  (alterparam).
.include spice/common.inc
.include spice/cells/mos.lib
.include spice/cells/cells.lib
.include spice/cells/dff_tspc.lib

.param TSU=500p TH=500p DPOL=1
.param V0={SUPPLY*(1-DPOL)} V1={SUPPLY*DPOL}
.param TS1={3n-TSU} TS2={3n-TSU+TR}
.param TH1={3n+TH}  TH2={3n+TH+TR}

Vclk clk 0 PULSE(0 {SUPPLY} 1n {TR} {TR} {1n-TR} 2n)
* setup DUT
Vds ds 0 PWL(0 {V0} {TS1} {V0} {TS2} {V1})
XFS ds clk qs DFF_TSPC
XLS qs qls LOADINV
* hold DUT : new value V1 at 2n, back to V0 at 3n+TH
Vdh dh 0 PWL(0 {V0} 2n {V0} {2n+TR} {V1} {TH1} {V1} {TH2} {V0})
XFH dh clk qh DFF_TSPC
XLH qh qlh LOADINV

.tran 1p 6n

.control
set curplottitle=$myname-Q4-setup-hold
compose tsus values 600p 400p 300p 250p 200p 170p 150p 130p 110p 90p 70p 50p 30p 10p
compose ths  values 300p 200p 150p 120p 100p 80p 60p 40p 20p 0 -20p -40p -60p
foreach pol 1 0
  alterparam DPOL = $pol
  echo "=== SETUP sweep  DPOL=$pol (1 = rising D, 0 = falling D) ==="
  echo "SETUPHDR pol tsu tcq qfinal"
  let i = 0
  while i < length(tsus)
    let t = tsus[i]
    alterparam TSU = $&t
    reset
    run
    let qf = qs[length(qs)-1]
    if $pol = 1
      meas tran tcq TRIG v(clk) VAL=0.9 RISE=2 TARG v(qs) VAL=0.9 RISE=1
    else
      meas tran tcq TRIG v(clk) VAL=0.9 RISE=2 TARG v(qs) VAL=0.9 FALL=1
    end
    echo "SETUP $pol $&t $&tcq $&qf"
    let i = i + 1
  end
  echo "=== HOLD sweep DPOL=$pol ==="
  echo "HOLDHDR pol th q_at_4p5n"
  let i = 0
  while i < length(ths)
    let t = ths[i]
    alterparam TH = $&t
    reset
    run
    meas tran qh45 FIND v(qh) AT=4.5n
    echo "HOLD $pol $&t $&qh45"
    let i = i + 1
  end
end
.endc
.end
