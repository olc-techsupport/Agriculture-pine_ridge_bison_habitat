# Facilitator guide: Pine Ridge Bison Habitat

## Purpose and audience

This seven-session series introduces spatial data literacy, reproducible habitat modeling, model critique, and responsible interpretation using public environmental data describing Pine Ridge. It is intended for OLC learners and collaborators with mixed coding experience. The maps are educational screening products, not decisions about where bison belong or where restoration should occur.

## Before the series

- Confirm the current governance and release status with the designated OLC/OST reviewer.
- Provide a tested Conda environment or prepared lab computers.
- Run `python -m pytest` before instruction.
- Confirm that no restricted data or precise unapproved candidate locations will be displayed or shared.
- Explain that component weights and patch parameters are hypotheses for critique, not approved ecological or management standards.

## Repeating session pattern

Allow 75–100 minutes per notebook:

1. **Orient (10 minutes):** purpose, objectives, governance checkpoint, and source.
2. **Predict (10 minutes):** learners record expected spatial patterns and evidence that might change their view.
3. **Run and inspect (30–40 minutes):** execute cells in pairs and pause at the learner checkpoint.
4. **Interpret (15–20 minutes):** separate observations, interpretations, outside evidence, and decisions.
5. **Contribute (10–20 minutes):** improve one label, citation, limitation, test, or explanation and review it with a partner.

## Mixed-skill roles

- **Facilitator:** protects time and participation.
- **Data steward:** checks provenance, permissions, scope, and sensitivity.
- **Analyst:** runs and explains transformations.
- **Skeptic:** tests assumptions and alternative explanations.
- **Documentarian:** records decisions and limitations in plain language.
- **Reviewer:** checks whether another learner can reproduce and interpret the work.

Rotate roles; none is a lesser technical contribution.

## Session map

| Notebook | Core skill | Interpretation focus |
|---|---|---|
| 01 Study area | Boundaries and raster grids | Statistical boundary versus jurisdiction and community-defined lands |
| 02 Vegetation | Classification and temporal summaries | Satellite class versus forage condition observed on the land |
| 03 Soils | Attributes and spatial variation | Why a reservation-wide fallback cannot rank patches |
| 04 Topography | DEM derivatives | Resolution, resampling, slope assumptions, and mobility |
| 05 Water | Distance surfaces | Mapped water versus reliable and accessible water |
| 06 Climate | Scenarios and thresholds | Projection versus forecast; model and threshold uncertainty |
| 07 Synthesis | Weighted models and connected patches | Assumptions, sensitivity, review gates, and decision authority |

## Interpretation protocol

Require every team to distinguish:

1. **Observation:** what the public data and computation show, including unit, date, scale, and missingness.
2. **Interpretation:** a plausible explanation or implication, stated with uncertainty.
3. **Additional evidence:** literature, field observation, local expertise, tenure, infrastructure, or validation needed.
4. **Decision authority:** who is authorized to approve publication, priorities, parameters, or land-management action.

## Governance pause conditions

Stop before adding restricted data, precise sensitive locations, community knowledge, tenure information, or external publication claims. A `.gitignore` entry is not a governance agreement. Follow the locally approved process once it is documented.

## Completion evidence

A learner completes the series by tracing one map result to its source and transformation, explaining one assumption and one limitation, comparing one alternative model setting, identifying required additional evidence and decision authority, and contributing one reviewed improvement.
