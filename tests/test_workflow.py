import csv
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.prepare_website_input import KITS, csv_text, prepare_rows, read_records, trace_sequence


class WorkflowTests(unittest.TestCase):
    def test_start_final_and_next_force_are_distinct(self):
        # Forces observed: 0.16, 0.4, 0.6, 0.4, 0.6, 0.4.
        # Last O would select 0.6 next, but no such observation was recorded.
        trace = trace_sequence("OOXOXO", 0.16, KITS["standard"])
        self.assertEqual(trace.forces, (0.16, 0.4, 0.6, 0.4, 0.6, 0.4))
        self.assertFalse(trace.clamped)

    def test_boundary_and_censoring_are_retained(self):
        trace = trace_sequence("XXXXXX", 0.16, KITS["standard"])
        self.assertEqual(trace.forces[-1], 0.07)
        self.assertTrue(trace.clamped)
        self.assertTrue(trace.censored)
        # Reaching a boundary is not by itself clipping.
        self.assertFalse(trace_sequence("OX", 1.4, KITS["standard"]).clamped)

    def test_invalid_inputs_fail(self):
        for sequence, start in [("OX?X", 0.16), ("", 0.16), ("OX", 0.17)]:
            with self.assertRaises(ValueError):
                trace_sequence(sequence, start, KITS["standard"])

    def test_duplicate_record_id_fails(self):
        row = {"subject": "DEMO", "timepoint": "baseline", "sequence": "OX", "start_force_g": ".16"}
        with self.assertRaises(ValueError):
            prepare_rows([row, row], KITS["standard"])

    def test_synthetic_fixture_matches_expected_export(self):
        records = read_records(ROOT / "examples/synthetic_sequences.csv")
        self.assertTrue(all(row["synthetic"] == "true" for row in records))
        self.assertTrue(all(row["subject"].startswith("DEMO-") for row in records))
        rows, warnings = prepare_rows(records, KITS["standard"])
        self.assertEqual(csv_text(rows), (ROOT / "examples/expected_website_input.csv").read_text())
        self.assertEqual(len(warnings), 2)

    def test_cli_does_not_overwrite_exports(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "export.csv"
            output.write_text("existing record")
            process = subprocess.run([
                sys.executable, str(ROOT / "tools/prepare_website_input.py"),
                str(ROOT / "examples/synthetic_sequences.csv"), "--kit", "standard", "--output", str(output)
            ], capture_output=True)
            self.assertNotEqual(process.returncode, 0)
            self.assertEqual(output.read_text(), "existing record")

    @unittest.skipUnless(importlib.util.find_spec("scipy"), "optional analysis dependencies not installed")
    def test_preview_keeps_censored_rows_out_of_finite_estimates(self):
        process = subprocess.run([
            sys.executable, str(ROOT / "tools/preview_pwt.py"),
            str(ROOT / "examples/synthetic_sequences.csv"), "--kit", "standard"
        ], capture_output=True, text=True, check=True)
        rows = list(csv.DictReader(process.stdout.splitlines()))
        self.assertTrue(all(row["source"] == "legacy_preview" for row in rows))
        self.assertTrue(all(row["preview_pwt_g"] == "" for row in rows[-2:]))
        self.assertEqual([row["censor_direction"] for row in rows[-2:]], ["<", ">"])


if __name__ == "__main__":
    unittest.main()
