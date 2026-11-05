#!/usr/bin/env python3
"""Generator tests that need no simulator.

Run from part1/cells: python3 -m unittest discover -s tests
"""
import re
import sys
import unittest
from itertools import product
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cellgen import Block, Cell, D, S, Pa, config as cfg
from cellgen import parse_flat, parse_subckt
from cellgen.schematic import draw
from cellgen.lvs import compare, schematic_devices
from cellgen.switchlevel import evaluate
from library import (all_blocks, all_cells, carry, carry4_mirror, carry_r, inv, nand, nor, pg_block,
                     sum_block, xor_aoi22, xor_nand4, xor_static12, xor_tg)

CHAR_RUNS = cfg.PART1 / "simulations" / "characterisation" / "runs"


def logic_errors(cell):
    """Evaluate the emitted SPICE text, not the definition tree. Returns problem strings."""
    devices = parse_flat(cell.spice(), cell.name)
    problems = []
    for vec in cell.vectors():
        values, shorts = evaluate(devices, vec)
        if shorts:
            problems.append(f"short at {vec}: {shorts}")
        expected = cell.truth(vec)
        for out in cell.outputs:
            got = values.get(out)
            if got is None:
                problems.append(f"{out} floating at {vec}")
            elif got != expected[out]:
                problems.append(f"{out}={got}, expected {expected[out]} at {vec}")
    return problems


class TestLogic(unittest.TestCase):
    def test_every_cell_and_block_implements_its_logic(self):
        for cell in all_cells() + all_blocks():
            with self.subTest(cell=cell.name):
                self.assertEqual(logic_errors(cell), [])

    def test_checker_catches_wrong_function(self):
        cell = Cell("w", S(D("a"), D("b")), ["a", "b"], lambda v: 1 - (v["a"] | v["b"]))
        self.assertTrue(logic_errors(cell))

    def test_checker_catches_floating_output(self):
        cell = Cell("f", S(D("a"), D("b")), ["a", "b"], lambda v: 1 - (v["a"] & v["b"]),
                    pun=S(D("a"), D("b")))
        self.assertTrue(any("floating" in p for p in logic_errors(cell)))

    def test_checker_catches_short(self):
        cell = Cell("s", S(D("a"), D("b")), ["a", "b"], lambda v: 1 - (v["a"] & v["b"]),
                    pun=Pa(D("a"), D("b"), D("c")))
        cell.vectors = lambda: [{"a": 1, "b": 1, "c": 0}]
        self.assertTrue(any("short" in p for p in logic_errors(cell)))

    def test_blocks_wired_together_add_correctly(self):
        """All 4 sum variants with the P/G and carry blocks, over all 512 inputs. Logic only."""
        for xor_cell, rail in ((xor_aoi22, True), (xor_tg, True), (xor_static12, False), (xor_nand4, False)):
            pg, cg, sm = pg_block(), carry_r(), sum_block(xor_cell, rail)
            ab = [f"a{i}" for i in range(4)] + [f"b{i}" for i in range(4)]
            pg_pins = {p: p for p in pg.inputs + pg.outputs}
            cg_pins = {p: p for p in cg.inputs + cg.outputs}
            sm_pins = {p: p for p in sm.inputs + sm.outputs}
            pg_pins = {p: p for p in pg.ports if p not in ("vdd", "gnd")}
            top = Block("top_check", ab + ["c0"], [f"s{i}" for i in range(4)] + ["c4"], None,
                        [("pg", pg, pg_pins), ("cg", cg, cg_pins), ("sm", sm, sm_pins)])
            devices = parse_flat(top.spice(), "top_check")
            bad = 0
            for bits in product([0, 1], repeat=9):
                vec = dict(zip(ab + ["c0"], bits))
                values, shorts = evaluate(devices, vec)
                a = sum(vec[f"a{i}"] << i for i in range(4))
                b = sum(vec[f"b{i}"] << i for i in range(4))
                got = sum(values[f"s{i}"] << i for i in range(4)) + (values["c4"] << 4)
                if shorts or got != a + b + vec["c0"]:
                    bad += 1
            with self.subTest(sum_cell=sm.name):
                self.assertEqual(bad, 0)
            self.assertEqual(top.transistor_count, 80 + 52 + 4 * xor_cell().transistor_count)


class TestStructure(unittest.TestCase):
    def test_widths_legal_and_bodies_tied(self):
        for cell in all_cells():
            for dev in cell.devices:
                self.assertGreaterEqual(dev.w_lam, cfg.WMIN_LAM)
                self.assertEqual(dev.w_lam, int(dev.w_lam), "width off the lambda grid")
                self.assertEqual(dev.bulk, "gnd" if dev.kind == "n" else "vdd")

    def test_schematic_shows_exactly_the_netlist(self):
        lam = cfg.LAMBDA_M
        for cell in all_cells():
            drawn = draw(cell)
            shown = sorted((d.name.lower(), d.kind, d.gate, d.drain, d.source,
                            round(d.w_lam * lam, 12), round(d.l_lam * lam, 12)) for d in drawn)
            _, parsed = parse_subckt(cell.spice())
            spice = sorted((d["name"].lower(), d["kind"], d["gate"], d["drain"], d["source"],
                            round(d["W"], 12), round(d["L"], 12)) for d in parsed)
            self.assertEqual(shown, spice, cell.name)

    def test_block_drawing_shows_the_netlist_connections(self):
        for block in all_blocks():
            drawn = draw(block)
            text = block.spice()
            lines = [l.split() for l in text.split(f".subckt {block.name} ")[1].splitlines() if l.startswith("X")]
            for inst, cell_name, pins in drawn:
                line = next(l for l in lines if l[0] == f"X{inst}")
                self.assertEqual(line[-1], cell_name)
                cell = next(c for i, c, _ in block.instances if i == inst)
                expected = [{"vdd": "vdd", "gnd": "gnd", **pins}[p] for p in cell.ports]
                self.assertEqual(line[1:-1], expected, block.name)

    def test_expected_counts(self):
        """The counts given in the architecture comparison."""
        self.assertEqual(carry(0).transistor_count, 6)
        self.assertEqual(carry(1).transistor_count, 10)
        self.assertEqual(carry(2).transistor_count, 14)
        self.assertEqual(carry4_mirror().transistor_count, 18)
        self.assertEqual(pg_block().transistor_count, 80)
        self.assertEqual(carry_r().transistor_count, 52)
        self.assertEqual(sum_block(xor_aoi22, True).transistor_count, 40)
        self.assertEqual(xor_tg().transistor_count, 8)
        self.assertEqual(xor_static12().transistor_count, 12)
        self.assertEqual(xor_nand4().transistor_count, 16)

    def test_stack_heights(self):
        """Series devices from output to rail, on the longest path."""
        def height(devices, start, rail):
            best, visited = 0, {start}

            def walk(net, depth):
                nonlocal best
                if net == rail:
                    best = max(best, depth)
                    return
                for d in devices:
                    if net not in (d["drain"], d["source"]):
                        continue
                    other = d["source"] if net == d["drain"] else d["drain"]
                    if other in visited:  # a real conduction path never revisits a node
                        continue
                    visited.add(other)
                    walk(other, depth + 1)
                    visited.discard(other)
            walk(start, 0)
            return best

        for cell, expected in ((carry(0), 2), (carry(1), 3), (carry(2), 4), (carry4_mirror(), 3)):
            _, devices = parse_subckt(cell.spice())
            nmos = [d for d in devices if d["kind"] == "n"]
            pmos = [d for d in devices if d["kind"] == "p"]
            with self.subTest(cell=cell.name):
                self.assertEqual(height(nmos, cell.output, "gnd"), expected)
                self.assertEqual(height(pmos, cell.output, "vdd"), expected)

    def test_inverter_output_is_not_treated_as_shared_junction(self):
        """An internal node joining one NMOS and one PMOS must be contacted."""
        devices = xor_aoi22().devices
        cb = [d for d in devices if "cb" in (d.drain, d.source)]
        length = cfg.SD_CONTACTED_LAM
        for dev in cb:
            area = dev.ad_lam2 if dev.drain == "cb" else dev.as_lam2
            self.assertEqual(area, dev.w_lam * length)

    def test_geometry_matches_characterisation_netlists(self):
        """Generated stacks must carry the same W, L and junction values as measured ones."""
        for kind, n, make in (("nand", 3, nand), ("nor", 3, nor), ("nand", 5, nand), ("nor", 5, nor)):
            text = (CHAR_RUNS / f"e4_{kind}{n}_near_fo1.cir").read_text()
            body = re.search(rf"\.subckt g{kind}{n} .*?\.ends", text, re.S).group(0)
            reference = parse_subckt(body)[1]
            generated = parse_subckt(make(n).spice())[1]

            def key(devs):
                return sorted((d["kind"], round(d["W"], 12), round(d["L"], 12),
                               tuple(sorted([(round(d["AS"], 19), round(d["PS"], 12)),
                                             (round(d["AD"], 19), round(d["PD"], 12))])))
                              for d in devs)
            with self.subTest(gate=f"{kind}{n}"):
                self.assertEqual(key(generated), key(reference))


class TestLvs(unittest.TestCase):
    """The comparison must pass a true match and fail each kind of real layout fault."""

    def setUp(self):
        self.cell = xor_tg()
        self.base = schematic_devices(parse_flat(self.cell.spice(), self.cell.name))
        self.ports = set(self.cell.ports)

    def test_identical_circuit_matches_with_renamed_internal_nets(self):
        mapping = {"m": "a_12_34#", "cb": "a_5_6#"}
        renamed = [dict(d, gate=mapping.get(d["gate"], d["gate"]), a=mapping.get(d["a"], d["a"]),
                        b=mapping.get(d["b"], d["b"])) for d in self.base]
        self.assertTrue(compare(renamed, self.base, self.ports)[0])

    def test_fingers_match_one_wide_device(self):
        d = self.base[0]
        split = self.base[1:] + [dict(d, w=d["w"] / 2), dict(d, w=d["w"] / 2)]
        self.assertTrue(compare(split, self.base, self.ports)[0])

    def test_catches_wrong_width(self):
        bad = [dict(self.base[0], w=self.base[0]["w"] * 2)] + self.base[1:]
        self.assertFalse(compare(bad, self.base, self.ports)[0])

    def test_catches_swapped_gate(self):
        bad = [dict(self.base[2], gate="p" if self.base[2]["gate"] != "p" else "c")] + self.base[:2] + self.base[3:]
        self.assertFalse(compare(bad, self.base, self.ports)[0])

    def test_catches_missing_device(self):
        self.assertFalse(compare(self.base[1:], self.base, self.ports)[0])

    def test_catches_short_between_nets(self):
        bad = [dict(d, gate="p" if d["gate"] == "m" else d["gate"], a="p" if d["a"] == "m" else d["a"],
                    b="p" if d["b"] == "m" else d["b"]) for d in self.base]
        self.assertFalse(compare(bad, self.base, self.ports)[0])


if __name__ == "__main__":
    unittest.main()
