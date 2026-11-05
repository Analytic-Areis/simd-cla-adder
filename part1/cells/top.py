#!/usr/bin/env python3
"""Assemble tiles into a hierarchical MAGIC layout, route with metal 3 and 4, then check it.

Rows of tiles share power rails. Routing runs over the cells on a 9 lambda grid: metal 3
horizontal, metal 4 vertical. Cells use only metal 1 and 2 inside, so these layers are free.
"""
import heapq
import os
from collections import defaultdict
import re
import subprocess
from pathlib import Path

from cellgen import Block, config as cfg, parse_flat
from cellgen.layout import devices_from_block, generate, tcl_for_cell, tcl_labels
from cellgen.lvs import compare, read_extracted, schematic_devices

TECH = cfg.ROOT / "technology" / "SCN6M_DEEP.09.tech27"
GRID = 9
ROW_GAP = 14
STRAP_W = 6


def magic(work, script_name, body, timeout=900):
    work = Path(work)
    work.mkdir(parents=True, exist_ok=True)
    link = work / TECH.name
    if not link.exists():
        os.symlink(os.path.relpath(TECH, work), link)
    (work / f"{script_name}.tcl").write_text(body)
    res = subprocess.run(["magic", "-dnull", "-noconsole", "-T", TECH.name, f"{script_name}.tcl"],
                         cwd=work, capture_output=True, text=True, timeout=timeout)
    (work / f"{script_name}.magic.log").write_text(res.stdout + res.stderr)
    return res.stdout


DRC_TCL = """select top cell
drc euclidean on
drc style drc
drc check
drc catchup
set why [drc listall why]
set total 0
foreach {message boxes} $why {
    incr total [llength $boxes]
    puts "DRC_ERR $message : [lrange $boxes 0 3]"
}
puts "DRC_COUNT $total"
"""
EXTRACT_TCL = """extract do local
extract all
ext2spice lvs
ext2spice cthresh 0
ext2spice rthresh 0
ext2spice format ngspice
ext2spice hierarchy off
ext2spice subcircuit top on
ext2spice
puts DONE
quit -noprompt
"""


def tile_block(name, instances, external):
    used = set()
    for _, cell, pins in instances:
        used |= set(pins.values())
    ports = sorted(used & set(external))
    return Block(name, ports, [], None, instances, f"tile {name}")


def partition(adder, groups, top_ports):
    """groups: list of rows; a row is a list of (tile name, list of instance names)."""
    owner = {}
    by_name = {i[0]: i for i in adder.instances}
    for row in groups:
        for tile, names in row:
            for n in names:
                owner[n] = tile
    usage = {}
    for inst, cell, pins in adder.instances:
        for net in pins.values():
            usage.setdefault(net, set()).add(owner[inst])
    external = {n for n, t in usage.items() if len(t) > 1 or n in top_ports}
    return [[tile_block(tile, [by_name[n] for n in names], external) for tile, names in row] for row in groups]


class Router:
    def __init__(self, width, height):
        self.nx, self.ny = width // GRID + 2, height // GRID + 2
        self.owner = {}   # (i, j, layer): net
        self.rects = []
        self.m3 = defaultdict(list)
        self.current = None

    def node_xy(self, i, j):
        return i * GRID, j * GRID

    def reserve(self, x, y, net, radius=11):
        """Keep other nets off the metal 3 around a pin, and any via off the landing itself."""
        for i in range(max(0, (x - 18) // GRID), min(self.nx, (x + 22) // GRID + 1)):
            for j in range(max(0, (y - 18) // GRID), min(self.ny, (y + 22) // GRID + 1)):
                gx, gy = self.node_xy(i, j)
                if abs(gx - x - 0.5) < radius and abs(gy - y - 2.5) < radius:
                    self.owner.setdefault((i, j, 3), net)
                if abs(gx - x - 0.5) < 7 and abs(gy - y - 2.5) < 7:
                    self.owner[(i, j, 4)] = "#landing"

    def clear_of_others(self, box, net, margin=4):
        for other, boxes in self.m3.items():
            if other == net:
                continue
            for q in boxes:
                if max(box[0], q[0]) - min(box[2], q[2]) < margin and max(box[1], q[1]) - min(box[3], q[3]) < margin:
                    return False
        return True

    def attach(self, x, y, net):
        """Metal 3 from the pin landing to the nearest own grid node, clear of every other net."""
        options = []
        for i in range(max(0, (x - 54) // GRID), min(self.nx, (x + 63) // GRID + 1)):
            for j in range(max(0, (y - 54) // GRID), min(self.ny, (y + 63) // GRID + 1)):
                if self.owner.get((i, j, 3), net) != net:
                    continue
                gx, gy = self.node_xy(i, j)
                options.append((abs(gx - x) + abs(gy - y), i, j, gx, gy))
        for _, i, j, gx, gy in sorted(options):
            # a solid box: thin L-shaped stubs leave notches that break the 4 lambda spacing
            box = (min(x - 2, gx - 1), min(y, gy - 1), max(x + 3, gx + 2), max(y + 5, gy + 2))
            if self.clear_of_others(box, net):
                self.owner[(i, j, 3)] = net
                self.rects.append(("m3", *box))
                self.m3[net].append(box)
                self.block_near(box, net)
                return i, j
        raise RuntimeError(f"no clear node near pin of {net} at {x},{y}")

    def block_near(self, box, net):
        """No other net's grid wire may pass within the spacing rule of this shape."""
        for i in range(max(0, (box[0] - 18) // GRID), min(self.nx, (box[2] + 18) // GRID + 1)):
            for j in range(max(0, (box[1] - 18) // GRID), min(self.ny, (box[3] + 18) // GRID + 1)):
                gx, gy = self.node_xy(i, j)
                # a horizontal wire at node j occupies gy-1..gy+2; along x it reaches neighbouring nodes
                near_y = max(box[1], gy - 1) - min(box[3], gy + 2) < 4
                near_x = max(box[0], gx - GRID) - min(box[2], gx + GRID) < 4
                if near_x and near_y:
                    self.owner.setdefault((i, j, 3), net)

    def fill_notches(self):
        """Close same-net metal 3 gaps narrower than the spacing rule with a small patch."""
        for net, boxes in self.m3.items():
            for _ in range(6):
                added = []
                for a in range(len(boxes)):
                    for b in range(a + 1, len(boxes)):
                        p, q = boxes[a], boxes[b]
                        dx = max(p[0], q[0]) - min(p[2], q[2])
                        dy = max(p[1], q[1]) - min(p[3], q[3])
                        if not (dx < 4 and dy < 4) or (dx <= 0 and dy <= 0):
                            continue
                        # patch only the gap between the facing edges
                        x0, x1 = (min(p[2], q[2]), max(p[0], q[0])) if dx > 0 else (max(p[0], q[0]), min(p[2], q[2]))
                        y0, y1 = (min(p[3], q[3]), max(p[1], q[1])) if dy > 0 else (max(p[1], q[1]), min(p[3], q[3]))
                        if 0 < x1 - x0 < 3:   # metal 3 minimum width
                            x1 = x0 + 3
                        if 0 < y1 - y0 < 3:
                            y1 = y0 + 3
                        patch = (x0, y0, x1, y1)
                        if patch[2] > patch[0] and patch[3] > patch[1] and self.clear_of_others(patch, net):
                            added.append(patch)
                if not added:
                    break
                for patch in added:
                    if patch not in boxes:
                        boxes.append(patch)
                        self.rects.append(("m3", *patch))

    def conflicts(self):
        """Different-net metal 3 pairs closer than 4 lambda. An empty list is the goal."""
        items = [(net, box) for net, boxes in self.m3.items() for box in boxes]
        found = []
        for a in range(len(items)):
            for b in range(a + 1, len(items)):
                if items[a][0] == items[b][0]:
                    continue
                p, q = items[a][1], items[b][1]
                dx = max(p[0], q[0]) - min(p[2], q[2])
                dy = max(p[1], q[1]) - min(p[3], q[3])
                if dx < 4 and dy < 4:
                    found.append((items[a], items[b]))
        return found

    def route(self, net, nodes):
        """Join nodes on the grid with Dijkstra, growing a tree from the first."""
        self.current = net
        tree = {(nodes[0][0], nodes[0][1], 3)}
        for target in nodes[1:]:
            goal = (target[0], target[1], 3)
            if goal in tree:
                continue
            dist = {n: 0 for n in tree}
            prev = {}
            heap = [(0, n) for n in tree]
            heapq.heapify(heap)
            found = None
            while heap:
                d, node = heapq.heappop(heap)
                if d > dist.get(node, 1e18):
                    continue
                if node == goal:
                    found = node
                    break
                i, j, layer = node
                steps = []
                if layer == 3:
                    steps += [((i + 1, j, 3), 1), ((i - 1, j, 3), 1), ((i, j, 4), 4)]
                else:
                    steps += [((i, j + 1, 4), 1), ((i, j - 1, 4), 1), ((i, j, 3), 4)]
                for nxt, cost in steps:
                    a, b, lay = nxt
                    if not (0 <= a < self.nx and 0 <= b < self.ny):
                        continue
                    if self.owner.get(nxt, net) != net:
                        continue
                    gx, gy = self.node_xy(a, b)
                    if lay != layer and not self.clear_of_others((gx - 2, gy - 2, gx + 3, gy + 3), net):
                        continue
                    if lay == 3 and layer == 3 and not self.clear_of_others((gx - 1, gy - 1, gx + 2, gy + 2), net):
                        continue
                    nd = d + cost
                    if nd < dist.get(nxt, 1e18):
                        dist[nxt] = nd
                        prev[nxt] = node
                        heapq.heappush(heap, (nd, nxt))
            if found is None:
                raise RuntimeError(f"cannot route {net}")
            node = found
            while node not in tree:
                self.owner[node] = net
                tree.add(node)
                p = prev[node]
                self._paint(p, node)
                node = p
        return tree

    def _paint(self, a, b):
        (i, j, la), (k, m, lb) = a, b
        x0, y0 = self.node_xy(i, j)
        x1, y1 = self.node_xy(k, m)
        if la != lb:
            self.rects.append(("m4c", x0 - 2, y0 - 2, x0 + 3, y0 + 3))
            self.m3[self.current].append((x0 - 2, y0 - 2, x0 + 3, y0 + 3))
        elif la == 3:
            box = (min(x0, x1) - 1, y0 - 1, max(x0, x1) + 2, y0 + 2)
            self.rects.append(("m3", *box))
            self.m3[self.current].append(box)
        else:
            self.rects.append(("m4", x0 - 1, min(y0, y1) - 1, x0 + 2, max(y0, y1) + 2))


def assemble(name, rows, schematic, top_ports, work, align=None, extra_pins=None):
    """rows: list of rows of tile Blocks. Returns a result dict; layout files stay in work.

    align maps a row index to a reference row: tile k starts at the x of that row's tile k,
    giving a common bit pitch. Rails and well are painted across any gaps this leaves.
    extra_pins maps a net to x positions of extra metal 3 pads above the top row, routed like
    any other pin of the net. A parent cell can land a via on such a pad without touching
    anything else in the cell. The result lists their positions under "pads".
    """
    align = align or {}
    row_x = {}
    row_extent = {}
    work = Path(work)
    work.mkdir(parents=True, exist_ok=True)
    placements, y = [], 0
    max_w = 0
    top_pins = {}
    for r_index, row in enumerate(rows):
        layouts = []
        for tile in row:
            devs = devices_from_block(tile)
            layouts.append((tile, generate(tile.name, devs, tile.inputs), devs))
        hn = max(l.hn for _, l, _ in layouts)
        hp = max(l.hp for _, l, _ in layouts)
        tracks = max(l.n_tracks for _, l, _ in layouts)
        regenerated = [(t, generate(t.name, d, t.inputs, hn=hn, hp=hp, min_tracks=tracks)) for t, _, d in layouts]
        x = 0
        row_x[r_index] = []
        for k, (tile, layout) in enumerate(regenerated):
            if r_index in align:
                reference = row_x.get(align[r_index], [])
                if k < len(reference):
                    x = max(x, reference[k])
            row_x[r_index].append(x)
            body = f"cellname rename (UNNAMED) {tile.name}\n{tcl_for_cell(layout)}\n{tcl_labels(layout)}\n" + DRC_TCL + \
                f"save {tile.name}\nquit -noprompt\n"
            out = magic(work, tile.name, body)
            count = re.search(r"DRC_COUNT (\d+)", out)
            if count is None or int(count.group(1)):
                raise RuntimeError(f"tile {tile.name} DRC: {[l for l in out.splitlines() if 'DRC_' in l][:4]}")
            placements.append(dict(tile=tile, layout=layout, x=x, y=y, row=r_index))
            x += layout.width
        row_extent[r_index] = x
        max_w = max(max_w, x)
        y += regenerated[0][1].height + ROW_GAP
    height = y
    # pin locations
    pins = {}
    for p in placements:
        for net, (px, py, _) in p["layout"].pin_stack.items():
            pins.setdefault(net, []).append((px + p["x"], py + p["y"]))
    pads = {net: [(x, height + 12) for x in xs] for net, xs in (extra_pins or {}).items()}
    for net, locs in pads.items():
        pins.setdefault(net, []).extend(locs)
    order = sorted(pins, key=lambda n: (max(q[0] for q in pins[n]) - min(q[0] for q in pins[n]))
                   + (max(q[1] for q in pins[n]) - min(q[1] for q in pins[n])))
    # rip up and retry: a net that cannot be routed goes first on the next attempt
    router = None
    for attempt in range(60):
        trial = Router(max_w + 40, height + 40)
        for net, locs in pins.items():
            for (px, py) in locs:
                trial.reserve(px, py, net, radius=11 if attempt < 25 else 8)
                trial.m3[net].append((px - 2, py, px + 3, py + 5))   # the landing inside the cell
        nodes = {}
        try:
            for net in order:
                nodes[net] = [trial.attach(px, py, net) for px, py in pins[net]]
            for net in order:
                if len(nodes[net]) > 1:
                    failing = net
                    trial.route(net, nodes[net])
            router = trial
            break
        except RuntimeError as exc:
            print("  routing retry", attempt, exc, flush=True)
            failed = re.search(r"(?:route|pin of) (\S+)", str(exc)).group(1)
            order = [failed] + [n for n in order if n != failed]
    if router is None:
        raise RuntimeError(f"{name}: routing failed after retries, last net {failed}")
    for net, locs in pads.items():
        for px, py in locs:   # the landing a tile would otherwise provide
            router.rects.append(("m3", px - 2, py, px + 3, py + 5))
    router.fill_notches()
    for (n1, b1), (n2, b2) in router.conflicts():
        print("M3 conflict", n1, b1, n2, b2, flush=True)
    # top ports: label on the metal 3 stub of one pin
    label_tcl = []
    idx = 1
    for net in sorted(top_ports):
        if net not in pins:
            raise RuntimeError(f"port {net} has no pin")
        px, py = pins[net][0]
        label_tcl.append(f"box {px} {py} {px + 1} {py + 5}; label {net} center m3; port make {idx}")
        idx += 1

    # power straps on metal 2 at the left, rails extended to them with vias
    vdd_x, gnd_x = -28, -16
    lines = [f"cellname rename (UNNAMED) {name}"]
    for p in placements:
        lines.append(f"box {p['x']} {p['y']} {p['x']} {p['y']}; getcell {p['tile'].name}")
    ytop = max(p["y"] + p["layout"].height for p in placements)
    power = [("m2", vdd_x, -6, vdd_x + STRAP_W, ytop + 6), ("m2", gnd_x, -6, gnd_x + STRAP_W, ytop + 6)]
    rows_seen = {}
    for p in placements:
        rows_seen.setdefault(p["row"], p)
    for p in rows_seen.values():
        layout, yy = p["layout"], p["y"]
        extent = row_extent[p["row"]]
        power.append(("nwell", 0, yy + layout.y_vdd[0] - layout.hp - 6, extent, yy + layout.y_vdd[1] + 3))
        power.append(("m1", 0, yy + layout.y_vdd[0], extent, yy + layout.y_vdd[1]))
        power.append(("m1", 0, yy + layout.y_gnd[0], extent, yy + layout.y_gnd[1]))
        for (yr0, yr1), strap in ((layout.y_vdd, vdd_x), (layout.y_gnd, gnd_x)):
            power.append(("m1", strap, yy + yr0, 0, yy + yr1))
            power.append(("m2c", strap, yy + yr0, strap + STRAP_W, yy + yr1))
    for layer, x0, y0, x1, y1 in power + router.rects:
        lines.append(f"box {x0} {y0} {x1} {y1}; paint {layer}")
    lines += label_tcl
    lines.append(f"box {vdd_x} {ytop} {vdd_x + STRAP_W} {ytop + 6}; label vdd center m2; port make {idx}")
    lines.append(f"box {gnd_x} {ytop} {gnd_x + STRAP_W} {ytop + 6}; label gnd center m2; port make {idx + 1}")
    lines.append("save " + name)
    body = "\n".join(lines) + "\n" + DRC_TCL + "save " + name + "\n" + EXTRACT_TCL
    out = magic(work, name, body)
    count = re.search(r"DRC_COUNT (\d+)", out)
    errors = [l for l in out.splitlines() if l.startswith("DRC_ERR")]
    spice_path = work / f"{name}.spice"
    extracted = read_extracted(spice_path.read_text()) if spice_path.exists() else []
    flat = parse_flat(schematic.spice(), schematic.name)
    matched, message = compare(extracted, schematic_devices(flat), set(top_ports) | {"vdd", "gnd"})
    total_w = max_w + 34
    total_h = max([ytop] + [py + 5 for locs in pads.values() for _, py in locs]) + 12
    return dict(name=name, drc=int(count.group(1)) if count else -1, drc_first=errors[:6], lvs=matched, lvs_message=message,
                width_lambda=total_w, height_lambda=total_h, area_um2=round(total_w * total_h * 0.09 ** 2, 1),
                placements=[(p["tile"].name, p["x"], p["y"], p["layout"].width, p["layout"].height) for p in placements],
                pads=pads)


PG_GROUP = [(f"pg{i}", [f"nand{i}", f"nor{i}", f"aoi{i}", f"oai{i}"]) for i in range(4)]
SUM_GROUP = [(f"sum{i}", [f"x{i}"]) for i in range(4)]


# carry gates ordered by the bit they serve, so that wires to the bit columns stay short
CARRY_ORDER = ["invc0", "c1", "g10", "t10", "ig10", "it10", "c2", "ig2", "it2", "g20", "t20", "c3",
               "g32", "t32", "g30", "t30", "c4g", "c4m", "invc4"]


def adder_rows(adder):
    pg_names = {n for _, names in PG_GROUP for n in names}
    sum_names = {n for _, names in SUM_GROUP for n in names}
    carry_names = [i[0] for i in adder.instances if i[0] not in pg_names | sum_names]
    carry_names.sort(key=lambda n: CARRY_ORDER.index(n) if n in CARRY_ORDER else 99)
    return [PG_GROUP, [("carry", carry_names)], SUM_GROUP]


if __name__ == "__main__":
    from candidates import INPUTS, OUTPUTS, candidate_c4
    adder = candidate_c4(sum_style="tg", name="cla_c4_tg_trial")
    ports = INPUTS + OUTPUTS
    rows = partition(adder, adder_rows(adder), ports)
    result = assemble("cla_trial", rows, adder, ports, cfg.PART1 / "layout" / "integrated" / "trial", align={2: 0})
    print({k: v for k, v in result.items() if k != "placements"})
    print(result["placements"])
