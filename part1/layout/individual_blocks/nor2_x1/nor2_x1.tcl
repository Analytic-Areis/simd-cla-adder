cellname rename (UNNAMED) nor2_x1
box 0 55 57 114; paint nwell
box 8 10 20 20; paint ndiff
box 19 10 30 20; paint ndiff
box 8 61 20 101; paint pdiff
box 19 61 30 101; paint pdiff
box 14 7 16 104; paint poly
box 23 7 25 104; paint poly
box 8 10 12 20; paint ndc
box 17 10 21 20; paint ndc
box 26 10 30 20; paint ndc
box 8 61 12 101; paint pdc
box 26 61 30 101; paint pdc
box 13 38 17 43; paint pc
box 22 47 26 52; paint pc
box 4 1 8 5; paint psc
box 28 1 32 5; paint psc
box 4 106 8 110; paint nsc
box 28 106 32 110; paint nsc
box 0 0 57 6; paint m1
box 0 105 57 111; paint m1
box 8 10 12 20; paint m1
box 8 10 12 26; paint m1
box 17 10 21 20; paint m1
box 17 0 21 20; paint m1
box 26 10 30 20; paint m1
box 26 10 30 26; paint m1
box 8 61 12 101; paint m1
box 8 61 12 111; paint m1
box 26 61 30 101; paint m1
box 26 55 30 101; paint m1
box 8 29 31 34; paint m1
box 13 38 40 43; paint m1
box 22 47 49 52; paint m1
box 8 21 13 26; paint m2c
box 8 29 13 34; paint m2c
box 26 21 31 26; paint m2c
box 26 29 31 34; paint m2c
box 26 55 31 60; paint m2c
box 26 29 31 34; paint m2c
box 35 38 40 43; paint m2c
box 44 47 49 52; paint m2c
box 8 21 13 34; paint m2
box 26 21 31 34; paint m2
box 26 29 31 60; paint m2
box 35 38 40 43; paint m2
box 44 47 49 52; paint m2
box 35 38 40 43; paint m3c
box 44 47 49 52; paint m3c
box 26 29 31 34; paint m3c
box 13 38 15 43; label i0 center m1; port make 1
box 22 47 24 52; label i1 center m1; port make 2
box 8 29 10 34; label y center m1; port make 3
box 0 105 2 111; label vdd center m1; port make 4
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
save nor2_x1
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
