cellname rename (UNNAMED) xor_static12_x1
box 0 92 84 151; paint nwell
box 8 20 20 30; paint ndiff
box 19 10 29 30; paint ndiff
box 28 10 38 30; paint ndiff
box 37 10 47 30; paint ndiff
box 46 10 56 30; paint ndiff
box 55 20 66 30; paint ndiff
box 8 98 20 118; paint pdiff
box 19 98 29 138; paint pdiff
box 28 98 38 138; paint pdiff
box 37 98 47 138; paint pdiff
box 46 98 56 138; paint pdiff
box 55 98 66 118; paint pdiff
box 14 17 16 121; paint poly
box 23 7 25 53; paint poly
box 23 57 25 141; paint poly
box 32 7 34 141; paint poly
box 41 7 43 62; paint poly
box 41 84 43 141; paint poly
box 50 7 52 141; paint poly
box 59 17 61 121; paint poly
box 8 20 12 30; paint ndc
box 17 10 21 30; paint ndc
box 35 10 39 30; paint ndc
box 53 10 57 30; paint ndc
box 62 20 66 30; paint ndc
box 8 98 12 118; paint pdc
box 17 98 21 138; paint pdc
box 26 98 30 138; paint pdc
box 35 98 39 138; paint pdc
box 44 98 48 138; paint pdc
box 53 98 57 138; paint pdc
box 62 98 66 118; paint pdc
box 13 57 17 62; paint pc
box 22 48 26 53; paint pc
box 22 57 26 62; paint pc
box 31 39 35 44; paint pc
box 40 57 44 62; paint pc
box 40 84 44 89; paint pc
box 49 39 53 44; paint pc
box 58 39 62 44; paint pc
box 4 1 8 5; paint psc
box 28 1 32 5; paint psc
box 52 1 56 5; paint psc
box 4 143 8 147; paint nsc
box 28 143 32 147; paint nsc
box 52 143 56 147; paint nsc
box 0 0 84 6; paint m1
box 0 142 84 148; paint m1
box 8 20 12 30; paint m1
box 8 20 12 36; paint m1
box 17 10 21 30; paint m1
box 17 0 21 30; paint m1
box 35 10 39 30; paint m1
box 35 10 39 36; paint m1
box 53 10 57 30; paint m1
box 53 0 57 30; paint m1
box 62 20 66 30; paint m1
box 62 20 66 36; paint m1
box 8 98 12 118; paint m1
box 8 92 12 118; paint m1
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
box 62 98 66 118; paint m1
box 62 92 66 118; paint m1
box 8 39 36 44; paint m1
box 49 39 63 44; paint m1
box 22 48 76 53; paint m1
box 13 57 45 62; paint m1
box 26 66 49 71; paint m1
box 35 75 40 80; paint m1
box 40 84 76 89; paint m1
box 8 31 13 36; paint m2c
box 8 39 13 44; paint m2c
box 35 31 40 36; paint m2c
box 35 75 40 80; paint m2c
box 62 31 67 36; paint m2c
box 62 48 67 53; paint m2c
box 8 92 13 97; paint m2c
box 8 39 13 44; paint m2c
box 26 92 31 97; paint m2c
box 26 66 31 71; paint m2c
box 35 92 40 97; paint m2c
box 35 75 40 80; paint m2c
box 44 92 49 97; paint m2c
box 44 66 49 71; paint m2c
box 62 92 67 97; paint m2c
box 62 84 67 89; paint m2c
box 71 84 76 89; paint m2c
box 71 48 76 53; paint m2c
box 53 39 58 44; paint m2c
box 17 57 22 62; paint m2c
box 8 31 13 44; paint m2
box 35 31 40 80; paint m2
box 62 31 67 53; paint m2
box 8 39 13 97; paint m2
box 26 66 31 97; paint m2
box 35 75 40 97; paint m2
box 44 66 49 97; paint m2
box 62 84 67 97; paint m2
box 71 48 76 89; paint m2
box 53 39 58 44; paint m2
box 17 57 22 62; paint m2
box 53 39 58 44; paint m3c
box 17 57 22 62; paint m3c
box 35 75 40 80; paint m3c
box 49 39 51 44; label c center m1; port make 1
box 13 57 15 62; label p center m1; port make 2
box 35 75 37 80; label s center m1; port make 3
box 0 142 2 148; label vdd center m1; port make 4
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
save xor_static12_x1
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
