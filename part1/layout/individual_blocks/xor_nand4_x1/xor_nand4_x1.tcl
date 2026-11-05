cellname rename (UNNAMED) xor_nand4_x1
box 0 74 101 113; paint nwell
box 8 10 20 30; paint ndiff
box 19 10 29 30; paint ndiff
box 28 10 38 30; paint ndiff
box 37 10 48 30; paint ndiff
box 53 10 65 30; paint ndiff
box 64 10 74 30; paint ndiff
box 73 10 83 30; paint ndiff
box 82 10 93 30; paint ndiff
box 8 80 20 100; paint pdiff
box 19 80 29 100; paint pdiff
box 28 80 38 100; paint pdiff
box 37 80 51 100; paint pdiff
box 51 80 65 100; paint pdiff
box 64 80 74 100; paint pdiff
box 73 80 83 100; paint pdiff
box 82 80 93 100; paint pdiff
box 14 7 16 103; paint poly
box 23 7 25 103; paint poly
box 32 7 34 103; paint poly
box 41 7 43 103; paint poly
box 59 7 61 103; paint poly
box 68 7 70 103; paint poly
box 77 7 79 103; paint poly
box 86 7 88 103; paint poly
box 8 10 12 30; paint ndc
box 26 10 30 30; paint ndc
box 44 10 48 30; paint ndc
box 53 10 57 30; paint ndc
box 71 10 75 30; paint ndc
box 89 10 93 30; paint ndc
box 8 80 12 100; paint pdc
box 17 80 21 100; paint pdc
box 26 80 30 100; paint pdc
box 35 80 39 100; paint pdc
box 49 80 53 100; paint pdc
box 62 80 66 100; paint pdc
box 71 80 75 100; paint pdc
box 80 80 84 100; paint pdc
box 89 80 93 100; paint pdc
box 13 48 17 53; paint pc
box 22 57 26 62; paint pc
box 31 39 35 44; paint pc
box 40 48 44 53; paint pc
box 58 57 62 62; paint pc
box 67 39 71 44; paint pc
box 76 48 80 53; paint pc
box 85 66 89 71; paint pc
box 4 1 8 5; paint psc
box 28 1 32 5; paint psc
box 52 1 56 5; paint psc
box 76 1 80 5; paint psc
box 4 105 8 109; paint nsc
box 28 105 32 109; paint nsc
box 52 105 56 109; paint nsc
box 76 105 80 109; paint nsc
box 0 0 101 6; paint m1
box 0 104 101 110; paint m1
box 8 10 12 30; paint m1
box 8 10 12 36; paint m1
box 26 10 30 30; paint m1
box 26 0 30 30; paint m1
box 44 10 48 30; paint m1
box 44 10 48 36; paint m1
box 53 10 57 30; paint m1
box 53 10 57 36; paint m1
box 71 10 75 30; paint m1
box 71 0 75 30; paint m1
box 89 10 93 30; paint m1
box 89 10 93 36; paint m1
box 8 80 12 100; paint m1
box 8 80 12 110; paint m1
box 17 80 21 100; paint m1
box 17 74 21 100; paint m1
box 26 80 30 100; paint m1
box 26 80 30 110; paint m1
box 35 80 39 100; paint m1
box 35 74 39 100; paint m1
box 49 80 53 100; paint m1
box 49 80 53 110; paint m1
box 62 80 66 100; paint m1
box 62 74 66 100; paint m1
box 71 80 75 100; paint m1
box 71 80 75 110; paint m1
box 80 80 84 100; paint m1
box 80 74 84 100; paint m1
box 89 80 93 100; paint m1
box 89 80 93 110; paint m1
box 8 39 72 44; paint m1
box 80 39 94 44; paint m1
box 13 48 45 53; paint m1
box 53 48 81 53; paint m1
box 22 57 63 62; paint m1
box 35 66 90 71; paint m1
box 8 31 13 36; paint m2c
box 8 39 13 44; paint m2c
box 44 31 49 36; paint m2c
box 44 66 49 71; paint m2c
box 53 31 58 36; paint m2c
box 53 48 58 53; paint m2c
box 89 31 94 36; paint m2c
box 89 39 94 44; paint m2c
box 17 74 22 79; paint m2c
box 17 39 22 44; paint m2c
box 35 74 40 79; paint m2c
box 35 66 40 71; paint m2c
box 62 74 67 79; paint m2c
box 62 48 67 53; paint m2c
box 80 74 85 79; paint m2c
box 80 39 85 44; paint m2c
box 26 57 31 62; paint m2c
box 26 48 31 53; paint m2c
box 8 31 13 44; paint m2
box 44 31 49 71; paint m2
box 53 31 58 53; paint m2
box 89 31 94 44; paint m2
box 17 39 22 79; paint m2
box 35 66 40 79; paint m2
box 62 48 67 79; paint m2
box 80 39 85 79; paint m2
box 26 57 31 62; paint m2
box 26 48 31 53; paint m2
box 26 57 31 62; paint m3c
box 26 48 31 53; paint m3c
box 80 39 85 44; paint m3c
box 22 57 24 62; label c center m1; port make 1
box 13 48 15 53; label p center m1; port make 2
box 80 39 82 44; label s center m1; port make 3
box 0 104 2 110; label vdd center m1; port make 4
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
save xor_nand4_x1
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
