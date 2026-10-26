-- MySQL 8.0 outcome analyses. Descriptive only; synthetic outcomes are not clinical evidence.
USE synthetic_ivf_demo;

-- Outcome rate by cycle-level grade summary (denominator = known outcomes in transfer cycles).
SELECT embryo_grade_category, COUNT(*) AS known_outcomes,
       SUM(clinical_pregnancy_outcome = 1) AS positive,
       ROUND(AVG(clinical_pregnancy_outcome) * 100, 1) AS positive_rate_pct
FROM ivf_cycles_cleaned
WHERE embryos_transferred > 0 AND clinical_pregnancy_outcome IS NOT NULL
GROUP BY embryo_grade_category ORDER BY embryo_grade_category;

-- Age groups are pre-defined for this educational analysis; not clinical cutoffs.
SELECT CASE
         WHEN patient_age <= 34 THEN '≤34'
         WHEN patient_age <= 37 THEN '35-37'
         WHEN patient_age <= 40 THEN '38-40'
         ELSE '41+'
       END AS age_group,
       COUNT(*) AS known_outcomes,
       SUM(clinical_pregnancy_outcome = 1) AS positive,
       ROUND(AVG(clinical_pregnancy_outcome) * 100, 1) AS positive_rate_pct
FROM ivf_cycles_cleaned
WHERE embryos_transferred > 0 AND clinical_pregnancy_outcome IS NOT NULL
GROUP BY age_group ORDER BY MIN(patient_age);

-- Clinical, biochemical, and live-birth simulation counts; unknowns stay NULL.
SELECT
  COUNT(*) AS all_cleaned_cycles,
  SUM(embryos_transferred > 0) AS transfer_cycles,
  COUNT(clinical_pregnancy_outcome) AS known_clinical_outcomes,
  SUM(clinical_pregnancy_outcome = 1) AS clinical_positive,
  SUM(biochemical_pregnancy_outcome = 1) AS biochemical_positive_known,
  SUM(live_birth_outcome = 1) AS live_birth_positive_known
FROM ivf_cycles_cleaned;

-- Raw versus cleaned data: import raw file to ivf_cycles_raw using the raw schema
-- in docs/data_dictionary.md, then compare. Raw intentionally contains duplicate
-- cycle rows, malformed dates, and range/logical issues for practice.
SELECT 'raw' AS dataset, COUNT(*) AS rows FROM ivf_cycles_raw
UNION ALL
SELECT 'cleaned' AS dataset, COUNT(*) AS rows FROM ivf_cycles_cleaned;

SELECT COUNT(*) AS duplicate_raw_cycle_records
FROM (
  SELECT synthetic_cycle_id FROM ivf_cycles_raw
  GROUP BY synthetic_cycle_id HAVING COUNT(*) > 1
) AS repeated_cycles;
