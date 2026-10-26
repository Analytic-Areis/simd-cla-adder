# Decision & results log

## 2026-10-25 — Step 0
* Decisions (by Bhargav): ngspice only for now (MAGIC later); **TSPC** flip-flops; **C0 is registered** too;
  plot titles via `set myname=Bhargav-ROLL` in `.spiceinit`.
* Model: `tech/TSMC_180nm.txt` (BSIM3v3.2, level 8; µ0n = 280.6, µ0p = 115.7 → µn/µp ≈ 2.4).
* Architecture fixed (see design.md). Boolean simulation of the actual netlist (`scripts/logic_check_netlist.py`):
  **42 gates, 512/512 vectors pass; c0 → every output = 2 gate levels; any input → output ≤ 6 levels.**
* Next: run `./scripts/run.sh step1` and `step2`.
