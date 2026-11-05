"""Cell definitions for the 4-bit CLA candidates.

Sizes here are unit-drive starting points, not the optimised design. Input order is
also provisional; both are set by the comparison and optimisation phases.
Pin names ending in b are active-low, so g0b means g-bar 0.
"""
from itertools import product

from cellgen import Block, Cell, D, GateStage, Pa, S, StagedCell, TGStage, dual, mirror


def inv(drive=1.0, name=None):
    return Cell(name or f"inv_x{drive:g}".replace(".", "p"), D("a"), ["a"], lambda v: 1 - v["a"],
                drive=drive, description="inverter")


def nand(n, drive=1.0):
    pins = [f"i{k}" for k in range(n)]

    def logic(v):
        return 1 - min(v[p] for p in pins)
    return Cell(f"nand{n}_x{drive:g}".replace(".", "p"), S(*[D(p) for p in pins]), pins, logic,
                drive=drive, description=f"{n}-input NAND")


def nor(n, drive=1.0):
    pins = [f"i{k}" for k in range(n)]

    def logic(v):
        return 1 - max(v[p] for p in pins)
    return Cell(f"nor{n}_x{drive:g}".replace(".", "p"), Pa(*[D(p) for p in pins]), pins, logic,
                drive=drive, description=f"{n}-input NOR")


def _flipped(pdn, flip_n, flip_p):
    pun = dual(pdn)
    return (_reversed_series(pdn) if flip_n else pdn), (_reversed_series(pun) if flip_p else pun)


def _flip_tag(flip_n, flip_p):
    tag = ("n" if flip_n else "") + ("p" if flip_p else "")
    return f"_f{tag}" if tag else ""


def aoi21(drive=1.0, flip_n=False, flip_p=False):
    pdn, pun = _flipped(Pa(S(D("a"), D("b")), D("c")), flip_n, flip_p)
    return Cell(f"aoi21{_flip_tag(flip_n, flip_p)}_x{drive:g}".replace(".", "p"), pdn, ["a", "b", "c"],
                lambda v: 1 - ((v["a"] & v["b"]) | v["c"]), pun=pun, drive=drive, description="NOT(a b + c)")


def oai21(drive=1.0, flip_n=False, flip_p=False):
    pdn, pun = _flipped(S(Pa(D("a"), D("b")), D("c")), flip_n, flip_p)
    return Cell(f"oai21{_flip_tag(flip_n, flip_p)}_x{drive:g}".replace(".", "p"), pdn, ["a", "b", "c"],
                lambda v: 1 - ((v["a"] | v["b"]) & v["c"]), pun=pun, drive=drive, description="NOT((a + b) c)")


def aoi22(drive=1.0):
    return Cell(f"aoi22_x{drive:g}".replace(".", "p"), Pa(S(D("a"), D("b")), S(D("c"), D("d"))),
                ["a", "b", "c", "d"], lambda v: 1 - ((v["a"] & v["b"]) | (v["c"] & v["d"])),
                drive=drive, description="NOT(a b + c d)")


def _carry_pdn(top):
    """Nested carry pull-down over g-bar, t-bar and c0-bar, for carry C(top+1)."""
    node = Pa(D("t0b"), D("c0b"))
    for i in range(top + 1):
        node = S(D(f"g{i}b"), node)
        if i < top:
            node = Pa(D(f"t{i + 1}b"), node)
    return node


def _carry_logic(top):
    def logic(v):
        c = 1 - v["c0b"]
        for i in range(top + 1):
            c = (1 - v[f"g{i}b"]) | ((1 - v[f"t{i}b"]) & c)
        return c
    return logic


def _reversed_series(node):
    """Same function, series order reversed throughout: moves the inner group next to the output."""
    if isinstance(node, D):
        return D(node.gate, node.w)
    if isinstance(node, S):
        return S(*[_reversed_series(c) for c in reversed(node.children)])
    return Pa(*[_reversed_series(c) for c in node.children])


def carry(top, drive=1.0, flip_n=False, flip_p=False):
    """C1, C2, C3 or C4 for top = 0, 1, 2, 3. Stack height top + 2 in each network.

    flip_n and flip_p reverse the series order in that network, changing which inputs
    sit next to the output. The logic is unchanged.
    """
    pins = [p for i in range(top + 1) for p in (f"g{i}b", f"t{i}b")] + ["c0b"]
    pdn = _carry_pdn(top)
    pun = dual(pdn)
    if flip_n:
        pdn = _reversed_series(pdn)
    if flip_p:
        pun = _reversed_series(pun)
    tag = ("n" if flip_n else "") + ("p" if flip_p else "")
    name = f"c{top + 1}{'_f' + tag if tag else ''}_x{drive:g}".replace(".", "p")
    return Cell(name, pdn, pins, _carry_logic(top), pun=pun, drive=drive, output=f"c{top + 1}",
                description=f"C{top + 1} complex gate, stack {top + 2}")


def carry3_mirror(drive=1.0):
    """C3-bar mirror gate over a2, b2 and C2, with C2 nearest the output. 10T."""
    pdn = Pa(S(D("a2"), D("b2")), S(D("c2"), Pa(D("a2"), D("b2"))))

    def logic(v):
        return 1 - ((v["a2"] & v["b2"]) | ((v["a2"] | v["b2"]) & v["c2"]))
    return Cell(f"c3b_mirror_x{drive:g}".replace(".", "p"), pdn, ["a2", "b2", "c2"], logic,
                pun=mirror(pdn), drive=drive, output="c3b", description="C3-bar mirror gate, stack 2")


def carry4_mirror(drive=1.0):
    """C4-bar mirror gate over a3, b3, a2, b2 and C2, with C2 nearest the output."""
    inner = Pa(S(D("a2"), D("b2")), S(D("c2"), Pa(D("a2"), D("b2"))))
    pdn = Pa(S(D("a3"), D("b3")), S(inner, Pa(D("a3"), D("b3"))))

    def logic(v):
        c3 = (v["a2"] & v["b2"]) | ((v["a2"] | v["b2"]) & v["c2"])
        return 1 - ((v["a3"] & v["b3"]) | ((v["a3"] | v["b3"]) & c3))
    return Cell(f"c4b_mirror_x{drive:g}".replace(".", "p"), pdn, ["a3", "b3", "a2", "b2", "c2"], logic,
                pun=mirror(pdn), drive=drive, output="c4b",
                description="C4-bar mirror gate, stack 3")


def _rail_pairs(signal, rail):
    """Vectors over p and c where rail (p-bar) is always the complement of signal."""
    return [{signal: p, rail: 1 - p, "c": c} for p, c in product([0, 1], repeat=2)]


def _xor(v):
    return {"s": v["p"] ^ v["c"]}


def _fmt(*values):
    return "_".join(f"{v:g}".replace(".", "p") for v in values)


def xor_aoi22(drive=1.0, inv_drive=None):
    """Dual-rail XOR: inverter makes c-bar, AOI22 forms NOT(p c + p-bar c-bar). 10T."""
    inv_drive = drive if inv_drive is None else inv_drive
    name = f"xor_aoi22_x{_fmt(drive)}" if inv_drive == drive else f"xor_aoi22_x{_fmt(drive, inv_drive)}"
    return StagedCell(name, ["p", "pb", "c"], ["s"], _xor, [
        GateStage(D("c"), "cb", drive=inv_drive),
        GateStage(Pa(S(D("p"), D("c")), S(D("pb"), D("cb"))), "s", drive=drive),
    ], "dual-rail XOR, AOI22 with c-bar inverter", vector_fn=lambda: _rail_pairs("p", "pb"))


def xor_tg(drive=1.0, inv_drive=None, tg_drive=1.0):
    """Carry selects p or p-bar through transmission gates, then an inverter drives. 8T."""
    inv_drive = drive if inv_drive is None else inv_drive
    default = inv_drive == drive and tg_drive == 1.0
    name = f"xor_tg_x{_fmt(drive)}" if default else f"xor_tg_x{_fmt(drive, inv_drive, tg_drive)}"
    wn, wp = max(3, round(10 * tg_drive)), max(3, round(20 * tg_drive))
    return StagedCell(name, ["p", "pb", "c"], ["s"], _xor, [
        GateStage(D("c"), "cb", drive=inv_drive),
        TGStage("p", "m", "c", "cb", wn, wp),
        TGStage("pb", "m", "cb", "c", wn, wp),
        GateStage(D("m"), "s", drive=drive),
    ], "transmission-gate mux XOR with output inverter", vector_fn=lambda: _rail_pairs("p", "pb"))


def xor_static12(drive=1.0):
    """Single-rail static XOR: two inverters and AOI22. 12T."""
    return StagedCell(f"xor_static12_x{drive:g}".replace(".", "p"), ["p", "c"], ["s"], _xor, [
        GateStage(D("p"), "pb", drive=drive),
        GateStage(D("c"), "cb", drive=drive),
        GateStage(Pa(S(D("p"), D("c")), S(D("pb"), D("cb"))), "s", drive=drive),
    ], "static XOR, AOI22 with two inverters")


def xor_nand4(drive=1.0):
    """Baseline four-NAND XOR. 16T."""
    return StagedCell(f"xor_nand4_x{drive:g}".replace(".", "p"), ["p", "c"], ["s"], _xor, [
        GateStage(S(D("p"), D("c")), "n1", drive=drive),
        GateStage(S(D("p"), D("n1")), "n2", drive=drive),
        GateStage(S(D("c"), D("n1")), "n3", drive=drive),
        GateStage(S(D("n2"), D("n3")), "s", drive=drive),
    ], "four-NAND XOR baseline")


def mcc_bit(drive=1.0):
    """Static Manchester stage: co = p ? ci : a, as two transmission gates. 4T."""
    wn, wp = max(3, round(10 * drive)), max(3, round(20 * drive))

    def logic(v):
        return {"co": v["ci"] if v["p"] else v["a"]}

    def vectors():
        return [{"ci": c, "a": a, "p": p, "pb": 1 - p} for c, a, p in product([0, 1], repeat=3)]
    return StagedCell(f"mcc_bit_x{drive:g}".replace(".", "p"), ["ci", "a", "p", "pb"], ["co"], logic, [
        TGStage("ci", "co", "p", "pb", wn, wp),
        TGStage("a", "co", "pb", "p", wn, wp),
    ], "Manchester carry stage, transmission-gate mux", vector_fn=vectors)


def pg_bit(drive=1.0):
    """One bit of the P/G block: g-bar, t-bar, P and P-bar. 20T, no internal inverter."""
    def logic(v):
        g, t = v["a"] & v["b"], v["a"] | v["b"]
        p = v["a"] ^ v["b"]
        return {"gb": 1 - g, "tb": 1 - t, "p": p, "pb": 1 - p}
    suffix = f"x{drive:g}".replace(".", "p")
    return Block(f"pg_bit_{suffix}", ["a", "b"], ["gb", "tb", "p", "pb"], logic, [
        ("nand", nand(2, drive), {"i0": "a", "i1": "b", "y": "gb"}),
        ("nor", nor(2, drive), {"i0": "a", "i1": "b", "y": "tb"}),
        ("aoi", aoi21(drive), {"a": "a", "b": "b", "c": "tb", "y": "p"}),
        ("oai", oai21(drive), {"a": "a", "b": "b", "c": "gb", "y": "pb"}),
    ], "P/G bit: NAND2, NOR2, compound AOI21 and OAI21")


def pg_block(drive=1.0):
    bit = pg_bit(drive)

    def logic(v):
        out = {}
        for i in range(4):
            r = bit.logic({"a": v[f"a{i}"], "b": v[f"b{i}"]})
            out.update({f"g{i}b": r["gb"], f"t{i}b": r["tb"], f"p{i}": r["p"], f"p{i}b": r["pb"]})
        return out
    inputs = [f"a{i}" for i in range(4)] + [f"b{i}" for i in range(4)]
    outputs = [f"{n}" for i in range(4) for n in (f"g{i}b", f"t{i}b", f"p{i}", f"p{i}b")]
    instances = [(f"bit{i}", bit, {"a": f"a{i}", "b": f"b{i}", "gb": f"g{i}b", "tb": f"t{i}b",
                                   "p": f"p{i}", "pb": f"p{i}b"}) for i in range(4)]
    return Block(f"pg_block_x{drive:g}".replace(".", "p"), inputs, outputs, logic, instances,
                 "4-bit propagate and generate block")


def carry_r(drive=1.0):
    """Candidate R carry generator: C1 to C3 single gates, C4 mirror gate over C2."""
    gates = {0: carry(0, drive), 1: carry(1, drive), 2: carry(2, drive)}
    inputs = ["g0b", "t0b", "g1b", "t1b", "g2b", "t2b", "c0", "a2", "b2", "a3", "b3"]

    def logic(v):
        c = v["c0"]
        out = {}
        for i in range(3):
            c = (1 - v[f"g{i}b"]) | ((1 - v[f"t{i}b"]) & c)
            out[f"c{i + 1}"] = c
        c3_from_c2 = (v["a2"] & v["b2"]) | ((v["a2"] | v["b2"]) & out["c2"])
        out["c4"] = (v["a3"] & v["b3"]) | ((v["a3"] | v["b3"]) & c3_from_c2)
        return out

    instances = [("invc0", inv(drive), {"a": "c0", "y": "c0b"})]
    for i, gate in gates.items():
        pins = {p: p for p in gate.inputs}
        pins[gate.output] = gate.output
        instances.append((f"c{i + 1}", gate, pins))
    instances += [
        ("c4m", carry4_mirror(drive), {"a3": "a3", "b3": "b3", "a2": "a2", "b2": "b2", "c2": "c2", "c4b": "c4b"}),
        ("invc4", inv(drive), {"a": "c4b", "y": "c4"}),
    ]
    return Block(f"carry_r_x{drive:g}".replace(".", "p"), inputs, ["c1", "c2", "c3", "c4"], logic, instances,
                 "candidate R carry generator")


def sum_block(xor_cell, needs_rail, drive=1.0):
    """Four XOR stages. Si = Pi xor Ci."""
    cell = xor_cell(drive)
    base = cell.name.rsplit("_x", 1)[0]
    inputs = [f"p{i}" for i in range(4)] + ([f"p{i}b" for i in range(4)] if needs_rail else []) + \
             [f"c{i}" for i in range(4)]

    def logic(v):
        return {f"s{i}": v[f"p{i}"] ^ v[f"c{i}"] for i in range(4)}

    def vectors():
        out = []
        for bits in product([0, 1], repeat=8):
            vec = {f"p{i}": bits[i] for i in range(4)}
            vec.update({f"c{i}": bits[4 + i] for i in range(4)})
            if needs_rail:
                vec.update({f"p{i}b": 1 - bits[i] for i in range(4)})
            out.append(vec)
        return out

    instances = []
    for i in range(4):
        pins = {"p": f"p{i}", "c": f"c{i}", "s": f"s{i}"}
        if needs_rail:
            pins["pb"] = f"p{i}b"
        instances.append((f"sum{i}", cell, pins))
    return Block(f"sum_{base}_x{drive:g}".replace(".", "p"), inputs, [f"s{i}" for i in range(4)], logic,
                 instances, f"4-bit sum block using {base}", vector_fn=vectors)


def all_cells():
    return [inv(), nand(2), nand(3), nand(4), nand(5), nor(2), nor(3), nor(4), nor(5),
            aoi21(), oai21(), aoi22(), carry(0), carry(1), carry(2), carry(3), carry3_mirror(), carry4_mirror(),
            mcc_bit(), xor_aoi22(), xor_tg(), xor_static12(), xor_nand4()]


def all_blocks():
    return [pg_bit(), pg_block(), carry_r(), sum_block(xor_aoi22, True), sum_block(xor_tg, True),
            sum_block(xor_static12, False), sum_block(xor_nand4, False)]
