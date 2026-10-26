# Limitations, synthetic-data notice, and ethics

- All records, IDs, measurements, costs, and outcomes are fabricated by a seeded generator. There is no clinical data source and no connection to real patients or clinics.
- Outcome probabilities are arbitrary educational assumptions, not clinically calibrated rates. Model results quantify recovery of the generator's patterns on simulated data only.
- This project is not a diagnostic, prognostic, treatment-selection, triage, or patient-counselling tool. It must not be used for clinical decisions.
- Cycle-level summaries cannot represent embryo-level variation. A cycle may contain multiple embryos; this design deliberately has one row per cycle and a summary grade/stage for transfer candidate.
- Repeated cycles per synthetic patient create dependence. Group-based train/test split is used, but one random holdout is not robust external validation.
- Missing outcomes can reflect no transfer or unknown follow-up. The project keeps them null and limits outcome analyses to known outcomes among transfer cycles.
- Simulated values omit many real-world confounders, laboratory factors, treatment decisions, patient preferences, socioeconomic and clinical context, and follow-up definitions.
- Statistical significance and feature importance do not imply causation, clinical importance, or actionable effect.
- Synthetic INR cost is not a quote, cost estimate, health-economic evaluation, or savings claim.
- Age-group bands are analytic bins for this synthetic demonstration, not clinical cutoffs.
- Data is intentionally not described as realistic clinical ground truth. All publication, resume and dashboard wording must preserve the synthetic qualifier.

Responsible use: keep the synthetic disclaimer visible; do not combine these records with real patient data; do not make clinical recommendations; document seeds and generator changes; and seek qualified clinical, privacy, ethics, and regulatory review before any real healthcare analytics project.
