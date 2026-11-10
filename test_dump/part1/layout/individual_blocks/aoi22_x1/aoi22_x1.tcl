cellname rename (UNNAMED) aoi22_x1
box 0 92 93 151; paint nwell
box 8 10 20 30; paint ndiff
box 19 10 29 30; paint ndiff
box 28 10 38 30; paint ndiff
box 37 10 48 30; paint ndiff
box 8 98 20 138; paint pdiff
box 19 98 29 138; paint pdiff
box 28 98 38 138; paint pdiff
box 37 98 48 138; paint pdiff
box 14 7 16 141; paint poly
box 23 7 25 141; paint poly
box 32 7 34 141; paint poly
box 41 7 43 141; paint poly
box 8 10 12 30; paint ndc
box 26 10 30 30; paint ndc
box 44 10 48 30; paint ndc
box 8 98 12 138; paint pdc
box 17 98 21 138; paint pdc
box 26 98 30 138; paint pdc
box 35 98 39 138; paint pdc
box 44 98 48 138; paint pdc
box 13 57 17 62; paint pc
box 22 66 26 71; paint pc
box 31 75 35 80; paint pc
box 40 84 44 89; paint pc
box 4 1 8 5; paint psc
box 28 1 32 5; paint psc
box 52 1 56 5; paint psc
box 76 1 80 5; paint psc
box 4 143 8 147; paint nsc
box 28 143 32 147; paint nsc
box 52 143 56 147; paint nsc
box 76 143 80 147; paint nsc
box 0 0 93 6; paint m1
box 0 142 93 148; paint m1
box 8 10 12 30; paint m1
box 8 10 12 36; paint m1
box 26 10 30 30; paint m1
box 26 0 30 30; paint m1
box 44 10 48 30; paint m1
box 44 10 48 36; paint m1
box 8 98 12 138; paint m1
box 8 92 12 138; paint m1
box 17 98 21 138; paint m1
box 17 98 21 148; paint m1
box 26 98 30 138; paint m1
box 26 92 30 138; paint m1
box 35 98 39 138; paint m1
box 35 92 39 138; paint m1
box 44 98 48 138; paint m1
box 44 92 48 138; paint m1
box 8 39 49 44; paint m1
box 8 48 49 53; paint m1
box 13 57 58 62; paint m1
box 22 66 67 71; paint m1
box 31 75 85 80; paint m1
box 40 84 76 89; paint m1
box 8 31 13 36; paint m2c
box 8 39 13 44; paint m2c
box 44 31 49 36; paint m2c
box 44 39 49 44; paint m2c
box 8 92 13 97; paint m2c
box 8 48 13 53; paint m2c
box 26 92 31 97; paint m2c
box 26 48 31 53; paint m2c
box 35 92 40 97; paint m2c
box 35 39 40 44; paint m2c
box 44 92 49 97; paint m2c
box 44 48 49 53; paint m2c
box 53 57 58 62; paint m2c
box 62 66 67 71; paint m2c
box 71 84 76 89; paint m2c
box 80 75 85 80; paint m2c
box 8 31 13 44; paint m2
box 44 31 49 44; paint m2
box 8 48 13 97; paint m2
box 26 48 31 97; paint m2
box 35 39 40 97; paint m2
box 44 48 49 97; paint m2
box 53 57 58 62; paint m2
box 62 66 67 71; paint m2
box 71 84 76 89; paint m2
box 80 75 85 80; paint m2
box 53 57 58 62; paint m3c
box 62 66 67 71; paint m3c
box 71 84 76 89; paint m3c
box 80 75 85 80; paint m3c
box 35 39 40 44; paint m3c
box 13 57 15 62; label a center m1; port make 1
box 22 66 24 71; label b center m1; port make 2
box 40 84 42 89; label c center m1; port make 3
box 31 75 33 80; label d center m1; port make 4
box 8 39 10 44; label y center m1; port make 5
box 0 142 2 148; label vdd center m1; port make 6
box 0 0 2 6; label gnd center m1; port make 7
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
save aoi22_x1
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
