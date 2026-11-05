load top_final_C4_aoi22_1
select top cell
expand
extract do resistance
extract all
ext2sim labels on
ext2sim
extresist tolerance 1
extresist all
ext2spice lvs
ext2spice format ngspice
ext2spice cthresh 0
ext2spice rthresh 0
ext2spice hierarchy off
ext2spice subcircuit top on
ext2spice extresist on
ext2spice -o rx_top.spice
puts DONE_RX
quit -noprompt
