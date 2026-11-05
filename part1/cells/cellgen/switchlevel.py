"""Switch-level evaluation of a flat device list. Checks logic without a simulator.

Each MOSFET is an ideal switch: NMOS on at gate 1, PMOS on at gate 0. Handles several
stages and transmission gates by iterating until net values stop changing.
"""


def evaluate(devices, inputs):
    """Return (net values, list of short-circuit descriptions)."""
    values = dict(inputs)
    values.update(vdd=1, gnd=0)
    fixed = set(values)
    shorts = []
    for _ in range(len(devices) + 3):
        parent = {}

        def find(x):
            parent.setdefault(x, x)
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        for dev in devices:
            gate = values.get(dev["gate"])
            on = (gate == 1) if dev["kind"] == "n" else (gate == 0)
            if on:
                parent[find(dev["drain"])] = find(dev["source"])
            else:
                find(dev["drain"])
                find(dev["source"])
        groups = {}
        for net in list(parent):
            groups.setdefault(find(net), []).append(net)

        new_values = {k: values[k] for k in fixed}
        shorts = []
        for nets in groups.values():
            sources = {values[n] for n in nets if n in fixed}
            if len(sources) > 1:
                shorts.append(sorted(nets))
            elif sources:
                level = sources.pop()
                for net in nets:
                    new_values[net] = level
        if new_values == values:
            break
        values = new_values
    return values, shorts
