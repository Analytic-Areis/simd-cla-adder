"""Gate-level (boolean) simulation of spice/blocks/cla4.lib.
Parses the X-instances of subckt CLA4 and evaluates them as logic gates,
so wiring/equation errors are caught before any SPICE run.
Also reports the logic depth (gate levels) from every input to every output."""
import itertools, re

F = {
 "INV":   lambda i: [1 - i[0]],
 "NAND2": lambda i: [1 - (i[0] & i[1])],
 "NOR2":  lambda i: [1 - (i[0] | i[1])],
 "AOI21": lambda i: [1 - ((i[0] & i[1]) | i[2])],
 "OAI21": lambda i: [1 - ((i[0] | i[1]) & i[2])],
 "SUMCELL": lambda i: [i[0] if i[2] else i[1]],      # p, pb, cb -> s
}
NIN = {"INV": 1, "NAND2": 2, "NOR2": 2, "AOI21": 3, "OAI21": 3, "SUMCELL": 3}

txt = open("spice/blocks/cla4.lib").read()
body = re.search(r"\.subckt CLA4 (.*?)\n(.*?)\.ends", txt, re.S)
ports = body.group(1).split()
gates = []
for line in body.group(2).splitlines():
    tok = line.split("*")[0].split()
    if not tok or not tok[0].upper().startswith("X"):
        continue
    nodes = [t for t in tok[1:] if "=" not in t]
    cell = nodes[-1]; nodes = nodes[:-1]
    n = NIN[cell]
    gates.append((tok[0], cell, nodes[:n], nodes[n]))

ins = ["a0","a1","a2","a3","b0","b1","b2","b3","c0"]
outs = ["s0","s1","s2","s3","c4","c4b"]

def evaluate(vec):
    val = dict(zip(ins, vec)); lvl = {k: 0 for k in ins}
    pending = list(gates)
    while pending:
        rest = []
        for g in pending:
            name, cell, i, o = g
            if all(x in val for x in i):
                val[o] = F[cell]([val[x] for x in i])[0]
                lvl[o] = 1 + max(lvl[x] for x in i)
            else:
                rest.append(g)
        if len(rest) == len(pending):
            raise SystemExit(f"unresolved nodes / loop: {[g[0] for g in rest]}")
        pending = rest
    return val, lvl

bad = 0
for k in range(512):
    vec = [(k >> i) & 1 for i in range(9)]
    A = sum(vec[i] << i for i in range(4)); B = sum(vec[4+i] << i for i in range(4))
    s = A + B + vec[8]
    v, lvl = evaluate(vec)
    got = [v[o] for o in outs]
    exp = [(s >> i) & 1 for i in range(5)] + [1 - (s >> 4)]
    if got != exp:
        bad += 1; print("FAIL", A, B, vec[8], got, exp)
print(f"gates: {len(gates)}   boolean check of 512 vectors: {'PASS' if not bad else str(bad)+' FAIL'}")

# logic depth from c0 only (structural path length)
def depth_from(src):
    d = {src: 0}; changed = True
    while changed:
        changed = False
        for _, _, i, o in gates:
            ds = [d[x] for x in i if x in d]
            if ds and d.get(o, -1) < 1 + max(ds):
                d[o] = 1 + max(ds); changed = True
    return d
_, lvl = evaluate([0]*9)
print("max gate levels from any input :", {o: lvl[o] for o in outs})
d = depth_from("c0")
print("gate levels from c0            :", {o: d.get(o) for o in outs})
