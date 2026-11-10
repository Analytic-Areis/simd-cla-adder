cellname rename (UNNAMED) c3b_mirror_x1
box 0 92 82 151; paint nwell
box 8 10 19 30; paint ndiff
box 18 10 27 30; paint ndiff
box 26 10 36 30; paint ndiff
box 35 10 45 30; paint ndiff
box 44 10 55 30; paint ndiff
box 8 98 19 138; paint pdiff
box 18 98 27 138; paint pdiff
box 26 98 36 138; paint pdiff
box 35 98 45 138; paint pdiff
box 44 98 55 138; paint pdiff
box 14 7 16 141; paint poly
box 21 7 23 141; paint poly
box 30 7 32 141; paint poly
box 39 7 41 141; paint poly
box 48 7 50 141; paint poly
box 8 10 12 30; paint ndc
box 24 10 28 30; paint ndc
box 33 10 37 30; paint ndc
box 42 10 46 30; paint ndc
box 51 10 55 30; paint ndc
box 8 98 12 138; paint pdc
box 24 98 28 138; paint pdc
box 33 98 37 138; paint pdc
box 42 98 46 138; paint pdc
box 51 98 55 138; paint pdc
box 13 39 17 44; paint pc
box 20 48 24 53; paint pc
box 29 66 33 71; paint pc
box 38 48 42 53; paint pc
box 47 39 51 44; paint pc
box 4 1 8 5; paint psc
box 28 1 32 5; paint psc
box 52 1 56 5; paint psc
box 4 143 8 147; paint nsc
box 28 143 32 147; paint nsc
box 52 143 56 147; paint nsc
box 0 0 82 6; paint m1
box 0 142 82 148; paint m1
box 8 10 12 30; paint m1
box 8 0 12 30; paint m1
box 24 10 28 30; paint m1
box 24 10 28 36; paint m1
box 33 10 37 30; paint m1
box 33 10 37 36; paint m1
box 42 10 46 30; paint m1
box 42 0 46 30; paint m1
box 51 10 55 30; paint m1
box 51 10 55 36; paint m1
box 8 98 12 138; paint m1
box 8 98 12 148; paint m1
box 24 98 28 138; paint m1
box 24 92 28 138; paint m1
box 33 98 37 138; paint m1
box 33 92 37 138; paint m1
box 42 98 46 138; paint m1
box 42 98 46 148; paint m1
box 51 98 55 138; paint m1
box 51 92 55 138; paint m1
box 13 39 52 44; paint m1
box 20 48 65 53; paint m1
box 24 57 29 62; paint m1
box 29 66 74 71; paint m1
box 33 75 56 80; paint m1
box 33 84 56 89; paint m1
box 24 31 29 36; paint m2c
box 24 57 29 62; paint m2c
box 33 31 38 36; paint m2c
box 33 75 38 80; paint m2c
box 51 31 56 36; paint m2c
box 51 75 56 80; paint m2c
box 24 92 29 97; paint m2c
box 24 57 29 62; paint m2c
box 33 92 38 97; paint m2c
box 33 84 38 89; paint m2c
box 51 92 56 97; paint m2c
box 51 84 56 89; paint m2c
box 60 48 65 53; paint m2c
box 42 39 47 44; paint m2c
box 69 66 74 71; paint m2c
box 24 31 29 62; paint m2
box 33 31 38 80; paint m2
box 51 31 56 80; paint m2
box 24 57 29 97; paint m2
box 33 84 38 97; paint m2
box 51 84 56 97; paint m2
box 60 48 65 53; paint m2
box 42 39 47 44; paint m2
box 69 66 74 71; paint m2
box 60 48 65 53; paint m3c
box 42 39 47 44; paint m3c
box 69 66 74 71; paint m3c
box 24 57 29 62; paint m3c
box 20 48 22 53; label a2 center m1; port make 1
box 13 39 15 44; label b2 center m1; port make 2
box 29 66 31 71; label c2 center m1; port make 3
box 24 57 26 62; label c3b center m1; port make 4
box 0 142 2 148; label vdd center m1; port make 5
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
save c3b_mirror_x1
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
