#!/usr/bin/env python3
"""Phase 0 exit check: generated cells must reproduce earlier hand-built measurements.

Check 1 repeats the FO4 inverter of characterisation experiment E3.
Check 2 repeats the schematic inverter of the MAGIC flow check.
Both testbenches use only generator-produced subcircuits. Reference values are read
from the earlier result files, never typed in.
"""
import csv
import re

from cellgen import config as cfg
from cellgen.sim import ps_to_png, run_ngspice
from library import inv

OUT = cfg.PART1 / "simulations" / "phase0"
RESULTS = cfg.PART1 / "results"
TOLERANCE_PCT = 0.5
HEADER = ("* {title}\n* Uses generator-produced subcircuits only.\n"
          ".include ../../spice/models/TSMC_180nm.txt\n.options reltol=1e-4\n"
          "VDD vdd gnd 1.8\nVin in0 gnd PULSE(0 1.8 1n 20p 20p 2n 4n)\n")


def meas(prefix, innode, outnode):
    return (f".meas tran {prefix}tphl TRIG v({innode}) VAL=0.9 RISE=2 TARG v({outnode}) VAL=0.9 FALL=2\n"
            f".meas tran {prefix}tplh TRIG v({innode}) VAL=0.9 FALL=2 TARG v({outnode}) VAL=0.9 RISE=2\n")


def check_fo4():
    """Same widths as E3: 3/6 lambda shaper and driver, DUT 10/20, loads x4 and x16."""
    shaper, dut, load, load2 = inv(0.3, "ish"), inv(1.0, "idut"), inv(4.0, "ilo"), inv(16.0, "ill")
    title = cfg.plot_title("phase0", "generated-inverter-FO4")
    net = HEADER.format(title="Phase 0 check 1: generated FO4 inverter against E3")
    net += "".join(c.spice() for c in (shaper, dut, load, load2))
    net += ("X0 in0 n1 vdd gnd ish\nX1 n1 ndut vdd gnd ish\nX2 ndut nout vdd gnd idut\n"
            "X3 nout n3 vdd gnd ilo\nX4 n3 n4 vdd gnd ill\n")
    net += ".tran 0.5p 11n\n" + meas("", "ndut", "nout")
    net += (".control\nset hcopypscolor=1\nset color0=white\nset color1=black\nrun\n"
            f"set curplottitle={title}\n"
            "hardcopy phase0_fo4.ps v(ndut) v(nout) xlimit 4.8n 5.4n\n"
            "wrdata phase0_fo4_wave v(ndut) v(nout)\n"
            "quit\n.endc\n.end\n")
    cir = OUT / "phase0_fo4.cir"
    cir.write_text(net)
    values, result = run_ngspice(cir)
    if "tphl" not in values or "tplh" not in values:
        raise RuntimeError(f"measurements missing, see {cir.with_suffix('.log')}\n{result.stderr[-400:]}")
    # ngspice lowercases the title, so the required text is compared in lower case
    ps_text = (OUT / "phase0_fo4.ps").read_text(errors="ignore")
    if title.lower() not in ps_text:
        raise RuntimeError("curplottitle did not reach the hardcopy")
    ps_to_png(OUT / "phase0_fo4.ps")
    ref = next(r for r in csv.DictReader(open(cfg.PART1 / "simulations/characterisation/results/e3_inverter_fanout.csv"))
               if r["h"] == "4")
    return [("FO4 tpHL", values["tphl"] * 1e12, float(ref["tphl_ps"])),
            ("FO4 tpLH", values["tplh"] * 1e12, float(ref["tplh_ps"]))]


def check_flow_inverter():
    """Same conditions as the schematic inverter in part1/layout/flow_check."""
    driver, gate = inv(2.0, "idrv"), inv(1.0, "igate")
    net = HEADER.format(title="Phase 0 check 2: generated inverter against flow check schematic")
    net += driver.spice() + gate.spice()
    net += ("XD in0 b vdd gnd idrv\nXG b os vdd gnd igate\nXL os l2 vdd gnd igate\n"
            ".tran 0.5p 11n\n" + meas("sch_", "b", "os") + ".end\n")
    cir = OUT / "phase0_flow_inverter.cir"
    cir.write_text(net)
    values, result = run_ngspice(cir)
    if "sch_tphl" not in values:
        raise RuntimeError(f"measurements missing\n{result.stderr[-400:]}")
    log = (cfg.PART1 / "layout/flow_check/flow_inv_tb.log").read_text()
    ref = {k: float(re.search(rf"{k}\s*=\s*([-+0-9.eE]+)", log).group(1)) for k in ("sch_tphl", "sch_tplh")}
    return [("Flow inverter tpHL", values["sch_tphl"] * 1e12, ref["sch_tphl"] * 1e12),
            ("Flow inverter tpLH", values["sch_tplh"] * 1e12, ref["sch_tplh"] * 1e12)]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    RESULTS.mkdir(parents=True, exist_ok=True)
    rows = []
    for label, new, ref in check_fo4() + check_flow_inverter():
        err = 100 * (new - ref) / ref
        rows.append(dict(check=label, generated_ps=round(new, 3), reference_ps=round(ref, 3),
                         difference_pct=round(err, 3), passed=abs(err) <= TOLERANCE_PCT))
        print(rows[-1])
    with open(RESULTS / "phase0_generator_check.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    if not all(r["passed"] for r in rows):
        raise SystemExit("PHASE 0 CHECK FAILED")
    print("PHASE 0 CHECK PASSED")


if __name__ == "__main__":
    main()
