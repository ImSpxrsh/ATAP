"""
03_score_real.py — run the mechanistic scorer on a REAL cohort fetched live from the
public cBioPortal API (no download/registration). Default: BeatAML (aml_ohsu_2022).

This is real-patient *prediction* + an internal mechanistic check. It is NOT venetoclax-
response validation: cBioPortal's BeatAML lacks the ex-vivo AUC readout (see docs/DATA.md),
so the salvage_target predictions here are hypotheses about real patients, not confirmed
resistant cases. Reported honestly as such.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from atap import data, features, scoring  # noqa: E402


def main(study: str = "aml_ohsu_2022") -> None:
    co = data.load_cbioportal(study=study)
    print(co)
    blocks = features.build_feature_blocks(co.expr, co.mutations)
    scores = scoring.SusceptibilityModel().score(blocks)

    print(f"\n=== REAL {co.name} — predicted quadrants (n={len(scores)}) ===")
    print(scoring.summarize(scores).to_string())

    # Internal mechanistic check on real data: salvage_target must carry a lower
    # effector (BAX/BAK) axis than the rest — the model's core claim, on real expression.
    eff = blocks["effector_competence"]
    st = scores["quadrant"] == "salvage_target"
    print(f"\neffector_competence  salvage_target={eff[st].mean():.3f}  "
          f"rest={eff[~st].mean():.3f}  (lower in salvage_target => mechanism holds)")
    print("\nNOTE: prediction only — no venetoclax ex-vivo response in cBioPortal; "
          "response validation needs the Vizome/Bottomly-2022 supplement.")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "aml_ohsu_2022")
