cellname rename (UNNAMED) fib2
box 0 91 99 150; paint nwell
box 8 10 19 38; paint ndiff
box 18 10 27 38; paint ndiff
box 26 10 40 38; paint ndiff
box 40 10 55 38; paint ndiff
box 60 18 76 38; paint ndiff
box 76 30 91 38; paint ndiff
box 8 97 19 129; paint pdiff
box 18 97 27 129; paint pdiff
box 26 97 37 125; paint pdiff
box 42 97 58 125; paint pdiff
box 58 97 73 137; paint pdiff
box 14 7 16 61; paint poly
box 14 65 16 132; paint poly
box 21 7 23 70; paint poly
box 21 74 23 132; paint poly
box 30 7 32 128; paint poly
box 48 7 50 128; paint poly
box 66 15 68 140; paint poly
box 84 27 86 79; paint poly
box 8 10 12 38; paint ndc
box 24 10 28 38; paint ndc
box 51 10 55 38; paint ndc
box 60 18 64 38; paint ndc
box 74 18 78 38; paint ndc
box 87 30 91 38; paint ndc
box 8 97 12 129; paint pdc
box 24 97 28 129; paint pdc
box 33 97 37 125; paint pdc
box 42 97 46 125; paint pdc
box 56 97 60 137; paint pdc
box 69 97 73 137; paint pdc
box 13 56 17 61; paint pc
box 13 65 17 70; paint pc
box 20 65 24 70; paint pc
box 20 74 24 79; paint pc
box 29 47 33 52; paint pc
box 47 65 51 70; paint pc
box 65 83 69 88; paint pc
box 83 74 87 79; paint pc
box 17 65 20 70; paint pc
box 4 1 8 5; paint psc
box 28 1 32 5; paint psc
box 52 1 56 5; paint psc
box 76 1 80 5; paint psc
box 4 142 8 146; paint nsc
box 28 142 32 146; paint nsc
box 52 142 56 146; paint nsc
box 76 142 80 146; paint nsc
box 0 0 99 6; paint m1
box 0 141 99 147; paint m1
box 8 10 12 38; paint m1
box 8 10 12 44; paint m1
box 24 10 28 38; paint m1
box 24 0 28 38; paint m1
box 51 10 55 38; paint m1
box 51 10 55 44; paint m1
box 60 18 64 38; paint m1
box 60 18 64 44; paint m1
box 74 18 78 38; paint m1
box 74 0 78 38; paint m1
box 87 30 91 38; paint m1
box 87 30 91 44; paint m1
box 8 97 12 129; paint m1
box 8 91 12 129; paint m1
box 24 97 28 129; paint m1
box 24 97 28 147; paint m1
box 33 97 37 125; paint m1
box 33 91 37 125; paint m1
box 42 97 46 125; paint m1
box 42 91 46 125; paint m1
box 56 97 60 137; paint m1
box 56 97 60 147; paint m1
box 69 97 73 137; paint m1
box 69 91 73 137; paint m1
box 8 47 47 52; paint m1
box 60 47 74 52; paint m1
box 8 56 92 61; paint m1
box 13 65 52 70; paint m1
box 20 74 88 79; paint m1
box 33 83 70 88; paint m1
box 8 39 13 44; paint m2c
box 8 47 13 52; paint m2c
box 51 39 56 44; paint m2c
box 51 83 56 88; paint m2c
box 60 39 65 44; paint m2c
box 60 47 65 52; paint m2c
box 87 39 92 44; paint m2c
box 87 56 92 61; paint m2c
box 8 91 13 96; paint m2c
box 8 56 13 61; paint m2c
box 33 91 38 96; paint m2c
box 33 83 38 88; paint m2c
box 42 91 47 96; paint m2c
box 42 47 47 52; paint m2c
box 69 91 74 96; paint m2c
box 69 47 74 52; paint m2c
box 24 65 29 70; paint m2c
box 24 74 29 79; paint m2c
box 8 39 13 52; paint m2
box 51 39 56 88; paint m2
box 60 39 65 52; paint m2
box 87 39 92 61; paint m2
box 8 56 13 96; paint m2
box 33 83 38 96; paint m2
box 42 47 47 96; paint m2
box 69 47 74 96; paint m2
box 24 65 29 70; paint m2
box 24 74 29 79; paint m2
box 69 47 74 52; paint m3c
box 24 65 29 70; paint m3c
box 24 74 29 79; paint m3c
box 60 47 62 52; label b2 center m1; port make 1
box 13 65 15 70; label clk center m1; port make 2
box 20 74 22 79; label d_b2 center m1; port make 3
box 8 56 10 61; label fi_b2_a center m1
box 8 47 10 52; label fi_b2_b center m1
box 33 83 35 88; label fi_b2_qb center m1
box 0 141 2 147; label vdd center m1; port make 4
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
save fib2
quit -noprompt
