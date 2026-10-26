"""Post-run structural and data assertions for the synthetic IVF portfolio."""
from pathlib import Path
import json
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]

def validate():
    raw = pd.read_csv(ROOT / "data/synthetic_ivf_raw.csv")
    clean = pd.read_csv(ROOT / "data/synthetic_ivf_cleaned.csv")
    dictionary = pd.read_csv(ROOT / "data/synthetic_ivf_data_dictionary.csv")
    assert len(raw) == 3005 and len(clean) == 2998
    assert raw.synthetic_record_flag.eq("SYNTHETIC").all()
    assert clean.synthetic_record_flag.eq("SYNTHETIC").all()
    assert clean.synthetic_cycle_id.is_unique
    assert clean.synthetic_patient_id.nunique() == 2100
    assert clean.clinical_pregnancy_outcome.dropna().isin([0, 1]).all()
    assert clean.clinical_pregnancy_outcome.isna().sum() == 122
    assert set(clean.embryos_transferred.dropna().astype(int).unique()).issubset({0, 1, 2})
    assert len(dictionary) == len(raw.columns)
    with open(ROOT / "outputs/analysis_summary.json") as f: stats = json.load(f)
    with open(ROOT / "outputs/model_split_and_feature_notes.json") as f: model = json.load(f)
    assert stats["cycles"] == len(clean)
    assert stats["known_transfer_outcomes"] == 2876
    assert model["patient_overlap"] == 0
    assert not ({"synthetic_patient_id", "synthetic_cycle_id", "biochemical_pregnancy_outcome", "live_birth_outcome"} & set(model["features"]))
    chart_names = ["project_architecture.png", "age_distribution.png", "embryo_grade_distribution.png",
                   "clinical_outcome_distribution.png", "grade_vs_outcome.png", "age_group_vs_outcome.png",
                   "amh_distribution.png", "total_oocytes_distribution.png", "stage_vs_outcome.png",
                   "monthly_cycle_trends.png", "treatment_cost_distribution.png", "correlation_heatmap.png",
                   "missingness_map.png", "outcome_analysis.png", "model_confusion_matrices.png", "model_roc_curves.png"]
    missing = [name for name in chart_names if not (ROOT / "visuals" / name).exists()]
    assert not missing, missing
    assert len(list((ROOT / "notebooks").glob("*.ipynb"))) == 5
    assert len(list((ROOT / "sql").glob("*.sql"))) == 3
    print("PASS: synthetic flags, row counts, IDs, outcome missingness, patient split, feature exclusions, notebooks, SQL, and visuals validated.")
    print(f"Raw rows={len(raw)}, cleaned rows={len(clean)}, synthetic patients={clean.synthetic_patient_id.nunique()}, known transfer outcomes={stats['known_transfer_outcomes']}.")

if __name__ == "__main__":
    validate()
