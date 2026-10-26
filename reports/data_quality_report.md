# Data quality report

## Scope
This audit covers the generated synthetic cycle-level CSVs. All rows and identifiers are fictional. The generator seed is `20260618`; raw data intentionally contain issues for cleaning practice.

## Before and after

| Check | Raw | Cleaned | Treatment |
|---|---:|---:|---|
| Rows | 3,005 | 2,998 | Remove 5 exact duplicate rows; remove 2 cycles with malformed/unusable cycle dates |
| Columns | 29 | 30 | Add `cycle_month` derived from valid `cycle_date` |
| Exact duplicates | 5 | 0 | Keep first exact record; duplicate row is generated intentionally |
| Missing cells | 375 (0.43%) | 380 (0.42%) | Missing values retained; additional nulls document invalid ranges/logical counts |
| Malformed dates | 2 after deduplication | 0 | Drop two rows with unparseable cycle date; date range retained 2022-01-01 to 2025-12-30 |
| Patients | — | 2,100 | Fictional IDs; repeated cycles remain linked |
| Unique cycle IDs | — | 2,998 | One cleaned row per cycle |
| Transfer cycles | — | 2,910 | No-transfer cycles have outcome fields null |
| Known clinical target | — | 2,876 | 34 transfer-cycle outcomes remain unknown/null |

Raw missing cells include 122 clinical outcome nulls (88 non-transfer cycles plus 34 unknown transfer outcomes), 88 nulls each for biochemical/live-birth outcomes in non-transfer cycles, and intentionally missing measurement/cost cells. Raw missingness percentages are exported in `outputs/raw_quality_profile.csv`; cleaned percentages are in `outputs/cleaned_quality_profile.csv`.

## Invalid values and normalization

- Two age values (15 and 61) fall outside the cleaning bounds 18–50 and are set to missing; cycles are retained.
- Two BMI values (-2 and 75) fall outside bounds 12–60 and are set to missing; cycles are retained.
- One mature-oocyte count exceeds its total-oocyte count; the impossible child count is set to missing, not clipped.
- Two unparseable cycle dates are excluded because a valid cycle timestamp is required for temporal analysis.
- Category strings are trimmed, whitespace normalized, and canonical capitalization applied for protocol, grade and stage. The generator's spaces/case examples map to expected categories.
- Missing outcome values are not imputed for descriptive outcome rates or ML targets. Transfer cycles with unknown clinical outcome are excluded from the supervised target set; no-transfer cycles are structurally ineligible.
- IQR fences are calculated and exported to `outputs/iqr_outlier_screen.csv`. **IQR-flagged values are retained**; a statistical flag is not evidence of an error.

Raw and cleaned per-column dtypes, missing counts/percentages and unique counts are machine-readable in the two profile CSVs. Counts are from executed generation/cleaning code.
