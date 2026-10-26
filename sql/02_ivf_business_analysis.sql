-- MySQL 8.0 business analysis examples. Outcomes are synthetic and not clinical evidence.
USE synthetic_ivf_demo;

-- Overall demo KPIs. NULL outcomes are not counted as negative.
SELECT COUNT(DISTINCT synthetic_cycle_id) AS cycles,
       COUNT(DISTINCT synthetic_patient_id) AS fictional_patients,
       SUM(treatment_cycle_cost_inr) AS total_observed_cost_inr,
       AVG(treatment_cycle_cost_inr) AS average_observed_cycle_cost_inr,
       SUM(embryos_transferred > 0) AS transfer_cycles,
       SUM(clinical_pregnancy_outcome IS NOT NULL) AS known_transfer_outcomes,
       AVG(clinical_pregnancy_outcome) AS clinical_positive_rate_known_outcomes
FROM ivf_cycles_cleaned;

-- Cycle costs and transfer counts by simulation protocol.
SELECT stimulation_protocol, COUNT(*) AS cycles,
       ROUND(AVG(treatment_cycle_cost_inr), 2) AS mean_cost_inr,
       ROUND(AVG(embryos_transferred), 2) AS mean_embryos_transferred
FROM ivf_cycles_cleaned
GROUP BY stimulation_protocol ORDER BY cycles DESC;

-- Monthly treatment volume and known clinical outcomes.
SELECT cycle_month, COUNT(*) AS cycles,
       SUM(embryos_transferred > 0) AS transfers,
       COUNT(clinical_pregnancy_outcome) AS known_outcomes,
       SUM(clinical_pregnancy_outcome = 1) AS simulated_positive_outcomes,
       ROUND(AVG(clinical_pregnancy_outcome) * 100, 1) AS known_outcome_positive_pct
FROM ivf_cycles_cleaned
GROUP BY cycle_month ORDER BY cycle_month;

-- Cost summary by synthetic infertility-factor category.
SELECT infertility_factor, COUNT(*) AS cycles,
       ROUND(AVG(treatment_cycle_cost_inr), 2) AS mean_cost_inr,
       ROUND(MIN(treatment_cycle_cost_inr), 2) AS min_cost_inr,
       ROUND(MAX(treatment_cycle_cost_inr), 2) AS max_cost_inr
FROM ivf_cycles_cleaned
GROUP BY infertility_factor ORDER BY mean_cost_inr DESC;

-- Cycle volume and outcome rate by developmental stage.
SELECT embryo_developmental_stage, COUNT(*) AS known_outcomes,
       SUM(clinical_pregnancy_outcome = 1) AS positives,
       ROUND(AVG(clinical_pregnancy_outcome) * 100, 1) AS simulated_positive_rate_pct
FROM ivf_cycles_cleaned
WHERE embryos_transferred > 0 AND clinical_pregnancy_outcome IS NOT NULL
GROUP BY embryo_developmental_stage;
