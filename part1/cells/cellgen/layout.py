"""Row-based layout generator: devices in, MAGIC Tcl out.

One cell is a PMOS row and an NMOS row with a routing channel between them. Channel tracks
are metal 1 horizontals; source and drain connections reach them on metal 2 verticals; gates
reach them on poly. Metal 3 and 4 stay free for routing between blocks.

Geometry is in lambda, from the DRC section of SCN6M_DEEP.09.tech27. Every generated cell is
checked with MAGIC DRC, so a rule misread here shows up as a reported error, not a bad layout.
"""
from dataclasses import dataclass, field
from itertools import permutations

GATE_PITCH_SHARED = 7     # uncontacted shared diffusion; poly must clear a neighbouring poly contact by 4
GATE_PITCH_CONTACT = 9    # two gates with a contact between them; 5 lambda vias need a 9 lambda column pitch
ISLAND_BREAK = 18         # gates on separate diffusion islands
CONTACT = 4
GATE_TO_CONTACT = 1
POLY_OVERHANG = 3
RAIL_H = 6
TRACK_PITCH = 9   # metal 2 vias on neighbouring tracks need 4 lambda spacing
TRACK_W = 5
VIA = 5
WFOLD = {"n": 60, "p": 80}   # wider devices become parallel fingers
EDGE = 8


@dataclass
class Dev:
    name: str
    kind: str
    gate: str
    a: str          # one diffusion terminal
    b: str          # the other
    w: int
    group: int = 0


@dataclass
class Rect:
    layer: str
    x0: int
    y0: int
    x1: int
    y1: int


@dataclass
class CellLayout:
    name: str
    rects: list = field(default_factory=list)
    width: int = 0
    height: int = 0
    pins: dict = field(default_factory=dict)      # net: (track y, x0, x1)
    tracks: dict = field(default_factory=dict)
    m2_columns: list = field(default_factory=list)  # (x, y0, y1) of metal 2 verticals
    y_gnd: tuple = (0, RAIL_H)
    y_vdd: tuple = (0, 0)
    hn: int = 0
    hp: int = 0
    n_tracks: int = 0
    pin_stack: dict = field(default_factory=dict)   # net: (x, track y, unused)


def fold(devices):
    """Split wide devices into parallel fingers. Terminal order alternates for sharing."""
    out = []
    for d in devices:
        n = max(1, -(-d.w // WFOLD[d.kind]))
        each = max(3, round(d.w / n))
        for k in range(n):
            a, b = (d.a, d.b) if k % 2 == 0 else (d.b, d.a)
            out.append(Dev(f"{d.name}_f{k}", d.kind, d.gate, a, b, each, d.group))
    return out


def _trails(devs, shared_ok, limit=4000):
    """Enumerate orderings with terminal orientation, preferring shared diffusion.

    Returns a list of trails. Each trail is a list of (device, left net, right net).
    Depth-first search; continuing through a shared net always comes first, so the first
    results have the fewest diffusion breaks.
    """
    n = len(devs)
    results = []
    counter = [0]

    def walk(trail, used, end, breaks):
        if counter[0] >= limit:
            return
        if len(trail) == n:
            results.append((breaks, list(trail)))
            counter[0] += 1
            return
        nxt = []
        for i, d in enumerate(devs):
            if used >> i & 1:
                continue
            if end is not None and d.a == end:
                nxt.append((0, i, d.a, d.b))
            elif end is not None and d.b == end:
                nxt.append((0, i, d.b, d.a))
            else:
                nxt.append((1, i, d.a, d.b))
                if d.a != d.b:
                    nxt.append((1, i, d.b, d.a))
        nxt.sort(key=lambda m: m[0])
        best_join = nxt[0][0] if nxt else 1
        for join, i, left, right in nxt:
            if join > best_join:
                break
            trail.append((devs[i], left, right))
            walk(trail, used | 1 << i, right, breaks + join)
            trail.pop()

    walk([], 0, None, 0)
    results.sort(key=lambda r: r[0])
    return results


def _align_cost(pt, nt):
    """Fewest diffusion breaks first, then the most columns where P and N share a gate net."""
    match = sum(1 for (p, _, _), (m, _, _) in zip(pt, nt) if p.gate == m.gate)
    return -match


def order_group(p_devs, n_devs, shared_ok):
    """Choose P and N orders for one instance. Returns candidates, best first."""
    pts = _trails(p_devs, shared_ok, 1500) or [(0, [])]
    nts = _trails(n_devs, shared_ok, 1500) or [(0, [])]
    pts = pts[:120]
    nts = nts[:120]
    ranked = []
    for bp, pt in pts:
        for bn, nt in nts:
            ranked.append((bp + bn, _align_cost(pt, nt), len(ranked), pt, nt))
    ranked.sort(key=lambda r: r[:3])
    return ranked[:60]


def _place_row(slots, row_key):
    return [s[row_key] for s in slots]


def assign_tracks(pins, poly_pairs, m2_pairs):
    """Constrained left-edge channel assignment.

    pins: net -> (xmin, xmax). Track 0 is lowest. pairs (upper net, lower net) require the
    upper net on a higher track. Returns ({net: track}, blocked nets). Blocked is non-empty when
    constraints form a cycle.
    """
    above = {n: set() for n in pins}   # above[n]: nets that must be below n
    for u, v in list(poly_pairs) + list(m2_pairs):
        if u != v and u in pins and v in pins:
            above[u].add(v)
    placed, tracks = {}, []
    remaining = set(pins)
    level = 0
    while remaining:
        ready = [n for n in remaining if above[n] <= set(placed)]
        if not ready:
            return placed, set(remaining)
        ready.sort(key=lambda n: pins[n][0])
        last_end = None
        chosen = []
        for n in ready:
            lo, hi = pins[n]
            if last_end is None or lo >= last_end + TRACK_W + 3:
                chosen.append(n)
                last_end = hi
        # a net constrained to sit below another may share this level only if nothing here requires it above
        for n in chosen:
            placed[n] = level
            remaining.discard(n)
        level += 1
    return placed, set()


def generate(name, devices, ports, hn=None, hp=None, min_tracks=0, reserve=None):
    """devices: list of Dev. Returns a CellLayout. Raises if no ordering routes."""
    reserve = set(reserve or ())
    devs = fold(devices)
    groups = sorted({d.group for d in devs})
    touch = {}
    for d in devs:
        for net in (d.a, d.b):
            touch.setdefault(net, []).append(d.kind)
    gate_nets = {d.gate for d in devs}

    def shared_ok(net, kind):
        return (net not in ports and net not in ("vdd", "gnd") and net not in gate_nets
                and len(touch[net]) == 2 and touch[net] == [kind, kind])

    choices = []
    for g in groups:
        p_devs = [d for d in devs if d.group == g and d.kind == "p"]
        n_devs = [d for d in devs if d.group == g and d.kind == "n"]
        choices.append(order_group(p_devs, n_devs, shared_ok))

    # try the best orderings first, moving to alternatives only if routing has a cycle
    index = [0] * len(choices)
    for attempt in range(400):
        layout = _try_layout(name, choices, index, ports, shared_ok, hn, hp, min_tracks, reserve)
        if isinstance(layout, set):   # gate-only ports with no free spot: give each its own column
            reserve |= layout
            layout = _try_layout(name, choices, index, ports, shared_ok, hn, hp, min_tracks, reserve)
        if layout is not None and not isinstance(layout, set):
            return layout
        g = attempt % len(choices)
        index[g] = min(index[g] + 1, len(choices[g]) - 1)
    raise RuntimeError(f"{name}: no ordering could be routed")


def _try_layout(name, choices, index, ports, shared_ok, hn_req, hp_req, min_tracks, reserve=()):
    # build columns: each slot holds one P and/or one N device on the same gate column
    slots = []
    for g, ranked in enumerate(choices):
        _, _, _, pt, nt = ranked[index[g]]
        for k in range(max(len(pt), len(nt))):
            slots.append(dict(group=g, p=pt[k] if k < len(pt) else None, n=nt[k] if k < len(nt) else None))

    def gap(prev_entry, next_entry, kind):
        """Required gate pitch between neighbouring devices in a row, and the mid-node style."""
        if prev_entry is None or next_entry is None:
            return ISLAND_BREAK, "break"
        pdev, _, pr = prev_entry
        ndev, nl, _ = next_entry
        if pr != nl:
            return ISLAND_BREAK, "break"
        if shared_ok(pr, kind) and pdev.w == ndev.w:
            return GATE_PITCH_SHARED, "shared"
        return GATE_PITCH_CONTACT, "contact"

    x_gate = []
    x = EDGE + 7
    styles = {"p": [], "n": []}
    for i, slot in enumerate(slots):
        if i:
            prev = slots[i - 1]
            pp, sp = gap(prev["p"], slot["p"], "p")
            pn, sn = gap(prev["n"], slot["n"], "n")
            step = max(pp, pn)
            if prev["group"] != slot["group"]:
                step = max(step, ISLAND_BREAK)
                sp, sn = "break", "break"
            x += step
            styles["p"].append(sp)
            styles["n"].append(sn)
        x_gate.append(x)
    width = x + 1 + GATE_TO_CONTACT + CONTACT + EDGE

    hn = max([s["n"][0].w for s in slots if s["n"]] + [hn_req or 0, 4])
    hp = max([s["p"][0].w for s in slots if s["p"]] + [hp_req or 0, 4])

    # gather channel pins
    contacts = {"p": [], "n": []}   # (x, net, height)
    for kind in ("p", "n"):
        entries = [s[kind] for s in slots]
        for i in range(len(slots)):
            if entries[i] is None:
                continue
            dev, left, right = entries[i]
            prev_ok = i > 0 and entries[i - 1] is not None and styles[kind][i - 1] != "break"
            if not prev_ok:
                contacts[kind].append((x_gate[i] - 5, left, max(dev.w, 4)))
            if i + 1 < len(slots) and entries[i + 1] is not None and styles[kind][i] != "break":
                if styles[kind][i] == "contact":
                    contacts[kind].append(((x_gate[i] + x_gate[i + 1]) // 2, right, max(dev.w, entries[i + 1][0].w, 4)))
            else:
                contacts[kind].append((x_gate[i] + 1 + GATE_TO_CONTACT + CONTACT // 2, right, max(dev.w, 4)))

    base_pins = {"top": {}, "bot": {}}   # side: net: list of x
    for kind, side in (("p", "top"), ("n", "bot")):
        for xc, net, _ in contacts[kind]:
            if net not in ("vdd", "gnd"):
                base_pins[side].setdefault(net, []).append(("diff", xc))
    poly_pairs_raw = set()
    for i, s in enumerate(slots):
        pg = s["p"][0].gate if s["p"] else None
        ng = s["n"][0].gate if s["n"] else None
        if pg and pg == ng:
            base_pins["top"].setdefault(pg, []).append(("through", x_gate[i]))
            continue
        if pg:
            base_pins["top"].setdefault(pg, []).append(("poly", x_gate[i]))
        if ng:
            base_pins["bot"].setdefault(ng, []).append(("poly", x_gate[i]))
        if pg and ng:
            poly_pairs_raw.add((pg, ng))

    # a net in a constraint cycle is split into a top part and a bottom part, joined by a
    # metal 2 connector in its own column to the right of the devices
    splits = []
    x_right = width - EDGE
    while True:
        def key(net, side):
            if net in splits:
                return f"{net}@{side}"
            return net

        pins_x = {}
        for side in ("top", "bot"):
            for net, entries in base_pins[side].items():
                pins_x.setdefault(key(net, side), []).extend(e[1] for e in entries)
        connector_x = {net: x_right + 7 + 9 * k for k, net in enumerate(splits)}
        for net, xc in connector_x.items():
            pins_x.setdefault(f"{net}@top", []).append(xc)
            pins_x.setdefault(f"{net}@bot", []).append(xc)
        reserved_x = {net: x_right + 7 + 9 * (len(splits) + k) for k, net in enumerate(sorted(reserve))}
        for net, xc in reserved_x.items():
            pins_x.setdefault(key(net, "top"), []).append(xc)
        spans = {k: (min(v) - 2, max(v) + 3) for k, v in pins_x.items()}
        poly_pairs = {(key(u, "top"), key(v, "bot")) for u, v in poly_pairs_raw}
        m2_pairs = set()
        for nt, et in base_pins["top"].items():
            for nb, eb in base_pins["bot"].items():
                if nt == nb and nt not in splits:
                    continue
                for kt, xt in et:
                    for kb, xb in eb:
                        if kt == "diff" and kb == "diff" and abs(xt - xb) < 9:
                            m2_pairs.add((key(nt, "top"), key(nb, "bot")))
        tracks, blocked = assign_tracks(spans, poly_pairs, m2_pairs)
        if not blocked:
            break
        options = [n for n in base_pins["top"] if n in base_pins["bot"] and n not in splits
                   and (key(n, "top") in blocked or key(n, "bot") in blocked)]
        if not options:
            return None
        options.sort(key=lambda n: -(spans[key(n, "top")][1] - spans[key(n, "top")][0]))
        splits.append(options[0])
    if splits or reserved_x:
        width = max(width, x_right + 7 + 9 * (len(splits) + len(reserved_x) - 1) + 3 + EDGE)

    n_tracks = max(max(tracks.values(), default=-1) + 1, min_tracks)
    y_nb = RAIL_H + 4
    y_nt = y_nb + hn
    def track_y(t):
        return y_nt + 9 + TRACK_PITCH * t

    channel_top = track_y(n_tracks - 1) + TRACK_W if n_tracks else y_nt + 9
    y_pb = max(channel_top + 9, y_nt + 12)
    y_pt = y_pb + hp
    y_v0 = y_pt + 4
    y_v1 = y_v0 + RAIL_H

    out = CellLayout(name, width=width, y_gnd=(0, RAIL_H), y_vdd=(y_v0, y_v1), hn=hn, hp=hp, n_tracks=n_tracks)
    r = out.rects

    def add_rect(layer, x0, y0, x1, y1):
        r.append(Rect(layer, x0, y0, x1, y1))

    # n well and rails
    add_rect("nwell", 0, y_pb - 6, width, y_v1 + 3)
    add_rect("m1", 0, 0, width, RAIL_H)
    add_rect("m1", 0, y_v0, width, y_v1)
    # body contacts every 24 lambda in each rail, as far from diffusion as the rail allows
    for xb in range(4, max(width - 8, 5), 24):
        add_rect("psc", xb, 1, xb + 4, 5)
        add_rect("nsc", xb, y_v0 + 1, xb + 4, y_v0 + 5)

    # diffusion and gates
    for kind, top_edge in (("n", y_nt), ("p", y_pb)):
        layer, contact = ("ndiff", "ndc") if kind == "n" else ("pdiff", "pdc")
        for i, s in enumerate(slots):
            if not s[kind]:
                continue
            dev = s[kind][0]
            y0, y1 = (top_edge - dev.w, top_edge) if kind == "n" else (top_edge, top_edge + dev.w)
            left_prev = i > 0 and s[kind] and slots[i - 1][kind] is not None and styles[kind][i - 1] != "break"
            right_next = i + 1 < len(slots) and slots[i + 1][kind] is not None and styles[kind][i] != "break"
            # each side extends at least 4 lambda past the gate, as the overhang rule needs
            x_l = (x_gate[i - 1] + x_gate[i]) // 2 if left_prev else x_gate[i] - 7
            x_r = (x_gate[i] + x_gate[i + 1] + 1) // 2 if right_next else x_gate[i] + 1 + GATE_TO_CONTACT + CONTACT
            add_rect(layer, x_l, y0, x_r, y1)
        for xc, net, w in contacts[kind]:
            y0, y1 = (top_edge - w, top_edge) if kind == "n" else (top_edge, top_edge + w)
            add_rect(contact, xc - 2, y0, xc + 2, y1)
            add_rect("m1", xc - 2, y0, xc + 2, y1)
            if net == "gnd":
                add_rect("m1", xc - 2, 0, xc + 2, y1)
            elif net == "vdd":
                add_rect("m1", xc - 2, y0, xc + 2, y_v1)
            else:
                t_y = track_y(tracks[key(net, "bot" if kind == "n" else "top")])
                if kind == "n":
                    add_rect("m1", xc - 2, y0, xc + 2, y1 + 6)
                    add_rect("m2c", xc - 2, y1 + 1, xc + 3, y1 + 6)
                    add_rect("m2", xc - 2, y1 + 1, xc + 3, t_y + TRACK_W)
                    out.m2_columns.append((xc, y1 + 1, t_y + TRACK_W))
                else:
                    add_rect("m1", xc - 2, y0 - 6, xc + 2, y1)
                    add_rect("m2c", xc - 2, y0 - 6, xc + 3, y0 - 1)
                    add_rect("m2", xc - 2, t_y, xc + 3, y0 - 1)
                    out.m2_columns.append((xc, t_y, y0 - 1))
                add_rect("m2c", xc - 2, t_y, xc + 3, t_y + TRACK_W)

    # gate poly and its connection to the channel
    for i, s in enumerate(slots):
        xg = x_gate[i]
        pg = s["p"][0] if s["p"] else None
        ng = s["n"][0] if s["n"] else None
        if pg and ng and pg.gate == ng.gate:
            add_rect("poly", xg - 1, y_nt - ng.w - POLY_OVERHANG, xg + 1, y_pb + pg.w + POLY_OVERHANG)
            t_y = track_y(tracks[key(pg.gate, "top")])
            add_rect("pc", xg - 2, t_y, xg + 2, t_y + TRACK_W)
        else:
            if ng:
                t_y = track_y(tracks[key(ng.gate, "bot")])
                add_rect("poly", xg - 1, y_nt - ng.w - POLY_OVERHANG, xg + 1, t_y + TRACK_W)
                add_rect("pc", xg - 2, t_y, xg + 2, t_y + TRACK_W)
            if pg:
                t_y = track_y(tracks[key(pg.gate, "top")])
                add_rect("poly", xg - 1, t_y, xg + 1, y_pb + pg.w + POLY_OVERHANG)
                add_rect("pc", xg - 2, t_y, xg + 2, t_y + TRACK_W)

    # poly contacts of one net on one track, closer than the spacing rule, become one contact
    contacts_pc = sorted((q for q in r if q.layer == "pc"), key=lambda q: (q.y0, q.x0))
    for q0, q1 in zip(contacts_pc, contacts_pc[1:]):
        if q0.y0 == q1.y0 and 0 < q1.x0 - q0.x1 < 4:
            add_rect("pc", q0.x1, q0.y0, q1.x0, q0.y1)
    # channel tracks
    for part, t in tracks.items():
        t_y = track_y(t)
        x0, x1 = spans[part]
        add_rect("m1", x0, t_y, x1, t_y + TRACK_W)
        net = part.split("@")[0]
        out.tracks[part] = (t_y, x0, x1)
        if net in ports and (net not in out.pins or part.endswith("@top")):
            out.pins[net] = (t_y, x0, x1)
    # same-net metal 2 columns closer than the spacing rule are filled at their shared track
    for part, t in tracks.items():
        t_y = track_y(t)
        net = part.split("@")[0]
        columns = sorted(xc for kind in ("p", "n") for xc, n, _ in contacts[kind]
                         if n == net and key(n, "bot" if kind == "n" else "top") == part)
        for x_a, x_b in zip(columns, columns[1:]):
            if 0 < x_b - x_a < 9:
                add_rect("m2", x_a - 2, t_y, x_b + 3, t_y + TRACK_W)
    # connectors joining the two parts of a split net
    for net, xc in connector_x.items():
        y_a = track_y(tracks[f"{net}@top"])
        y_b = track_y(tracks[f"{net}@bot"])
        low, high = min(y_a, y_b), max(y_a, y_b)
        add_rect("m2", xc - 2, low, xc + 3, high + TRACK_W)
        add_rect("m2c", xc - 2, y_a, xc + 3, y_a + TRACK_W)
        add_rect("m2c", xc - 2, y_b, xc + 3, y_b + TRACK_W)
        out.m2_columns.append((xc, low, high + TRACK_W))
    out.height = y_v1 + 3
    # pin stack location for routing between blocks: an existing via, or a free track spot
    all_m2 = [q for q in r if q.layer in ("m2", "m2c")]
    missing = set()
    landings = []

    def clear_landing(xc, t_y):
        return all(abs(xc - qx) >= 9 or abs(t_y - qy) >= 9 for qx, qy in landings)

    def not_touching_via(xc, t_y):
        """A stacked via may not touch a neighbouring metal 2 via, even of its own net."""
        box = (xc - 2, t_y, xc + 3, t_y + TRACK_W)
        for q in r:
            if q.layer == "m2c" and (q.x0, q.y0, q.x1, q.y1) != box:
                if max(box[0], q.x0) - min(box[2], q.x1) < 1 and max(box[1], q.y0) - min(box[3], q.y1) < 1:
                    return False
        return True

    for net in sorted(ports):
        if net in ("vdd", "gnd") or net not in base_pins["top"] and net not in base_pins["bot"]:
            continue
        options = []
        for kind, side in (("p", "top"), ("n", "bot")):
            for xc, n, _ in contacts[kind]:
                if n == net:
                    options.append((xc, track_y(tracks[key(net, side)])))
        choice = next((o for o in options if clear_landing(*o) and not_touching_via(*o)), None)
        if choice is None and net in reserve:
            part = key(net, "top")
            t_y = out.tracks[part][0]
            xc = reserved_x[net]
            add_rect("m2c", xc - 2, t_y, xc + 3, t_y + TRACK_W)
            add_rect("m2", xc - 2, t_y, xc + 3, t_y + TRACK_W)
            all_m2.append(Rect("m2", xc - 2, t_y, xc + 3, t_y + TRACK_W))
            choice = (xc, t_y)
        if choice is None:
            part = key(net, "top") if net in base_pins["top"] else key(net, "bot")
            t_y, x0, x1 = out.tracks[part]
            for xc in range(x0 + 2, x1 - 2):
                box_ok = all(q.x1 + 4 <= xc - 2 or q.x0 - 4 >= xc + 3 or q.y1 + 4 <= t_y or q.y0 - 4 >= t_y + TRACK_W
                             for q in all_m2)
                pc_clear = all(q.layer != "pc" or q.x1 <= xc - 2 or q.x0 >= xc + 3 or q.y1 <= t_y
                               or q.y0 >= t_y + TRACK_W for q in r)
                if box_ok and pc_clear and clear_landing(xc, t_y):
                    add_rect("m2c", xc - 2, t_y, xc + 3, t_y + TRACK_W)
                    add_rect("m2", xc - 2, t_y, xc + 3, t_y + TRACK_W)
                    all_m2.append(Rect("m2", xc - 2, t_y, xc + 3, t_y + TRACK_W))
                    choice = (xc, t_y)
                    break
        if choice is None:
            missing.add(net)
            continue
        landings.append(choice)
        out.pin_stack[net] = (choice[0], choice[1], False)
    if missing:
        return missing
    # the metal 3 landing belongs to the cell: MAGIC forbids a via stack split across hierarchy
    for net, (xc, t_y, _) in out.pin_stack.items():
        add_rect("m3c", xc - 2, t_y, xc + 3, t_y + TRACK_W)
    return out


def devices_from_cell(cell, group=0):
    """Dev records from a Cell or StagedCell."""
    return [Dev(d.name, d.kind, d.gate, d.drain, d.source, d.w_lam, group) for d in cell.devices]


def devices_from_block(block):
    """Dev records from a Block, one layout group per leaf instance. Handles nested blocks."""
    out = []
    counter = [0]

    def walk(node, prefix, mapping):
        for inst, cell, pins in node.instances:
            local = {"vdd": mapping["vdd"], "gnd": mapping["gnd"]}
            for pin, net in pins.items():
                local[pin] = mapping.get(net, f"{prefix}{net}")
            if hasattr(cell, "instances"):
                walk(cell, f"{prefix}{inst}_", local)
                continue
            group = counter[0]
            counter[0] += 1
            for d in cell.devices:
                def net(n):
                    return local.get(n, f"{prefix}{inst}_{n}")
                out.append(Dev(f"{prefix}{inst}_{d.name}", d.kind, net(d.gate), net(d.drain), net(d.source),
                               d.w_lam, group))

    mapping = {"vdd": "vdd", "gnd": "gnd"}
    for p in block.inputs + block.outputs:
        mapping[p] = p
    walk(block, "", mapping)
    return out


def tcl_for_cell(layout):
    """MAGIC Tcl that paints the cell in the current edit cell, in safe layer order."""
    order = ["nwell", "ndiff", "pdiff", "poly", "ndc", "pdc", "pc", "psc", "nsc", "m1", "m2c", "m2", "m3c"]
    lines = []
    for layer in order:
        for rect in layout.rects:
            if rect.layer == layer:
                lines.append(f"box {rect.x0} {rect.y0} {rect.x1} {rect.y1}; paint {layer}")
    extra = {rect.layer for rect in layout.rects} - set(order)
    if extra:
        raise ValueError(f"unexpected layers {extra}")
    return "\n".join(lines)


def tcl_labels(layout, vdd="vdd", gnd="gnd"):
    lines = []
    index = 1
    y0, y1 = layout.y_gnd
    for net, (ty, x0, x1) in sorted(layout.pins.items()):
        lines.append(f"box {x0} {ty} {x0 + 2} {ty + TRACK_W}; label {net} center m1; port make {index}")
        index += 1
    # internal nets get plain labels, so extracted netlists keep readable names for back-annotation
    for part, (ty, x0, x1) in sorted(layout.tracks.items()):
        net = part.split("@")[0]
        if net not in layout.pins:
            lines.append(f"box {x0} {ty} {x0 + 2} {ty + TRACK_W}; label {net} center m1")
    lines.append(f"box 0 {layout.y_vdd[0]} 2 {layout.y_vdd[1]}; label {vdd} center m1; port make {index}")
    index += 1
    lines.append(f"box 0 {y0} 2 {y1}; label {gnd} center m1; port make {index}")
    return "\n".join(lines)
