cellname rename (UNNAMED) gtile
box 0 74 93 133; paint nwell
box 8 20 21 30; paint ndiff
box 26 10 38 30; paint ndiff
box 37 10 48 30; paint ndiff
box 53 10 66 30; paint ndiff
box 8 80 21 100; paint pdiff
box 26 80 38 100; paint pdiff
box 37 80 48 100; paint pdiff
box 53 80 66 120; paint pdiff
box 14 17 16 103; paint poly
box 32 7 34 103; paint poly
box 41 7 43 103; paint poly
box 59 7 61 123; paint poly
box 8 20 12 30; paint ndc
box 17 20 21 30; paint ndc
box 26 10 30 30; paint ndc
box 44 10 48 30; paint ndc
box 53 10 57 30; paint ndc
box 62 10 66 30; paint ndc
box 8 80 12 100; paint pdc
box 17 80 21 100; paint pdc
box 26 80 30 100; paint pdc
box 35 80 39 100; paint pdc
box 44 80 48 100; paint pdc
box 53 80 57 120; paint pdc
box 62 80 66 120; paint pdc
box 13 48 17 53; paint pc
box 31 66 35 71; paint pc
box 40 39 44 44; paint pc
box 58 57 62 62; paint pc
box 4 1 8 5; paint psc
box 28 1 32 5; paint psc
box 52 1 56 5; paint psc
box 76 1 80 5; paint psc
box 4 125 8 129; paint nsc
box 28 125 32 129; paint nsc
box 52 125 56 129; paint nsc
box 76 125 80 129; paint nsc
box 0 0 93 6; paint m1
box 0 124 93 130; paint m1
box 8 20 12 30; paint m1
box 8 20 12 36; paint m1
box 17 20 21 30; paint m1
box 17 0 21 30; paint m1
box 26 10 30 30; paint m1
box 26 10 30 36; paint m1
box 44 10 48 30; paint m1
box 44 0 48 30; paint m1
box 53 10 57 30; paint m1
box 53 10 57 36; paint m1
box 62 10 66 30; paint m1
box 62 0 66 30; paint m1
box 8 80 12 100; paint m1
box 8 74 12 100; paint m1
box 17 80 21 100; paint m1
box 17 80 21 130; paint m1
box 26 80 30 100; paint m1
box 26 74 30 100; paint m1
box 35 80 39 100; paint m1
box 35 80 39 130; paint m1
box 44 80 48 100; paint m1
box 44 74 48 100; paint m1
box 53 80 57 120; paint m1
box 53 74 57 120; paint m1
box 62 80 66 120; paint m1
box 62 80 66 130; paint m1
box 8 39 45 44; paint m1
box 53 39 58 44; paint m1
box 13 48 85 53; paint m1
box 26 57 63 62; paint m1
box 31 66 76 71; paint m1
box 8 31 13 36; paint m2c
box 8 39 13 44; paint m2c
box 26 31 31 36; paint m2c
box 26 57 31 62; paint m2c
box 53 31 58 36; paint m2c
box 53 39 58 44; paint m2c
box 8 74 13 79; paint m2c
box 8 39 13 44; paint m2c
box 26 74 31 79; paint m2c
box 26 57 31 62; paint m2c
box 44 74 49 79; paint m2c
box 44 57 49 62; paint m2c
box 53 74 58 79; paint m2c
box 53 39 58 44; paint m2c
box 71 66 76 71; paint m2c
box 80 48 85 53; paint m2c
box 8 31 13 44; paint m2
box 26 31 31 62; paint m2
box 53 31 58 44; paint m2
box 8 39 13 79; paint m2
box 26 57 31 79; paint m2
box 44 57 49 79; paint m2
box 53 39 58 79; paint m2
box 71 66 76 71; paint m2
box 80 48 85 53; paint m2
box 53 39 58 44; paint m3c
box 71 66 76 71; paint m3c
box 80 48 85 53; paint m3c
box 53 39 55 44; label cin_hi center m1; port make 1
box 31 66 33 71; label cout_lo center m1; port make 2
box 13 48 15 53; label mode center m1; port make 3
box 26 57 28 62; label gn center m1
box 8 39 10 44; label modeb center m1
box 0 124 2 130; label vdd center m1; port make 4
box 0 0 2 6; label gnd center m1; port make 5
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
save gtile
quit -noprompt
