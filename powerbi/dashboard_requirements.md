# Power BI dashboard implementation guide (PBIX not generated)

A `.pbix` cannot be authored or validated in this environment. The CSVs, model definitions and DAX below are ready for manual implementation in Power BI Desktop. Do not represent a PBIX or screenshot as completed until saved and reviewed in Power BI.

## Import and model

1. In Power BI Desktop, **Get data → Text/CSV** and load `data/synthetic_ivf_cleaned.csv` as `IVF Cycles`.
2. Set `cycle_date` and `cycle_month` to Date; costs to Decimal/Currency (INR); outcome and indicator fields to Whole Number; measurements to Decimal Number; IDs and categories to Text.
3. Create a calendar table and mark it as the date table. Relate `Calendar[Date]` (1) → `IVF Cycles[cycle_date]` (*) active.
4. Optional star-schema dimensions: `Patient` with distinct synthetic patient IDs, `Grade`, `Stage`, `Protocol`, `Infertility Factor`, and `Calendar`. Use one-to-many, single-direction relationships to the cycle fact. The cleaned table is one row per cycle; it is not an embryo table.
5. Keep the synthetic-data warning in a visible card on every report page.

### Suggested DAX measures

```DAX
Synthetic Cycles = DISTINCTCOUNT('IVF Cycles'[synthetic_cycle_id])
Synthetic Patients = DISTINCTCOUNT('IVF Cycles'[synthetic_patient_id])
Transfer Cycles =
CALCULATE([Synthetic Cycles], 'IVF Cycles'[embryos_transferred] > 0)
Known Clinical Outcomes =
CALCULATE(COUNT('IVF Cycles'[clinical_pregnancy_outcome]),
          'IVF Cycles'[embryos_transferred] > 0)
Clinical Positive Outcomes =
CALCULATE(COUNT('IVF Cycles'[clinical_pregnancy_outcome]),
          'IVF Cycles'[clinical_pregnancy_outcome] = 1,
          'IVF Cycles'[embryos_transferred] > 0)
Simulated Clinical Pregnancy Rate =
DIVIDE([Clinical Positive Outcomes], [Known Clinical Outcomes])
Average Synthetic Cycle Cost (INR) =
AVERAGE('IVF Cycles'[treatment_cycle_cost_inr])
Mean Age = AVERAGE('IVF Cycles'[patient_age])
Clinical Outcome Unknown Among Transfers =
CALCULATE([Transfer Cycles], ISBLANK('IVF Cycles'[clinical_pregnancy_outcome]))
```

`COUNT` ignores blank outcome values. Always show the known-outcome denominator beside a rate. Do not call the measure a real IVF success rate.

## Page layouts

### Page 1 — Executive overview
- Cards: synthetic cycles, synthetic patients, transfer cycles, known simulated clinical outcome rate, mean synthetic cycle cost.
- Monthly combo line/column: cycle count and simulated positive rate; exclude months with no known outcomes from rate plot.
- Funnel/small bars: generated cycle-stage counts; never imply clinical process outcomes.

### Page 2 — Embryo cycle summaries
- Grade count; simulated positive proportion by grade with known outcome denominator in tooltip.
- Stage comparison; blastocyst indicator comparison.
- Slicers for date, protocol, age band and factor. Grade/stage refer to a cycle-level transfer-candidate summary, not each embryo.

### Page 3 — Patient and treatment characteristics
- Age-group outcome rates; AMH/AFC and total oocytes distributions; protocol and stimulation duration summaries.
- Include cycle number as a repeated-cycle descriptor; don't treat repeated cycles as independent patients.

### Page 4 — Cost and data quality
- Cost distribution and mean/median by protocol/factor and month.
- Cards for raw/clean row counts and missing target/feature values; raw-to-clean comparison if both tables are loaded.
- IQR flags are screening markers only; valid values are not excluded automatically.

## Design and QA

Use a restrained navy/teal palette, high contrast, readable fonts, meaningful titles and units, consistent page navigation, and visible filter selections. Add date range, age group, grade, stage, protocol and infertility-factor slicers. Validate DAX outputs against `outputs/analysis_summary.json` and known denominators. Label all KPIs and chart titles **SIMULATED**. Do not publish patient-facing advice. Save as `powerbi/Synthetic_IVF_Analytics.pbix` only after actual manual construction and validation; capture screenshots directly from that genuine saved report, otherwise leave the screenshot folder empty.
