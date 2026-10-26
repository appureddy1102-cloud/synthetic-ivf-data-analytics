"""EDA, descriptive/inferential statistics, and reproducible chart exports."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from .data_quality import clean_data, iqr_screen
from .generate_data import DATA_DIR, write_data_dictionary

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
VIS = ROOT / "visuals"
SEED = 20260618


def _save(fig, name):
    VIS.mkdir(exist_ok=True, parents=True)
    path = VIS / name
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def descriptive_statistics(df):
    numeric = ["patient_age", "infertility_duration_months", "bmi", "afc", "amh_ng_ml", "stimulation_days",
               "estradiol_pg_ml", "progesterone_ng_ml", "total_oocytes", "mature_oocytes", "fertilization_count",
               "embryos_formed", "endometrial_thickness_mm", "treatment_cycle_cost_inr"]
    out = df[numeric].describe(percentiles=[.25, .5, .75]).T
    out["variance"] = df[numeric].var()
    out["mode"] = df[numeric].mode(dropna=True).iloc[0]
    out["skewness"] = df[numeric].skew()
    out["kurtosis"] = df[numeric].kurt()
    return out


def _rates(df, group):
    x = df[df.clinical_pregnancy_outcome.notna()].groupby(group, observed=False).clinical_pregnancy_outcome.agg(["count", "sum", "mean"])
    x = x.rename(columns={"count": "known_outcomes", "sum": "positive_outcomes", "mean": "positive_rate"})
    return x


def run_eda(cleaned_path=DATA_DIR / "synthetic_ivf_cleaned.csv"):
    if not (DATA_DIR / "synthetic_ivf_raw.csv").exists():
        from .generate_data import generate
        generate()
        write_data_dictionary()
    raw, df, before, after, raw_prof, clean_prof = clean_data(clean_path=cleaned_path)
    iqr = iqr_screen(df)
    desc = descriptive_statistics(df)
    desc.to_csv(OUT / "descriptive_statistics.csv")
    # Outcome denominators are known clinical outcomes among transfer cycles only.
    eligible = df[(df.embryos_transferred > 0) & df.clinical_pregnancy_outcome.notna()].copy()
    grade_rates = _rates(eligible, "embryo_grade_category")
    age_bins = [0, 34, 37, 40, 60]
    age_labels = ["≤34", "35–37", "38–40", "41+"]
    eligible["age_group"] = pd.cut(eligible.patient_age, bins=age_bins, labels=age_labels)
    age_rates = _rates(eligible, "age_group")
    stage_rates = _rates(eligible, "embryo_developmental_stage")
    cost_by_factor = df.groupby("infertility_factor").treatment_cycle_cost_inr.agg(["count", "mean", "median"]).round(2)
    cost_by_protocol = df.groupby("stimulation_protocol").treatment_cycle_cost_inr.agg(["count", "mean", "median"]).round(2)
    grade_rates.to_csv(OUT / "outcome_by_embryo_grade.csv")
    age_rates.to_csv(OUT / "outcome_by_age_group.csv")
    stage_rates.to_csv(OUT / "outcome_by_developmental_stage.csv")
    cost_by_factor.to_csv(OUT / "cost_by_infertility_factor.csv")
    cost_by_protocol.to_csv(OUT / "cost_by_protocol.csv")
    # Tests describe association, not clinical evidence.
    rho_age, p_age = stats.spearmanr(eligible.patient_age, eligible.clinical_pregnancy_outcome, nan_policy="omit")
    rho_amh, p_amh = stats.spearmanr(eligible.amh_ng_ml, eligible.clinical_pregnancy_outcome, nan_policy="omit")
    ct = pd.crosstab(eligible.embryo_grade_category, eligible.clinical_pregnancy_outcome)
    chi2_grade, p_grade, dof_grade, _ = stats.chi2_contingency(ct)
    cramers_v = float(np.sqrt(chi2_grade / (ct.to_numpy().sum() * max(1, min(ct.shape[0]-1, ct.shape[1]-1)))))
    positive_cost = eligible.loc[eligible.clinical_pregnancy_outcome.eq(1), "treatment_cycle_cost_inr"].dropna()
    negative_cost = eligible.loc[eligible.clinical_pregnancy_outcome.eq(0), "treatment_cycle_cost_inr"].dropna()
    cost_u, cost_p = stats.mannwhitneyu(positive_cost, negative_cost, alternative="two-sided")
    monthly = df.groupby("cycle_month").agg(cycles=("synthetic_cycle_id", "nunique"),
             transfers=("embryos_transferred", lambda x: int(x.gt(0).sum())),
             known_outcomes=("clinical_pregnancy_outcome", "count"),
             clinical_positive=("clinical_pregnancy_outcome", "sum"))
    monthly["clinical_positive_rate"] = monthly.clinical_positive / monthly.known_outcomes.replace(0, np.nan)
    monthly.to_csv(OUT / "monthly_cycle_trends.csv")
    summary = {
        "synthetic_only": True, "raw_rows": len(raw), "clean_rows": len(df), "raw_columns": raw.shape[1],
        "clean_columns": df.shape[1], "patients": int(df.synthetic_patient_id.nunique()),
        "cycles": int(df.synthetic_cycle_id.nunique()), "transfers": int(df.embryos_transferred.gt(0).sum()),
        "known_transfer_outcomes": int(len(eligible)), "clinical_positive_count": int(eligible.clinical_pregnancy_outcome.sum()),
        "clinical_positive_rate_known_transfers": float(eligible.clinical_pregnancy_outcome.mean()),
        "biochemical_positive_count_known": int(df.biochemical_pregnancy_outcome.sum()),
        "biochemical_known_outcomes": int(df.biochemical_pregnancy_outcome.notna().sum()),
        "biochemical_positive_rate_known": float(df.biochemical_pregnancy_outcome.mean()),
        "live_birth_count_known": int(df.live_birth_outcome.sum()),
        "live_birth_known_outcomes": int(df.live_birth_outcome.notna().sum()),
        "live_birth_positive_rate_known": float(df.live_birth_outcome.mean()),

        "mean_cost_inr": float(df.treatment_cycle_cost_inr.mean()),
        "median_cost_inr": float(df.treatment_cycle_cost_inr.median()),
        "age_spearman_rho": float(rho_age), "age_spearman_p": float(p_age),
        "amh_spearman_rho": float(rho_amh), "amh_spearman_p": float(p_amh),
        "grade_chi2": float(chi2_grade), "grade_chi2_p": float(p_grade), "grade_chi2_dof": int(dof_grade),
        "grade_cramers_v": cramers_v, "cost_mannwhitney_u": float(cost_u), "cost_mannwhitney_p": float(cost_p),
        "quality": after
    }
    with open(OUT / "analysis_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    sns.set_theme(style="whitegrid", context="notebook")
    # 1 age distribution
    fig, ax = plt.subplots(figsize=(8, 4)); sns.histplot(df.patient_age, bins=20, kde=True, ax=ax, color="#247BA0"); ax.set(title="Synthetic Patient Age Distribution", xlabel="Age (years)"); _save(fig, "age_distribution.png")
    # 2 grade distribution among transferred cycles
    fig, ax = plt.subplots(figsize=(7, 4)); sns.countplot(data=df[df.embryos_transferred.gt(0)], x="embryo_grade_category", order=["A", "B", "C"], ax=ax, color="#70C1B3"); ax.set(title="Transferred-Cycle Embryo Grade Summary", xlabel="Cycle-level grade category", ylabel="Cycles"); _save(fig, "embryo_grade_distribution.png")
    # 3 outcome distribution
    fig, ax = plt.subplots(figsize=(6, 4)); sns.countplot(data=eligible, x="clinical_pregnancy_outcome", order=[0, 1], ax=ax, color="#247BA0"); ax.set_xticks([0, 1], labels=["Negative", "Positive"]); ax.set(title="Simulated Clinical Pregnancy Outcome", xlabel="Outcome (known transfer cycles)", ylabel="Cycles"); _save(fig, "clinical_outcome_distribution.png")
    # 4 grade vs outcome rate
    fig, ax = plt.subplots(figsize=(7, 4)); sns.barplot(data=eligible, x="embryo_grade_category", y="clinical_pregnancy_outcome", order=["A", "B", "C"], errorbar=None, ax=ax, color="#70C1B3"); ax.set(title="Simulated Outcome Rate by Grade", ylabel="Positive proportion", xlabel="Cycle-level grade"); _save(fig, "grade_vs_outcome.png")
    # 5 age groups
    fig, ax = plt.subplots(figsize=(7, 4)); sns.barplot(data=eligible, x="age_group", y="clinical_pregnancy_outcome", order=age_labels, errorbar=None, ax=ax, color="#F3A712"); ax.set(title="Simulated Outcome Rate by Age Group", ylabel="Positive proportion", xlabel="Age group (years)"); _save(fig, "age_group_vs_outcome.png")
    # 6 AMH distribution
    fig, ax = plt.subplots(figsize=(8, 4)); sns.histplot(df.amh_ng_ml, bins=25, kde=True, ax=ax, color="#5B8E7D"); ax.set(title="Synthetic AMH Distribution", xlabel="AMH (ng/mL)"); _save(fig, "amh_distribution.png")
    # 7 oocyte distribution
    fig, ax = plt.subplots(figsize=(8, 4)); sns.histplot(df.total_oocytes, discrete=True, ax=ax, color="#9B5DE5"); ax.set(title="Synthetic Total Oocytes per Cycle", xlabel="Total oocytes", ylabel="Cycles"); _save(fig, "total_oocytes_distribution.png")
    # 8 stage vs outcome
    fig, ax = plt.subplots(figsize=(8, 4)); sns.barplot(data=eligible, x="embryo_developmental_stage", y="clinical_pregnancy_outcome", errorbar=None, ax=ax, color="#247BA0"); ax.set(title="Simulated Outcome Rate by Developmental Stage", ylabel="Positive proportion", xlabel="Cycle-level transfer stage"); _save(fig, "stage_vs_outcome.png")
    # 9 monthly trends
    fig, ax = plt.subplots(figsize=(10, 4)); ax.plot(monthly.index, monthly.cycles, label="Cycles", color="#247BA0"); ax.plot(monthly.index, monthly.transfers, label="Transfer cycles", color="#F3A712"); ax.set(title="Synthetic Treatment Cycles by Month", ylabel="Cycles", xlabel="Month"); ax.legend(); _save(fig, "monthly_cycle_trends.png")
    # 10 cost distribution
    fig, ax = plt.subplots(figsize=(8, 4)); sns.histplot(df.treatment_cycle_cost_inr, bins=25, kde=True, ax=ax, color="#F28482"); ax.set(title="Synthetic Treatment Cost Distribution", xlabel="Treatment-cycle cost (INR)"); _save(fig, "treatment_cost_distribution.png")
    # 11 correlation heatmap (numerics)
    corr_cols = ["patient_age", "bmi", "afc", "amh_ng_ml", "total_oocytes", "mature_oocytes", "embryos_formed", "endometrial_thickness_mm", "treatment_cycle_cost_inr", "clinical_pregnancy_outcome"]
    fig, ax = plt.subplots(figsize=(10, 7)); sns.heatmap(df[corr_cols].corr(method="spearman"), cmap="vlag", center=0, annot=True, fmt=".2f", ax=ax); ax.set_title("Spearman Correlation Heatmap (Synthetic Cycle Variables)"); _save(fig, "correlation_heatmap.png")
    # 12 missingness map of raw fields, sampled rows
    fig, ax = plt.subplots(figsize=(12, 4)); sns.heatmap(raw.isna().sample(min(220, len(raw)), random_state=SEED), cbar=False, yticklabels=False, cmap=["#EDF2F4", "#E76F51"], ax=ax); ax.set(title="Raw Data Missingness (Sample of Rows)", xlabel="Columns"); _save(fig, "missingness_map.png")
    # outcome summary multi-chart requested name
    fig, axes = plt.subplots(1, 3, figsize=(13, 4))
    for ax, table, title in [(axes[0], grade_rates, "By Grade"), (axes[1], age_rates, "By Age"), (axes[2], stage_rates, "By Stage")]:
        ax.bar(table.index.astype(str), table.positive_rate, color="#247BA0"); ax.set_title(title); ax.set_ylim(0, 1); ax.set_ylabel("Positive rate"); ax.tick_params(axis="x", rotation=25)
    _save(fig, "outcome_analysis.png")
    return raw, df, before, after, desc, grade_rates, age_rates, stage_rates, cost_by_factor, monthly, summary, iqr

if __name__ == "__main__":
    results = run_eda()
    print("Synthetic IVF EDA complete. Summary:", json.dumps(results[10], indent=2))
    print("IQR flags are retained; see outputs/iqr_outlier_screen.csv")
