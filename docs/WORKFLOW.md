# Experimental and data workflow

[中文](WORKFLOW.zh-CN.md) · [Repository](../README.md)

## 1. Prepare the study record

Use the [protocol worksheet](PROTOCOL_TEMPLATE.md) before collecting data. Record animal IDs, group allocation, sex/strain information, the experimental unit, tested side and surface, filament kit, intervention, and measurement schedule. Document who performs testing and analysis, and how randomization and blinding are implemented.

The repository's defaults do not establish an approved protocol. Acclimation, stimulus duration, interstimulus interval, positive-response criteria, stopping rules, upper force limit, and sampling frequency must follow the study's own documented procedure. Record actual timestamps so that the frequency and cumulative exposure can be assessed.

## 2. Acquire per-trial observations

Open `app/von_frey_entry.html` through the local server described in the README. Set the protocol ID, operator, device/kit, date, and actual starting force. Configure the timepoints to match the approved schedule.

For each animal and timepoint, preserve the observed response sequence. Under the panel's convention, `O` means no positive response and `X` means a positive response. The up-down walk uses the preceding response to select the next force: `O` moves up one available filament and `X` moves down one.

Retain the actual per-trial force record whenever available, especially at a kit boundary. A trajectory that clips at a boundary may not be uniquely reconstructed from its final force. Do not replace a recorded start force with a reverse-inferred value without checking the original notes.

## 3. Review queries without changing observations to fit an expectation

Check duplicate animal IDs, missing fields, unsupported start forces, timepoint labels, all-identical sequences, and boundary clipping. Check entries against original observations and record corrections with a reason.

The panel also contains trend-based prompts inherited from the local project. These are review prompts, not evidence that a record is wrong or that an intervention must work. Retain verified negative findings. An acknowledged query and a corrected transcription error are different events and should remain distinguishable in the audit trail.

## 4. Export for reference calculation

Export the website input CSV or run `tools/prepare_website_input.py` on the long-format synthetic example. The calculator expects:

```text
ID, Final Filament, XO Pattern
```

`Final Filament` is the force applied for the **last recorded response**. It is neither the initial force nor the force that would have been selected after the last response.

For the existing project's reference workflow, select **Force** and **Exact** in the external calculator and supply the full ordered filament list used for the experiment. Preserve the input file, selected steps, calculator settings, and raw output. All-identical sequences and clipped trajectories require explicit review rather than automatic interpretation as ordinary finite estimates.

The entry panel does not automatically transmit observations to the external calculator. Uploading its exported CSV is a separate user action. Use synthetic or appropriately deidentified input when demonstrating the external service.

## 5. Reconcile and freeze results

Import the raw website result CSV into the entry panel. Match animal/timepoint IDs and inspect discrepancies alongside the local preview. Keep the imported source file and calculation configuration available for traceability.

The current project convention selects the imported Force + Exact output for final reporting. The local handle-number/fixed-σ preview is retained for entry feedback. Do not pool these two calculation conventions in one reported endpoint without a predefined justification and a recorded source field.

For a sequence containing only `X` or only `O`, retain the censoring direction and last applied force. The inherited panel may display that force as a numeric boundary convention; it is still a censored observation. Its treatment in statistics must be specified rather than silently analyzed as an ordinary point estimate.

## 6. Analyze and archive

Keep animal and group metadata attached to each timepoint. The animal is the experimental unit for the longitudinal study; repeated trials and timepoints are not additional independent animals. Use the planned analysis, missing-data and censoring rules. This repository does not assert a treatment effect or provide a completed statistical comparison.

Archive the full response record, start and final forces, kit definition, operator/timestamps, query resolutions, raw reference input/output, long table, and JSON audit export. Retain dated versions when correcting an archive.

The encrypted snapshot provides owner-controlled recovery of the original local research files. Browser drafts and the public synthetic example serve different purposes and do not replace that research archive.
