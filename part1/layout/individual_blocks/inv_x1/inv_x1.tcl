cellname rename (UNNAMED) inv_x1
box 0 46 39 85; paint nwell
box 8 10 21 20; paint ndiff
box 8 52 21 72; paint pdiff
box 14 7 16 75; paint poly
box 8 10 12 20; paint ndc
box 17 10 21 20; paint ndc
box 8 52 12 72; paint pdc
box 17 52 21 72; paint pdc
box 13 38 17 43; paint pc
box 4 1 8 5; paint psc
box 28 1 32 5; paint psc
box 4 77 8 81; paint nsc
box 28 77 32 81; paint nsc
box 0 0 39 6; paint m1
box 0 76 39 82; paint m1
box 8 10 12 20; paint m1
box 8 10 12 26; paint m1
box 17 10 21 20; paint m1
box 17 0 21 20; paint m1
box 8 52 12 72; paint m1
box 8 46 12 72; paint m1
box 17 52 21 72; paint m1
box 17 52 21 82; paint m1
box 8 29 13 34; paint m1
box 13 38 31 43; paint m1
box 8 21 13 26; paint m2c
box 8 29 13 34; paint m2c
box 8 46 13 51; paint m2c
box 8 29 13 34; paint m2c
box 26 38 31 43; paint m2c
box 8 21 13 34; paint m2
box 8 29 13 51; paint m2
box 26 38 31 43; paint m2
box 26 38 31 43; paint m3c
box 8 29 13 34; paint m3c
box 13 38 15 43; label a center m1; port make 1
box 8 29 10 34; label y center m1; port make 2
box 0 76 2 82; label vdd center m1; port make 3
box 0 0 2 6; label gnd center m1; port make 4
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
save inv_x1
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
