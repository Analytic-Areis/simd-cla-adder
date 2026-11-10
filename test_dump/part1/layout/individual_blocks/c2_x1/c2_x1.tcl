cellname rename (UNNAMED) c2_x1
box 0 111 120 190; paint nwell
box 8 10 21 40; paint ndiff
box 26 20 38 40; paint ndiff
box 37 10 47 40; paint ndiff
box 46 10 56 40; paint ndiff
box 55 10 66 40; paint ndiff
box 8 117 24 137; paint pdiff
box 24 117 38 177; paint pdiff
box 37 117 47 157; paint pdiff
box 46 117 56 177; paint pdiff
box 55 117 66 177; paint pdiff
box 14 7 16 140; paint poly
box 32 17 34 180; paint poly
box 41 7 43 160; paint poly
box 50 7 52 180; paint poly
box 59 7 61 180; paint poly
box 8 10 12 40; paint ndc
box 17 10 21 40; paint ndc
box 26 20 30 40; paint ndc
box 35 10 39 40; paint ndc
box 44 10 48 40; paint ndc
box 53 10 57 40; paint ndc
box 62 10 66 40; paint ndc
box 8 117 12 137; paint pdc
box 22 117 26 177; paint pdc
box 35 117 39 177; paint pdc
box 44 117 48 177; paint pdc
box 62 117 66 177; paint pdc
box 13 58 17 63; paint pc
box 31 67 35 72; paint pc
box 40 76 44 81; paint pc
box 49 49 53 54; paint pc
box 58 94 62 99; paint pc
box 4 1 8 5; paint psc
box 28 1 32 5; paint psc
box 52 1 56 5; paint psc
box 76 1 80 5; paint psc
box 100 1 104 5; paint psc
box 4 182 8 186; paint nsc
box 28 182 32 186; paint nsc
box 52 182 56 186; paint nsc
box 76 182 80 186; paint nsc
box 100 182 104 186; paint nsc
box 0 0 120 6; paint m1
box 0 181 120 187; paint m1
box 8 10 12 40; paint m1
box 8 10 12 46; paint m1
box 17 10 21 40; paint m1
box 17 10 21 46; paint m1
box 26 20 30 40; paint m1
box 26 0 30 40; paint m1
box 35 10 39 40; paint m1
box 35 10 39 46; paint m1
box 44 10 48 40; paint m1
box 44 10 48 46; paint m1
box 53 10 57 40; paint m1
box 53 0 57 40; paint m1
box 62 10 66 40; paint m1
box 62 10 66 46; paint m1
box 8 117 12 137; paint m1
box 8 111 12 137; paint m1
box 22 117 26 177; paint m1
box 22 117 26 187; paint m1
box 35 117 39 177; paint m1
box 35 111 39 177; paint m1
box 44 117 48 177; paint m1
box 44 111 48 177; paint m1
box 62 117 66 177; paint m1
box 62 111 66 177; paint m1
box 8 49 40 54; paint m1
box 49 49 76 54; paint m1
box 13 58 94 63; paint m1
box 31 67 112 72; paint m1
box 40 76 85 81; paint m1
box 44 85 67 90; paint m1
box 8 94 49 99; paint m1
box 58 94 103 99; paint m1
box 35 103 67 108; paint m1
box 8 41 13 46; paint m2c
box 8 49 13 54; paint m2c
box 17 41 22 46; paint m2c
box 17 94 22 99; paint m2c
box 35 41 40 46; paint m2c
box 35 49 40 54; paint m2c
box 44 41 49 46; paint m2c
box 44 85 49 90; paint m2c
box 62 41 67 46; paint m2c
box 62 85 67 90; paint m2c
box 8 111 13 116; paint m2c
box 8 94 13 99; paint m2c
box 35 111 40 116; paint m2c
box 35 103 40 108; paint m2c
box 44 111 49 116; paint m2c
box 44 94 49 99; paint m2c
box 62 111 67 116; paint m2c
box 62 103 67 108; paint m2c
box 71 49 76 54; paint m2c
box 80 76 85 81; paint m2c
box 89 58 94 63; paint m2c
box 98 94 103 99; paint m2c
box 107 67 112 72; paint m2c
box 8 41 13 54; paint m2
box 17 41 22 99; paint m2
box 35 41 40 54; paint m2
box 44 41 49 90; paint m2
box 62 41 67 90; paint m2
box 8 94 13 116; paint m2
box 35 103 40 116; paint m2
box 44 94 49 116; paint m2
box 62 103 67 116; paint m2
box 71 49 76 54; paint m2
box 80 76 85 81; paint m2
box 89 58 94 63; paint m2
box 98 94 103 99; paint m2
box 107 67 112 72; paint m2
box 71 49 76 54; paint m3c
box 8 94 13 99; paint m3c
box 80 76 85 81; paint m3c
box 89 58 94 63; paint m3c
box 98 94 103 99; paint m3c
box 107 67 112 72; paint m3c
box 49 49 51 54; label c0b center m1; port make 1
box 8 94 10 99; label c2 center m1; port make 2
box 40 76 42 81; label g0b center m1; port make 3
box 13 58 15 63; label g1b center m1; port make 4
box 58 94 60 99; label t0b center m1; port make 5
box 31 67 33 72; label t1b center m1; port make 6
box 0 181 2 187; label vdd center m1; port make 7
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
save c2_x1
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
