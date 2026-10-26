"""Check results/logs/cells.dat against the truth table of every cell."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from wrdata import load, at, logic

t, c = load("results/logs/cells.dat")
names = ["A", "B", "C", "INV", "NAND2", "NOR2", "AOI21", "OAI21", "SUM(xnor A,B)"]
ref = {
    "INV":   lambda a, b, cc: 1 - a,
    "NAND2": lambda a, b, cc: 1 - (a & b),
    "NOR2":  lambda a, b, cc: 1 - (a | b),
    "AOI21": lambda a, b, cc: 1 - ((a & b) | cc),
    "OAI21": lambda a, b, cc: 1 - ((a | b) & cc),
    "SUM(xnor A,B)": lambda a, b, cc: 1 - (a ^ b),   # SUMCELL(p=A, pb=A', cb=B)
}
bad = 0
for k in range(8):
    ts = (k + 0.9) * 1e-9
    a, b, cc = k & 1, (k >> 1) & 1, (k >> 2) & 1
    for idx, n in enumerate(names[3:], start=3):
        got = logic(at(t, c[idx], ts))
        exp = ref[n](a, b, cc)
        if got != exp:
            bad += 1
            print(f"FAIL {n:14s} A={a} B={b} C={cc}  expected {exp} got {got}")
print("CELLS:", "ALL PASS" if bad == 0 else f"{bad} failures")
