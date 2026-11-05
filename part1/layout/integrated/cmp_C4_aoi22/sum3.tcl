cellname rename (UNNAMED) sum3
box 0 97 84 166; paint nwell
box 8 25 20 35; paint ndiff
box 19 25 29 35; paint ndiff
box 28 25 38 35; paint ndiff
box 37 25 47 35; paint ndiff
box 46 25 57 35; paint ndiff
box 8 103 20 123; paint pdiff
box 19 103 29 123; paint pdiff
box 28 103 38 123; paint pdiff
box 37 103 47 123; paint pdiff
box 46 103 57 123; paint pdiff
box 14 22 16 126; paint poly
box 23 22 25 126; paint poly
box 32 22 34 126; paint poly
box 41 22 43 126; paint poly
box 50 22 52 126; paint poly
box 8 25 12 35; paint ndc
box 26 25 30 35; paint ndc
box 44 25 48 35; paint ndc
box 53 25 57 35; paint ndc
box 8 103 12 123; paint pdc
box 17 103 21 123; paint pdc
box 26 103 30 123; paint pdc
box 35 103 39 123; paint pdc
box 44 103 48 123; paint pdc
box 53 103 57 123; paint pdc
box 13 53 17 58; paint pc
box 22 62 26 67; paint pc
box 31 89 35 94; paint pc
box 40 44 44 49; paint pc
box 49 53 53 58; paint pc
box 4 1 8 5; paint psc
box 28 1 32 5; paint psc
box 52 1 56 5; paint psc
box 4 158 8 162; paint nsc
box 28 158 32 162; paint nsc
box 52 158 56 162; paint nsc
box 0 0 84 6; paint m1
box 0 157 84 163; paint m1
box 8 25 12 35; paint m1
box 8 0 12 35; paint m1
box 26 25 30 35; paint m1
box 26 25 30 41; paint m1
box 44 25 48 35; paint m1
box 44 0 48 35; paint m1
box 53 25 57 35; paint m1
box 53 25 57 41; paint m1
box 8 103 12 123; paint m1
box 8 97 12 123; paint m1
box 17 103 21 123; paint m1
box 17 103 21 163; paint m1
box 26 103 30 123; paint m1
box 26 97 30 123; paint m1
box 35 103 39 123; paint m1
box 35 97 39 123; paint m1
box 44 103 48 123; paint m1
box 44 97 48 123; paint m1
box 53 103 57 123; paint m1
box 53 103 57 163; paint m1
box 8 44 58 49; paint m1
box 13 53 54 58; paint m1
box 22 62 67 67; paint m1
box 26 71 40 76; paint m1
box 26 80 49 85; paint m1
box 31 89 76 94; paint m1
box 26 36 31 41; paint m2c
box 26 71 31 76; paint m2c
box 53 36 58 41; paint m2c
box 53 44 58 49; paint m2c
box 8 97 13 102; paint m2c
box 8 44 13 49; paint m2c
box 26 97 31 102; paint m2c
box 26 80 31 85; paint m2c
box 35 97 40 102; paint m2c
box 35 71 40 76; paint m2c
box 44 97 49 102; paint m2c
box 44 80 49 85; paint m2c
box 17 53 22 58; paint m2c
box 62 62 67 67; paint m2c
box 71 89 76 94; paint m2c
box 26 36 31 76; paint m2
box 53 36 58 49; paint m2
box 8 44 13 102; paint m2
box 26 80 31 102; paint m2
box 35 71 40 102; paint m2
box 44 80 49 102; paint m2
box 17 53 22 58; paint m2
box 62 62 67 67; paint m2
box 71 89 76 94; paint m2
box 17 53 22 58; paint m3c
box 62 62 67 67; paint m3c
box 71 89 76 94; paint m3c
box 35 71 40 76; paint m3c
box 13 53 15 58; label c3 center m1; port make 1
box 22 62 24 67; label p3 center m1; port make 2
box 31 89 33 94; label p3b center m1; port make 3
box 26 71 28 76; label s3 center m1; port make 4
box 8 44 10 49; label x3_cb center m1
box 26 80 28 85; label x3_s1xp1 center m1
box 0 157 2 163; label vdd center m1; port make 5
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
