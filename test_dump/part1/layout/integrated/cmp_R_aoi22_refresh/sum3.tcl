cellname rename (UNNAMED) sum3
box 0 88 84 139; paint nwell
box 8 19 20 26; paint ndiff
box 19 19 29 26; paint ndiff
box 28 19 38 26; paint ndiff
box 37 19 47 26; paint ndiff
box 46 18 57 26; paint ndiff
box 8 94 20 110; paint pdiff
box 19 94 29 107; paint pdiff
box 28 94 38 107; paint pdiff
box 37 94 47 107; paint pdiff
box 46 94 57 107; paint pdiff
box 14 16 16 113; paint poly
box 23 16 25 110; paint poly
box 32 16 34 110; paint poly
box 41 16 43 110; paint poly
box 50 15 52 110; paint poly
box 8 19 12 26; paint ndc
box 26 19 30 26; paint ndc
box 44 18 48 26; paint ndc
box 53 18 57 26; paint ndc
box 8 94 12 110; paint pdc
box 17 94 21 110; paint pdc
box 26 94 30 107; paint pdc
box 35 94 39 107; paint pdc
box 44 94 48 107; paint pdc
box 53 94 57 107; paint pdc
box 13 44 17 49; paint pc
box 22 53 26 58; paint pc
box 31 80 35 85; paint pc
box 40 35 44 40; paint pc
box 49 44 53 49; paint pc
box 4 1 8 5; paint psc
box 28 1 32 5; paint psc
box 52 1 56 5; paint psc
box 4 131 8 135; paint nsc
box 28 131 32 135; paint nsc
box 52 131 56 135; paint nsc
box 0 0 84 6; paint m1
box 0 130 84 136; paint m1
box 8 19 12 26; paint m1
box 8 0 12 26; paint m1
box 26 19 30 26; paint m1
box 26 19 30 32; paint m1
box 44 18 48 26; paint m1
box 44 0 48 26; paint m1
box 53 18 57 26; paint m1
box 53 18 57 32; paint m1
box 8 94 12 110; paint m1
box 8 88 12 110; paint m1
box 17 94 21 110; paint m1
box 17 94 21 136; paint m1
box 26 94 30 107; paint m1
box 26 88 30 107; paint m1
box 35 94 39 107; paint m1
box 35 88 39 107; paint m1
box 44 94 48 107; paint m1
box 44 88 48 107; paint m1
box 53 94 57 107; paint m1
box 53 94 57 136; paint m1
box 8 35 58 40; paint m1
box 13 44 54 49; paint m1
box 22 53 67 58; paint m1
box 26 62 40 67; paint m1
box 26 71 49 76; paint m1
box 31 80 76 85; paint m1
box 26 27 31 32; paint m2c
box 26 62 31 67; paint m2c
box 53 27 58 32; paint m2c
box 53 35 58 40; paint m2c
box 8 88 13 93; paint m2c
box 8 35 13 40; paint m2c
box 26 88 31 93; paint m2c
box 26 71 31 76; paint m2c
box 35 88 40 93; paint m2c
box 35 62 40 67; paint m2c
box 44 88 49 93; paint m2c
box 44 71 49 76; paint m2c
box 17 44 22 49; paint m2c
box 62 53 67 58; paint m2c
box 71 80 76 85; paint m2c
box 26 27 31 67; paint m2
box 53 27 58 40; paint m2
box 8 35 13 93; paint m2
box 26 71 31 93; paint m2
box 35 62 40 93; paint m2
box 44 71 49 93; paint m2
box 17 44 22 49; paint m2
box 62 53 67 58; paint m2
box 71 80 76 85; paint m2
box 17 44 22 49; paint m3c
box 62 53 67 58; paint m3c
box 71 80 76 85; paint m3c
box 35 62 40 67; paint m3c
box 13 44 15 49; label c3 center m1; port make 1
box 22 53 24 58; label p3 center m1; port make 2
box 31 80 33 85; label p3b center m1; port make 3
box 26 62 28 67; label s3 center m1; port make 4
box 8 35 10 40; label x3_cb center m1
box 26 71 28 76; label x3_s1xp1 center m1
box 0 130 2 136; label vdd center m1; port make 5
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
