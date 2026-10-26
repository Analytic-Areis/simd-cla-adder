# Design rationale — what is optimised and why

## 1. What the project scores
Part-I is graded on post-layout **tpd,max** (C0 0→1 with A=1111, B=0000), **fmax = 1/(tpd,max + tsetup + thold)**,
and **PDP = Pavg(fmax) × tpd,max**. So the target is *minimum PDP with a layout that is realistic to draw by hand*,
with the C0 → {S, C4} path as the first priority. Part-II chains two of these adders through C4 → Cin, so the
same path matters again there.

## 2. Equations used
Per bit: `g = a·b`, `t = a+b` (used in the carry network), `p = a⊕b` (used only for the sum).
Using t instead of p in carries is valid: if a=b=1 then g=1 already makes the carry 1.

```
c1 = G0  + T0 ·c0          G0 = g0                 T0 = t0
c2 = G10 + T10·c0          G10 = g1 + t1·g0        T10 = t1·t0
c3 = G20 + T20·c0          G20 = g2 + t2·G10       T20 = t2·T10
c4 = G30 + T30·c0          G30 = G32 + T32·G10     T30 = T32·T10
                           G32 = g3 + t3·g2        T32 = t3·t2
s_i = p_i ⊕ c_i
```
Every G/T term is independent of c0, so it is ready before c0 matters; only the final `AOI21(c0, T, G)` sees c0.

## 3. Gate mapping (all single-stage inverting static CMOS)
| Signal | Gate | Why |
|---|---|---|
| gb = (ab)', tb = (a+b)' | NAND2, NOR2 | natural CMOS polarity |
| p = (ab + tb)' | AOI21(a,b,tb) | XOR in 2 small gates, no extra inverters |
| pb = ((a+b)·gb)' | OAI21(a,b,gb) | gives the complement for the sum cell for free |
| G10, G32 | OAI21 on gb/tb | true polarity straight from level-1 outputs |
| T10, T32 | NOR2 on tb | idem |
| G20, G30, T20, T30 | AOI21/NAND2 + INV | keeps every stack ≤ 2 high |
| ci' | AOI21(c0, T, G) | **one gate from c0**; c0 placed on the transistor next to the output |
| s_i | SUMCELL(p, pb, ci') | c' is the only late input |

Polarity is alternated deliberately (inverted outputs feed gates that expect inverted inputs) instead of using
AND/OR (= NAND/NOR + INV), which saves a stage on every path.

## 4. Sum cell – two candidates (decided by simulation, step 2)
* **TG mux (6T)**: c' selects p or p' through two transmission gates. Fastest on paper, fewest transistors, but
  the two TGs overlap briefly (local inverter delay) and the output is not restored.
* **AOI22 (10T)**: `s = (c·p + c'·p')'`. Restoring, no contention, more capacitance.
Choice criterion: lower PDP on the worst-case vector, with full output swing.

## 5. Flip-flop: TSPC (11T)
Single clock (no clk-bar routing, no two-phase skew), 3 clocked transistors per stage pair → low clock load
(14 flip-flops share the clock, so clock power is a large share of Pavg), short tcq and small setup.
Risk: dynamic nodes — must be checked at a low clock frequency (done in step 4).

## 6. Sizing method
Every cell is sized to the strength of a unit inverter × s (stacked devices doubled; logical-effort style).
Knobs: `UN` (unit NMOS width, λ), `BETA` (Wp/Wn, model µn/µp ≈ 2.4 → 2 used), and per-block multipliers
`SPG, SGRP, SCAR, SSUM, SC0`. Step 3 sweeps them: delay saturates as widths grow while power rises linearly,
so PDP has a minimum at moderate sizes — that minimum is the chosen design point.

## 7. Timing definitions used in the report
* tpd: 50 % VDD of C0 to 50 % VDD of the slowest of S0..S3, C4, both tpLH and tpHL.
* tsetup: smallest D→CLK time with tcq ≤ 1.1 × nominal tcq. thold: smallest CLK→D-change time with correct capture.
* fmax reported two ways: the project formula, and the strict register-to-register limit
  (tcq + tpd,reg-reg + tsetup), verified by running the full circuit at that clock.
