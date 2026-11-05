cellname rename (UNNAMED) sum3
box 0 104 84 188; paint nwell
box 8 29 20 42; paint ndiff
box 19 29 29 42; paint ndiff
box 28 29 38 42; paint ndiff
box 37 29 47 42; paint ndiff
box 46 29 57 42; paint ndiff
box 8 110 20 136; paint pdiff
box 19 110 29 137; paint pdiff
box 28 110 38 137; paint pdiff
box 37 110 47 137; paint pdiff
box 46 110 57 137; paint pdiff
box 14 26 16 139; paint poly
box 23 26 25 140; paint poly
box 32 26 34 140; paint poly
box 41 26 43 140; paint poly
box 50 26 52 140; paint poly
box 8 29 12 42; paint ndc
box 26 29 30 42; paint ndc
box 44 29 48 42; paint ndc
box 53 29 57 42; paint ndc
box 8 110 12 136; paint pdc
box 17 110 21 137; paint pdc
box 26 110 30 137; paint pdc
box 35 110 39 137; paint pdc
box 44 110 48 137; paint pdc
box 53 110 57 137; paint pdc
box 13 60 17 65; paint pc
box 22 69 26 74; paint pc
box 31 96 35 101; paint pc
box 40 51 44 56; paint pc
box 49 60 53 65; paint pc
box 4 1 8 5; paint psc
box 28 1 32 5; paint psc
box 52 1 56 5; paint psc
box 4 180 8 184; paint nsc
box 28 180 32 184; paint nsc
box 52 180 56 184; paint nsc
box 0 0 84 6; paint m1
box 0 179 84 185; paint m1
box 8 29 12 42; paint m1
box 8 0 12 42; paint m1
box 26 29 30 42; paint m1
box 26 29 30 48; paint m1
box 44 29 48 42; paint m1
box 44 0 48 42; paint m1
box 53 29 57 42; paint m1
box 53 29 57 48; paint m1
box 8 110 12 136; paint m1
box 8 104 12 136; paint m1
box 17 110 21 137; paint m1
box 17 110 21 185; paint m1
box 26 110 30 137; paint m1
box 26 104 30 137; paint m1
box 35 110 39 137; paint m1
box 35 104 39 137; paint m1
box 44 110 48 137; paint m1
box 44 104 48 137; paint m1
box 53 110 57 137; paint m1
box 53 110 57 185; paint m1
box 8 51 58 56; paint m1
box 13 60 54 65; paint m1
box 22 69 67 74; paint m1
box 26 78 40 83; paint m1
box 26 87 49 92; paint m1
box 31 96 76 101; paint m1
box 26 43 31 48; paint m2c
box 26 78 31 83; paint m2c
box 53 43 58 48; paint m2c
box 53 51 58 56; paint m2c
box 8 104 13 109; paint m2c
box 8 51 13 56; paint m2c
box 26 104 31 109; paint m2c
box 26 87 31 92; paint m2c
box 35 104 40 109; paint m2c
box 35 78 40 83; paint m2c
box 44 104 49 109; paint m2c
box 44 87 49 92; paint m2c
box 17 60 22 65; paint m2c
box 62 69 67 74; paint m2c
box 71 96 76 101; paint m2c
box 26 43 31 83; paint m2
box 53 43 58 56; paint m2
box 8 51 13 109; paint m2
box 26 87 31 109; paint m2
box 35 78 40 109; paint m2
box 44 87 49 109; paint m2
box 17 60 22 65; paint m2
box 62 69 67 74; paint m2
box 71 96 76 101; paint m2
box 17 60 22 65; paint m3c
box 62 69 67 74; paint m3c
box 71 96 76 101; paint m3c
box 35 78 40 83; paint m3c
box 13 60 15 65; label c3 center m1; port make 1
box 22 69 24 74; label p3 center m1; port make 2
box 31 96 33 101; label p3b center m1; port make 3
box 26 78 28 83; label s3 center m1; port make 4
box 8 51 10 56; label x3_cb center m1
box 26 87 28 92; label x3_s1xp1 center m1
box 0 179 2 185; label vdd center m1; port make 5
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
