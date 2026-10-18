#!/usr/bin/env python3
"""Prepare calculator input from recorded O/X sequences; standard library only."""

import argparse
import csv
import io
import math
from dataclasses import dataclass
from pathlib import Path
import sys


KITS = {
    "standard": (0.07, 0.16, 0.4, 0.6, 1.0, 1.4, 2.0),
    "extended": (0.008, 0.02, 0.04, 0.07, 0.16, 0.4, 0.6, 1.0, 1.4, 2.0, 4.0),
    "aesthesia20": (0.008, 0.02, 0.04, 0.07, 0.16, 0.4, 0.6, 1.0, 1.4,
                    2.0, 4.0, 6.0, 8.0, 10.0, 15.0, 26.0, 60.0, 100.0,
                    180.0, 300.0),
}
REQUIRED_COLUMNS = {"subject", "timepoint", "sequence", "start_force_g"}


@dataclass(frozen=True)
class Trace:
    sequence: str
    forces: tuple
    clamped: bool
    censored: bool


def trace_sequence(sequence, start_force, kit):
    """The last response does not advance to another recorded stimulus."""
    sequence = str(sequence).strip().upper()
    if not sequence or any(char not in "OX" for char in sequence):
        raise ValueError("Response sequence must contain only O and X")
    if not kit or any(not math.isfinite(x) or x <= 0 for x in kit):
        raise ValueError("Kit forces must be finite and positive")
    if any(a >= b for a, b in zip(kit, kit[1:])):
        raise ValueError("Kit forces must be strictly increasing")
    try:
        index = kit.index(float(start_force))
    except (ValueError, TypeError) as exc:
        raise ValueError("Start force is not in the selected kit") from exc
    forces = [kit[index]]
    clamped = False
    for previous in sequence[:-1]:
        wanted = index + (1 if previous == "O" else -1)
        actual = max(0, min(len(kit) - 1, wanted))
        clamped |= wanted != actual
        index = actual
        forces.append(kit[index])
    return Trace(sequence, tuple(forces), clamped, len(set(sequence)) == 1)


def read_records(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not REQUIRED_COLUMNS.issubset(reader.fieldnames or []):
            raise ValueError("Required CSV columns: " + ", ".join(sorted(REQUIRED_COLUMNS)))
        records = list(reader)
    if not records:
        raise ValueError("Input has no records")
    return records


def prepare_rows(records, kit):
    output, warnings, seen = [], [], set()
    for number, row in enumerate(records, start=2):
        subject = (row.get("subject") or "").strip()
        timepoint = (row.get("timepoint") or "").strip()
        if not subject or not timepoint or any(c in subject + timepoint for c in "|\r\n\t"):
            raise ValueError(f"Row {number}: invalid subject or timepoint")
        record_id = subject + "-" + timepoint
        if record_id in seen:
            raise ValueError(f"Row {number}: duplicate subject/timepoint ID")
        seen.add(record_id)
        trace = trace_sequence(row.get("sequence", ""), row.get("start_force_g"), kit)
        output.append({"ID": record_id, "Final Filament": trace.forces[-1],
                       "XO Pattern": trace.sequence})
        flags = []
        if trace.clamped:
            flags.append("clipped trajectory; final force does not uniquely recover the path")
        if trace.censored:
            flags.append("all-identical responses; censored observation")
        if flags:
            warnings.append(f"Row {number}: " + "; ".join(flags))
    return output, warnings


def csv_text(rows):
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=["ID", "Final Filament", "XO Pattern"],
                            lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--kit", required=True, choices=KITS)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        rows, warnings = prepare_rows(read_records(args.input), KITS[args.kit])
        rendered = csv_text(rows)
        if args.output:
            with args.output.open("x", encoding="utf-8", newline="") as handle:
                handle.write(rendered)
        else:
            sys.stdout.write(rendered)
        for warning in warnings:
            print("REVIEW: " + warning, file=sys.stderr)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
