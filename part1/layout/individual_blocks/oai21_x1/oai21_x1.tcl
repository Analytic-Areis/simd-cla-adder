cellname rename (UNNAMED) oai21_x1
box 0 83 75 142; paint nwell
box 8 10 20 30; paint ndiff
box 19 10 29 30; paint ndiff
box 28 10 39 30; paint ndiff
box 8 89 20 129; paint pdiff
box 19 89 29 129; paint pdiff
box 28 89 39 109; paint pdiff
box 14 7 16 132; paint poly
box 23 7 25 132; paint poly
box 32 7 34 112; paint poly
box 8 10 12 30; paint ndc
box 17 10 21 30; paint ndc
box 26 10 30 30; paint ndc
box 35 10 39 30; paint ndc
box 8 89 12 129; paint pdc
box 26 89 30 129; paint pdc
box 35 89 39 109; paint pdc
box 13 48 17 53; paint pc
box 22 66 26 71; paint pc
box 31 75 35 80; paint pc
box 4 1 8 5; paint psc
box 28 1 32 5; paint psc
box 52 1 56 5; paint psc
box 4 134 8 138; paint nsc
box 28 134 32 138; paint nsc
box 52 134 56 138; paint nsc
box 0 0 75 6; paint m1
box 0 133 75 139; paint m1
box 8 10 12 30; paint m1
box 8 10 12 36; paint m1
box 17 10 21 30; paint m1
box 17 10 21 36; paint m1
box 26 10 30 30; paint m1
box 26 10 30 36; paint m1
box 35 10 39 30; paint m1
box 35 0 39 30; paint m1
box 8 89 12 129; paint m1
box 8 89 12 139; paint m1
box 26 89 30 129; paint m1
box 26 83 30 129; paint m1
box 35 89 39 109; paint m1
box 35 89 39 139; paint m1
box 8 39 31 44; paint m1
box 13 48 49 53; paint m1
box 17 57 31 62; paint m1
box 22 66 58 71; paint m1
box 31 75 67 80; paint m1
box 8 31 13 36; paint m2c
box 8 39 13 44; paint m2c
box 17 31 22 36; paint m2c
box 17 57 22 62; paint m2c
box 26 31 31 36; paint m2c
box 26 39 31 44; paint m2c
box 26 83 31 88; paint m2c
box 26 57 31 62; paint m2c
box 44 48 49 53; paint m2c
box 53 66 58 71; paint m2c
box 62 75 67 80; paint m2c
box 8 31 13 44; paint m2
box 17 31 22 62; paint m2
box 26 31 31 44; paint m2
box 26 57 31 88; paint m2
box 44 48 49 53; paint m2
box 53 66 58 71; paint m2
box 62 75 67 80; paint m2
box 44 48 49 53; paint m3c
box 53 66 58 71; paint m3c
box 62 75 67 80; paint m3c
box 26 57 31 62; paint m3c
box 13 48 15 53; label a center m1; port make 1
box 22 66 24 71; label b center m1; port make 2
box 31 75 33 80; label c center m1; port make 3
box 17 57 19 62; label y center m1; port make 4
box 0 133 2 139; label vdd center m1; port make 5
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
save oai21_x1
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
