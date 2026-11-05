# Toolchain check only (not a design cell): draw the assignment's 20L/10L inverter,
# run DRC, extract, write a SPICE netlist with all parasitic caps.
cellname rename (UNNAMED) flow_inv
proc rect {layer x0 y0 x1 y1} { box $x0 $y0 $x1 $y1; paint $layer }
rect nwell -12 20 14 58
rect ndiff -6 0 8 10
rect pdiff -6 26 8 46
rect poly 0 -3 2 49
rect poly -4 15 2 19
rect pc -4 15 0 19
rect ndc -6 0 -2 10
rect ndc 4 0 8 10
rect pdc -6 26 -2 46
rect pdc 4 26 8 46
rect m1 4 0 8 46
rect m1 -6 -8 -2 0
rect m1 -6 46 -2 56
rect m1 -14 -10 16 -6
rect m1 -14 52 16 56
rect nsc -6 50 -2 54
rect psc -6 -8 -2 -4
rect m1 -8 15 0 19
box -8 15 -6 19; label in center m1; port make 1
box 4 20 8 22; label out center m1; port make 2
box -14 52 16 56; label vdd center m1; port make 3
box -14 -10 16 -6; label gnd center m1; port make 4
select top cell
drc euclidean on
drc check
drc catchup
set why [drc listall why]
puts "DRC_COUNT [llength $why]"
foreach {m b} $why { puts "DRC_ERR $m : $b" }
save flow_inv
extract do local
extract all
ext2spice lvs
ext2spice cthresh 0
ext2spice rthresh 0
ext2spice format ngspice
ext2spice subcircuit top on
ext2spice
puts DONE
quit -noprompt
