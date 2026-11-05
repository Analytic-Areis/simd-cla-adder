#!/usr/bin/env python3
"""Boolean check of the proposed candidate R gate functions over all 512 inputs.

Logic only: no circuit is simulated. Prints the number of mismatches.
"""
from itertools import product


def main():
    bad = 0
    for bits in product([0, 1], repeat=9):
        a, b, c0 = bits[:4], bits[4:8], bits[8]
        g = [x & y for x, y in zip(a, b)]
        t = [x | y for x, y in zip(a, b)]
        p = [x ^ y for x, y in zip(a, b)]
        gb = [1 - x for x in g]
        tb = [1 - x for x in t]
        cb = 1 - c0
        # compound P and P-bar reuse the NAND and NOR outputs
        pc = [1 - ((a[i] & b[i]) | tb[i]) for i in range(4)]
        pbc = [1 - ((a[i] | b[i]) & gb[i]) for i in range(4)]
        if pc != p or pbc != [1 - x for x in p]:
            bad += 1
        c = [c0]
        for i in range(4):
            c.append(g[i] | (p[i] & c[i]))
        c1 = 1 - (gb[0] & (tb[0] | cb))
        c2 = 1 - (gb[1] & (tb[1] | (gb[0] & (tb[0] | cb))))
        c3 = 1 - (gb[2] & (tb[2] | (gb[1] & (tb[1] | (gb[0] & (tb[0] | cb))))))
        c4b = 1 - ((a[3] & b[3]) | ((a[3] | b[3]) & ((a[2] & b[2]) | ((a[2] | b[2]) & c2))))
        c4 = 1 - c4b
        s = [1 - ((p[i] & c[i]) | ((1 - p[i]) & (1 - c[i]))) for i in range(4)]
        total = sum(x << i for i, x in enumerate(a)) + sum(x << i for i, x in enumerate(b)) + c0
        out = sum(x << i for i, x in enumerate(s)) + (c4 << 4)
        if (c1, c2, c3, c4) != tuple(c[1:]) or out != total:
            bad += 1
    print(f"boolean mismatches over 512 vectors: {bad}")


if __name__ == "__main__":
    main()
