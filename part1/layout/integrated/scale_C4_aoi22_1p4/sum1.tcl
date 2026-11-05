cellname rename (UNNAMED) sum1
box 0 107 84 196; paint nwell
box 8 17 20 45; paint ndiff
box 19 17 29 45; paint ndiff
box 28 17 38 45; paint ndiff
box 37 17 47 45; paint ndiff
box 46 36 57 45; paint ndiff
box 8 113 20 131; paint pdiff
box 19 113 29 169; paint pdiff
box 28 113 38 169; paint pdiff
box 37 113 47 169; paint pdiff
box 46 113 57 169; paint pdiff
box 14 14 16 134; paint poly
box 23 14 25 172; paint poly
box 32 14 34 172; paint poly
box 41 14 43 172; paint poly
box 50 33 52 172; paint poly
box 8 17 12 45; paint ndc
box 26 17 30 45; paint ndc
box 44 17 48 45; paint ndc
box 53 36 57 45; paint ndc
box 8 113 12 131; paint pdc
box 17 113 21 169; paint pdc
box 26 113 30 169; paint pdc
box 35 113 39 169; paint pdc
box 44 113 48 169; paint pdc
box 53 113 57 169; paint pdc
box 13 63 17 68; paint pc
box 22 72 26 77; paint pc
box 31 99 35 104; paint pc
box 40 54 44 59; paint pc
box 49 63 53 68; paint pc
box 4 1 8 5; paint psc
box 28 1 32 5; paint psc
box 52 1 56 5; paint psc
box 4 188 8 192; paint nsc
box 28 188 32 192; paint nsc
box 52 188 56 192; paint nsc
box 0 0 84 6; paint m1
box 0 187 84 193; paint m1
box 8 17 12 45; paint m1
box 8 0 12 45; paint m1
box 26 17 30 45; paint m1
box 26 17 30 51; paint m1
box 44 17 48 45; paint m1
box 44 0 48 45; paint m1
box 53 36 57 45; paint m1
box 53 36 57 51; paint m1
box 8 113 12 131; paint m1
box 8 107 12 131; paint m1
box 17 113 21 169; paint m1
box 17 113 21 193; paint m1
box 26 113 30 169; paint m1
box 26 107 30 169; paint m1
box 35 113 39 169; paint m1
box 35 107 39 169; paint m1
box 44 113 48 169; paint m1
box 44 107 48 169; paint m1
box 53 113 57 169; paint m1
box 53 113 57 193; paint m1
box 8 54 58 59; paint m1
box 13 63 54 68; paint m1
box 22 72 67 77; paint m1
box 26 81 40 86; paint m1
box 26 90 49 95; paint m1
box 31 99 76 104; paint m1
box 26 46 31 51; paint m2c
box 26 81 31 86; paint m2c
box 53 46 58 51; paint m2c
box 53 54 58 59; paint m2c
box 8 107 13 112; paint m2c
box 8 54 13 59; paint m2c
box 26 107 31 112; paint m2c
box 26 90 31 95; paint m2c
box 35 107 40 112; paint m2c
box 35 81 40 86; paint m2c
box 44 107 49 112; paint m2c
box 44 90 49 95; paint m2c
box 17 63 22 68; paint m2c
box 62 72 67 77; paint m2c
box 71 99 76 104; paint m2c
box 26 46 31 86; paint m2
box 53 46 58 59; paint m2
box 8 54 13 112; paint m2
box 26 90 31 112; paint m2
box 35 81 40 112; paint m2
box 44 90 49 112; paint m2
box 17 63 22 68; paint m2
box 62 72 67 77; paint m2
box 71 99 76 104; paint m2
box 17 63 22 68; paint m3c
box 62 72 67 77; paint m3c
box 71 99 76 104; paint m3c
box 35 81 40 86; paint m3c
box 13 63 15 68; label c1 center m1; port make 1
box 22 72 24 77; label p1 center m1; port make 2
box 31 99 33 104; label p1b center m1; port make 3
box 26 81 28 86; label s1 center m1; port make 4
box 8 54 10 59; label x1_cb center m1
box 26 90 28 95; label x1_s1xp1 center m1
box 0 187 2 193; label vdd center m1; port make 5
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
save sum1
quit -noprompt
