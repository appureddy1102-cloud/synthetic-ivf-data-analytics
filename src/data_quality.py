"""Quality profiling and conservative cleaning for synthetic IVF cycles."""
from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

NUMERIC = ["cycle_number", "patient_age", "infertility_duration_months", "bmi", "afc", "amh_ng_ml",
           "stimulation_days", "estradiol_pg_ml", "progesterone_ng_ml", "total_oocytes",
           "mature_oocytes", "fertilization_count", "embryos_formed", "day_of_embryo_transfer",
           "embryos_transferred", "blastocyst_indicator", "endometrial_thickness_mm",
           "clinical_pregnancy_outcome", "biochemical_pregnancy_outcome", "live_birth_outcome",
           "treatment_cycle_cost_inr"]
CATEGORICAL = ["infertility_factor", "stimulation_protocol", "embryo_grade_category", "embryo_developmental_stage"]


def profile(df):
    return pd.DataFrame({"dtype": df.dtypes.astype(str), "missing_count": df.isna().sum(),
                         "missing_pct": (df.isna().mean() * 100).round(3),
                         "unique_non_null": df.nunique(dropna=True)})


def clean_data(raw_path=DATA / "synthetic_ivf_raw.csv", clean_path=DATA / "synthetic_ivf_cleaned.csv"):
    raw = pd.read_csv(raw_path, low_memory=False)
    before = {"raw_rows": int(len(raw)), "raw_columns": int(raw.shape[1]),
              "exact_duplicate_rows": int(raw.duplicated().sum()), "missing_cells": int(raw.isna().sum().sum())}
    raw_prof = profile(raw)
    (ROOT / "outputs").mkdir(parents=True, exist_ok=True)
    df = raw.drop_duplicates().copy()
    df["cycle_date"] = pd.to_datetime(df["cycle_date"], errors="coerce")
    invalid_date = int(df["cycle_date"].isna().sum())
    df = df.dropna(subset=["synthetic_patient_id", "synthetic_cycle_id", "cycle_date"]).copy()
    for col in NUMERIC:
        if col in df:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    # Canonicalize categories without changing their meaning.
    for col in CATEGORICAL:
        df[col] = df[col].astype("string").str.strip().str.replace(r"\s+", " ", regex=True).str.title()
    protocol_map = {"Antagonist": "Antagonist", "Long Agonist": "Long agonist",
                    "Mild Stimulation": "Mild stimulation", "Flare": "Flare"}
    df["stimulation_protocol"] = df["stimulation_protocol"].map(protocol_map).astype("string")
    df["embryo_grade_category"] = df["embryo_grade_category"].replace({"A": "A", "B": "B", "C": "C", "No Transfer": "No transfer"})
    df["embryo_developmental_stage"] = df["embryo_developmental_stage"].replace({"Day 3": "Day 3", "Day 5 Blastocyst": "Day 5 blastocyst", "Not Applicable": "Not applicable"})
    # Range violations become missing, not silently clipped or deleted.
    bounds = {"patient_age": (18, 50), "infertility_duration_months": (0, 240), "bmi": (12, 60),
              "afc": (0, 60), "amh_ng_ml": (0, 20), "stimulation_days": (1, 30),
              "estradiol_pg_ml": (0, 20000), "progesterone_ng_ml": (0, 20),
              "total_oocytes": (0, 60), "mature_oocytes": (0, 60), "fertilization_count": (0, 60),
              "embryos_formed": (0, 60), "day_of_embryo_transfer": (0, 6),
              "embryos_transferred": (0, 3), "blastocyst_indicator": (0, 1),
              "clinical_pregnancy_outcome": (0, 1), "biochemical_pregnancy_outcome": (0, 1),
              "live_birth_outcome": (0, 1), "endometrial_thickness_mm": (0, 30),
              "treatment_cycle_cost_inr": (0, 1000000)}
    invalid_range_counts = {}
    for col, (lo, hi) in bounds.items():
        if col in df:
            bad = df[col].notna() & ~df[col].between(lo, hi)
            invalid_range_counts[col] = int(bad.sum())
            df.loc[bad, col] = np.nan
    # Logical count consistency: null the impossible downstream count; preserve row.
    logical_counts = {}
    for child, parent in [("mature_oocytes", "total_oocytes"), ("fertilization_count", "mature_oocytes"),
                          ("embryos_formed", "fertilization_count"), ("embryos_transferred", "embryos_formed")]:
        bad = df[child].notna() & df[parent].notna() & (df[child] > df[parent])
        logical_counts[f"{child}_greater_than_{parent}"] = int(bad.sum())
        df.loc[bad, child] = np.nan
    # Ensure primary outcome remains nullable; no-transfer is structurally not eligible.
    no_transfer = df["embryos_transferred"].fillna(0).eq(0)
    df.loc[no_transfer, ["clinical_pregnancy_outcome", "biochemical_pregnancy_outcome", "live_birth_outcome"]] = np.nan
    # Row-level dates retained; add month for trend reporting.
    df["cycle_month"] = df["cycle_date"].dt.to_period("M").dt.to_timestamp()
    clean_prof = profile(df)
    after = {"clean_rows": int(len(df)), "clean_columns": int(df.shape[1]),
             "rows_removed_exact_duplicates": before["exact_duplicate_rows"],
             "rows_removed_invalid_identity_or_date": int(before["raw_rows"] - before["exact_duplicate_rows"] - len(df)),
             "invalid_dates_after_dedup": invalid_date,
             "missing_cells_after_cleaning": int(df.isna().sum().sum()),
             "unique_patients": int(df.synthetic_patient_id.nunique()),
             "unique_cycles": int(df.synthetic_cycle_id.nunique()),
             "transfer_cycles": int(df.embryos_transferred.fillna(0).gt(0).sum()),
             "known_clinical_outcomes": int(df.clinical_pregnancy_outcome.notna().sum()),
             "missing_clinical_outcomes_among_transfers": int((df.embryos_transferred.gt(0) & df.clinical_pregnancy_outcome.isna()).sum()),
             "invalid_range_counts": invalid_range_counts,
             "logical_count_violations": logical_counts,
             "date_min": str(df.cycle_date.min().date()), "date_max": str(df.cycle_date.max().date())}
    Path(clean_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(clean_path, index=False)
    raw_prof.to_csv(ROOT / "outputs" / "raw_quality_profile.csv")
    clean_prof.to_csv(ROOT / "outputs" / "cleaned_quality_profile.csv")
    with open(ROOT / "outputs" / "data_quality_summary.json", "w") as f:
        json.dump({"before": before, "after": after}, f, indent=2)
    return raw, df, before, after, raw_prof, clean_prof


def iqr_screen(df):
    rows = []
    for col in [c for c in NUMERIC if c in df and df[c].notna().sum() > 0]:
        q1, q3 = df[col].quantile([.25, .75])
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        flagged = df[col].notna() & ~df[col].between(lower, upper)
        rows.append({"column": col, "q1": q1, "q3": q3, "iqr": iqr, "lower_fence": lower,
                     "upper_fence": upper, "flagged_count": int(flagged.sum()),
                     "flagged_pct_nonmissing": float(flagged.sum() / df[col].notna().sum() * 100)})
    result = pd.DataFrame(rows)
    result.to_csv(ROOT / "outputs" / "iqr_outlier_screen.csv", index=False)
    return result

if __name__ == "__main__":
    raw, cleaned, before, after, *_ = clean_data()
    print("Before:", before)
    print("After:", {k: v for k, v in after.items() if not isinstance(v, dict)})
    print("IQR flags (retained):", iqr_screen(cleaned).set_index("column").flagged_count.to_dict())
