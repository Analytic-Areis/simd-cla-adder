"""Candidate 4-bit adders, each a flat connection of library leaf cells.

sizes maps a role to a drive multiplier. A per-bit key such as "nor0" overrides the
role key "nor". Everything defaults to unit drive. Candidate letters follow
part1/planning/architecture_comparison.md.
"""
from cellgen import Block
from library import (aoi21, carry, carry3_mirror, carry4_mirror, inv, mcc_bit, nand, nor, oai21, xor_aoi22,
                     xor_nand4, xor_static12, xor_tg)

INPUTS = [f"a{i}" for i in range(4)] + [f"b{i}" for i in range(4)] + ["c0"]
OUTPUTS = [f"s{i}" for i in range(4)] + ["c4"]


def adder_logic(v):
    a = sum(v[f"a{i}"] << i for i in range(4))
    b = sum(v[f"b{i}"] << i for i in range(4))
    total = a + b + v["c0"]
    out = {f"s{i}": (total >> i) & 1 for i in range(4)}
    out["c4"] = (total >> 4) & 1
    return out


class Sizes:
    def __init__(self, table=None):
        self.table = dict(table or {})

    def __call__(self, key, bit=None):
        if bit is not None and f"{key}{bit}" in self.table:
            return self.table[f"{key}{bit}"]
        return self.table.get(key, 1.0)


class Builder:
    def __init__(self, name, description):
        self.name, self.description, self.inst = name, description, []

    def add(self, inst, cell, **pins):
        self.inst.append((inst, cell, pins))

    def block(self):
        return Block(self.name, INPUTS, OUTPUTS, adder_logic, self.inst, self.description)


def _front_end(b, s):
    """NAND2, NOR2, compound P and P-bar for all four bits."""
    for i in range(4):
        b.add(f"nand{i}", nand(2, s("nand", i)), i0=f"a{i}", i1=f"b{i}", y=f"g{i}b")
        b.add(f"nor{i}", nor(2, s("nor", i)), i0=f"a{i}", i1=f"b{i}", y=f"t{i}b")
        b.add(f"aoi{i}", aoi21(s("aoi", i)), a=f"a{i}", b=f"b{i}", c=f"t{i}b", y=f"p{i}")
        b.add(f"oai{i}", oai21(s("oai", i)), a=f"a{i}", b=f"b{i}", c=f"g{i}b", y=f"p{i}b")


def _sum_stage(b, s, style="aoi22"):
    for i in range(4):
        carry_net = "c0" if i == 0 else f"c{i}"
        if style == "aoi22":
            b.add(f"x{i}", xor_aoi22(s("xor", i), s("xinv", i)), p=f"p{i}", pb=f"p{i}b", c=carry_net, s=f"s{i}")
        elif style == "tg":
            b.add(f"x{i}", xor_tg(s("xor", i), s("xinv", i), s("xtg", i)), p=f"p{i}", pb=f"p{i}b", c=carry_net,
                  s=f"s{i}")
        elif style == "static12":
            b.add(f"x{i}", xor_static12(s("xor", i)), p=f"p{i}", c=carry_net, s=f"s{i}")
        elif style == "nand4":
            b.add(f"x{i}", xor_nand4(s("xor", i)), p=f"p{i}", c=carry_net, s=f"s{i}")
        else:
            raise ValueError(style)


def _flat_carries(b, s, tops, flips=None):
    flips = flips or {}
    b.add("invc0", inv(s("invc0")), a="c0", y="c0b")
    for top in tops:
        gate = carry(top, s(f"c{top + 1}"), *flips.get(top, (False, False)))
        pins = {p: p for p in gate.inputs}
        pins[gate.output] = gate.output
        b.add(f"c{top + 1}", gate, **pins)


def candidate_r(sizes=None, sum_style="aoi22", flips=None, name=None):
    """Lead candidate: C1 to C3 single gates, C4 mirror gate over C2 plus inverter."""
    s = Sizes(sizes)
    b = Builder(name or f"cla_r_{sum_style}", "Candidate R: flat C1 to C3, mirror C4 over C2")
    _front_end(b, s)
    _flat_carries(b, s, [0, 1, 2], flips)
    b.add("c4m", carry4_mirror(s("c4m")), a3="a3", b3="b3", a2="a2", b2="b2", c2="c2", c4b="c4b")
    b.add("invc4", inv(s("invc4")), a="c4b", y="c4")
    _sum_stage(b, s, sum_style)
    return b.block()


def candidate_c2(sizes=None, sum_style="aoi22", flips=None, name=None):
    """Direct rival: one complex gate per carry, including a 5-high C4 gate."""
    s = Sizes(sizes)
    b = Builder(name or f"cla_c2_{sum_style}", "Candidate C2: one complex gate per carry, stack up to 5")
    _front_end(b, s)
    _flat_carries(b, s, [0, 1, 2, 3], flips)
    _sum_stage(b, s, sum_style)
    return b.block()


def candidate_c3(sizes=None, sum_style="aoi22", name=None):
    """Stack limit 3: C1, C2 single gates; C3 and C4 mirror gates over C2."""
    s = Sizes(sizes)
    b = Builder(name or "cla_c3", "Candidate C3: stack limit 3, two carry levels")
    _front_end(b, s)
    _flat_carries(b, s, [0, 1])
    b.add("c3m", carry3_mirror(s("c3m")), a2="a2", b2="b2", c2="c2", c3b="c3b")
    b.add("invc3", inv(s("invc3")), a="c3b", y="c3")
    b.add("c4m", carry4_mirror(s("c4m")), a3="a3", b3="b3", a2="a2", b2="b2", c2="c2", c4b="c4b")
    b.add("invc4", inv(s("invc4")), a="c4b", y="c4")
    _sum_stage(b, s, sum_style)
    return b.block()


def candidate_c4(sizes=None, sum_style="aoi22", flips=None, name=None):
    """Valency-2 prefix tree with C0 entering last."""
    s = Sizes(sizes)
    flips = flips or {}

    def oai21_f(key):
        return oai21(s(key), *flips.get(key, (False, False)))

    def aoi21_f(key):
        return aoi21(s(key), *flips.get(key, (False, False)))
    b = Builder(name or f"cla_c4_{sum_style}", "Candidate C4: valency-2 prefix, late C0")
    _front_end(b, s)
    b.add("invc0", inv(s("invc0")), a="c0", y="c0b")
    # level 1, active high group terms from active-low bits
    b.add("g10", oai21_f("g10"), a="t1b", b="g0b", c="g1b", y="g1_0")
    b.add("t10", nor(2, s("t10")), i0="t1b", i1="t0b", y="t1_0")
    b.add("g32", oai21_f("g32"), a="t3b", b="g2b", c="g3b", y="g3_2")
    b.add("t32", nor(2, s("t32")), i0="t3b", i1="t2b", y="t3_2")
    b.add("ig2", inv(s("ig2")), a="g2b", y="g2")
    b.add("it2", inv(s("it2")), a="t2b", y="t2")
    # level 2, active low groups spanning down to bit 0
    b.add("g30", aoi21_f("g30"), a="t3_2", b="g1_0", c="g3_2", y="g3_0b")
    b.add("t30", nand(2, s("t30")), i0="t3_2", i1="t1_0", y="t3_0b")
    b.add("g20", aoi21_f("g20"), a="t2", b="g1_0", c="g2", y="g2_0b")
    b.add("t20", nand(2, s("t20")), i0="t2", i1="t1_0", y="t2_0b")
    b.add("ig10", inv(s("ig10")), a="g1_0", y="g1_0b")
    b.add("it10", inv(s("it10")), a="t1_0", y="t1_0b")
    # final carries with C0
    b.add("c1", oai21_f("c1"), a="t0b", b="c0b", c="g0b", y="c1")
    b.add("c2", oai21_f("c2"), a="t1_0b", b="c0b", c="g1_0b", y="c2")
    b.add("c3", oai21_f("c3"), a="t2_0b", b="c0b", c="g2_0b", y="c3")
    b.add("c4g", oai21_f("c4g"), a="t3_0b", b="c0b", c="g3_0b", y="c4")
    _sum_stage(b, s, sum_style)
    return b.block()


def candidate_e(sizes=None, sum_style="aoi22", name=None):
    """Static Manchester chain with a buffer at C2 and at C4."""
    s = Sizes(sizes)
    b = Builder(name or "cla_e", "Candidate E: static Manchester transmission-gate chain")
    _front_end(b, s)
    b.add("m0", mcc_bit(s("mcc")), ci="c0", a="a0", p="p0", pb="p0b", co="c1")
    b.add("m1", mcc_bit(s("mcc")), ci="c1", a="a1", p="p1", pb="p1b", co="c2r")
    b.add("buf2a", inv(s("buf")), a="c2r", y="c2n")
    b.add("buf2b", inv(s("buf")), a="c2n", y="c2")
    b.add("m2", mcc_bit(s("mcc")), ci="c2", a="a2", p="p2", pb="p2b", co="c3")
    b.add("m3", mcc_bit(s("mcc")), ci="c3", a="a3", p="p3", pb="p3b", co="c4r")
    b.add("buf4a", inv(s("buf")), a="c4r", y="c4n")
    b.add("buf4b", inv(s("buf")), a="c4n", y="c4")
    _sum_stage(b, s, sum_style)
    return b.block()


def candidate_c1(sizes=None, name=None):
    """Baseline: XOR propagate, AND generate, NAND-NAND carries, 12T XOR sums."""
    s = Sizes(sizes)
    b = Builder(name or "cla_c1", "Candidate C1: textbook XOR propagate, NAND-NAND carries")
    for i in range(4):
        b.add(f"px{i}", xor_static12(s("px", i)), p=f"a{i}", c=f"b{i}", s=f"p{i}")
        b.add(f"gn{i}", nand(2, s("gn", i)), i0=f"a{i}", i1=f"b{i}", y=f"g{i}b")
        b.add(f"gi{i}", inv(s("gi", i)), a=f"g{i}b", y=f"g{i}")
    for k in range(1, 5):
        # Ck = g(k-1) + p(k-1)g(k-2) + ... + p(k-1)..p0 c0, built NAND-NAND
        terms = [f"g{k - 1}b"]
        for j in range(k - 1, -1, -1):
            pins = [f"p{m}" for m in range(k - 1, j - 1, -1)]
            pins.append("c0" if j == 0 else f"g{j - 1}")
            term = f"n{k}_{j}"
            cell = nand(len(pins), s("cn"))
            b.add(f"cn{k}_{j}", cell, y=term, **{f"i{n}": p for n, p in enumerate(pins)})
            terms.append(term)
        cell = nand(len(terms), s("cm"))
        b.add(f"cm{k}", cell, y=f"c{k}", **{f"i{n}": t for n, t in enumerate(terms)})
    _sum_stage_c1(b, s)
    return b.block()


def _sum_stage_c1(b, s):
    for i in range(4):
        b.add(f"sx{i}", xor_static12(s("xor", i)), p=f"p{i}", c="c0" if i == 0 else f"c{i}", s=f"s{i}")


CANDIDATES = {
    "C1": candidate_c1, "C2": candidate_c2, "R": candidate_r, "C3": candidate_c3,
    "C4": candidate_c4, "E": candidate_e,
}
