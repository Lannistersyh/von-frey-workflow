# Calculation conventions

## Response and force records

The panel uses `O` for no positive response and `X` for a positive response. The first response is observed at the recorded start force. Each subsequent force is chosen from the previous response: move one kit step up after `O`, or one step down after `X`.

The final applied force is the force at the last observation. The previous response chooses that force; the last response does not create another recorded observation.

`tools/prepare_website_input.py` mirrors this walk and flags any attempted movement beyond the kit. It exports the final applied force without pretending that a clipped path is uniquely reversible.

## Local preview

The original panel and `analysis/pwt_mle.py` use the project's stored manufacturer handle-number mapping and a fixed scale:

```text
sigma = (highest_handle - lowest_handle) / (number_of_kit_steps - 1)
PWT_g = 10**mu / 10000
```

The model fits a normal-CDF response curve with fixed sigma. This is retained as an existing preview convention. The Python module defaults to the seven-step standard kit; the preview CLI passes the selected kit explicitly. The lookup table is an inherited cross-check and is not promoted as an independently verified implementation of the original printed tables.

## Reference output

The current project's recorded reporting convention uses the external calculator with `step_type = Force` and `delta_type = Exact`, together with the actual ordered force list. The reference method and upstream implementation are linked from the README. Force-based Exact calculations and the panel's fixed-sigma handle-number preview can differ; keep the source and settings attached to each result.

The original project's local R source and derived Exact implementation are preserved inside the encrypted snapshot. This release does not reimplement or silently substitute that method.

## Boundary observations

An all-`X` or all-`O` sequence does not bracket a finite 50% threshold within the observed pattern. Retain the last force and censoring direction (`<` for all X; `>` for all O). The original panel's numeric boundary convention does not turn such an observation into an ordinary finite PWT estimate.

The preview CLI emits a blank `preview_pwt_g` and a separate `censor_bound_g` for these rows. Both the software workflow and the eventual analysis must preserve the censoring status.

## Scope of checks

The release tests check force walks, export semantics, synthetic-record isolation, and encryption behavior. They do not establish biological validity, external calculator equivalence, statistical power, or treatment efficacy. Historical local verification records remain available to the owner in the encrypted snapshot rather than being restated as newly reproduced results.
