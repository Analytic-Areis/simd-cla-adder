* ---------------------------------------------------------------------
* SUMCELL (variant AOI22) : sout = (c.p + cb.pb)' = p XOR c
* Fully restoring static gate (8T) + 1 local inverter = 10T.
* Late carry signals c / cb placed next to the output.
* ---------------------------------------------------------------------
.subckt SUMCELL p pb cb sout s=1
XI  cb c INV s={s}
XN1 sout c  n1  NM w={2*s*UN}
XN2 n1   p  0   NM w={2*s*UN}
XN3 sout cb n2  NM w={2*s*UN}
XN4 n2   pb 0   NM w={2*s*UN}
XP1 n3   p  vdd PM w={2*s*BETA*UN}
XP2 n3   c  vdd PM w={2*s*BETA*UN}
XP3 sout pb n3  PM w={2*s*BETA*UN}
XP4 sout cb n3  PM w={2*s*BETA*UN}
.ends SUMCELL
