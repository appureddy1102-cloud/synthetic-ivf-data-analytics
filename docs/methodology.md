# Methodology and reproducibility

## Data grain and simulation
One row represents a synthetic treatment cycle. A fictional patient may have one or two cycles; `synthetic_patient_id` groups repeated cycles, and `synthetic_cycle_id` identifies one cycle. Embryo features are cycle-level summaries for a transferred candidate, not one record per embryo. Every identifier and measurement is generated with NumPy seed `20260618`; there are no real patient records.

Clinical pregnancy is simulated for transfer cycles as Bernoulli(p), where p = 1/(1+exp(−η)) and η = −0.34 − 0.052×(age−33) + 0.17×(AMH−3)/2 + 0.025×(endometrial thickness−9) + grade effect + 0.26×blastocyst indicator + protocol effect + 0.06×I(two embryos transferred). Grade effects are A=+0.34, B=0, C=−0.39; protocol effects are Antagonist=+0.08, long agonist=+0.02, mild stimulation=−0.04, Flare=−0.08. This is an arbitrary pedagogical formula, not estimated from patients and not clinically validated. Non-transfer cycles have null outcomes. For transferred cycles, biochemical pregnancy is drawn with probability 0.87 conditional on simulated clinical-positive, otherwise 0.13; live birth is drawn with probability 0.68 conditional on clinical-positive, otherwise 0.015. A random 1.2% of transfer outcome follow-ups are set to unknown/null. Costs are generated as ₹65,000 + ₹7,800×stimulation days + ₹2,100×oocytes + ₹12,000×embryos transferred + Normal(0, ₹18,000), clipped to ₹60,000–₹350,000. Full measurement-generation assumptions reside in `src/generate_data.py`.

## Pipeline

1. `python -m src.generate_data --n-cycles 3000 --seed 20260618` writes a raw cycle-level CSV and dictionary.
2. `src.data_quality.clean_data` profiles raw columns, removes exact duplicate records, parses cycle dates, removes the two malformed-date rows, normalizes categories, converts numeric fields, sets impossible age/BMI/count values to null, preserves outcome unknowns, and adds a month field.
3. IQR fences are calculated for continuous/count features. IQR-flagged records are **retained**; flags prompt review, not deletion.
4. `src.analysis.run_eda` creates descriptive statistics, known-transfer outcome rates, category tables, nonparametric/categorical association checks and 13 charts.
5. `src.modeling.run_models` excludes cycles without transfer or with unknown target; removes identifiers and all secondary outcomes from features; uses a patient-group holdout; trains a Dummy prior baseline, Logistic Regression and Random Forest with imputation, one-hot encoding and numeric scaling where appropriate.

## Known outcome denominator
Clinical pregnancy rates use only transfer cycles with observed (non-null) clinical-pregnancy outcome. Cycles without transfer and cycles with unknown follow-up remain null, never negative. Report each denominator alongside the rate.

## Statistical methods
Descriptive distributions include mean, median, mode, variance, standard deviation, min/max, quartiles, skew and kurtosis. Spearman rank correlations are exploratory. Grade/outcome association uses a chi-square test and Cramér's V; cost comparison uses Mann–Whitney U. Results are simulation-specific and do not establish causality or clinical significance.

## Model validation
The holdout is split by synthetic patient using `GroupShuffleSplit`, so cycles from a patient cannot occur in both train and test. Identifiers and target-derived secondary outcomes are excluded. Metrics characterize only the synthetic generator and must not be presented as real-world clinical performance.

## Re-run
Run from project root, in order:

```bash
python -m src.generate_data --n-cycles 3000 --seed 20260618
python -m src.analysis
python -m src.modeling
```

Then execute notebooks `01` through `05`. See `outputs/` and `visuals/` for generated artifacts.
