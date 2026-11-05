"""Series-parallel transistor networks.

A network is written from its upper terminal to its lower terminal: VDD to output for
a pull-up, output to ground for a pull-down. Child order in S() is physical order, so
it also sets which input sits nearest the output.
"""
from dataclasses import dataclass, field


@dataclass
class D:
    """One device. w is an explicit width in lambda; None means size automatically."""
    gate: str
    w: int | None = None
    dev: object = field(default=None, repr=False, compare=False)


@dataclass
class S:
    """Series connection, upper terminal first."""
    children: list = field(default_factory=list)
    nets: list = field(default_factory=list, repr=False, compare=False)

    def __init__(self, *children):
        self.children = list(children)
        self.nets = []


@dataclass
class Pa:
    """Parallel connection."""
    children: list = field(default_factory=list)

    def __init__(self, *children):
        self.children = list(children)


def copy_tree(node):
    if isinstance(node, D):
        return D(node.gate, node.w)
    return type(node)(*[copy_tree(c) for c in node.children])


def dual(node):
    """Complementary network: swap series and parallel, keep child order."""
    if isinstance(node, D):
        return D(node.gate, node.w)
    kids = [dual(c) for c in node.children]
    return Pa(*kids) if isinstance(node, S) else S(*kids)


def mirror(node):
    """Same shape as the given pull-down, for a pull-up in a mirror gate.

    Series order is reversed because a pull-up is written from VDD to the output while
    a pull-down is written from the output to ground. An input nearest the output in
    one network therefore stays nearest the output in the other.
    """
    if isinstance(node, D):
        return D(node.gate, node.w)
    if isinstance(node, S):
        return S(*[mirror(c) for c in reversed(node.children)])
    return Pa(*[mirror(c) for c in node.children])


def longest(node):
    """Largest number of series devices across the network."""
    if isinstance(node, D):
        return 1
    depths = [longest(c) for c in node.children]
    return sum(depths) if isinstance(node, S) else max(depths)


def leaves(node):
    if isinstance(node, D):
        return [node]
    return [leaf for c in node.children for leaf in leaves(c)]


def series_depth_map(node, extra=0, out=None):
    """For each device: the longest rail-to-output series path passing through it.

    Sizing each device in proportion to this gives every path unit resistance.
    """
    out = {} if out is None else out
    if isinstance(node, D):
        out[id(node)] = 1 + extra
    elif isinstance(node, Pa):
        for c in node.children:
            series_depth_map(c, extra, out)
    else:
        depths = [longest(c) for c in node.children]
        for i, c in enumerate(node.children):
            series_depth_map(c, extra + sum(depths) - depths[i], out)
    return out
