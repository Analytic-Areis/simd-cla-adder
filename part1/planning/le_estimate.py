#!/usr/bin/env python3
"""First-order logical-effort ranking of candidate 4-bit CLA critical paths.

THEORETICAL EXPECTATION ONLY. This is not a simulation of any adder. g and p per
stage come from part1/simulations/characterisation/results/e4_stack_summary.csv
(measured on isolated NAND/NOR stacks) and from textbook values for XOR, then
D = N * F^(1/N) + sum(p). It ignores wires, input-slope interaction and the fact
that a real sizing has to satisfy several paths at once. Its only job is to decide
which architectures earn a place in the SPICE comparison.

Every stage is (label, g, p, b): logical effort, parasitic delay, branching effort.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
E4 = ROOT / "simulations/characterisation/results/e4_stack_summary.csv"
FIT = ROOT / "simulations/characterisation/results/e3_fit.csv"
OUT = Path(__file__).resolve().parent / "le_estimate_results.csv"

CL_FF = 7.58     # measured input capacitance of the 20L/10L load inverter (E1)
CIN_FF = 15.0    # budget per primary input: about 2 load inverters

rows = list(csv.DictReader(open(E4)))
tau = float(next(csv.DictReader(open(FIT)))["tau_ps"])
meas = {(r["kind"], int(r["n"]), r["input"]): (float(r["g"]), float(r["p"])) for r in rows}
pinv = meas[("nand", 1, "near")][1]


MODE = "measured"


def nand(n, pos="near"):
    if MODE == "textbook":
        return nand_th(n), float(n)
    return meas[("nand", n, pos)]


def nor(n, pos="near"):
    if MODE == "textbook":
        return nor_th(n), float(n)
    return meas[("nor", n, pos)]


def cplx(n, pos):
    """Symmetric complex gate with an n-high stack in both networks (AOI/OAI family).

    Sizing both stacks for unit drive makes every input device n x unit, so the input
    capacitance is the sum of the NAND-n and NOR-n cases relative to a 3-unit inverter;
    p is the mean of the NAND-n and NOR-n parasitics because a rising and a falling
    transition exercise one stack each.
    """
    if MODE == "textbook":
        return float(n), 2.0 * n
    (gn, pn), (gp, pp) = nand(n, pos), nor(n, pos)
    # Cin(NAND-n)=gn*3, Cin(NOR-n)=gp*3 in inverter units; n-device of the first plus
    # p-device of the second. Expressed in g: textbook value is g = n.
    return n * (gn + gp) / (nand_th(n) + nor_th(n)), (pn + pp) / 2


def nand_th(n):
    return (n + 2) / 3


def nor_th(n):
    return (2 * n + 1) / 3




def build_paths():
    pi = 1.0 if MODE == "textbook" else pinv
    XOR = (4.0, 2 * pi)   # textbook dual-rail static XOR: g=4 summed over a rail pair
    INV = (1.0, pi)
    return {
        "C1 textbook XOR + AND-OR (NAND-NAND), A0 to S3": [
            ("INV in XOR", *INV, 2), ("XOR P0", *XOR, 5),
            ("NAND4", *nand(4, "far"), 1), ("NAND4 merge", *nand(4, "far"), 1),
            ("INV in XOR", *INV, 2), ("XOR S3", *XOR, 1)],
        "C1 textbook XOR + AND-OR (NAND-NAND), C0 to S3": [
            ("NAND4", *nand(4, "near"), 4), ("NAND4 merge", *nand(4, "far"), 1),
            ("INV in XOR", *INV, 2), ("XOR S3", *XOR, 1)],
        "C1 textbook XOR + AND-OR (NAND-NAND), A0 to C4": [
            ("INV in XOR", *INV, 2), ("XOR P0", *XOR, 5),
            ("NAND5", *nand(5, "far"), 1), ("NAND5 merge", *nand(5, "far"), 1)],
        "C2 flat complex gate per carry (stack 5), A0 to S3": [
            ("NOR2 t0", *nor(2, "near"), 4), ("OAI stack4 C3", *cplx(4, "far"), 1),
            ("INV in XOR", *INV, 2), ("XOR S3", *XOR, 1)],
        "C2 flat complex gate per carry (stack 5), C0 to S3": [
            ("INV C0bar", *INV, 4), ("OAI stack4 C3", *cplx(4, "near"), 1),
            ("INV in XOR", *INV, 2), ("XOR S3", *XOR, 1)],
        "C2 flat complex gate per carry (stack 5), A0 to C4": [
            ("NOR2 t0", *nor(2, "near"), 4), ("OAI stack5 C4", *cplx(5, "far"), 1)],
        "C3 hybrid, stack <= 3, two carry levels, A0 to S3": [
            ("NOR2 t0", *nor(2, "near"), 2), ("OAI stack3 C2", *cplx(3, "far"), 2),
            ("AOI stack2 C3", *cplx(2, "near"), 1),
            ("INV in XOR", *INV, 2), ("XOR S3", *XOR, 1)],
        "C3 hybrid, stack <= 3, two carry levels, C0 to S3": [
            ("INV C0bar", *INV, 2), ("OAI stack3 C2", *cplx(3, "near"), 2),
            ("AOI stack2 C3", *cplx(2, "near"), 1),
            ("INV in XOR", *INV, 2), ("XOR S3", *XOR, 1)],
        "C3 hybrid, stack <= 3, two carry levels, A0 to C4": [
            ("NOR2 t0", *nor(2, "near"), 2), ("OAI stack3 C2", *cplx(3, "far"), 2),
            ("AOI stack3 C4", *cplx(3, "near"), 1)],
        "C4 prefix, valency 2, late C0, A0 to S3": [
            ("NOR2 t0", *nor(2, "near"), 2), ("AOI21 G1:0", *cplx(2, "far"), 2),
            ("OAI21 G2:0", *cplx(2, "far"), 1), ("AOI21 with C0", *cplx(2, "near"), 1),
            ("INV in XOR", *INV, 2), ("XOR S3", *XOR, 1)],
        "C4 prefix, valency 2, late C0, C0 to S3": [
            ("AOI21 with C0", *cplx(2, "near"), 4),
            ("INV in XOR", *INV, 2), ("XOR S3", *XOR, 1)],
        "C4 prefix, valency 2, late C0, A0 to C4": [
            ("NOR2 t0", *nor(2, "near"), 2), ("AOI21 G1:0", *cplx(2, "far"), 2),
            ("OAI21 G3:0", *cplx(2, "far"), 1), ("AOI21 with C0", *cplx(2, "near"), 1)],
        "R flat C1-C3 + C4 mirror over C2, A0 to S3": [
            ("NOR2 t0", *nor(2, "near"), 4), ("OAI stack4 C3", *cplx(4, "far"), 1),
            ("INV in XOR", *INV, 2), ("XOR S3", *XOR, 1)],
        "R flat C1-C3 + C4 mirror over C2, C0 to S3": [
            ("INV C0bar", *INV, 3), ("OAI stack4 C3", *cplx(4, "near"), 1),
            ("INV in XOR", *INV, 2), ("XOR S3", *XOR, 1)],
        "R flat C1-C3 + C4 mirror over C2, A0 to C4": [
            ("NOR2 t0", *nor(2, "near"), 4), ("OAI stack3 C2", *cplx(3, "far"), 2),
            ("mirror stack3 C4bar", *cplx(3, "near"), 1), ("INV C4", *INV, 1)],
    }


def evaluate(stages, cl=CL_FF, cin=CIN_FF):
    G = B = 1.0
    P = 0.0
    for _, g, p, b in stages:
        G *= g
        B *= b
        P += p
    F = G * B * cl / cin
    N = len(stages)
    f = F ** (1 / N)
    return F, N, f, P, N * f + P


def main():
    global MODE
    out = []
    MODE = "textbook"
    textbook = {k: evaluate(v)[4] for k, v in build_paths().items()}
    MODE = "measured"
    PATHS = build_paths()
    print(f"tau={tau:.2f} ps, pinv(effective)={pinv:.2f}, CL={CL_FF} fF, Cin={CIN_FF} fF\n")
    print(f"{'path':58s} {'F':>7s} {'N':>2s} {'f':>5s} {'P':>6s} {'D(tau)':>7s} {'D(ps)':>7s} {'textbook(ps)':>12s}")
    for name, stages in PATHS.items():
        F, N, f, P, D = evaluate(stages)
        print(f"{name:58s} {F:7.1f} {N:2d} {f:5.2f} {P:6.1f} {D:7.1f} {D * tau:7.0f} {textbook[name] * tau:12.0f}")
        out.append(dict(path=name, F=round(F, 2), N=N, f=round(f, 2), P=round(P, 2),
                        D_tau=round(D, 2), D_ps=round(D * tau, 1),
                        D_textbook_ps=round(textbook[name] * tau, 1)))
    with open(OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)


if __name__ == "__main__":
    main()
