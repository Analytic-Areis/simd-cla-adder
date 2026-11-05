cellname rename (UNNAMED) base8_top
getcell cla4_cell child 0 0 parent 0 0
getcell cla4_cell child 0 0 parent 638 0
save base8_top
select top cell
expand
flatten -nolabels base8_flat
load base8_flat
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
box 657 53 658 58; paint m3
box 794 53 795 58; paint m3
box 931 53 932 58; paint m3
box 1068 53 1069 58; paint m3
box 684 62 685 67; paint m3
box 821 62 822 67; paint m3
box 958 62 959 67; paint m3
box 1095 62 1096 67; paint m3
box 1134 261 1135 266; paint m3
box 1116 279 1117 284; paint m3
box 675 516 676 521; paint m3
box 812 516 813 521; paint m3
box 949 516 950 521; paint m3
box 1086 516 1087 521; paint m3
box 461 637 466 642; paint m345c
box 461 637 466 642; paint m5
box 1135 637 1140 642; paint m345c
box 1135 637 1140 642; paint m5
box 462 637 466 688; paint m5
box 1136 637 1140 688; paint m5
box 462 684 1140 688; paint m5
box -28 -60 -22 2; paint m2
box -16 -42 -10 2; paint m2
box -16 -42 -10 -36; paint m3c
box 610 -60 616 2; paint m2
box 622 -42 628 2; paint m2
box 622 -42 628 -36; paint m3c
box -40 -60 1196 -54; paint m2
box -40 -42 1196 -36; paint m3
box 19 53 20 58; label a0 center m3; port make 1
box 156 53 157 58; label a1 center m3; port make 2
box 293 53 294 58; label a2 center m3; port make 3
box 430 53 431 58; label a3 center m3; port make 4
box 46 62 47 67; label b0 center m3; port make 5
box 183 62 184 67; label b1 center m3; port make 6
box 320 62 321 67; label b2 center m3; port make 7
box 457 62 458 67; label b3 center m3; port make 8
box 496 261 497 266; label c0 center m3; port make 9
box 478 279 479 284; label c4lo center m3
box 37 516 38 521; label s0 center m3; port make 10
box 174 516 175 521; label s1 center m3; port make 11
box 311 516 312 521; label s2 center m3; port make 12
box 448 516 449 521; label s3 center m3; port make 13
box 657 53 658 58; label a4 center m3; port make 14
box 794 53 795 58; label a5 center m3; port make 15
box 931 53 932 58; label a6 center m3; port make 16
box 1068 53 1069 58; label a7 center m3; port make 17
box 684 62 685 67; label b4 center m3; port make 18
box 821 62 822 67; label b5 center m3; port make 19
box 958 62 959 67; label b6 center m3; port make 20
box 1095 62 1096 67; label b7 center m3; port make 21
box 1134 261 1135 266; label c4lo center m3
box 1116 279 1117 284; label c8 center m3; port make 22
box 675 516 676 521; label s4 center m3; port make 23
box 812 516 813 521; label s5 center m3; port make 24
box 949 516 950 521; label s6 center m3; port make 25
box 1086 516 1087 521; label s7 center m3; port make 26
box -40 -60 -34 -54; label vdd center m2; port make 27
box -40 -42 -34 -36; label gnd center m3; port make 28
save base8_flat
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
save base8_flat
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
