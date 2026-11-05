cellname rename (UNNAMED) fos1
box 0 83 99 142; paint nwell
box 8 10 19 30; paint ndiff
box 18 10 27 30; paint ndiff
box 26 10 40 30; paint ndiff
box 40 10 55 30; paint ndiff
box 60 10 76 30; paint ndiff
box 76 24 91 30; paint ndiff
box 8 89 19 113; paint pdiff
box 18 89 27 113; paint pdiff
box 26 89 37 109; paint pdiff
box 42 89 58 109; paint pdiff
box 58 89 73 129; paint pdiff
box 14 7 16 53; paint poly
box 14 57 16 116; paint poly
box 21 7 23 62; paint poly
box 21 66 23 116; paint poly
box 30 7 32 112; paint poly
box 48 7 50 112; paint poly
box 66 7 68 132; paint poly
box 84 21 86 71; paint poly
box 8 10 12 30; paint ndc
box 24 10 28 30; paint ndc
box 51 10 55 30; paint ndc
box 60 10 64 30; paint ndc
box 74 10 78 30; paint ndc
box 87 24 91 30; paint ndc
box 8 89 12 113; paint pdc
box 24 89 28 113; paint pdc
box 33 89 37 109; paint pdc
box 42 89 46 109; paint pdc
box 56 89 60 129; paint pdc
box 69 89 73 129; paint pdc
box 13 48 17 53; paint pc
box 13 57 17 62; paint pc
box 20 57 24 62; paint pc
box 20 66 24 71; paint pc
box 29 39 33 44; paint pc
box 47 57 51 62; paint pc
box 65 75 69 80; paint pc
box 83 66 87 71; paint pc
box 17 57 20 62; paint pc
box 4 1 8 5; paint psc
box 28 1 32 5; paint psc
box 52 1 56 5; paint psc
box 76 1 80 5; paint psc
box 4 134 8 138; paint nsc
box 28 134 32 138; paint nsc
box 52 134 56 138; paint nsc
box 76 134 80 138; paint nsc
box 0 0 99 6; paint m1
box 0 133 99 139; paint m1
box 8 10 12 30; paint m1
box 8 10 12 36; paint m1
box 24 10 28 30; paint m1
box 24 0 28 30; paint m1
box 51 10 55 30; paint m1
box 51 10 55 36; paint m1
box 60 10 64 30; paint m1
box 60 10 64 36; paint m1
box 74 10 78 30; paint m1
box 74 0 78 30; paint m1
box 87 24 91 30; paint m1
box 87 24 91 36; paint m1
box 8 89 12 113; paint m1
box 8 83 12 113; paint m1
box 24 89 28 113; paint m1
box 24 89 28 139; paint m1
box 33 89 37 109; paint m1
box 33 83 37 109; paint m1
box 42 89 46 109; paint m1
box 42 83 46 109; paint m1
box 56 89 60 129; paint m1
box 56 89 60 139; paint m1
box 69 89 73 129; paint m1
box 69 83 73 129; paint m1
box 8 39 47 44; paint m1
box 60 39 74 44; paint m1
box 8 48 92 53; paint m1
box 13 57 52 62; paint m1
box 20 66 88 71; paint m1
box 33 75 70 80; paint m1
box 8 31 13 36; paint m2c
box 8 39 13 44; paint m2c
box 51 31 56 36; paint m2c
box 51 75 56 80; paint m2c
box 60 31 65 36; paint m2c
box 60 39 65 44; paint m2c
box 87 31 92 36; paint m2c
box 87 48 92 53; paint m2c
box 8 83 13 88; paint m2c
box 8 48 13 53; paint m2c
box 33 83 38 88; paint m2c
box 33 75 38 80; paint m2c
box 42 83 47 88; paint m2c
box 42 39 47 44; paint m2c
box 69 83 74 88; paint m2c
box 69 39 74 44; paint m2c
box 24 57 29 62; paint m2c
box 24 66 29 71; paint m2c
box 8 31 13 44; paint m2
box 51 31 56 80; paint m2
box 60 31 65 44; paint m2
box 87 31 92 53; paint m2
box 8 48 13 88; paint m2
box 33 75 38 88; paint m2
box 42 39 47 88; paint m2
box 69 39 74 88; paint m2
box 24 57 29 62; paint m2
box 24 66 29 71; paint m2
box 24 57 29 62; paint m3c
box 69 39 74 44; paint m3c
box 24 66 29 71; paint m3c
box 13 57 15 62; label clk center m1; port make 1
box 60 39 62 44; label q_s1 center m1; port make 2
box 20 66 22 71; label s1 center m1; port make 3
box 8 48 10 53; label fo_s1_a center m1
box 8 39 10 44; label fo_s1_b center m1
box 33 75 35 80; label fo_s1_qb center m1
box 0 133 2 139; label vdd center m1; port make 4
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
save fos1
quit -noprompt
