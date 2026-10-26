# Executive summary — synthetic IVF analytics demonstration

## Purpose and caution
This portfolio demonstrates a reproducible healthcare-style analytics workflow on **entirely synthetic, seeded data**. It contains no real patient or clinic records. The generated outcomes, clinical measurements, costs and observed patterns are not representative clinical probabilities, not validated predictors, and must never be used to guide treatment or counselling.

## Dataset and quality
The generator created 3,000 synthetic cycles (2,100 fictional patient IDs, with some repeated cycles). Five intentional duplicate rows and two malformed cycle dates resulted in 3,005 raw CSV rows; after exact deduplication and exclusion of the two invalid-date rows, 2,998 cleaned cycle records remained. There are 2,910 transfer cycles and 2,876 known clinical-pregnancy outcomes; 34 transfer-cycle outcomes are unknown and retained as null.

## Descriptive results from the fixed seed
Among known outcomes for transfer cycles, 1,364 were simulated positive, a **47.4% simulated proportion**. Simulated positive proportions were 56.4% for grade A (n=876), 46.2% for grade B (n=1,404), and 37.2% for grade C (n=596). By synthetic age bin, rates were 53.2% for ≤34 (n=1,726), 39.9% for 35–37 (n=619), 38.9% for 38–40 (n=352), and 33.9% for 41+ (n=177). Day 5-stage rate was 50.2% (n=1,775) vs Day 3 43.0% (n=1,101). Mean synthetic cycle cost was ₹179,660; median ₹180,008.

Spearman association of age with simulated binary outcome was ρ = −0.153 (p≈1.65×10⁻¹⁶); AMH association was ρ = 0.096 (p≈2.37×10⁻⁷). Grade/outcome chi-square was χ²(2)=53.92, p≈1.96×10⁻¹², Cramér's V=0.137. These findings are artifacts of a programmed probability process; p-values do not confer clinical validity. Cost distributions by outcome did not show a detectable difference in this draw (Mann–Whitney p≈0.559).

## Exploratory models
A patient-grouped 80/20 holdout (zero patient overlap) compared a majority-prior Dummy baseline, Logistic Regression and Random Forest. Held-out ROC-AUCs were 0.500, 0.641 and 0.612 respectively; F1 values were 0.000, 0.589 and 0.588. These metrics measure how models recover the synthetic generator only. They are not healthcare model performance or clinical accuracy.

## Recommended next steps
Treat this as a technical demonstration only. For any future real-data work, obtain approved de-identified data and governance review, define outcome and follow-up carefully, prespecify analysis, validate externally, evaluate calibration/fairness, and involve qualified clinical experts. No treatment, patient-selection, savings, or success-rate recommendation is made.
