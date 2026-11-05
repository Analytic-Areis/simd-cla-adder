cellname rename (UNNAMED) sum0
box 0 90 84 144; paint nwell
box 8 10 20 28; paint ndiff
box 19 10 29 28; paint ndiff
box 28 10 38 28; paint ndiff
box 37 10 47 28; paint ndiff
box 46 24 57 28; paint ndiff
box 8 96 20 103; paint pdiff
box 19 96 29 131; paint pdiff
box 28 96 38 131; paint pdiff
box 37 96 47 131; paint pdiff
box 46 96 57 131; paint pdiff
box 14 7 16 106; paint poly
box 23 7 25 134; paint poly
box 32 7 34 134; paint poly
box 41 7 43 134; paint poly
box 50 21 52 134; paint poly
box 8 10 12 28; paint ndc
box 26 10 30 28; paint ndc
box 44 10 48 28; paint ndc
box 53 24 57 28; paint ndc
box 8 96 12 103; paint pdc
box 17 96 21 131; paint pdc
box 26 96 30 131; paint pdc
box 35 96 39 131; paint pdc
box 44 96 48 131; paint pdc
box 53 96 57 131; paint pdc
box 13 46 17 51; paint pc
box 22 55 26 60; paint pc
box 31 82 35 87; paint pc
box 40 37 44 42; paint pc
box 49 46 53 51; paint pc
box 4 1 8 5; paint psc
box 28 1 32 5; paint psc
box 52 1 56 5; paint psc
box 4 136 8 140; paint nsc
box 28 136 32 140; paint nsc
box 52 136 56 140; paint nsc
box 0 0 84 6; paint m1
box 0 135 84 141; paint m1
box 8 10 12 28; paint m1
box 8 0 12 28; paint m1
box 26 10 30 28; paint m1
box 26 10 30 34; paint m1
box 44 10 48 28; paint m1
box 44 0 48 28; paint m1
box 53 24 57 28; paint m1
box 53 24 57 34; paint m1
box 8 96 12 103; paint m1
box 8 90 12 103; paint m1
box 17 96 21 131; paint m1
box 17 96 21 141; paint m1
box 26 96 30 131; paint m1
box 26 90 30 131; paint m1
box 35 96 39 131; paint m1
box 35 90 39 131; paint m1
box 44 96 48 131; paint m1
box 44 90 48 131; paint m1
box 53 96 57 131; paint m1
box 53 96 57 141; paint m1
box 8 37 58 42; paint m1
box 13 46 54 51; paint m1
box 22 55 67 60; paint m1
box 26 64 40 69; paint m1
box 26 73 49 78; paint m1
box 31 82 76 87; paint m1
box 26 29 31 34; paint m2c
box 26 64 31 69; paint m2c
box 53 29 58 34; paint m2c
box 53 37 58 42; paint m2c
box 8 90 13 95; paint m2c
box 8 37 13 42; paint m2c
box 26 90 31 95; paint m2c
box 26 73 31 78; paint m2c
box 35 90 40 95; paint m2c
box 35 64 40 69; paint m2c
box 44 90 49 95; paint m2c
box 44 73 49 78; paint m2c
box 17 46 22 51; paint m2c
box 62 55 67 60; paint m2c
box 71 82 76 87; paint m2c
box 26 29 31 69; paint m2
box 53 29 58 42; paint m2
box 8 37 13 95; paint m2
box 26 73 31 95; paint m2
box 35 64 40 95; paint m2
box 44 73 49 95; paint m2
box 17 46 22 51; paint m2
box 62 55 67 60; paint m2
box 71 82 76 87; paint m2
box 17 46 22 51; paint m3c
box 62 55 67 60; paint m3c
box 71 82 76 87; paint m3c
box 35 64 40 69; paint m3c
box 13 46 15 51; label c0 center m1; port make 1
box 22 55 24 60; label p0 center m1; port make 2
box 31 82 33 87; label p0b center m1; port make 3
box 26 64 28 69; label s0 center m1; port make 4
box 8 37 10 42; label x0_cb center m1
box 26 73 28 78; label x0_s1xp1 center m1
box 0 135 2 141; label vdd center m1; port make 5
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
save sum0
quit -noprompt
