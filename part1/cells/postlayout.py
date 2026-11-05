"""Wrap an extracted MAGIC netlist so that benches can use it like a schematic adder."""
import re
from pathlib import Path


class ExtractedCell:
    """Holds an extracted subcircuit behind a wrapper with a chosen port order.

    Model names are renamed on the text in memory: nfet to CMOSN, pfet to CMOSP. The file
    MAGIC wrote is not changed. The .global line is removed so rails connect through ports.
    """

    def __init__(self, spice_path, name, inputs, outputs):
        text = Path(spice_path).read_text()
        text = re.sub(r"\bnfet\b", "CMOSN", text)
        text = re.sub(r"\bpfet\b", "CMOSP", text)
        text = re.sub(r"(?im)^\.global.*$", "", text)
        joined = re.sub(r"\n\+", " ", text)   # long headers continue on + lines
        match = re.search(r"(?im)^\.subckt\s+(\S+)\s*(.*)$", joined)
        self.inner, inner_ports = match.group(1), [p.lower() for p in match.group(2).split()]
        self.name = f"{name}_post"
        self.inputs, self.outputs = list(inputs), list(outputs)
        self.ports = self.inputs + self.outputs + ["vdd", "gnd"]
        missing = set(self.ports) - set(inner_ports)
        if missing:
            raise ValueError(f"extracted cell lacks ports {sorted(missing)}; it has {inner_ports}")
        self.body = text
        self.inner_ports = inner_ports
        self.capacitors = len(re.findall(r"(?m)^C", text))
        self.transistors = len(re.findall(r"(?m)^M", text))
        self.cap_total_ff = sum(_cap(m) for m in re.findall(r"(?m)^C\S+\s+\S+\s+\S+\s+(\S+)", text))

    @property
    def transistor_count(self):
        return self.transistors

    @property
    def total_width_lam(self):
        return 0

    def spice(self):
        return (self.body + f"\n.subckt {self.name} {' '.join(self.ports)}\n"
                f"X0 {' '.join(self.inner_ports)} {self.inner}\n.ends\n")


def _cap(text):
    text = text.lower()
    for suffix, scale in (("ff", 1), ("f", 1), ("pf", 1e3), ("p", 1e3)):
        if text.endswith(suffix):
            return float(text[: -len(suffix)]) * scale
    return float(text) * 1e15


def net_capacitance(spice_path, known_nets):
    """Wire capacitance per schematic net from an extracted file, in fF.

    Junction capacitance is not in these C lines (the tech file leaves it to the model), so
    this is wiring and fringe only. Coupling between two signal nets is counted on both nets.
    Only nets visible at the adder level can be annotated; nets inside a leaf cell are short.
    """
    known = set(known_nets)
    caps = {}
    for m in re.finditer(r"(?m)^C\S+\s+(\S+)\s+(\S+)\s+(\S+)\s*$", Path(spice_path).read_text()):
        value = _cap(m.group(3))
        for node in (m.group(1), m.group(2)):
            base = node.split("/")[-1].lower()
            if base in known:
                caps[base] = caps.get(base, 0.0) + value
    return caps
