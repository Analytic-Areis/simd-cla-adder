#!/usr/bin/env bash
# Run ngspice testbenches in batch mode and keep the logs.
# Usage (from anywhere):   ./scripts/run.sh step1   |  step2  |  <tb-name>
# Logs  -> results/logs/<tb>.log      Plots -> results/plots/*.eps
set -u
cd "$(dirname "$0")/.."
mkdir -p results/logs results/plots results/tmp
command -v ngspice >/dev/null || { echo "ngspice not found in PATH"; exit 1; }
ngspice -v 2>/dev/null | head -2 > results/logs/ngspice_version.txt

run_tb () {           # $1 = netlist path, $2 = log name
  echo ">> $1"
  ngspice -b "$1" > "results/logs/$2.log" 2>&1
  grep -E "^(RESULT|SETUP|HOLD|[a-z0-9_]+ +=)" "results/logs/$2.log" | head -80
}

case "${1:-step1}" in
  step1)
    run_tb spice/tb/tb_cells.sp        cells
    run_tb spice/tb/tb_dff.sp          dff
    run_tb spice/tb/tb_dff_setup_hold.sp dff_setup_hold
    python3 scripts/check_cells.py ;;
  step2)
    for v in tg aoi; do               # compare the two SUM-cell variants
      sed "s#spice/cells/sumcell.inc#spice/cells/sum_$v.inc#" spice/tb/tb_cla_worst.sp \
        | sed "s#cla_worst.dat#cla_worst_$v.dat#; s#q9_core_worst.eps#q9_core_worst_$v.eps#; s#worstcase#worstcase-$v#" \
        > results/tmp/tb_cla_worst_$v.sp
      run_tb results/tmp/tb_cla_worst_$v.sp cla_worst_$v
    done
    run_tb spice/tb/tb_cla_func.sp     cla_func
    python3 scripts/check_cla.py ;;
  *)
    run_tb "spice/tb/$1.sp" "$1" ;;
esac
echo "done - logs in results/logs/"
