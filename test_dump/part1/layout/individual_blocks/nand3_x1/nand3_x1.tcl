cellname rename (UNNAMED) nand3_x1
box 0 84 75 123; paint nwell
box 8 10 20 40; paint ndiff
box 19 10 29 40; paint ndiff
box 28 10 39 40; paint ndiff
box 8 90 20 110; paint pdiff
box 19 90 29 110; paint pdiff
box 28 90 39 110; paint pdiff
box 14 7 16 113; paint poly
box 23 7 25 113; paint poly
box 32 7 34 113; paint poly
box 8 10 12 40; paint ndc
box 35 10 39 40; paint ndc
box 8 90 12 110; paint pdc
box 17 90 21 110; paint pdc
box 26 90 30 110; paint pdc
box 35 90 39 110; paint pdc
box 13 58 17 63; paint pc
box 22 67 26 72; paint pc
box 31 76 35 81; paint pc
box 4 1 8 5; paint psc
box 28 1 32 5; paint psc
box 52 1 56 5; paint psc
box 4 115 8 119; paint nsc
box 28 115 32 119; paint nsc
box 52 115 56 119; paint nsc
box 0 0 75 6; paint m1
box 0 114 75 120; paint m1
box 8 10 12 40; paint m1
box 8 10 12 46; paint m1
box 35 10 39 40; paint m1
box 35 0 39 40; paint m1
box 8 90 12 110; paint m1
box 8 84 12 110; paint m1
box 17 90 21 110; paint m1
box 17 90 21 120; paint m1
box 26 90 30 110; paint m1
box 26 84 30 110; paint m1
box 35 90 39 110; paint m1
box 35 90 39 120; paint m1
box 8 49 31 54; paint m1
box 13 58 49 63; paint m1
box 22 67 58 72; paint m1
box 31 76 67 81; paint m1
box 8 41 13 46; paint m2c
box 8 49 13 54; paint m2c
box 8 84 13 89; paint m2c
box 8 49 13 54; paint m2c
box 26 84 31 89; paint m2c
box 26 49 31 54; paint m2c
box 44 58 49 63; paint m2c
box 53 67 58 72; paint m2c
box 62 76 67 81; paint m2c
box 8 41 13 54; paint m2
box 8 49 13 89; paint m2
box 26 49 31 89; paint m2
box 44 58 49 63; paint m2
box 53 67 58 72; paint m2
box 62 76 67 81; paint m2
box 44 58 49 63; paint m3c
box 53 67 58 72; paint m3c
box 62 76 67 81; paint m3c
box 8 49 13 54; paint m3c
box 13 58 15 63; label i0 center m1; port make 1
box 22 67 24 72; label i1 center m1; port make 2
box 31 76 33 81; label i2 center m1; port make 3
box 8 49 10 54; label y center m1; port make 4
box 0 114 2 120; label vdd center m1; port make 5
box 0 0 2 6; label gnd center m1; port make 6
select top cell
drc euclidean on
drc check
drc catchup
set why [drc listall why]
set total 0
foreach {message boxes} $why {
    incr total [llength $boxes]
    puts "DRC_ERR $message : [lrange $boxes 0 3]"
}
puts "DRC_COUNT $total"
save nand3_x1
extract do local
extract all
ext2spice lvs
ext2spice cthresh 0
ext2spice rthresh 0
ext2spice format ngspice
ext2spice subcircuit top on
ext2spice
puts DONE
quit -noprompt
