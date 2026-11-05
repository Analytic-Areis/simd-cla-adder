cellname rename (UNNAMED) nor4_x1
box 0 73 93 172; paint nwell
box 8 10 20 20; paint ndiff
box 19 10 29 20; paint ndiff
box 28 10 38 20; paint ndiff
box 37 10 48 20; paint ndiff
box 8 79 20 159; paint pdiff
box 19 79 29 159; paint pdiff
box 28 79 38 159; paint pdiff
box 37 79 48 159; paint pdiff
box 14 7 16 162; paint poly
box 23 7 25 162; paint poly
box 32 7 34 162; paint poly
box 41 7 43 162; paint poly
box 8 10 12 20; paint ndc
box 17 10 21 20; paint ndc
box 26 10 30 20; paint ndc
box 35 10 39 20; paint ndc
box 44 10 48 20; paint ndc
box 8 79 12 159; paint pdc
box 44 79 48 159; paint pdc
box 13 38 17 43; paint pc
box 22 47 26 52; paint pc
box 31 56 35 61; paint pc
box 40 65 44 70; paint pc
box 4 1 8 5; paint psc
box 28 1 32 5; paint psc
box 52 1 56 5; paint psc
box 76 1 80 5; paint psc
box 4 164 8 168; paint nsc
box 28 164 32 168; paint nsc
box 52 164 56 168; paint nsc
box 76 164 80 168; paint nsc
box 0 0 93 6; paint m1
box 0 163 93 169; paint m1
box 8 10 12 20; paint m1
box 8 10 12 26; paint m1
box 17 10 21 20; paint m1
box 17 0 21 20; paint m1
box 26 10 30 20; paint m1
box 26 10 30 26; paint m1
box 35 10 39 20; paint m1
box 35 0 39 20; paint m1
box 44 10 48 20; paint m1
box 44 10 48 26; paint m1
box 8 79 12 159; paint m1
box 8 79 12 169; paint m1
box 44 79 48 159; paint m1
box 44 73 48 159; paint m1
box 8 29 49 34; paint m1
box 13 38 58 43; paint m1
box 22 47 67 52; paint m1
box 31 56 76 61; paint m1
box 40 65 85 70; paint m1
box 8 21 13 26; paint m2c
box 8 29 13 34; paint m2c
box 26 21 31 26; paint m2c
box 26 29 31 34; paint m2c
box 44 21 49 26; paint m2c
box 44 29 49 34; paint m2c
box 44 73 49 78; paint m2c
box 44 29 49 34; paint m2c
box 53 38 58 43; paint m2c
box 62 47 67 52; paint m2c
box 71 56 76 61; paint m2c
box 80 65 85 70; paint m2c
box 8 21 13 34; paint m2
box 26 21 31 34; paint m2
box 44 21 49 34; paint m2
box 44 29 49 78; paint m2
box 53 38 58 43; paint m2
box 62 47 67 52; paint m2
box 71 56 76 61; paint m2
box 80 65 85 70; paint m2
box 53 38 58 43; paint m3c
box 62 47 67 52; paint m3c
box 71 56 76 61; paint m3c
box 80 65 85 70; paint m3c
box 44 29 49 34; paint m3c
box 13 38 15 43; label i0 center m1; port make 1
box 22 47 24 52; label i1 center m1; port make 2
box 31 56 33 61; label i2 center m1; port make 3
box 40 65 42 70; label i3 center m1; port make 4
box 8 29 10 34; label y center m1; port make 5
box 0 163 2 169; label vdd center m1; port make 6
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
save nor4_x1
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
