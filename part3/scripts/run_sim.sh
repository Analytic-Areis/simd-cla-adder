#!/bin/bash
# Compile and run every testbench with Icarus Verilog. Logs and VCD files go to fpga/sim/.
# Usage, from anywhere: bash fpga/scripts/run_sim.sh
set -e
FPGA="$(cd "$(dirname "$0")/.." && pwd)"
cd "$FPGA/sim"

RTL="$FPGA/rtl/cla4.v $FPGA/rtl/simd8.v $FPGA/rtl/cla4_reg.v $FPGA/rtl/simd8_reg.v"
BOARD="$FPGA/board/board_common.v $FPGA/board/fpga_cla4_top.v $FPGA/board/fpga_simd8_top.v"

status=0
run() {
    name=$1; shift
    iverilog -g2005 -Wall -o "$name.vvp" "$@" 2> "$name.compile.log" || { cat "$name.compile.log"; status=1; return; }
    vvp -n "$name.vvp" > "$name.log"
    result=$(grep -- "--- RESULT" "$name.log" || echo "no result line")
    echo "$name: $result"
    grep -q "PASS" <<< "$result" || status=1
}

run tb_cla4       $RTL "$FPGA/tb/tb_cla4.v"
run tb_simd8      $RTL "$FPGA/tb/tb_simd8.v"
run tb_registered $RTL "$FPGA/tb/tb_registered.v"
run tb_fpga_tops  $RTL $BOARD "$FPGA/tb/tb_fpga_tops.v"
exit $status
