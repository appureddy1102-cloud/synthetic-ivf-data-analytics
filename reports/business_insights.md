# Business and analytical insights — synthetic-only

## Boundary statement
Every number below comes from the executed seed-20260618 synthetic generator. It is a software demonstration, not evidence about IVF patients or any clinic. No clinical recommendation or real-world success estimate is made. “Outcome rate” means a simulated positive proportion among transfers with known simulated clinical-pregnancy outcomes only.

## EDA chart questions and observed results

| Chart | Question | Observed pattern in this generated sample | Potential analytical relevance (not clinical advice) |
|---|---|---|---|
| Patient age distribution | What ages did the generator produce? | Mean 33.50, median 33, SD 4.47, range 22–45; near-symmetric skew 0.02 | Verify age-range and age-bin denominators in future descriptive dashboards |
| Embryo grade distribution | How are transfer candidate grades distributed? | Among known transfer outcomes: A n=876, B n=1,404, C n=596 | Demonstrates category counts and outcome denominator reporting |
| Clinical outcome distribution | How many positive/negative labels are known? | 1,364 positive of 2,876 known transfer outcomes (47.4%); 34 transfer outcomes unknown | Keep unknown outcomes separate; show count and denominator |
| Grade vs simulated outcome | Do outcome proportions differ by grade? | A 56.4%, B 46.2%, C 37.2%; chi-square p≈1.96e-12, Cramér's V=0.137 | Shows a generated association; small effect size and synthetic mechanism require caution |
| Age group vs outcome | How do generated proportions vary by age bin? | ≤34: 53.2%; 35–37: 39.9%; 38–40: 38.9%; 41+: 33.9% | Demonstrates binning and denominators only; bins are not clinical cutoffs |
| AMH distribution | Is the simulated AMH distribution symmetric? | Mean 3.47, median 2.99 ng/mL, skew 1.53 | Log-normal simulation produces right skew; compare robust summaries |
| Total oocytes distribution | What is the count distribution? | Mean 10.33, median 10, SD 4.22; range 0–26 | Demonstrates count summaries and frequency charts |
| Stage vs outcome | How do simulated stage proportions compare? | Day 3 43.0% (n=1,101); Day 5 50.2% (n=1,775) | Stage association is generated; not evidence of treatment efficacy |
| Monthly cycle trend | Does generated volume vary by month? | Cycle volume varies across 48 months due to random cycle dates | Trend charts require volume and denominator context |
| Treatment cost distribution | What is simulated cost spread? | Mean ₹179,660; median ₹180,008; range ₹94,389–₹276,246 | INR values are arbitrary simulation inputs, not cost guidance |
| Spearman heatmap | Which numeric variables show monotonic association? | Age vs outcome ρ=−0.153; AMH vs outcome ρ=0.096 | Correlation summarizes generated association; not causation |
| Missingness visualization | Where are raw nulls concentrated? | Outcome nulls include structural no-transfer rows and 34 unknown transfer outcomes; selected measurements/cost are also missing | Distinguish structural ineligibility from unknown follow-up |

## Additional executed statistical checks

- Grade/outcome independence test: χ²(2)=53.92, p≈1.96×10⁻¹², Cramér's V=0.137.
- Age/outcome Spearman: ρ=−0.153, p≈1.65×10⁻¹⁶.
- AMH/outcome Spearman: ρ=0.096, p≈2.37×10⁻⁷.
- Cost by outcome Mann–Whitney U: p≈0.559; cost distributions are not detectably different in this draw.

The generator directly includes modest age, AMH, grade, stage and other terms in its outcome probability function. Statistical significance here largely reflects that programmed structure and sample size. It is not a clinical discovery.

## Exploratory ML comparison

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| Dummy prior baseline | 0.527 | 0.000 | 0.000 | 0.000 | 0.500 |
| Logistic Regression | 0.598 | 0.570 | 0.609 | 0.589 | 0.641 |
| Random Forest | 0.603 | 0.577 | 0.599 | 0.588 | 0.612 |

The holdout split grouped by synthetic patient, with zero patient overlap. Models exclude identifiers and all secondary outcomes; blastocyst indicator is excluded as redundant with stage. These metrics only show recoverability of the simulated process in one holdout. They are not suitable for clinical interpretation.

## Recommendations for further analysis

1. **Maintain denominator and missing-outcome reporting.** Separate no-transfer cycles, known outcomes and unknown follow-up; test sensitivity to the missingness mechanism.
2. **Validate the simulation before using it as a teaching benchmark.** Add generator unit tests for biological/process bounds, probability calibration checks against the intended synthetic assumptions, and scenario comparisons across seeds.
3. **For any real-data project, stop before clinical recommendations.** Obtain ethics/privacy approvals and de-identified data; prespecify endpoints and follow-up; use patient-level external validation, calibration and fairness review with qualified clinical oversight.

No savings, clinical benefits, treatment choices, or performance improvements are inferred.
