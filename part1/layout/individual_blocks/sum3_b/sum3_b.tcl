cellname rename (UNNAMED) sum3_b
box 0 82 84 121; paint nwell
box 8 10 20 20; paint ndiff
box 19 10 29 20; paint ndiff
box 28 10 38 20; paint ndiff
box 37 10 47 20; paint ndiff
box 46 10 57 20; paint ndiff
box 8 88 20 108; paint pdiff
box 19 88 29 108; paint pdiff
box 28 88 38 108; paint pdiff
box 37 88 47 108; paint pdiff
box 46 88 57 108; paint pdiff
box 14 7 16 111; paint poly
box 23 7 25 111; paint poly
box 32 7 34 111; paint poly
box 41 7 43 111; paint poly
box 50 7 52 111; paint poly
box 8 10 12 20; paint ndc
box 26 10 30 20; paint ndc
box 44 10 48 20; paint ndc
box 53 10 57 20; paint ndc
box 8 88 12 108; paint pdc
box 17 88 21 108; paint pdc
box 26 88 30 108; paint pdc
box 35 88 39 108; paint pdc
box 44 88 48 108; paint pdc
box 53 88 57 108; paint pdc
box 13 38 17 43; paint pc
box 22 47 26 52; paint pc
box 31 74 35 79; paint pc
box 40 29 44 34; paint pc
box 49 38 53 43; paint pc
box 4 1 8 5; paint psc
box 28 1 32 5; paint psc
box 52 1 56 5; paint psc
box 4 113 8 117; paint nsc
box 28 113 32 117; paint nsc
box 52 113 56 117; paint nsc
box 0 0 84 6; paint m1
box 0 112 84 118; paint m1
box 8 10 12 20; paint m1
box 8 0 12 20; paint m1
box 26 10 30 20; paint m1
box 26 10 30 26; paint m1
box 44 10 48 20; paint m1
box 44 0 48 20; paint m1
box 53 10 57 20; paint m1
box 53 10 57 26; paint m1
box 8 88 12 108; paint m1
box 8 82 12 108; paint m1
box 17 88 21 108; paint m1
box 17 88 21 118; paint m1
box 26 88 30 108; paint m1
box 26 82 30 108; paint m1
box 35 88 39 108; paint m1
box 35 82 39 108; paint m1
box 44 88 48 108; paint m1
box 44 82 48 108; paint m1
box 53 88 57 108; paint m1
box 53 88 57 118; paint m1
box 8 29 58 34; paint m1
box 13 38 54 43; paint m1
box 22 47 67 52; paint m1
box 26 56 40 61; paint m1
box 26 65 49 70; paint m1
box 31 74 76 79; paint m1
box 26 21 31 26; paint m2c
box 26 56 31 61; paint m2c
box 53 21 58 26; paint m2c
box 53 29 58 34; paint m2c
box 8 82 13 87; paint m2c
box 8 29 13 34; paint m2c
box 26 82 31 87; paint m2c
box 26 65 31 70; paint m2c
box 35 82 40 87; paint m2c
box 35 56 40 61; paint m2c
box 44 82 49 87; paint m2c
box 44 65 49 70; paint m2c
box 17 38 22 43; paint m2c
box 62 47 67 52; paint m2c
box 71 74 76 79; paint m2c
box 26 21 31 61; paint m2
box 53 21 58 34; paint m2
box 8 29 13 87; paint m2
box 26 65 31 87; paint m2
box 35 56 40 87; paint m2
box 44 65 49 87; paint m2
box 17 38 22 43; paint m2
box 62 47 67 52; paint m2
box 71 74 76 79; paint m2
box 17 38 22 43; paint m3c
box 62 47 67 52; paint m3c
box 71 74 76 79; paint m3c
box 35 56 40 61; paint m3c
box 13 38 15 43; label c3 center m1; port make 1
box 22 47 24 52; label p3 center m1; port make 2
box 31 74 33 79; label p3b center m1; port make 3
box 26 56 28 61; label s3 center m1; port make 4
box 8 29 10 34; label x3_cb center m1
box 26 65 28 70; label x3_s1xp1 center m1
box 0 112 2 118; label vdd center m1; port make 5
box 0 0 2 6; label gnd center m1; port make 6
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
save sum3_b
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
