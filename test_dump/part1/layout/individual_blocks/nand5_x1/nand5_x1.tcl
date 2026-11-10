cellname rename (UNNAMED) nand5_x1
box 0 122 111 161; paint nwell
box 8 10 20 60; paint ndiff
box 19 10 29 60; paint ndiff
box 28 10 38 60; paint ndiff
box 37 10 47 60; paint ndiff
box 46 10 57 60; paint ndiff
box 8 128 20 148; paint pdiff
box 19 128 29 148; paint pdiff
box 28 128 38 148; paint pdiff
box 37 128 47 148; paint pdiff
box 46 128 57 148; paint pdiff
box 14 7 16 151; paint poly
box 23 7 25 151; paint poly
box 32 7 34 151; paint poly
box 41 7 43 151; paint poly
box 50 7 52 151; paint poly
box 8 10 12 60; paint ndc
box 53 10 57 60; paint ndc
box 8 128 12 148; paint pdc
box 17 128 21 148; paint pdc
box 26 128 30 148; paint pdc
box 35 128 39 148; paint pdc
box 44 128 48 148; paint pdc
box 53 128 57 148; paint pdc
box 13 78 17 83; paint pc
box 22 87 26 92; paint pc
box 31 96 35 101; paint pc
box 40 105 44 110; paint pc
box 49 114 53 119; paint pc
box 4 1 8 5; paint psc
box 28 1 32 5; paint psc
box 52 1 56 5; paint psc
box 76 1 80 5; paint psc
box 100 1 104 5; paint psc
box 4 153 8 157; paint nsc
box 28 153 32 157; paint nsc
box 52 153 56 157; paint nsc
box 76 153 80 157; paint nsc
box 100 153 104 157; paint nsc
box 0 0 111 6; paint m1
box 0 152 111 158; paint m1
box 8 10 12 60; paint m1
box 8 10 12 66; paint m1
box 53 10 57 60; paint m1
box 53 0 57 60; paint m1
box 8 128 12 148; paint m1
box 8 122 12 148; paint m1
box 17 128 21 148; paint m1
box 17 128 21 158; paint m1
box 26 128 30 148; paint m1
box 26 122 30 148; paint m1
box 35 128 39 148; paint m1
box 35 128 39 158; paint m1
box 44 128 48 148; paint m1
box 44 122 48 148; paint m1
box 53 128 57 148; paint m1
box 53 128 57 158; paint m1
box 8 69 49 74; paint m1
box 13 78 67 83; paint m1
box 22 87 76 92; paint m1
box 31 96 85 101; paint m1
box 40 105 94 110; paint m1
box 49 114 103 119; paint m1
box 8 61 13 66; paint m2c
box 8 69 13 74; paint m2c
box 8 122 13 127; paint m2c
box 8 69 13 74; paint m2c
box 26 122 31 127; paint m2c
box 26 69 31 74; paint m2c
box 44 122 49 127; paint m2c
box 44 69 49 74; paint m2c
box 62 78 67 83; paint m2c
box 71 87 76 92; paint m2c
box 80 96 85 101; paint m2c
box 89 105 94 110; paint m2c
box 98 114 103 119; paint m2c
box 8 61 13 74; paint m2
box 8 69 13 127; paint m2
box 26 69 31 127; paint m2
box 44 69 49 127; paint m2
box 62 78 67 83; paint m2
box 71 87 76 92; paint m2
box 80 96 85 101; paint m2
box 89 105 94 110; paint m2
box 98 114 103 119; paint m2
box 62 78 67 83; paint m3c
box 71 87 76 92; paint m3c
box 80 96 85 101; paint m3c
box 89 105 94 110; paint m3c
box 98 114 103 119; paint m3c
box 8 69 13 74; paint m3c
box 13 78 15 83; label i0 center m1; port make 1
box 22 87 24 92; label i1 center m1; port make 2
box 31 96 33 101; label i2 center m1; port make 3
box 40 105 42 110; label i3 center m1; port make 4
box 49 114 51 119; label i4 center m1; port make 5
box 8 69 10 74; label y center m1; port make 6
box 0 152 2 158; label vdd center m1; port make 7
box 0 0 2 6; label gnd center m1; port make 8
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
save nand5_x1
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
