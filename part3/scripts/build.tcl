# Vivado batch build for one board top: synthesis, implementation, reports, bitstream.
# Usage, from the fpga/ folder:
#   vivado -mode batch -source scripts/build.tcl -tclargs fpga_cla4_top
#   vivado -mode batch -source scripts/build.tcl -tclargs fpga_simd8_top
# Outputs go to build/<top>/: the .bit file, utilisation, timing and power reports,
# and the post-synthesis netlist.

set top  [lindex $argv 0]
if {$top eq ""} { set top fpga_cla4_top }
set part xc7s50csga324-1
set root [file normalize [file dirname [info script]]/..]
set out  $root/build/$top
file mkdir $out

read_verilog [list \
    $root/rtl/cla4.v $root/rtl/simd8.v $root/rtl/cla4_reg.v $root/rtl/simd8_reg.v \
    $root/board/board_common.v $root/board/fpga_cla4_top.v $root/board/fpga_simd8_top.v ]
read_xdc $root/constraints/$top.xdc

synth_design -top $top -part $part
write_checkpoint -force $out/post_synth.dcp
write_verilog    -force -mode funcsim $out/${top}_synth_netlist.v
report_utilization -file $out/utilization_synth.rpt

opt_design
place_design
route_design
write_checkpoint -force $out/post_route.dcp
report_utilization    -file $out/utilization.rpt
report_timing_summary -file $out/timing_summary.rpt
report_power          -file $out/power.rpt
report_io             -file $out/io.rpt

write_bitstream -force $out/$top.bit
puts "Done: $out/$top.bit"
