# Synthetic fixtures

All records in this directory were constructed for software demonstration. They contain no experimental observations, real animal identifiers, treatment assignments, or efficacy results.

`synthetic_sequences.csv` illustrates two ordinary paired records and two boundary observations. Its six columns are `subject, group, timepoint, sequence, start_force_g, synthetic`. Every `synthetic` field is `true`.

`expected_website_input.csv` is the expected output of `tools/prepare_website_input.py --kit standard`. Boundary rows are included to demonstrate review flags; they should not be accepted as ordinary finite thresholds without addressing censoring and clipping.

The panel's built-in demo uses these same synthetic records. Its `baseline` and `followup` fixture labels map to the panel's `pre` and `model` slots, and boundary examples occupy `pre`. This mapping demonstrates the interface and does not represent an experimental schedule or a model effect.
