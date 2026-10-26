"""Exhaustive check of results/logs/cla_func.dat (512 vectors)."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from wrdata import load, at, logic

t, c = load("results/logs/cla_func.dat")      # s0 s1 s2 s3 c4
bad = 0
for k in range(512):
    A, B, C0 = k & 0xF, (k >> 4) & 0xF, (k >> 8) & 1
    exp = A + B + C0
    ts = (k + 0.95) * 1e-9
    got = [logic(at(t, c[i], ts)) for i in range(5)]
    e = [(exp >> i) & 1 for i in range(5)]
    if got != e:
        bad += 1
        if bad <= 20:
            print(f"FAIL A={A:2d} B={B:2d} C0={C0}: expected S={exp & 15:2d} C4={exp >> 4}  got {got}")
print("CLA FUNCTIONAL:", "ALL 512 VECTORS PASS" if bad == 0 else f"{bad} failing vectors")
