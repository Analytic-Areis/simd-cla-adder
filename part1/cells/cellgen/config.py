"""Project constants, paths and the course plot-title convention."""
import json
from pathlib import Path

PART1 = Path(__file__).resolve().parents[2]
ROOT = PART1.parent
MODEL = ROOT / "technology" / "TSMC_180nm.txt"

LAMBDA_M = 0.09e-6
VDD = 1.8
LMIN_LAM = 2       # channel length, 2 lambda
WMIN_LAM = 3       # tech file: diffusion width at least 3 lambda
WN_UNIT_LAM = 10   # unit NMOS width: the assignment's load inverter
WP_UNIT_LAM = 20   # unit PMOS width
SD_CONTACTED_LAM = 6  # tech file: 2 lambda gate-to-contact + 4 lambda contact
SD_SHARED_LAM = 3     # tech file: poly-to-poly spacing on an uncontacted series node


def plot_title(question, part):
    """Course convention: Your-name-roll-question-number-part.

    Name and roll number come from part1/project_config.json. Until they are filled
    in, a visible placeholder is used so that no identity is guessed.
    """
    cfg = json.loads((PART1 / "project_config.json").read_text())
    name = (cfg.get("name") or "NAME").strip().replace(" ", "-")
    roll = str(cfg.get("roll") or "ROLL").strip()
    return f"{name}-{roll}-{question}-{part}"
