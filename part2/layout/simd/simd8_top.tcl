cellname rename (UNNAMED) simd8_top
getcell cla4_cell child 0 0 parent 0 0
getcell cla4_cell child 0 0 parent 815 0
getcell gate_top child 0 0 parent 618 200
save simd8_top
select top cell
expand
flatten -nolabels simd8_flat
load simd8_flat
box 19 53 20 58; paint m3
box 156 53 157 58; paint m3
box 293 53 294 58; paint m3
box 430 53 431 58; paint m3
box 46 62 47 67; paint m3
box 183 62 184 67; paint m3
box 320 62 321 67; paint m3
box 457 62 458 67; paint m3
box 496 261 497 266; paint m3
box 478 279 479 284; paint m3
box 37 516 38 521; paint m3
box 174 516 175 521; paint m3
box 311 516 312 521; paint m3
box 448 516 449 521; paint m3
box 834 53 835 58; paint m3
box 971 53 972 58; paint m3
box 1108 53 1109 58; paint m3
box 1245 53 1246 58; paint m3
box 861 62 862 67; paint m3
box 998 62 999 67; paint m3
box 1135 62 1136 67; paint m3
box 1272 62 1273 67; paint m3
box 1311 261 1312 266; paint m3
box 1293 279 1294 284; paint m3
box 852 516 853 521; paint m3
box 989 516 990 521; paint m3
box 1126 516 1127 521; paint m3
box 1263 516 1264 521; paint m3
box 673 239 674 244; paint m3
box 691 266 692 271; paint m3
box 700 248 701 253; paint m3
box 461 637 466 642; paint m345c
box 461 637 466 642; paint m5
box 629 359 634 364; paint m345c
box 629 359 634 364; paint m5
box 462 637 466 688; paint m5
box 630 359 634 688; paint m5
box 462 684 634 688; paint m5
box 665 359 670 364; paint m345c
box 665 359 670 364; paint m5
box 1312 637 1317 642; paint m345c
box 1312 637 1317 642; paint m5
box 666 359 670 708; paint m5
box 1313 637 1317 708; paint m5
box 666 704 1317 708; paint m5
box -28 -60 -22 2; paint m2
box -16 -42 -10 2; paint m2
box -16 -42 -10 -36; paint m3c
box 787 -60 793 2; paint m2
box 799 -42 805 2; paint m2
box 799 -42 805 -36; paint m3c
box 590 -60 596 202; paint m2
box 602 -42 608 202; paint m2
box 602 -42 608 -36; paint m3c
box -40 -60 1373 -54; paint m2
box -40 -42 1373 -36; paint m3
box 19 53 20 58; label a0 center m3; port make 1
box 156 53 157 58; label a1 center m3; port make 2
box 293 53 294 58; label a2 center m3; port make 3
box 430 53 431 58; label a3 center m3; port make 4
box 46 62 47 67; label b0 center m3; port make 5
box 183 62 184 67; label b1 center m3; port make 6
box 320 62 321 67; label b2 center m3; port make 7
box 457 62 458 67; label b3 center m3; port make 8
box 496 261 497 266; label c0 center m3; port make 9
box 478 279 479 284; label c4lo center m3; port make 10
box 37 516 38 521; label s0 center m3; port make 11
box 174 516 175 521; label s1 center m3; port make 12
box 311 516 312 521; label s2 center m3; port make 13
box 448 516 449 521; label s3 center m3; port make 14
box 834 53 835 58; label a4 center m3; port make 15
box 971 53 972 58; label a5 center m3; port make 16
box 1108 53 1109 58; label a6 center m3; port make 17
box 1245 53 1246 58; label a7 center m3; port make 18
box 861 62 862 67; label b4 center m3; port make 19
box 998 62 999 67; label b5 center m3; port make 20
box 1135 62 1136 67; label b6 center m3; port make 21
box 1272 62 1273 67; label b7 center m3; port make 22
box 1311 261 1312 266; label cinh center m3
box 1293 279 1294 284; label c8 center m3; port make 23
box 852 516 853 521; label s4 center m3; port make 24
box 989 516 990 521; label s5 center m3; port make 25
box 1126 516 1127 521; label s6 center m3; port make 26
box 1263 516 1264 521; label s7 center m3; port make 27
box 673 239 674 244; label cinh center m3
box 691 266 692 271; label c4lo center m3; port make 28
box 700 248 701 253; label mode center m3; port make 29
box -40 -60 -34 -54; label vdd center m2; port make 30
box -40 -42 -34 -36; label gnd center m3; port make 31
save simd8_flat
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
save simd8_flat
extract do local
extract all
ext2spice lvs
ext2spice cthresh 0
ext2spice rthresh 0
ext2spice format ngspice
ext2spice hierarchy off
ext2spice subcircuit top on
ext2spice
puts DONE
quit -noprompt
