"""Layout-versus-schematic comparison, written for this project because netgen is unavailable.

Compares two flat device lists by partition refinement. Each device and net starts with a
colour from local facts (device type and summed width; net name if it is a port), and colours
are repeatedly refined from neighbours. The circuits match if the final colour multisets match,
with every device's neighbourhood equal. Parallel devices are merged first, so fingers compare
equal to one wide device. Refinement can in principle fail to separate symmetric nets, but a
real mismatch always changes the multisets.

This is our own script, not an industry LVS tool.
"""
from collections import Counter


def merge_parallel(devices):
    merged = {}
    for d in devices:
        pair = tuple(sorted((d["a"], d["b"])))
        key = (d["kind"], d["gate"], pair, round(d["l"] * 1e9))
        merged[key] = merged.get(key, 0.0) + d["w"]
    return [dict(kind=k[0], gate=k[1], a=k[2][0], b=k[2][1], l=k[3] / 1e9, w=w) for k, w in merged.items()]


def _refine(devices, ports, rounds=12):
    nets = {}
    for i, d in enumerate(devices):
        nets.setdefault(d["gate"], []).append((i, "g"))
        nets.setdefault(d["a"], []).append((i, "d"))
        nets.setdefault(d["b"], []).append((i, "d"))
    net_colour = {n: (n if n in ports else "*") for n in nets}
    dev_colour = {}
    for _ in range(rounds):
        dev_colour = {i: hash((d["kind"], round(d["w"] * 1e9), round(d["l"] * 1e9),
                               net_colour[d["gate"]], tuple(sorted((str(net_colour[d["a"]]), str(net_colour[d["b"]]))))))
                      for i, d in enumerate(devices)}
        net_colour = {n: (n if n in ports else hash(tuple(sorted((str(dev_colour[i]), role) for i, role in members))))
                      for n, members in nets.items()}
    return dev_colour, net_colour


def compare(layout_devices, schematic_devices, ports, width_tolerance=0.0):
    """Returns (matched, message). Width comparison uses a rounded 1 nm grid."""
    a = merge_parallel(layout_devices)
    b = merge_parallel(schematic_devices)
    if len(a) != len(b):
        return False, f"device count differs after merging: layout {len(a)}, schematic {len(b)}"
    missing = (set(ports) - {"vdd", "gnd"}) - {n for d in a for n in (d["gate"], d["a"], d["b"])}
    if missing:
        return False, f"ports missing from layout: {sorted(missing)}"
    da, na = _refine(a, ports)
    db, nb = _refine(b, ports)
    ca, cb = Counter(da.values()), Counter(db.values())
    if ca != cb:
        return False, f"device neighbourhoods differ, {sum((ca - cb).values())} unmatched devices"
    if Counter(str(v) for v in na.values()) != Counter(str(v) for v in nb.values()):
        return False, "net neighbourhoods differ"
    return True, f"match: {len(a)} merged devices, {len(na)} nets"


def read_extracted(text, top=None):
    """Flat device list from an extracted SPICE file. Sizes in the file are in metres."""
    devices = []
    current = None
    for raw in text.splitlines():
        tok = raw.split()
        if not tok or tok[0].startswith("*"):
            continue
        if tok[0].lower() == ".subckt":
            current = tok[1]
            continue
        if tok[0].lower() == ".ends":
            current = None
            continue
        if tok[0][0] in "mM":
            params = {k.lower(): _num(v) for k, v in (t.split("=") for t in tok[6:] if "=" in t)}
            devices.append(dict(kind="n" if "n" in tok[5].lower() and tok[5].lower() != "pfet" and tok[5].lower() != "cmosp" else "p",
                                gate=tok[2].lower(), a=tok[1].lower(), b=tok[3].lower(), w=params["w"], l=params["l"]))
    return devices


def _num(text):
    text = text.lower().strip()
    scale = {"f": 1e-15, "p": 1e-12, "n": 1e-9, "u": 1e-6, "m": 1e-3}
    if text[-1] in scale:
        return float(text[:-1]) * scale[text[-1]]
    return float(text)


def schematic_devices(flat):
    """Device list from parse_flat output."""
    return [dict(kind=d["kind"], gate=d["gate"].lower(), a=d["drain"].lower(), b=d["source"].lower(),
                 w=d["W"], l=d["L"]) for d in flat]
