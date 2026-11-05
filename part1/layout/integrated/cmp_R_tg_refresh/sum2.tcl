cellname rename (UNNAMED) sum2
box 0 82 75 121; paint nwell
box 8 16 20 20; paint ndiff
box 19 12 30 20; paint ndiff
box 35 15 47 20; paint ndiff
box 46 15 57 20; paint ndiff
box 8 88 20 96; paint pdiff
box 19 88 30 104; paint pdiff
box 35 88 47 98; paint pdiff
box 46 88 57 98; paint pdiff
box 14 13 16 99; paint poly
box 23 9 25 107; paint poly
box 41 12 43 101; paint poly
box 50 12 52 101; paint poly
box 8 16 12 20; paint ndc
box 17 12 21 20; paint ndc
box 26 12 30 20; paint ndc
box 35 15 39 20; paint ndc
box 44 15 48 20; paint ndc
box 53 15 57 20; paint ndc
box 8 88 12 96; paint pdc
box 17 88 21 104; paint pdc
box 26 88 30 104; paint pdc
box 35 88 39 98; paint pdc
box 44 88 48 98; paint pdc
box 53 88 57 98; paint pdc
box 13 38 17 43; paint pc
box 22 47 26 52; paint pc
box 40 29 44 34; paint pc
box 49 38 53 43; paint pc
box 4 1 8 5; paint psc
box 28 1 32 5; paint psc
box 52 1 56 5; paint psc
box 4 113 8 117; paint nsc
box 28 113 32 117; paint nsc
box 52 113 56 117; paint nsc
box 0 0 75 6; paint m1
box 0 112 75 118; paint m1
box 8 16 12 20; paint m1
box 8 16 12 26; paint m1
box 17 12 21 20; paint m1
box 17 0 21 20; paint m1
box 26 12 30 20; paint m1
box 26 12 30 26; paint m1
box 35 15 39 20; paint m1
box 35 15 39 26; paint m1
box 44 15 48 20; paint m1
box 44 15 48 26; paint m1
box 53 15 57 20; paint m1
box 53 15 57 26; paint m1
box 8 88 12 96; paint m1
box 8 82 12 96; paint m1
box 17 88 21 104; paint m1
box 17 88 21 118; paint m1
box 26 88 30 104; paint m1
box 26 82 30 104; paint m1
box 35 88 39 98; paint m1
box 35 82 39 98; paint m1
box 44 88 48 98; paint m1
box 44 82 48 98; paint m1
box 53 88 57 98; paint m1
box 53 82 57 98; paint m1
box 8 29 45 34; paint m1
box 53 29 67 34; paint m1
box 13 38 54 43; paint m1
box 22 47 49 52; paint m1
box 26 56 31 61; paint m1
box 35 65 58 70; paint m1
box 35 74 67 79; paint m1
box 8 21 13 26; paint m2c
box 8 29 13 34; paint m2c
box 26 21 31 26; paint m2c
box 26 56 31 61; paint m2c
box 35 21 40 26; paint m2c
box 35 65 40 70; paint m2c
box 44 21 49 26; paint m2c
box 44 47 49 52; paint m2c
box 53 21 58 26; paint m2c
box 53 29 58 34; paint m2c
box 8 82 13 87; paint m2c
box 8 29 13 34; paint m2c
box 26 82 31 87; paint m2c
box 26 56 31 61; paint m2c
box 35 82 40 87; paint m2c
box 35 74 40 79; paint m2c
box 44 82 49 87; paint m2c
box 44 47 49 52; paint m2c
box 53 82 58 87; paint m2c
box 53 65 58 70; paint m2c
box 62 74 67 79; paint m2c
box 62 29 67 34; paint m2c
box 17 38 22 43; paint m2c
box 8 21 13 34; paint m2
box 26 21 31 61; paint m2
box 35 21 40 70; paint m2
box 44 21 49 52; paint m2
box 53 21 58 34; paint m2
box 8 29 13 87; paint m2
box 26 56 31 87; paint m2
box 35 74 40 87; paint m2
box 44 47 49 87; paint m2
box 53 65 58 87; paint m2
box 62 29 67 79; paint m2
box 17 38 22 43; paint m2
box 17 38 22 43; paint m3c
box 35 74 40 79; paint m3c
box 53 65 58 70; paint m3c
box 26 56 31 61; paint m3c
box 13 38 15 43; label c2 center m1; port make 1
box 35 74 37 79; label p2 center m1; port make 2
box 35 65 37 70; label p2b center m1; port make 3
box 26 56 28 61; label s2 center m1; port make 4
box 8 29 10 34; label x2_cb center m1
box 22 47 24 52; label x2_m center m1
box 0 112 2 118; label vdd center m1; port make 5
box 0 0 2 6; label gnd center m1; port make 6
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
save sum2
quit -noprompt
