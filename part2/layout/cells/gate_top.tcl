cellname rename (UNNAMED) gate_top
box 0 0 0 0; getcell gtile
box -28 -6 -22 139; paint m2
box -16 -6 -10 139; paint m2
box 0 78 93 133; paint nwell
box 0 124 93 130; paint m1
box 0 0 93 6; paint m1
box -28 124 0 130; paint m1
box -28 124 -22 130; paint m2c
box -16 0 0 6; paint m1
box -16 0 -10 6; paint m2c
box 80 44 85 53; paint m3
box 53 35 58 44; paint m3
box 44 159 52 164; paint m3
box 71 62 76 71; paint m3
box 8 159 16 164; paint m3
box 35 161 47 164; paint m3
box 34 160 39 165; paint m4c
box 35 152 38 164; paint m4
box 35 143 38 155; paint m4
box 35 134 38 146; paint m4
box 35 125 38 137; paint m4
box 35 116 38 128; paint m4
box 35 107 38 119; paint m4
box 35 98 38 110; paint m4
box 35 89 38 101; paint m4
box 35 80 38 92; paint m4
box 35 71 38 83; paint m4
box 35 62 38 74; paint m4
box 35 53 38 65; paint m4
box 35 44 38 56; paint m4
box 35 35 38 47; paint m4
box 34 34 39 39; paint m4c
box 35 35 47 38; paint m3
box 44 35 56 38; paint m3
box 8 161 20 164; paint m3
box 17 161 29 164; paint m3
box 25 160 30 165; paint m4c
box 26 152 29 164; paint m4
box 26 143 29 155; paint m4
box 26 134 29 146; paint m4
box 26 125 29 137; paint m4
box 26 116 29 128; paint m4
box 26 107 29 119; paint m4
box 26 98 29 110; paint m4
box 26 89 29 101; paint m4
box 26 80 29 92; paint m4
box 26 71 29 83; paint m4
box 26 62 29 74; paint m4
box 25 61 30 66; paint m4c
box 26 62 38 65; paint m3
box 35 62 47 65; paint m3
box 44 62 56 65; paint m3
box 53 62 65 65; paint m3
box 62 62 74 65; paint m3
box 11 159 16 164; paint m3
box 47 159 52 164; paint m3
box 53 38 56 41; paint m3
box 71 65 74 68; paint m3
box 16 161 19 164; paint m3
box 55 39 56 44; label cin_hi center m3; port make 1
box 73 66 74 71; label cout_lo center m3; port make 2
box 82 48 83 53; label mode center m3; port make 3
box -28 133 -22 139; label vdd center m2; port make 4
box -16 133 -10 139; label gnd center m2; port make 5
save gate_top
select top cell
drc euclidean on
drc style drc
drc check
drc catchup
set why [drc listall why]
set total 0
foreach {message boxes} $why {
    incr total [llength $boxes]
    puts "DRC_ERR $message : [lrange $boxes 0 3]"
}
puts "DRC_COUNT $total"
save gate_top
extract do local
extract all
ext2spice lvs
ext2spice cthresh 0
ext2spice rthresh 0
ext2spice format ngspice
ext2spice hierarchy off
ext2spice subcircuit top on
ext2spice
puts DONE
quit -noprompt
