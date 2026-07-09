"""
scoring.py — the two-axis susceptibility model.

Two per-sample scores, each a transparent weighted sum of the mechanistic blocks
using the signs declared in biology.DIRECTIONAL_PRIORS:

    venetoclax_score : predicted efficacy of the BH3-mimetic class (BCL2-axis).
    atap_score       : predicted efficacy of BAX-independent pore-forming (ATAP-M8).

The point of the project lives in one line of the priors table:
    effector_competence -> venetoclax +1, ATAP -1.
BAX/BAK loss sinks the venetoclax axis and *lifts* the ATAP axis, which is why the
two scores separate exactly in the resistant population.

Nothing here is a black box: weights are explicit, and `explain_sample()` returns the
signed per-block contribution so any call can be traced back to biology.

The model is deliberately unsupervised/mechanistic by default (no labels required),
so it runs on any cohort. `calibrate_to_response()` optionally fits a logistic layer
on top when a real drug-response readout (BeatAML venetoclax AUC, PRISM) is available,
turning the mechanistic score into a probability without discarding interpretability.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from scipy.stats import rankdata

from . import biology

# Block weights. Uniform magnitude by default so the sign table drives behavior;
# effector_competence is up-weighted because it is the mechanistic crux and is the
# one block with opposite signs across the two agents.
BLOCK_WEIGHTS = {
    "bcl2_dependence":      1.0,
    "mcl1_bclxl_backup":    1.0,
    "priming_activators":   1.0,
    "effector_competence":  1.6,
    "execution_competence": 1.0,
    "mito_mass":            0.8,
}


@dataclass
class SusceptibilityModel:
    """Mechanistic two-axis scorer. Stateless except for optional response calibration."""

    weights: dict[str, float] = field(default_factory=lambda: dict(BLOCK_WEIGHTS))
    _veneto_cal: object | None = None  # fitted sklearn logistic, optional
    _atap_cal: object | None = None

    # --- core scoring -------------------------------------------------------------
    def _axis(self, blocks: pd.DataFrame, agent: str) -> pd.Series:
        """Signed weighted sum for one agent ('venetoclax' col index 0, 'atap' 1)."""
        idx = 0 if agent == "venetoclax" else 1
        total = pd.Series(0.0, index=blocks.index)
        for block, signs in biology.DIRECTIONAL_PRIORS.items():
            sign = signs[idx]
            if sign == 0 or block not in blocks.columns:
                continue
            total = total + sign * self.weights.get(block, 1.0) * blocks[block]
        return total

    def raw_scores(self, blocks: pd.DataFrame) -> pd.DataFrame:
        """Raw (uncalibrated) venetoclax and ATAP axis scores."""
        out = pd.DataFrame(index=blocks.index)
        out["venetoclax_score"] = self._axis(blocks, "venetoclax")
        out["atap_score"] = self._axis(blocks, "atap")
        # A binding mutation blocks venetoclax without touching BAX/BAK: apply as a
        # direct penalty to the venetoclax axis only.
        if "bcl2_binding_mut" in blocks.columns:
            out["venetoclax_score"] -= 2.0 * blocks["bcl2_binding_mut"]
        return out

    def score(self, blocks: pd.DataFrame) -> pd.DataFrame:
        """
        Full per-sample scoring: raw axes, cohort percentiles, quadrant label, and the
        salvage index (how strongly ATAP is preferred over venetoclax).
        """
        s = self.raw_scores(blocks)

        # Percentile ranks within cohort make the axes comparable and thresholdable.
        s["venetoclax_pct"] = _pct_rank(s["venetoclax_score"])
        s["atap_pct"] = _pct_rank(s["atap_score"])

        # Salvage index: positive = ATAP favored where venetoclax is predicted to fail.
        s["salvage_index"] = s["atap_pct"] - s["venetoclax_pct"]

        s["quadrant"] = _quadrant(s["venetoclax_pct"], s["atap_pct"])

        if self._veneto_cal is not None:
            s["venetoclax_response_prob"] = self._veneto_cal.predict_proba(
                s[["venetoclax_score"]].values)[:, 1]
        if self._atap_cal is not None:
            s["atap_response_prob"] = self._atap_cal.predict_proba(
                s[["atap_score"]].values)[:, 1]
        return s

    def explain_sample(self, blocks: pd.DataFrame, sample: str) -> pd.DataFrame:
        """Signed per-block contribution to each axis for one sample — an audit trail."""
        row = blocks.loc[sample]
        recs = []
        for block, signs in biology.DIRECTIONAL_PRIORS.items():
            if block not in blocks.columns:
                continue
            w = self.weights.get(block, 1.0)
            recs.append({
                "block": block,
                "value": round(float(row[block]), 3),
                "venetoclax_contrib": round(signs[0] * w * float(row[block]), 3),
                "atap_contrib": round(signs[1] * w * float(row[block]), 3),
            })
        return pd.DataFrame(recs).set_index("block")

    # --- optional supervised calibration -----------------------------------------
    def calibrate_to_response(
        self,
        blocks: pd.DataFrame,
        venetoclax_response: pd.Series | None = None,
        atap_response: pd.Series | None = None,
    ) -> "SusceptibilityModel":
        """
        Fit a 1-D logistic layer mapping each raw axis score to a response probability,
        when a real readout is available (1 = responder/sensitive, 0 = resistant).
        Keeps the mechanistic score as the only input, so calibration cannot invent
        signal the mechanism does not support — it only sets the threshold and slope.
        """
        from sklearn.linear_model import LogisticRegression

        s = self.raw_scores(blocks)
        if venetoclax_response is not None:
            y = venetoclax_response.reindex(s.index).dropna()
            if y.nunique() == 2:
                self._veneto_cal = LogisticRegression().fit(
                    s.loc[y.index, ["venetoclax_score"]].values, y.astype(int).values)
        if atap_response is not None:
            y = atap_response.reindex(s.index).dropna()
            if y.nunique() == 2:
                self._atap_cal = LogisticRegression().fit(
                    s.loc[y.index, ["atap_score"]].values, y.astype(int).values)
        return self


# ---- helpers ----------------------------------------------------------------------

def _pct_rank(x: pd.Series) -> pd.Series:
    """Percentile rank in [0, 1] within the cohort."""
    if len(x) == 1:
        return pd.Series(0.5, index=x.index)
    r = rankdata(x.values, method="average")
    return pd.Series((r - 1) / (len(x) - 1), index=x.index)


# Quadrant thresholds on cohort percentile. "low venetoclax" = bottom 40%,
# "high ATAP" = top 60%. Tunable; exposed as module constants for transparency.
VENETO_LOW = 0.40
ATAP_HIGH = 0.60


def _quadrant(veneto_pct: pd.Series, atap_pct: pd.Series) -> pd.Series:
    """
    Label each sample:
      'salvage_target'  : venetoclax predicted to fail, ATAP predicted to work  <-- the ask
      'standard_of_care': venetoclax predicted to work                          (use veneto)
      'hard_escape'     : both predicted to fail (downstream execution lost)    (neither)
      'ambiguous'       : middle ground
    """
    labels = pd.Series("ambiguous", index=veneto_pct.index, dtype=object)
    veneto_ok = veneto_pct >= VENETO_LOW
    atap_ok = atap_pct >= ATAP_HIGH

    labels[veneto_ok] = "standard_of_care"
    labels[(~veneto_ok) & atap_ok] = "salvage_target"
    labels[(~veneto_ok) & (~atap_ok)] = "hard_escape"
    return labels


def summarize(scores: pd.DataFrame) -> pd.DataFrame:
    """Cohort-level quadrant counts and mean salvage index — a one-glance readout."""
    g = scores.groupby("quadrant")
    out = pd.DataFrame({
        "n": g.size(),
        "frac": (g.size() / len(scores)).round(3),
        "mean_salvage_index": g["salvage_index"].mean().round(3),
    })
    return out.sort_values("n", ascending=False)
