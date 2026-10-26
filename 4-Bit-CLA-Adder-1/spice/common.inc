* =====================================================================
* common.inc  -  global settings for every netlist in this project
* Run ngspice from the project root (4-Bit-CLA-Adder-1/) so paths resolve.
* =====================================================================
.include tech/TSMC_180nm.txt

.param SUPPLY = 1.8
.param LAMBDA = 0.09u
.param LEN    = {2*LAMBDA}     $ Ln = Lp = 2 lambda (project rule)

* ---- sizing knobs (widths in units of lambda) ----
.param UN    = 4               $ unit NMOS width  (4 lambda = 0.36 um)
.param BETA  = 2               $ Wp/Wn ratio for equal rise/fall (mu_n/mu_p ~ 2.4)
.param TR    = 20p             $ rise/fall of ideal sources

.global vdd
Vdd vdd 0 {SUPPLY}
