cellname rename (UNNAMED) nand2_x1
box 0 65 57 104; paint nwell
box 8 10 20 30; paint ndiff
box 19 10 30 30; paint ndiff
box 8 71 20 91; paint pdiff
box 19 71 30 91; paint pdiff
box 14 7 16 94; paint poly
box 23 7 25 94; paint poly
box 8 10 12 30; paint ndc
box 26 10 30 30; paint ndc
box 8 71 12 91; paint pdc
box 17 71 21 91; paint pdc
box 26 71 30 91; paint pdc
box 13 48 17 53; paint pc
box 22 57 26 62; paint pc
box 4 1 8 5; paint psc
box 28 1 32 5; paint psc
box 4 96 8 100; paint nsc
box 28 96 32 100; paint nsc
box 0 0 57 6; paint m1
box 0 95 57 101; paint m1
box 8 10 12 30; paint m1
box 8 10 12 36; paint m1
box 26 10 30 30; paint m1
box 26 0 30 30; paint m1
box 8 71 12 91; paint m1
box 8 65 12 91; paint m1
box 17 71 21 91; paint m1
box 17 71 21 101; paint m1
box 26 71 30 91; paint m1
box 26 65 30 91; paint m1
box 8 39 31 44; paint m1
box 13 48 40 53; paint m1
box 22 57 49 62; paint m1
box 8 31 13 36; paint m2c
box 8 39 13 44; paint m2c
box 8 65 13 70; paint m2c
box 8 39 13 44; paint m2c
box 26 65 31 70; paint m2c
box 26 39 31 44; paint m2c
box 35 48 40 53; paint m2c
box 44 57 49 62; paint m2c
box 8 31 13 44; paint m2
box 8 39 13 70; paint m2
box 26 39 31 70; paint m2
box 35 48 40 53; paint m2
box 44 57 49 62; paint m2
box 35 48 40 53; paint m3c
box 44 57 49 62; paint m3c
box 8 39 13 44; paint m3c
box 13 48 15 53; label i0 center m1; port make 1
box 22 57 24 62; label i1 center m1; port make 2
box 8 39 10 44; label y center m1; port make 3
box 0 95 2 101; label vdd center m1; port make 4
box 0 0 2 6; label gnd center m1; port make 5
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
save nand2_x1
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
