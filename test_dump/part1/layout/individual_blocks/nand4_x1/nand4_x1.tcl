cellname rename (UNNAMED) nand4_x1
box 0 103 93 142; paint nwell
box 8 10 20 50; paint ndiff
box 19 10 29 50; paint ndiff
box 28 10 38 50; paint ndiff
box 37 10 48 50; paint ndiff
box 8 109 20 129; paint pdiff
box 19 109 29 129; paint pdiff
box 28 109 38 129; paint pdiff
box 37 109 48 129; paint pdiff
box 14 7 16 132; paint poly
box 23 7 25 132; paint poly
box 32 7 34 132; paint poly
box 41 7 43 132; paint poly
box 8 10 12 50; paint ndc
box 44 10 48 50; paint ndc
box 8 109 12 129; paint pdc
box 17 109 21 129; paint pdc
box 26 109 30 129; paint pdc
box 35 109 39 129; paint pdc
box 44 109 48 129; paint pdc
box 13 68 17 73; paint pc
box 22 77 26 82; paint pc
box 31 86 35 91; paint pc
box 40 95 44 100; paint pc
box 4 1 8 5; paint psc
box 28 1 32 5; paint psc
box 52 1 56 5; paint psc
box 76 1 80 5; paint psc
box 4 134 8 138; paint nsc
box 28 134 32 138; paint nsc
box 52 134 56 138; paint nsc
box 76 134 80 138; paint nsc
box 0 0 93 6; paint m1
box 0 133 93 139; paint m1
box 8 10 12 50; paint m1
box 8 10 12 56; paint m1
box 44 10 48 50; paint m1
box 44 0 48 50; paint m1
box 8 109 12 129; paint m1
box 8 103 12 129; paint m1
box 17 109 21 129; paint m1
box 17 109 21 139; paint m1
box 26 109 30 129; paint m1
box 26 103 30 129; paint m1
box 35 109 39 129; paint m1
box 35 109 39 139; paint m1
box 44 109 48 129; paint m1
box 44 103 48 129; paint m1
box 8 59 49 64; paint m1
box 13 68 58 73; paint m1
box 22 77 67 82; paint m1
box 31 86 76 91; paint m1
box 40 95 85 100; paint m1
box 8 51 13 56; paint m2c
box 8 59 13 64; paint m2c
box 8 103 13 108; paint m2c
box 8 59 13 64; paint m2c
box 26 103 31 108; paint m2c
box 26 59 31 64; paint m2c
box 44 103 49 108; paint m2c
box 44 59 49 64; paint m2c
box 53 68 58 73; paint m2c
box 62 77 67 82; paint m2c
box 71 86 76 91; paint m2c
box 80 95 85 100; paint m2c
box 8 51 13 64; paint m2
box 8 59 13 108; paint m2
box 26 59 31 108; paint m2
box 44 59 49 108; paint m2
box 53 68 58 73; paint m2
box 62 77 67 82; paint m2
box 71 86 76 91; paint m2
box 80 95 85 100; paint m2
box 53 68 58 73; paint m3c
box 62 77 67 82; paint m3c
box 71 86 76 91; paint m3c
box 80 95 85 100; paint m3c
box 8 59 13 64; paint m3c
box 13 68 15 73; label i0 center m1; port make 1
box 22 77 24 82; label i1 center m1; port make 2
box 31 86 33 91; label i2 center m1; port make 3
box 40 95 42 100; label i3 center m1; port make 4
box 8 59 10 64; label y center m1; port make 5
box 0 133 2 139; label vdd center m1; port make 6
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
save nand4_x1
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
