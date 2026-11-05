cellname rename (UNNAMED) sum0
box 0 102 84 181; paint nwell
box 8 10 20 40; paint ndiff
box 19 10 29 40; paint ndiff
box 28 10 38 40; paint ndiff
box 37 10 47 40; paint ndiff
box 46 34 57 40; paint ndiff
box 8 108 20 120; paint pdiff
box 19 108 29 168; paint pdiff
box 28 108 38 168; paint pdiff
box 37 108 47 168; paint pdiff
box 46 108 57 168; paint pdiff
box 14 7 16 123; paint poly
box 23 7 25 171; paint poly
box 32 7 34 171; paint poly
box 41 7 43 171; paint poly
box 50 31 52 171; paint poly
box 8 10 12 40; paint ndc
box 26 10 30 40; paint ndc
box 44 10 48 40; paint ndc
box 53 34 57 40; paint ndc
box 8 108 12 120; paint pdc
box 17 108 21 168; paint pdc
box 26 108 30 168; paint pdc
box 35 108 39 168; paint pdc
box 44 108 48 168; paint pdc
box 53 108 57 168; paint pdc
box 13 58 17 63; paint pc
box 22 67 26 72; paint pc
box 31 94 35 99; paint pc
box 40 49 44 54; paint pc
box 49 58 53 63; paint pc
box 4 1 8 5; paint psc
box 28 1 32 5; paint psc
box 52 1 56 5; paint psc
box 4 173 8 177; paint nsc
box 28 173 32 177; paint nsc
box 52 173 56 177; paint nsc
box 0 0 84 6; paint m1
box 0 172 84 178; paint m1
box 8 10 12 40; paint m1
box 8 0 12 40; paint m1
box 26 10 30 40; paint m1
box 26 10 30 46; paint m1
box 44 10 48 40; paint m1
box 44 0 48 40; paint m1
box 53 34 57 40; paint m1
box 53 34 57 46; paint m1
box 8 108 12 120; paint m1
box 8 102 12 120; paint m1
box 17 108 21 168; paint m1
box 17 108 21 178; paint m1
box 26 108 30 168; paint m1
box 26 102 30 168; paint m1
box 35 108 39 168; paint m1
box 35 102 39 168; paint m1
box 44 108 48 168; paint m1
box 44 102 48 168; paint m1
box 53 108 57 168; paint m1
box 53 108 57 178; paint m1
box 8 49 58 54; paint m1
box 13 58 54 63; paint m1
box 22 67 67 72; paint m1
box 26 76 40 81; paint m1
box 26 85 49 90; paint m1
box 31 94 76 99; paint m1
box 26 41 31 46; paint m2c
box 26 76 31 81; paint m2c
box 53 41 58 46; paint m2c
box 53 49 58 54; paint m2c
box 8 102 13 107; paint m2c
box 8 49 13 54; paint m2c
box 26 102 31 107; paint m2c
box 26 85 31 90; paint m2c
box 35 102 40 107; paint m2c
box 35 76 40 81; paint m2c
box 44 102 49 107; paint m2c
box 44 85 49 90; paint m2c
box 17 58 22 63; paint m2c
box 62 67 67 72; paint m2c
box 71 94 76 99; paint m2c
box 26 41 31 81; paint m2
box 53 41 58 54; paint m2
box 8 49 13 107; paint m2
box 26 85 31 107; paint m2
box 35 76 40 107; paint m2
box 44 85 49 107; paint m2
box 17 58 22 63; paint m2
box 62 67 67 72; paint m2
box 71 94 76 99; paint m2
box 17 58 22 63; paint m3c
box 62 67 67 72; paint m3c
box 71 94 76 99; paint m3c
box 35 76 40 81; paint m3c
box 13 58 15 63; label c0 center m1; port make 1
box 22 67 24 72; label p0 center m1; port make 2
box 31 94 33 99; label p0b center m1; port make 3
box 26 76 28 81; label s0 center m1; port make 4
box 8 49 10 54; label x0_cb center m1
box 26 85 28 90; label x0_s1xp1 center m1
box 0 172 2 178; label vdd center m1; port make 5
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
