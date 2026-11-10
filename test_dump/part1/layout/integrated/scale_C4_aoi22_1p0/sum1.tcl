cellname rename (UNNAMED) sum1
box 0 97 84 166; paint nwell
box 8 15 20 35; paint ndiff
box 19 15 29 35; paint ndiff
box 28 15 38 35; paint ndiff
box 37 15 47 35; paint ndiff
box 46 29 57 35; paint ndiff
box 8 103 20 116; paint pdiff
box 19 103 29 143; paint pdiff
box 28 103 38 143; paint pdiff
box 37 103 47 143; paint pdiff
box 46 103 57 143; paint pdiff
box 14 12 16 119; paint poly
box 23 12 25 146; paint poly
box 32 12 34 146; paint poly
box 41 12 43 146; paint poly
box 50 26 52 146; paint poly
box 8 15 12 35; paint ndc
box 26 15 30 35; paint ndc
box 44 15 48 35; paint ndc
box 53 29 57 35; paint ndc
box 8 103 12 116; paint pdc
box 17 103 21 143; paint pdc
box 26 103 30 143; paint pdc
box 35 103 39 143; paint pdc
box 44 103 48 143; paint pdc
box 53 103 57 143; paint pdc
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
box 8 15 12 35; paint m1
box 8 0 12 35; paint m1
box 26 15 30 35; paint m1
box 26 15 30 41; paint m1
box 44 15 48 35; paint m1
box 44 0 48 35; paint m1
box 53 29 57 35; paint m1
box 53 29 57 41; paint m1
box 8 103 12 116; paint m1
box 8 97 12 116; paint m1
box 17 103 21 143; paint m1
box 17 103 21 163; paint m1
box 26 103 30 143; paint m1
box 26 97 30 143; paint m1
box 35 103 39 143; paint m1
box 35 97 39 143; paint m1
box 44 103 48 143; paint m1
box 44 97 48 143; paint m1
box 53 103 57 143; paint m1
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
box 13 53 15 58; label c1 center m1; port make 1
box 22 62 24 67; label p1 center m1; port make 2
box 31 89 33 94; label p1b center m1; port make 3
box 26 71 28 76; label s1 center m1; port make 4
box 8 44 10 49; label x1_cb center m1
box 26 80 28 85; label x1_s1xp1 center m1
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
save sum1
quit -noprompt
