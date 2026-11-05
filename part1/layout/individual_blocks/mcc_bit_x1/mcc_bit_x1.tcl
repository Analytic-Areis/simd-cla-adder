cellname rename (UNNAMED) mcc_bit_x1
box 0 82 66 121; paint nwell
box 8 10 20 20; paint ndiff
box 19 10 30 20; paint ndiff
box 8 88 20 108; paint pdiff
box 19 88 30 108; paint pdiff
box 14 7 16 111; paint poly
box 23 7 25 111; paint poly
box 8 10 12 20; paint ndc
box 17 10 21 20; paint ndc
box 26 10 30 20; paint ndc
box 8 88 12 108; paint pdc
box 17 88 21 108; paint pdc
box 26 88 30 108; paint pdc
box 13 29 17 34; paint pc
box 22 47 26 52; paint pc
box 4 1 8 5; paint psc
box 28 1 32 5; paint psc
box 52 1 56 5; paint psc
box 4 113 8 117; paint nsc
box 28 113 32 117; paint nsc
box 52 113 56 117; paint nsc
box 0 0 66 6; paint m1
box 0 112 66 118; paint m1
box 8 10 12 20; paint m1
box 8 10 12 26; paint m1
box 17 10 21 20; paint m1
box 17 10 21 26; paint m1
box 26 10 30 20; paint m1
box 26 10 30 26; paint m1
box 8 88 12 108; paint m1
box 8 82 12 108; paint m1
box 17 88 21 108; paint m1
box 17 82 21 108; paint m1
box 26 88 30 108; paint m1
box 26 82 30 108; paint m1
box 13 29 58 34; paint m1
box 17 38 22 43; paint m1
box 22 47 49 52; paint m1
box 26 56 40 61; paint m1
box 8 65 31 70; paint m1
box 8 74 40 79; paint m1
box 8 21 13 26; paint m2c
box 8 65 13 70; paint m2c
box 17 21 22 26; paint m2c
box 17 38 22 43; paint m2c
box 26 21 31 26; paint m2c
box 26 56 31 61; paint m2c
box 8 82 13 87; paint m2c
box 8 74 13 79; paint m2c
box 17 82 22 87; paint m2c
box 17 38 22 43; paint m2c
box 26 82 31 87; paint m2c
box 26 65 31 70; paint m2c
box 35 74 40 79; paint m2c
box 35 56 40 61; paint m2c
box 44 47 49 52; paint m2c
box 53 29 58 34; paint m2c
box 8 21 13 70; paint m2
box 17 21 22 43; paint m2
box 26 21 31 61; paint m2
box 8 74 13 87; paint m2
box 17 38 22 87; paint m2
box 26 65 31 87; paint m2
box 35 56 40 79; paint m2
box 44 47 49 52; paint m2
box 53 29 58 34; paint m2
box 26 65 31 70; paint m3c
box 8 74 13 79; paint m3c
box 17 38 22 43; paint m3c
box 44 47 49 52; paint m3c
box 53 29 58 34; paint m3c
box 8 65 10 70; label a center m1; port make 1
box 8 74 10 79; label ci center m1; port make 2
box 17 38 19 43; label co center m1; port make 3
box 22 47 24 52; label p center m1; port make 4
box 13 29 15 34; label pb center m1; port make 5
box 0 112 2 118; label vdd center m1; port make 6
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
save mcc_bit_x1
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
