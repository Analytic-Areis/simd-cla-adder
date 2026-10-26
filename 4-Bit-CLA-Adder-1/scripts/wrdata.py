"""Reader for ngspice `wrdata` files: columns are (time, value) pairs."""
import bisect

def load(path):
    t, cols = [], None
    with open(path) as f:
        for line in f:
            parts = line.split()
            if not parts:
                continue
            try:
                vals = [float(x) for x in parts]
            except ValueError:
                continue                     # header line
            if cols is None:
                cols = [[] for _ in range(len(vals) // 2)]
            t.append(vals[0])
            for i in range(len(cols)):
                cols[i].append(vals[2 * i + 1])
    return t, cols

def at(t, col, time):
    i = min(max(bisect.bisect_left(t, time), 1), len(t) - 1)
    t0, t1 = t[i - 1], t[i]
    v0, v1 = col[i - 1], col[i]
    return v0 if t1 == t0 else v0 + (v1 - v0) * (time - t0) / (t1 - t0)

def logic(v, vdd=1.8):
    if v > 0.8 * vdd: return 1
    if v < 0.2 * vdd: return 0
    return None                              # not settled / bad level
