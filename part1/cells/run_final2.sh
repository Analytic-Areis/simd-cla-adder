#!/bin/bash
L=../results/final/logs
export OMP_NUM_THREADS=1
python3 final_flow.py verify_multi > $L/verify_multi.log 2>&1; echo "verify_multi exit $?"
python3 run_functional.py > $L/functional_blocks.log 2>&1; echo "blocks functional exit $?"
python3 final_flow.py functional > $L/functional_final.log 2>&1; echo "functional exit $?"
python3 final_flow.py design_power final_C4_aoi22_1 final_C4_tg_1 cmp_R_tg_refresh > $L/design_power.log 2>&1; echo "design_power exit $?"
python3 final_flow.py tradeoff C4_aoi22 0.7 0.85 1.0 1.2 1.4 > $L/tradeoff.log 2>&1; echo "tradeoff exit $?"
echo GROUP2_DONE
