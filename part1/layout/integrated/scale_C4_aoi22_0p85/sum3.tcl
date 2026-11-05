cellname rename (UNNAMED) sum3
box 0 93 84 154; paint nwell
box 8 22 20 31; paint ndiff
box 19 22 29 31; paint ndiff
box 28 22 38 31; paint ndiff
box 37 22 47 31; paint ndiff
box 46 23 57 31; paint ndiff
box 8 99 20 116; paint pdiff
box 19 99 29 116; paint pdiff
box 28 99 38 116; paint pdiff
box 37 99 47 116; paint pdiff
box 46 99 57 116; paint pdiff
box 14 19 16 119; paint poly
box 23 19 25 119; paint poly
box 32 19 34 119; paint poly
box 41 19 43 119; paint poly
box 50 20 52 119; paint poly
box 8 22 12 31; paint ndc
box 26 22 30 31; paint ndc
box 44 22 48 31; paint ndc
box 53 23 57 31; paint ndc
box 8 99 12 116; paint pdc
box 17 99 21 116; paint pdc
box 26 99 30 116; paint pdc
box 35 99 39 116; paint pdc
box 44 99 48 116; paint pdc
box 53 99 57 116; paint pdc
box 13 49 17 54; paint pc
box 22 58 26 63; paint pc
box 31 85 35 90; paint pc
box 40 40 44 45; paint pc
box 49 49 53 54; paint pc
box 4 1 8 5; paint psc
box 28 1 32 5; paint psc
box 52 1 56 5; paint psc
box 4 146 8 150; paint nsc
box 28 146 32 150; paint nsc
box 52 146 56 150; paint nsc
box 0 0 84 6; paint m1
box 0 145 84 151; paint m1
box 8 22 12 31; paint m1
box 8 0 12 31; paint m1
box 26 22 30 31; paint m1
box 26 22 30 37; paint m1
box 44 22 48 31; paint m1
box 44 0 48 31; paint m1
box 53 23 57 31; paint m1
box 53 23 57 37; paint m1
box 8 99 12 116; paint m1
box 8 93 12 116; paint m1
box 17 99 21 116; paint m1
box 17 99 21 151; paint m1
box 26 99 30 116; paint m1
box 26 93 30 116; paint m1
box 35 99 39 116; paint m1
box 35 93 39 116; paint m1
box 44 99 48 116; paint m1
box 44 93 48 116; paint m1
box 53 99 57 116; paint m1
box 53 99 57 151; paint m1
box 8 40 58 45; paint m1
box 13 49 54 54; paint m1
box 22 58 67 63; paint m1
box 26 67 40 72; paint m1
box 26 76 49 81; paint m1
box 31 85 76 90; paint m1
box 26 32 31 37; paint m2c
box 26 67 31 72; paint m2c
box 53 32 58 37; paint m2c
box 53 40 58 45; paint m2c
box 8 93 13 98; paint m2c
box 8 40 13 45; paint m2c
box 26 93 31 98; paint m2c
box 26 76 31 81; paint m2c
box 35 93 40 98; paint m2c
box 35 67 40 72; paint m2c
box 44 93 49 98; paint m2c
box 44 76 49 81; paint m2c
box 17 49 22 54; paint m2c
box 62 58 67 63; paint m2c
box 71 85 76 90; paint m2c
box 26 32 31 72; paint m2
box 53 32 58 45; paint m2
box 8 40 13 98; paint m2
box 26 76 31 98; paint m2
box 35 67 40 98; paint m2
box 44 76 49 98; paint m2
box 17 49 22 54; paint m2
box 62 58 67 63; paint m2
box 71 85 76 90; paint m2
box 17 49 22 54; paint m3c
box 62 58 67 63; paint m3c
box 71 85 76 90; paint m3c
box 35 67 40 72; paint m3c
box 13 49 15 54; label c3 center m1; port make 1
box 22 58 24 63; label p3 center m1; port make 2
box 31 85 33 90; label p3b center m1; port make 3
box 26 67 28 72; label s3 center m1; port make 4
box 8 40 10 45; label x3_cb center m1
box 26 76 28 81; label x3_s1xp1 center m1
box 0 145 2 151; label vdd center m1; port make 5
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
save sum3
quit -noprompt
