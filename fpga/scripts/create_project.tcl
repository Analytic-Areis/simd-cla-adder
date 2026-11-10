# Creates a Vivado project with every design file, both constraint files and all four testbenches,
# so the designs can be simulated, synthesised and programmed from the Vivado GUI.
#
# Usage, from this folder (the one holding rtl/, board/, tb/):
#   vivado -mode batch -source scripts/create_project.tcl
#   vivado -mode batch -source scripts/create_project.tcl -tclargs fpga_simd8_top
# or in the Vivado GUI: Tools > Run Tcl Script, then pick this file (it sets up the CLA4 board top).
# The project is written to vivado/vlsi_fpga/ and can then be opened with File > Open Project.

set top [lindex $argv 0]
if {$top eq ""} { set top fpga_cla4_top }
set other [expr {$top eq "fpga_cla4_top" ? "fpga_simd8_top" : "fpga_cla4_top"}]
set part xc7s50csga324-1
set root [file normalize [file dirname [info script]]/..]

create_project vlsi_fpga $root/vivado/vlsi_fpga -part $part -force

add_files -fileset sources_1 [list \
    $root/rtl/cla4.v $root/rtl/simd8.v $root/rtl/cla4_reg.v $root/rtl/simd8_reg.v \
    $root/board/board_common.v $root/board/fpga_cla4_top.v $root/board/fpga_simd8_top.v ]
add_files -fileset constrs_1 [list $root/constraints/fpga_cla4_top.xdc $root/constraints/fpga_simd8_top.xdc]

# Only the chosen top's pins are used; the other constraint file is kept in the project but disabled.
set_property top $top [get_filesets sources_1]
set_property is_enabled false [get_files $root/constraints/$other.xdc]

add_files -fileset sim_1 [list \
    $root/tb/tb_cla4.v $root/tb/tb_simd8.v $root/tb/tb_registered.v $root/tb/tb_fpga_tops.v ]
set_property top tb_cla4 [get_filesets sim_1]
# Every testbench ends with $finish; the longest, tb_simd8, stops at about 262 us.
set_property -name {xsim.simulate.runtime} -value {1ms} -objects [get_filesets sim_1]

update_compile_order -fileset sources_1
update_compile_order -fileset sim_1
puts "Project created: $root/vivado/vlsi_fpga/vlsi_fpga.xpr, top $top"
