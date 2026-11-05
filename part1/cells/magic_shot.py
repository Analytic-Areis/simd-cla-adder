#!/usr/bin/env python3
"""Screenshots of layouts in MAGIC's own window, for the reports.

MAGIC is started on the XQuartz display, loads a cell, fits it in a window of a fixed size,
and dumps that window with xwd. The dump is converted to PNG here, unchanged: these are
MAGIC's own rendering, not a redraw.

Needs XQuartz running. Usage:  python3 magic_shot.py <layout folder> <cell> <out.png> [display]
"""
import os
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

XWD = "/opt/X11/bin/xwd"


def read_xwd(path):
    """Pixels of a 24- or 32-bit TrueColor XWD file as an RGB array."""
    data = Path(path).read_bytes()
    h = struct.unpack(">25I", data[:100])
    header_size, width, height = h[0], h[4], h[5]
    byte_order, bpp, bytes_per_line = h[7], h[11], h[12]
    red_mask, green_mask, blue_mask = h[14], h[15], h[16]
    ncolors = h[19]
    offset = header_size + ncolors * 12
    rows = np.frombuffer(data[offset:offset + bytes_per_line * height], dtype=np.uint8).reshape(height, bytes_per_line)
    if bpp not in (24, 32):
        raise ValueError(f"only 24- and 32-bit XWD are handled, this is {bpp}-bit")
    n = bpp // 8
    b = rows[:, :width * n].reshape(height, width, n).astype(np.uint32)
    if not byte_order:          # LSBFirst: least significant byte first
        b = b[:, :, ::-1]
    px = np.zeros((height, width), dtype=np.uint32)
    for k in range(n):
        px = (px << 8) | b[:, :, k]

    def channel(mask):
        shift = (mask & -mask).bit_length() - 1
        return ((px & mask) >> shift).astype(np.uint8)
    return np.dstack([channel(red_mask), channel(green_mask), channel(blue_mask)])


def shoot(folder, cell, png, display=":1", size=(1400, 1000), area=None, timeout=120):
    """area: optional (x0, y0, x1, y1) in lambda to zoom on; the whole cell otherwise."""
    folder, png = Path(folder), Path(png)
    with tempfile.TemporaryDirectory() as tmp:
        dump = Path(tmp) / "shot.xwd"
        view = f"box {area[0]} {area[1]} {area[2]} {area[3]}\nfindbox zoom" if area else "view"
        script = Path(tmp) / "shot.tcl"
        script.write_text(f"""load {cell}
select top cell
expand
select clear
set w [lindex [magic::windownames layout] 0]
wm geometry [winfo toplevel $w] {size[0]}x{size[1]}+10+10
update
{view}
update
after 1500
update
exec {XWD} -id [wm frame [winfo toplevel $w]] -out {dump}
puts SHOT_DONE
quit -noprompt
""")
        env = {**os.environ, "DISPLAY": display}
        res = subprocess.run(["magic", "-d", "X11", "-noconsole", "-T", "SCN6M_DEEP.09.tech27", str(script)],
                             cwd=folder, env=env, capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
        if "SHOT_DONE" not in res.stdout or not dump.exists():
            raise RuntimeError(f"{cell}: no screenshot\n{res.stdout[-400:]}\n{res.stderr[-400:]}")
        img = read_xwd(dump)
        # drop the black margin XQuartz leaves around a window that is larger than the screen area
        keep_r = np.nonzero(img.max(axis=(1, 2)) > 0)[0]
        keep_c = np.nonzero(img.max(axis=(0, 2)) > 0)[0]
        img = img[keep_r[0]:keep_r[-1] + 1, keep_c[0]:keep_c[-1] + 1]
        if not area:
            # MAGIC outlines the cell in white: keep that outline and a small margin, drop the empty grey
            white = np.all(img == 255, axis=2)
            rows, cols = np.nonzero(white.sum(axis=1) > 50)[0], np.nonzero(white.sum(axis=0) > 50)[0]
            if len(rows) and len(cols):
                m = 14
                img = img[max(0, rows[0] - m):rows[-1] + m + 1, max(0, cols[0] - m):cols[-1] + m + 1]
        plt.imsave(png, img)
    return png


if __name__ == "__main__":
    print(shoot(sys.argv[1], sys.argv[2], sys.argv[3], *(sys.argv[4:5] or [":1"])))
