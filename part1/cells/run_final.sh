#!/bin/bash
# Final measurements on the chosen design. Each group runs side by side; logs in results/final/logs.
L=../results/final/logs
export OMP_NUM_THREADS=1
( python3 final_flow.py dff > $L/dff.log 2>&1 && python3 final_flow.py system > $L/system.log 2>&1; echo "dff+system exit $?" ) &
( python3 final_flow.py blocks > $L/blocks.log 2>&1; echo "blocks exit $?" ) &
( python3 resistance_bound.py final_C4_aoi22_1 7.7 > $L/resistance.log 2>&1; echo "resistance exit $?" ) &
wait
echo FINAL_GROUP1_DONE
