"""Cells: from networks to devices to SPICE.

Cell        one static complementary gate
StagedCell  several gate or transmission-gate stages, flat devices (for example an XOR)
Block       hierarchical connection of other cells (for example the carry generator)
"""
from dataclasses import dataclass
from itertools import product

from . import config as cfg
from .network import D, Pa, S, copy_tree, dual, series_depth_map


@dataclass
class Device:
    name: str
    kind: str   # "n" or "p"
    gate: str
    drain: str
    source: str
    bulk: str
    w_lam: int
    l_lam: int = cfg.LMIN_LAM
    as_lam2: int = 0
    ps_lam: int = 0
    ad_lam2: int = 0
    pd_lam: int = 0

    def spice(self):
        lam = cfg.LAMBDA_M
        model = "CMOSN" if self.kind == "n" else "CMOSP"
        return (f"{self.name} {self.drain} {self.gate} {self.source} {self.bulk} {model} "
                f"W={self.w_lam * lam:.4e} L={self.l_lam * lam:.4e} "
                f"AS={self.as_lam2 * lam ** 2:.4e} PS={self.ps_lam * lam:.4e} "
                f"AD={self.ad_lam2 * lam ** 2:.4e} PD={self.pd_lam * lam:.4e}")


def assign_junctions(devices, ports):
    """Estimate junctions before layout; extraction replaces these later.

    A node joining exactly two diffusion terminals of the same device type, with no
    connection leaving the cell, can be an uncontacted shared region. An inverter
    output joins an NMOS and a PMOS, so it needs contacts even though it has two
    terminals. All others need a contact.
    """
    touch = {}
    for dev in devices:
        for net in (dev.drain, dev.source):
            touch.setdefault(net, []).append(dev.kind)

    def size(net, w):
        kinds = touch[net]
        shared = net not in ports and len(kinds) == 2 and kinds[0] == kinds[1]
        length = cfg.SD_SHARED_LAM if shared else cfg.SD_CONTACTED_LAM
        return w * length, 2 * (w + length)

    for dev in devices:
        dev.as_lam2, dev.ps_lam = size(dev.source, dev.w_lam)
        dev.ad_lam2, dev.pd_lam = size(dev.drain, dev.w_lam)


class _Leaf:
    """Shared behaviour of cells whose devices are all at one level."""

    def definitions(self, seen=None):
        seen = set() if seen is None else seen
        if self.name in seen:
            return ""
        seen.add(self.name)
        lines = [f"* {self.name}: {self.description}" if self.description else f"* {self.name}",
                 "* GENERATED from part1/cells/library.py. Do not edit by hand.",
                 f".subckt {self.name} {' '.join(self.ports)}"]
        lines += [d.spice() for d in self.devices]
        lines.append(f".ends {self.name}")
        return "\n".join(lines) + "\n"

    def spice(self):
        return self.definitions()

    @property
    def transistor_count(self):
        return len(self.devices)

    @property
    def total_width_lam(self):
        return sum(d.w_lam for d in self.devices)


class Cell(_Leaf):
    """pdn is required. pun defaults to the dual of pdn.

    logic(values) returns the intended output for a dict of input values. It is kept
    separate from the networks so that tests can check one against the other.
    """

    def __init__(self, name, pdn, inputs, logic, pun=None, drive=1.0, output="y", description="",
                 prefix=""):
        self.name, self.inputs, self.logic = name, list(inputs), logic
        self.output, self.description, self.drive = output, description, drive
        self.outputs = [output]
        self.prefix = prefix
        self.pdn = copy_tree(pdn)
        self.pun = dual(pdn) if pun is None else copy_tree(pun)
        self.ports = self.inputs + [output, "vdd", "gnd"]
        self.devices = []
        self._counter = {"n": 0, "p": 0, "xn": 0, "xp": 0}
        self._flatten(self.pun, "vdd", output, "p", series_depth_map(self.pun))
        self._flatten(self.pdn, output, "gnd", "n", series_depth_map(self.pdn))
        assign_junctions(self.devices, self.ports)

    def _flatten(self, node, top, bot, kind, depth):
        if isinstance(node, D):
            unit = cfg.WN_UNIT_LAM if kind == "n" else cfg.WP_UNIT_LAM
            w = node.w if node.w is not None else round(self.drive * unit * depth[id(node)])
            w = max(w, cfg.WMIN_LAM)
            self._counter[kind] += 1
            drain, source = (top, bot) if kind == "n" else (bot, top)
            node.dev = Device(f"M{self.prefix}{kind}{self._counter[kind]}", kind, node.gate, drain,
                              source, "gnd" if kind == "n" else "vdd", w)
            self.devices.append(node.dev)
        elif isinstance(node, Pa):
            for child in node.children:
                self._flatten(child, top, bot, kind, depth)
        else:
            node.nets = []
            upper = top
            for i, child in enumerate(node.children):
                if i == len(node.children) - 1:
                    lower = bot
                else:
                    self._counter["x" + kind] += 1
                    lower = f"{self.prefix}x{kind}{self._counter['x' + kind]}"
                    node.nets.append(lower)
                self._flatten(child, upper, lower, kind, depth)
                upper = lower

    def truth(self, values):
        return {self.output: self.logic(values)}

    def vectors(self):
        return [dict(zip(self.inputs, bits)) for bits in product([0, 1], repeat=len(self.inputs))]


@dataclass
class GateStage:
    """A static gate inside a StagedCell. Pin names in the network are real nets."""
    pdn: object
    out: str
    pun: object = None
    drive: float = 1.0


@dataclass
class TGStage:
    """A transmission gate between nets a and b."""
    a: str
    b: str
    n_gate: str
    p_gate: str
    wn: int = cfg.WN_UNIT_LAM
    wp: int = cfg.WP_UNIT_LAM


class StagedCell(_Leaf):
    def __init__(self, name, inputs, outputs, logic, stages, description="", vector_fn=None):
        self.name, self.inputs, self.outputs = name, list(inputs), list(outputs)
        self.logic, self.stages, self.description = logic, stages, description
        self.vector_fn = vector_fn
        self.ports = self.inputs + self.outputs + ["vdd", "gnd"]
        self.devices = []
        for i, stage in enumerate(stages):
            if isinstance(stage, GateStage):
                stage.cell = Cell(f"{name}_s{i}", stage.pdn, [], None, pun=stage.pun, drive=stage.drive,
                                  output=stage.out, prefix=f"s{i}")
                self.devices += stage.cell.devices
            else:
                dn = Device(f"Ms{i}n", "n", stage.n_gate, stage.a, stage.b, "gnd", stage.wn)
                dp = Device(f"Ms{i}p", "p", stage.p_gate, stage.a, stage.b, "vdd", stage.wp)
                leaf_n, leaf_p = D(stage.n_gate, stage.wn), D(stage.p_gate, stage.wp)
                leaf_n.dev, leaf_p.dev = dn, dp
                stage.tree = Pa(leaf_n, leaf_p)
                self.devices += [dn, dp]
        assign_junctions(self.devices, self.ports)

    def truth(self, values):
        return self.logic(values)

    def vectors(self):
        if self.vector_fn:
            return self.vector_fn()
        return [dict(zip(self.inputs, bits)) for bits in product([0, 1], repeat=len(self.inputs))]


class Block:
    """Hierarchical cell. instances are (instance name, cell, {cell pin: block net})."""

    def __init__(self, name, inputs, outputs, logic, instances, description="", vector_fn=None):
        self.name, self.inputs, self.outputs = name, list(inputs), list(outputs)
        self.logic, self.instances, self.description = logic, instances, description
        self.vector_fn = vector_fn
        self.ports = self.inputs + self.outputs + ["vdd", "gnd"]
        self.net_caps = {}   # net: fF, wire load back-annotated from an extracted layout

    def definitions(self, seen=None):
        seen = set() if seen is None else seen
        if self.name in seen:
            return ""
        seen.add(self.name)
        text = "".join(cell.definitions(seen) for _, cell, _ in self.instances)
        lines = [f"* {self.name}: {self.description}" if self.description else f"* {self.name}",
                 "* GENERATED from part1/cells/library.py. Do not edit by hand.",
                 f".subckt {self.name} {' '.join(self.ports)}"]
        for inst, cell, pins in self.instances:
            nets = [{"vdd": "vdd", "gnd": "gnd", **pins}[p] for p in cell.ports]
            lines.append(f"X{inst} {' '.join(nets)} {cell.name}")
        for k, (net, cap) in enumerate(sorted(self.net_caps.items())):
            lines.append(f"Cw{k} {net} gnd {cap:.3f}f")
        lines.append(f".ends {self.name}")
        return text + "\n".join(lines) + "\n"

    def spice(self):
        return self.definitions()

    def truth(self, values):
        return self.logic(values)

    def vectors(self):
        if self.vector_fn:
            return self.vector_fn()
        return [dict(zip(self.inputs, bits)) for bits in product([0, 1], repeat=len(self.inputs))]

    @property
    def transistor_count(self):
        return sum(cell.transistor_count for _, cell, _ in self.instances)

    @property
    def total_width_lam(self):
        return sum(cell.total_width_lam for _, cell, _ in self.instances)


def parse_subckt(text):
    """Read one flat subcircuit from SPICE text."""
    ports, devices = [], []
    for line in text.splitlines():
        tok = line.split()
        if not tok or tok[0].startswith("*"):
            continue
        if tok[0].lower() == ".subckt":
            ports = tok[2:]
        elif tok[0][0] in "mM":
            devices.append(_parse_device(tok))
    return ports, devices


def _parse_device(tok):
    params = {k.upper(): float(v) for k, v in (t.split("=") for t in tok[6:])}
    return dict(name=tok[0], drain=tok[1], gate=tok[2], source=tok[3], bulk=tok[4],
                kind="n" if tok[5].upper() == "CMOSN" else "p", **params)


def parse_flat(text, top):
    """Read a hierarchical netlist from SPICE text and flatten one subcircuit to devices."""
    defs, current = {}, None
    for line in text.splitlines():
        tok = line.split()
        if not tok or tok[0].startswith("*"):
            continue
        if tok[0].lower() == ".subckt":
            current = defs.setdefault(tok[1], dict(ports=tok[2:], devices=[], instances=[]))
        elif tok[0].lower() == ".ends":
            current = None
        elif tok[0][0] in "mM":
            current["devices"].append(_parse_device(tok))
        elif tok[0][0] in "xX":
            current["instances"].append((tok[0], tok[-1], tok[1:-1]))

    def expand(name, mapping, path):
        out = []
        for dev in defs[name]["devices"]:
            flat = dict(dev)
            flat["name"] = path + dev["name"]
            for term in ("drain", "gate", "source", "bulk"):
                net = dev[term]
                flat[term] = mapping.get(net, path + net)
            out.append(flat)
        for inst, sub, nets in defs[name]["instances"]:
            actual = [mapping.get(n, path + n) for n in nets]
            out += expand(sub, dict(zip(defs[sub]["ports"], actual)), f"{path}{inst}.")
        return out

    return expand(top, {p: p for p in defs[top]["ports"]}, "")
