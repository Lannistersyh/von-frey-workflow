# Mouse von Frey Experimental Workflow

[English](README.md) · [简体中文](README.zh-CN.md)

A workflow for recording mouse mechanical sensitivity experiments: from an approved study plan and per-trial O/X responses to quality review, 50% paw withdrawal threshold (PWT) calculations, and traceable result archives.

The repository presents the experimental process, a browser-based data entry tool, and a reproducible synthetic example. The complete original research project is preserved in an **encrypted snapshot**; experimental records and unpublished treatment results are kept inside that archive.

```mermaid
flowchart LR
    A[Study plan and metadata] --> B[Baseline and scheduled testing]
    B --> C[Record each force and O/X response]
    C --> D[Review sequences and exceptions]
    D --> E[Export Final Filament and XO Pattern]
    E --> F[Calculate and import reference thresholds]
    F --> G[Review longitudinal results]
    G --> H[Archive raw records, results and audit trail]
```

## Start with the workflow

1. **Define the study.** Record the animal identifiers, experimental groups, tested paw, filament kit, baseline, intervention, and scheduled observations. Use the [protocol worksheet](docs/PROTOCOL_TEMPLATE.md) to document randomization, blinding, and the approved procedure.
2. **Record observations.** Enter `O` for no withdrawal and `X` for a positive response under the study's predefined scoring criteria. Preserve the actual starting force and full response sequence.
3. **Review data quality.** Check animal IDs, timepoints, missing values, start forces, boundary clipping, and operator notes. Resolve queries against the original record and retain reasons for corrections.
4. **Calculate and reconcile PWT.** Keep local preview estimates separate from imported reference results. The existing project workflow selects the external tool's **Force + Exact** output for final reporting.
5. **Archive the evidence.** Keep the original O/X records, calculation settings, imported result file, long-format export, and audit-bearing JSON together. Analyze repeated measurements at the animal level using the planned statistical method.

See the [detailed workflow](docs/WORKFLOW.md) for operational steps and the [Chinese guide](docs/WORKFLOW.zh-CN.md) for lab use. Study-specific animal procedures remain governed by the approved protocol; the panel's default timepoints and example filament lists are software presets.

## Try the entry panel

The entry panel is a single HTML file with a Chinese interface and no build step. From the repository root:

```bash
python3 -m http.server 8000 --bind 127.0.0.1
```

Open <http://127.0.0.1:8000/app/von_frey_entry.html> in a browser. Click **载入模拟 demo** to explore data entry, query handling, CSV/JSON export, and external result import. Every built-in example is synthetic and demonstrates software behavior rather than a treatment effect.

The panel stores drafts in browser IndexedDB with a localStorage fallback. Export JSON regularly for durable backups. This showcase uses its own browser storage namespace so that it does not automatically load drafts from the original laboratory panel.

## Reproduce the example export

This standard-library command walks the up-down sequence and prepares an input file for the external calculator:

```bash
python3 tools/prepare_website_input.py \
  examples/synthetic_sequences.csv \
  --kit standard \
  --output /tmp/von-frey-website-input.csv
```

It writes `ID, Final Filament, XO Pattern`, preserving the distinction between the **starting** and **last applied** filament. Clipped trajectories and all-identical response sequences are flagged for review. The tool does not calculate efficacy or infer experimental results.

To inspect the existing Python preview implementation, install the optional analysis dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-analysis.txt
python tools/preview_pwt.py examples/synthetic_sequences.csv --kit standard
```

Output is explicitly labelled `legacy_preview`; it is separate from an imported Exact δ threshold. See [calculation conventions](docs/CALCULATION.md).

## Repository contents

```text
app/          Browser entry panel with synthetic demo records
analysis/     Existing probit preview implementation
tools/        Sequence export, preview CLI, and archive recovery utility
examples/     Synthetic O/X records and expected export
docs/         Workflow, protocol worksheet, calculation and data guidance
tests/        Export, panel logic, privacy and encryption checks
private/      Encrypted original project and ciphertext metadata
```

The encrypted snapshot preserves the original spreadsheets, response data, result tables, scripts, historical exports, notes, and reference files. Its internal manifest records each file's SHA-256 digest. Operating-system metadata and Python bytecode caches are excluded. See [data protection and recovery](docs/DATA_PROTECTION.md) for restoration instructions. The decryption key is stored separately by the project owner and is never included in Git.

## Validation

```bash
python3 -m pip install -r requirements.txt
python3 -m unittest discover -s tests -p 'test_*.py' -v
node --test tests/panel.test.cjs
```

Checks cover force-chain reconstruction, the distinction between start and final forces, clipped trajectories, synthetic demo isolation, and authenticated archive recovery. They check software behavior; animal-level experimental validation and statistical interpretation require the study's own evidence.

## Method references

- Chaplan SR, et al. *Quantitative assessment of tactile allodynia in the rat paw.* Journal of Neuroscience Methods. 1994;53:55–63. [DOI: 10.1016/0165-0270(94)90144-9](https://doi.org/10.1016/0165-0270(94)90144-9).
- Christensen SL, et al. *Von Frey testing revisited: Provision of an online algorithm for improved accuracy of 50% thresholds.* European Journal of Pain. 2020;24:783–790. [DOI: 10.1002/ejp.1528](https://doi.org/10.1002/ejp.1528).
- [External von Frey calculator](https://bioapps.shinyapps.io/von_frey_app/) and [upstream R implementation](https://github.com/MikkelAStorm/Up.Down.Method).

References identify methodological sources. Rat methods require study-specific adaptation for mice. See [third-party notices](THIRD_PARTY_NOTICES.md) for source and redistribution boundaries.
