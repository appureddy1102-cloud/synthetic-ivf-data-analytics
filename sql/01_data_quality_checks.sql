-- MySQL 8.0: load CSV tables using the documented CREATE TABLE definitions below.
-- For beginner setup, import synthetic_ivf_raw.csv and synthetic_ivf_cleaned.csv
-- with MySQL Workbench's Table Data Import Wizard, or use LOAD DATA LOCAL INFILE.

CREATE DATABASE IF NOT EXISTS synthetic_ivf_demo;
USE synthetic_ivf_demo;

CREATE TABLE IF NOT EXISTS ivf_cycles_cleaned (
  synthetic_patient_id VARCHAR(20) NOT NULL,
  cycle_date DATE,
  cycle_number TINYINT UNSIGNED,
  synthetic_cycle_id VARCHAR(20) NOT NULL,
  patient_age TINYINT UNSIGNED,
  infertility_duration_months SMALLINT UNSIGNED,
  bmi DECIMAL(5,1),
  infertility_factor VARCHAR(40),
  afc SMALLINT UNSIGNED,
  amh_ng_ml DECIMAL(5,2),
  stimulation_protocol VARCHAR(40),
  stimulation_days TINYINT UNSIGNED,
  estradiol_pg_ml DECIMAL(9,1),
  progesterone_ng_ml DECIMAL(6,2),
  total_oocytes SMALLINT UNSIGNED,
  mature_oocytes SMALLINT UNSIGNED,
  fertilization_count SMALLINT UNSIGNED,
  embryos_formed SMALLINT UNSIGNED,
  embryo_grade_category VARCHAR(20),
  embryo_developmental_stage VARCHAR(30),
  day_of_embryo_transfer TINYINT UNSIGNED,
  embryos_transferred TINYINT UNSIGNED,
  blastocyst_indicator TINYINT,
  endometrial_thickness_mm DECIMAL(5,1),
  clinical_pregnancy_outcome TINYINT,
  biochemical_pregnancy_outcome TINYINT,
  live_birth_outcome TINYINT,
  treatment_cycle_cost_inr DECIMAL(12,2),
  synthetic_record_flag VARCHAR(20),
  cycle_month DATE,
  PRIMARY KEY (synthetic_cycle_id),
  INDEX idx_patient (synthetic_patient_id),
  INDEX idx_cycle_date (cycle_date),
  CHECK (clinical_pregnancy_outcome IS NULL OR clinical_pregnancy_outcome IN (0,1)),
  CHECK (biochemical_pregnancy_outcome IS NULL OR biochemical_pregnancy_outcome IN (0,1)),
  CHECK (live_birth_outcome IS NULL OR live_birth_outcome IN (0,1)),
  CHECK (bmi IS NULL OR bmi BETWEEN 12 AND 60),
  CHECK (treatment_cycle_cost_inr IS NULL OR treatment_cycle_cost_inr >= 0)
);

-- Raw table intentionally allows duplicates, malformed dates, and NULL quality issues.
-- Use the data import wizard with this column order; cycle_date is text so bad date
-- strings remain inspectable before Python cleaning.
CREATE TABLE IF NOT EXISTS ivf_cycles_raw (
  synthetic_patient_id VARCHAR(20), cycle_date VARCHAR(30), cycle_number DECIMAL(10,2),
  synthetic_cycle_id VARCHAR(20), patient_age DECIMAL(10,2), infertility_duration_months DECIMAL(10,2),
  bmi DECIMAL(8,2), infertility_factor VARCHAR(60), afc DECIMAL(10,2), amh_ng_ml DECIMAL(10,3),
  stimulation_protocol VARCHAR(60), stimulation_days DECIMAL(10,2), estradiol_pg_ml DECIMAL(12,2),
  progesterone_ng_ml DECIMAL(10,3), total_oocytes DECIMAL(10,2), mature_oocytes DECIMAL(10,2),
  fertilization_count DECIMAL(10,2), embryos_formed DECIMAL(10,2), embryo_grade_category VARCHAR(40),
  embryo_developmental_stage VARCHAR(60), day_of_embryo_transfer DECIMAL(10,2), embryos_transferred DECIMAL(10,2),
  blastocyst_indicator DECIMAL(10,2), endometrial_thickness_mm DECIMAL(10,2),
  clinical_pregnancy_outcome DECIMAL(10,2), biochemical_pregnancy_outcome DECIMAL(10,2),
  live_birth_outcome DECIMAL(10,2), treatment_cycle_cost_inr DECIMAL(14,2),
  synthetic_record_flag VARCHAR(30)
);

-- Counts, schema, and unique cycle IDs.
SELECT COUNT(*) AS cleaned_rows, COUNT(DISTINCT synthetic_cycle_id) AS unique_cycles,
       COUNT(DISTINCT synthetic_patient_id) AS synthetic_patients
FROM ivf_cycles_cleaned;

-- SQL NULL profile for key fields.
SELECT
  SUM(patient_age IS NULL) AS missing_age,
  SUM(amh_ng_ml IS NULL) AS missing_amh,
  SUM(clinical_pregnancy_outcome IS NULL) AS missing_or_ineligible_clinical_outcome,
  SUM(treatment_cycle_cost_inr IS NULL) AS missing_cycle_cost
FROM ivf_cycles_cleaned;

-- Duplicate cycle IDs (should return zero rows after primary key enforcement).
SELECT synthetic_cycle_id, COUNT(*) AS n
FROM ivf_cycles_cleaned
GROUP BY synthetic_cycle_id
HAVING COUNT(*) > 1;

-- Impossible count/range checks: investigate rather than silently delete valid records.
SELECT COUNT(*) AS invalid_age FROM ivf_cycles_cleaned WHERE patient_age NOT BETWEEN 18 AND 50;
SELECT COUNT(*) AS impossible_mature_count FROM ivf_cycles_cleaned
WHERE mature_oocytes > total_oocytes;
SELECT COUNT(*) AS impossible_fertilization_count FROM ivf_cycles_cleaned
WHERE fertilization_count > mature_oocytes;
SELECT COUNT(*) AS impossible_embryo_count FROM ivf_cycles_cleaned
WHERE embryos_formed > fertilization_count;

-- Synthetic flag check.
SELECT synthetic_record_flag, COUNT(*) AS records
FROM ivf_cycles_cleaned GROUP BY synthetic_record_flag;
