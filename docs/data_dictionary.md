# Data dictionary

All fields are generated synthetic cycle-level data. Each record represents one treatment cycle; patient IDs repeat across cycles. Embryo variables are a cycle-level transfer-candidate summary, not embryo-level rows. Outcomes and measurements are simulation-only, not clinical evidence.

| Column | Type | Definition | Notes |
|---|---|---|---|
| synthetic_patient_id | string | Fictional patient-level grouping key; repeated cycles share this ID | Identifier; exclude from model features |
| synthetic_cycle_id | string | Fictional unique cycle key | Identifier; exclude from model features |
| cycle_number | integer | Within-patient cycle sequence | Cycle-level feature |
| patient_age | integer years | Simulated age at cycle | Synthetic only; range 22-45 before intentional issue injection |
| infertility_duration_months | integer months | Simulated duration | Synthetic |
| bmi | float kg/m^2 | Simulated BMI | Synthetic |
| infertility_factor | category | Simulated infertility factor category | Synthetic categories |
| afc | integer | Simulated antral follicle count | Synthetic |
| amh_ng_ml | float ng/mL | Simulated AMH | Synthetic |
| stimulation_protocol | category | Simulated protocol | Synthetic |
| stimulation_days | integer days | Simulated stimulation duration | Synthetic |
| estradiol_pg_ml | float pg/mL | Simulated estradiol measurement | Synthetic; not clinical guidance |
| progesterone_ng_ml | float ng/mL | Simulated progesterone measurement | Synthetic; not clinical guidance |
| total_oocytes | integer | Simulated retrieved oocytes | Cycle-level count |
| mature_oocytes | integer | Simulated mature oocytes | Must not exceed total_oocytes |
| fertilization_count | integer | Simulated fertilized oocytes | Must not exceed mature_oocytes |
| embryos_formed | integer | Simulated embryos | Must not exceed fertilization_count |
| embryo_grade_category | category | Simulated summary grade for transfer candidate | Cycle-level summary, not embryo-level table |
| embryo_developmental_stage | category | Simulated transfer stage | Cycle-level stage |
| day_of_embryo_transfer | integer day | 3 or 5; 0 when no transfer | Synthetic |
| embryos_transferred | integer count | Simulated transferred embryos | Cycle-level count |
| blastocyst_indicator | binary | 1 for simulated Day 5 blastocyst; else 0 | Derived from stage; do not duplicate with stage in causal inference |
| endometrial_thickness_mm | float mm | Simulated measurement | Synthetic |
| clinical_pregnancy_outcome | binary nullable | Simulated primary outcome; 1 positive, 0 negative | Unknown/no-transfer are null; target for exploratory model |
| biochemical_pregnancy_outcome | binary nullable | Simulated secondary outcome | Outcome; exclude from primary clinical-pregnancy features |
| live_birth_outcome | binary nullable | Simulated secondary outcome | Outcome; exclude from primary target features |
| treatment_cycle_cost_inr | float INR | Simulated cycle cost | Not actual prices/costs |
| cycle_date | date | Simulated cycle date, 2022-2025 | Synthetic date; malformed strings intentionally injected in raw |
| synthetic_record_flag | category | Always SYNTHETIC | All generated records are fictional |
