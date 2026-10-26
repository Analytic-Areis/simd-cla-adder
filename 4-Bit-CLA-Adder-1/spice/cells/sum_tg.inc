* ---------------------------------------------------------------------
* SUMCELL (variant TG) : sout = p XOR c  given p, pb=p', cb=c'
*   cb=1 (c=0) -> pass p ;  cb=0 (c=1) -> pass pb
* 2 transmission gates + 1 local inverter = 6T. Late carry drives
* only TG gates; p/pb (early) come from strong static drivers.
* ---------------------------------------------------------------------
.subckt SUMCELL p pb cb sout s=1
XI  cb c INV s={s}
XN1 sout cb p  NM w={2*s*UN}
XP1 sout c  p  PM w={2*s*BETA*UN}
XN2 sout c  pb NM w={2*s*UN}
XP2 sout cb pb PM w={2*s*BETA*UN}
.ends SUMCELL
