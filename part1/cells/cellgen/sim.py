"""Run ngspice in batch, keep the log, return .meas values."""
import os
import re
import subprocess
from pathlib import Path


def run_ngspice(cir_path, timeout=600):
    cir_path = Path(cir_path)
    # one thread per run: parallelism comes from running many simulations at once
    result = subprocess.run(["ngspice", "-b", cir_path.name], cwd=cir_path.parent, capture_output=True, text=True,
                            timeout=timeout, env={**os.environ, "OMP_NUM_THREADS": "1"})
    log = cir_path.with_suffix(".log")
    log.write_text(result.stdout + "\n--- STDERR ---\n" + result.stderr)
    values = {}
    for line in result.stdout.splitlines():
        m = re.match(r"\s*(\w+)\s*=\s*([-+0-9.eE]+)\s", line + " ")
        if m:
            try:
                values[m.group(1).lower()] = float(m.group(2))
            except ValueError:
                pass
    return values, result


def ps_to_png(ps_path, dpi=110):
    """Convert an ngspice hardcopy to PNG and return the path."""
    ps_path = Path(ps_path)
    png = ps_path.with_suffix(".png")
    subprocess.run(["gs", "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=png16m", f"-r{dpi}",
                    f"-sOutputFile={png}", str(ps_path)], check=True, capture_output=True)
    return png
