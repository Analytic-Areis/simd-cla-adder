# part1_agy check and comparison

`part1_agy` and the raw simulation files of this check were removed on 3 Nov 2026; a backup is kept outside the project. Script: `part1/cells/agy_check.py`. `part1_agy` was only read. Its flow was rerun on a copy, since removed.

The run was stopped on the user's request before the common-bench clock limit, power and flip-flop stages. Those stages have no results here.

## Validity of part1_agy

| Check | Result |
|---|---|
| Logic, switch level, 512 inputs | 0 errors, 0 shorts |
| DRC, fresh | 0 |
| Full LVS with this project's script | Match, 402 merged devices, 234 nets |
| Fresh extraction against its netlist | Same device count, capacitor count and total, 1022.3 fF |
| Model file | Same as provided, apart from line endings |
| Rerun of its own post-layout flow | All stored delay, clock and power values reproduced to 0.1 |
| Delay on this project's bench | 664.51 ps against its 666.8 ps, same arc (b2 rise to s3) |

The larger bounding box first noted (5591 x 371 lambda) came from MAGIC's checkpaint layer. Painted extent is 5457 x 304 lambda.

## Common bench, both designs registered

T = 2 ns, 4608 single-input transitions launched by each design's own flip-flops, the same x1/x8 clock chain, an inverter on each Q, and 20/10 lambda inverters on the adder S and C4 nets. The extra inverters were added to this design's netlist to match part1_agy.

| Measure (ps) | part1_agy | This design, same load | This design, as designed |
|---|---|---|---|
| Schematic, Q to output | 491.70 | 536.71 | not run |
| Post-layout, Q to output | 664.51 | 615.68 | 589.17 |
| Post-layout, clock to output | 829.17 | 803.49 | 785.89 |
| Post-layout, hint vector, Q to output | 371.93 | 472.73 | 459.92 |
| Multi-input sample, clock to output | 831.24 | 815.41 | not run |
| Multi-input sample, first Q to output | 668.42 | 673.42 | not run |

The multi-input sample is one random sequence of 6000 changes (5702 distinct transitions). The first-Q figure includes the skew between flip-flop Q rise and fall, so clock to output is the cleaner measure there.

Wrong output samples were 0 in every sweep.

## Area, drawn extent by one method

| | part1_agy | This design |
|---|---|---|
| Width x height (lambda) | 5457 x 304 | 919 x 935 |
| Area (um2) | 13437 | 6960 |
| Area x post-layout Q to output, same load (um2 ns) | 8929 | 4285 |

## Not measured on a common bench

Each design's own figures only, on different benches and vectors:

| | part1_agy | This design |
|---|---|---|
| Shortest working period | 832.9 ps, 11 transitions | 872.1 ps, 264 vectors |
| Random power | 4186 uW at 935 ps, 12 vectors | 3390 uW at 872.1 ps, 200 vectors |
| Hint toggling power | 3067 uW at 935 ps | 2500 uW at 872.1 ps |
| Inputs constant | 1179 uW at 935 ps | 887 uW at 872.1 ps |
| Flip-flop tcq / tsu / thold | 163.2 / 105 / 25 ps, inverter load | 204.2 / 38.0 / 45.7 ps, 47.76 fF load |
