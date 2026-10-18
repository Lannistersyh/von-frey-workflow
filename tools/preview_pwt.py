#!/usr/bin/env python3
"""Display the existing handle-number preview; never label it Exact output."""

import argparse
import csv
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analysis.pwt_mle import LOGS, pwt
from tools.prepare_website_input import KITS, prepare_rows, read_records, trace_sequence


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--kit", required=True, choices=KITS)
    args = parser.parse_args()
    kit = KITS[args.kit]
    try:
        records = read_records(args.input)
        prepare_rows(records, kit)
        if any(force not in LOGS for force in kit):
            raise ValueError("Legacy Python handle map does not cover this kit; use standard or extended")
        sigma = (LOGS[kit[-1]] - LOGS[kit[0]]) / (len(kit) - 1)
        fields = ["subject", "timepoint", "source", "preview_pwt_g", "status",
                  "censor_direction", "censor_bound_g", "final_force_g", "clamped"]
        output = []
        for row in records:
            trace = trace_sequence(row["sequence"], row["start_force_g"], kit)
            estimate = ""
            if not trace.censored:
                estimate, _ = pwt(list(zip(trace.forces, trace.sequence)), sigma=sigma)
                estimate = format(estimate, ".9g")
            output.append({
                "subject": row["subject"], "timepoint": row["timepoint"],
                "source": "legacy_preview", "preview_pwt_g": estimate,
                "status": "censored" if trace.censored else ("clamped_review" if trace.clamped else "preview"),
                "censor_direction": ("<" if trace.sequence[0] == "X" else ">") if trace.censored else "",
                "censor_bound_g": trace.forces[-1] if trace.censored else "",
                "final_force_g": trace.forces[-1], "clamped": str(trace.clamped).lower(),
            })
        writer = csv.DictWriter(sys.stdout, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(output)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
