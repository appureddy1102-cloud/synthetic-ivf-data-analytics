"""Generate a fully synthetic, cycle-level IVF education dataset.

No real clinical records are used. All outcome probabilities are pedagogical
simulation assumptions and are NOT clinically validated.
"""
from pathlib import Path
import argparse
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
SEED = 20260618


def _sigmoid(z):
    return 1 / (1 + np.exp(-z))


def generate(n_cycles=3000, seed=SEED, output_dir=DATA_DIR, inject_issues=True):
    if n_cycles < 100:
        raise ValueError("Use at least 100 synthetic cycles for a useful demo")
    rng = np.random.default_rng(seed)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Allocate 1 or 2 cycles per fictional patient: 30% repeated-cycle patients.
    n_repeat = int(n_cycles * 0.30)
    n_single = n_cycles - 2 * n_repeat
    patients = [f"SYN-P-{i:05d}" for i in range(1, n_repeat + n_single + 1)]
    patient_ids = patients[:n_repeat] * 2 + patients[n_repeat:]
    rng.shuffle(patient_ids)
    dates = pd.to_datetime(rng.integers(pd.Timestamp("2022-01-01").value // 10**9,
                                       pd.Timestamp("2025-12-31").value // 10**9,
                                       size=n_cycles), unit="s").normalize()
    frame = pd.DataFrame({"synthetic_patient_id": patient_ids, "cycle_date": dates})
    frame = frame.sort_values(["synthetic_patient_id", "cycle_date"], kind="stable").reset_index(drop=True)
    frame["cycle_number"] = frame.groupby("synthetic_patient_id").cumcount() + 1
    frame["synthetic_cycle_id"] = [f"SYN-C-{i:06d}" for i in range(1, n_cycles + 1)]

    age = np.clip(np.rint(rng.normal(33.5, 4.4, n_cycles)), 22, 45).astype(int)
    duration = np.clip(np.rint(rng.gamma(2.2, 14, n_cycles)), 1, 120).astype(int)
    bmi = np.clip(rng.normal(25.4, 4.1, n_cycles), 17, 39).round(1)
    factor = rng.choice(["Female factor", "Male factor", "Combined", "Unexplained", "Tubal"], n_cycles,
                        p=[.28, .24, .20, .17, .11])
    afc = np.clip(np.rint(rng.normal(16 - .18 * (age - 32), 5.0, n_cycles)), 2, 38).astype(int)
    amh = np.clip(rng.lognormal(np.log(3.1) - .025 * (age - 32), .52, n_cycles), .15, 12).round(2)
    protocol = rng.choice(["Antagonist", "Long agonist", "Mild stimulation", "Flare"], n_cycles,
                          p=[.53, .25, .14, .08])
    days_stim = np.clip(np.rint(rng.normal(10.2, 1.7, n_cycles)), 6, 16).astype(int)
    estradiol = np.clip(450 + afc * rng.normal(115, 20, n_cycles) + rng.normal(0, 650, n_cycles), 250, 8500).round(0)
    progesterone = np.clip(rng.lognormal(np.log(.8), .48, n_cycles), .15, 4.2).round(2)
    total_oocytes = np.clip(np.rint(afc * rng.uniform(.48, .83, n_cycles) + rng.normal(0, 2, n_cycles)), 0, 35).astype(int)
    mature = np.array([rng.binomial(int(x), .77) for x in total_oocytes])
    fertilized = np.array([rng.binomial(int(x), .72) for x in mature])
    formed = np.array([rng.binomial(int(x), .78) for x in fertilized])
    grades = np.where(formed == 0, "No transfer", rng.choice(["A", "B", "C"], n_cycles, p=[.31, .48, .21]))
    stage = np.where(formed == 0, "Not applicable", rng.choice(["Day 3", "Day 5 blastocyst"], n_cycles, p=[.38, .62]))
    transferred = np.where(formed == 0, 0, rng.choice([1, 2], n_cycles, p=[.83, .17])).astype(int)
    transferred = np.minimum(transferred, formed)
    day_transfer = np.where(formed == 0, 0, np.where(stage == "Day 3", 3, 5)).astype(int)
    blastocyst = (stage == "Day 5 blastocyst").astype(int)
    endometrial = np.clip(rng.normal(9.1, 1.7, n_cycles), 4.2, 16).round(1)

    # Transparent probabilistic, non-clinical outcome simulation.
    grade_effect = pd.Series(grades).map({"A": .34, "B": 0.0, "C": -.39, "No transfer": 0.0}).to_numpy()
    protocol_effect = pd.Series(protocol).map({"Antagonist": .08, "Long agonist": .02, "Mild stimulation": -.04, "Flare": -.08}).to_numpy()
    eta = (-.34 - .052 * (age - 33) + .17 * (amh - 3) / 2 + .025 * (endometrial - 9)
           + grade_effect + .26 * blastocyst + protocol_effect + .06 * (transferred == 2))
    probability = _sigmoid(eta)
    clinical = np.where(formed > 0, rng.binomial(1, probability), np.nan).astype(float)
    biochemical = np.where(formed > 0,
                           np.array([rng.binomial(1, .87 if y == 1 else .13) for y in np.nan_to_num(clinical, nan=0)]),
                           np.nan).astype(float)
    live_birth = np.where(formed > 0,
                          np.array([rng.binomial(1, .68 if y == 1 else .015) for y in np.nan_to_num(clinical, nan=0)]),
                          np.nan).astype(float)
    # Cost is synthetic INR, generated from procedure components and random variation.
    cost = (65000 + days_stim * 7800 + total_oocytes * 2100 + transferred * 12000
            + rng.normal(0, 18000, n_cycles)).clip(60000, 350000).round(0)

    data = frame.assign(
        patient_age=age, infertility_duration_months=duration, bmi=bmi, infertility_factor=factor,
        afc=afc, amh_ng_ml=amh, stimulation_protocol=protocol, stimulation_days=days_stim,
        estradiol_pg_ml=estradiol, progesterone_ng_ml=progesterone, total_oocytes=total_oocytes,
        mature_oocytes=mature, fertilization_count=fertilized, embryos_formed=formed,
        embryo_grade_category=grades, embryo_developmental_stage=stage,
        day_of_embryo_transfer=day_transfer, embryos_transferred=transferred,
        blastocyst_indicator=blastocyst, endometrial_thickness_mm=endometrial,
        clinical_pregnancy_outcome=clinical, biochemical_pregnancy_outcome=biochemical,
        live_birth_outcome=live_birth, treatment_cycle_cost_inr=cost,
        synthetic_record_flag="SYNTHETIC"
    )
    raw = data.copy()
    # String representation permits a couple of intentional malformed-date examples.
    raw["cycle_date"] = pd.to_datetime(raw["cycle_date"]).dt.strftime("%Y-%m-%d")
    if inject_issues:
        # Configurable, documented quality examples (not clinical outliers).
        for col, ix in [("amh_ng_ml", [14, 61, 122]), ("progesterone_ng_ml", [23, 79]),
                        ("endometrial_thickness_mm", [44, 180]),
                        ("treatment_cycle_cost_inr", [70, 210])]:
            raw.loc[ix, col] = np.nan
        raw.loc[11, "patient_age"] = 15             # invalid age
        raw.loc[35, "patient_age"] = 61             # invalid age
        raw.loc[54, "bmi"] = -2                     # invalid BMI
        raw.loc[83, "bmi"] = 75                     # invalid BMI
        raw.loc[102, "mature_oocytes"] = raw.loc[102, "total_oocytes"] + 3  # impossible count relation
        raw.loc[19, "stimulation_protocol"] = " antagonist "
        raw.loc[29, "stimulation_protocol"] = "LONG AGONIST"
        raw.loc[47, "embryo_grade_category"] = str(raw.loc[47, "embryo_grade_category"]).lower() + " "
        raw.loc[5, "cycle_date"] = "not-a-date"
        raw.loc[9, "cycle_date"] = "2024-99-99"
        # Unknown outcomes only for cycles that had a transfer.
        eligible = raw.index[raw.embryos_transferred.gt(0)].to_numpy()
        unknown_idx = rng.choice(eligible, size=max(1, int(.012 * len(eligible))), replace=False)
        raw.loc[unknown_idx, ["clinical_pregnancy_outcome", "biochemical_pregnancy_outcome", "live_birth_outcome"]] = np.nan
        duplicate_indices = rng.choice(np.arange(n_cycles), size=5, replace=False)
        raw = pd.concat([raw, raw.loc[duplicate_indices]], ignore_index=True)
    raw.to_csv(output_dir / "synthetic_ivf_raw.csv", index=False)
    return raw


def write_data_dictionary(path=DATA_DIR / "synthetic_ivf_data_dictionary.csv"):
    rows = [
        ("synthetic_patient_id", "string", "Fictional patient-level grouping key; repeated cycles share this ID", "Identifier; exclude from model features"),
        ("synthetic_cycle_id", "string", "Fictional unique cycle key", "Identifier; exclude from model features"),
        ("cycle_number", "integer", "Within-patient cycle sequence", "Cycle-level feature"),
        ("patient_age", "integer years", "Simulated age at cycle", "Synthetic only; range 22-45 before intentional issue injection"),
        ("infertility_duration_months", "integer months", "Simulated duration", "Synthetic"), ("bmi", "float kg/m^2", "Simulated BMI", "Synthetic"),
        ("infertility_factor", "category", "Simulated infertility factor category", "Synthetic categories"),
        ("afc", "integer", "Simulated antral follicle count", "Synthetic"), ("amh_ng_ml", "float ng/mL", "Simulated AMH", "Synthetic"),
        ("stimulation_protocol", "category", "Simulated protocol", "Synthetic"), ("stimulation_days", "integer days", "Simulated stimulation duration", "Synthetic"),
        ("estradiol_pg_ml", "float pg/mL", "Simulated estradiol measurement", "Synthetic; not clinical guidance"),
        ("progesterone_ng_ml", "float ng/mL", "Simulated progesterone measurement", "Synthetic; not clinical guidance"),
        ("total_oocytes", "integer", "Simulated retrieved oocytes", "Cycle-level count"), ("mature_oocytes", "integer", "Simulated mature oocytes", "Must not exceed total_oocytes"),
        ("fertilization_count", "integer", "Simulated fertilized oocytes", "Must not exceed mature_oocytes"),
        ("embryos_formed", "integer", "Simulated embryos", "Must not exceed fertilization_count"),
        ("embryo_grade_category", "category", "Simulated summary grade for transfer candidate", "Cycle-level summary, not embryo-level table"),
        ("embryo_developmental_stage", "category", "Simulated transfer stage", "Cycle-level stage"),
        ("day_of_embryo_transfer", "integer day", "3 or 5; 0 when no transfer", "Synthetic"),
        ("embryos_transferred", "integer count", "Simulated transferred embryos", "Cycle-level count"),
        ("blastocyst_indicator", "binary", "1 for simulated Day 5 blastocyst; else 0", "Derived from stage; do not duplicate with stage in causal inference"),
        ("endometrial_thickness_mm", "float mm", "Simulated measurement", "Synthetic"),
        ("clinical_pregnancy_outcome", "binary nullable", "Simulated primary outcome; 1 positive, 0 negative", "Unknown/no-transfer are null; target for exploratory model"),
        ("biochemical_pregnancy_outcome", "binary nullable", "Simulated secondary outcome", "Outcome; exclude from primary clinical-pregnancy features"),
        ("live_birth_outcome", "binary nullable", "Simulated secondary outcome", "Outcome; exclude from primary target features"),
        ("treatment_cycle_cost_inr", "float INR", "Simulated cycle cost", "Not actual prices/costs"),
        ("cycle_date", "date", "Simulated cycle date, 2022-2025", "Synthetic date; malformed strings intentionally injected in raw"),
        ("synthetic_record_flag", "category", "Always SYNTHETIC", "All generated records are fictional")]
    pd.DataFrame(rows, columns=["column", "data_type", "definition", "notes"]).to_csv(path, index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-cycles", type=int, default=3000)
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()
    raw = generate(args.n_cycles, args.seed)
    write_data_dictionary()
    print(f"Wrote {len(raw)} raw synthetic rows to {DATA_DIR}")
