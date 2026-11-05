cellname rename (UNNAMED) sum1_b
box 0 92 84 151; paint nwell
box 8 10 20 30; paint ndiff
box 19 10 29 30; paint ndiff
box 28 10 38 30; paint ndiff
box 37 10 47 30; paint ndiff
box 46 24 57 30; paint ndiff
box 8 98 20 111; paint pdiff
box 19 98 29 138; paint pdiff
box 28 98 38 138; paint pdiff
box 37 98 47 138; paint pdiff
box 46 98 57 138; paint pdiff
box 14 7 16 114; paint poly
box 23 7 25 141; paint poly
box 32 7 34 141; paint poly
box 41 7 43 141; paint poly
box 50 21 52 141; paint poly
box 8 10 12 30; paint ndc
box 26 10 30 30; paint ndc
box 44 10 48 30; paint ndc
box 53 24 57 30; paint ndc
box 8 98 12 111; paint pdc
box 17 98 21 138; paint pdc
box 26 98 30 138; paint pdc
box 35 98 39 138; paint pdc
box 44 98 48 138; paint pdc
box 53 98 57 138; paint pdc
box 13 48 17 53; paint pc
box 22 57 26 62; paint pc
box 31 84 35 89; paint pc
box 40 39 44 44; paint pc
box 49 48 53 53; paint pc
box 4 1 8 5; paint psc
box 28 1 32 5; paint psc
box 52 1 56 5; paint psc
box 4 143 8 147; paint nsc
box 28 143 32 147; paint nsc
box 52 143 56 147; paint nsc
box 0 0 84 6; paint m1
box 0 142 84 148; paint m1
box 8 10 12 30; paint m1
box 8 0 12 30; paint m1
box 26 10 30 30; paint m1
box 26 10 30 36; paint m1
box 44 10 48 30; paint m1
box 44 0 48 30; paint m1
box 53 24 57 30; paint m1
box 53 24 57 36; paint m1
box 8 98 12 111; paint m1
box 8 92 12 111; paint m1
box 17 98 21 138; paint m1
box 17 98 21 148; paint m1
box 26 98 30 138; paint m1
box 26 92 30 138; paint m1
box 35 98 39 138; paint m1
box 35 92 39 138; paint m1
box 44 98 48 138; paint m1
box 44 92 48 138; paint m1
box 53 98 57 138; paint m1
box 53 98 57 148; paint m1
box 8 39 58 44; paint m1
box 13 48 54 53; paint m1
box 22 57 67 62; paint m1
box 26 66 40 71; paint m1
box 26 75 49 80; paint m1
box 31 84 76 89; paint m1
box 26 31 31 36; paint m2c
box 26 66 31 71; paint m2c
box 53 31 58 36; paint m2c
box 53 39 58 44; paint m2c
box 8 92 13 97; paint m2c
box 8 39 13 44; paint m2c
box 26 92 31 97; paint m2c
box 26 75 31 80; paint m2c
box 35 92 40 97; paint m2c
box 35 66 40 71; paint m2c
box 44 92 49 97; paint m2c
box 44 75 49 80; paint m2c
box 17 48 22 53; paint m2c
box 62 57 67 62; paint m2c
box 71 84 76 89; paint m2c
box 26 31 31 71; paint m2
box 53 31 58 44; paint m2
box 8 39 13 97; paint m2
box 26 75 31 97; paint m2
box 35 66 40 97; paint m2
box 44 75 49 97; paint m2
box 17 48 22 53; paint m2
box 62 57 67 62; paint m2
box 71 84 76 89; paint m2
box 17 48 22 53; paint m3c
box 62 57 67 62; paint m3c
box 71 84 76 89; paint m3c
box 35 66 40 71; paint m3c
box 13 48 15 53; label c1 center m1; port make 1
box 22 57 24 62; label p1 center m1; port make 2
box 31 84 33 89; label p1b center m1; port make 3
box 26 66 28 71; label s1 center m1; port make 4
box 8 39 10 44; label x1_cb center m1
box 26 75 28 80; label x1_s1xp1 center m1
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
save sum1_b
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
