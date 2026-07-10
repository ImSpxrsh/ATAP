"""Unit tests for the extended-track core logic (no big data required).

Exercises the load-bearing, non-circular pieces: executioner-loss calling, the "both low"
rule, the spatial routing decision, the susceptibility composite, and the synthetic
method-validation recovery. Fast; runs in CI without downloading DepMap/GDSC/etc.
"""
import numpy as np
import pandas as pd
import panels
import spatial


# ---------------- executioner-loss logic (panels.py) ----------------

def test_is_damaging_tokens():
    assert panels._is_damaging("stop_gained")
    assert panels._is_damaging("frameshift_variant&splice_region_variant")
    assert not panels._is_damaging("synonymous_variant")
    assert not panels._is_damaging(None)  # non-string -> False, no crash


def test_mutation_lof_flags_only_damaged_samples():
    mut = pd.DataFrame({
        "gene": ["BAX", "BAK1", "BAX", "TP53"],
        "sample": ["S1", "S2", "S3", "S4"],
        "cls": ["stop_gained", "synonymous_variant", "frameshift_variant", "stop_gained"],
    })
    hit = panels.mutation_lof(mut, "gene", "sample", "cls", ["BAX", "BAK1"])
    assert hit.get("S1", False)          # damaging BAX
    assert "S2" not in hit.index or not hit["S2"]  # synonymous -> not damaging
    assert hit.get("S3", False)          # frameshift BAX
    assert "S4" not in hit.index         # TP53 not an executioner


def test_mutation_lof_empty_is_safe():
    mut = pd.DataFrame({"gene": ["TP53"], "sample": ["S1"], "cls": ["stop_gained"]})
    out = panels.mutation_lof(mut, "gene", "sample", "cls", ["BAX", "BAK1"])
    assert out.empty  # no BAX/BAK1 -> empty Series, no exception


def test_cn_deep_deletion():
    cutoff = panels.CFG["executioner_loss"]["cn_deep_del_relative"]
    cn = pd.DataFrame({"BAX": [1.0, cutoff - 0.05], "BAK1": [1.0, 1.0]},
                      index=["neutral", "deleted"])
    out = panels.cn_deep_deletion(cn, ["BAX", "BAK1"])
    assert not out["neutral"] and out["deleted"]


def test_expression_low_both_requires_all_executioners_low():
    # 10 samples; S0 lowest in BOTH BAX and BAK1; S1 lowest in only BAX
    expr = pd.DataFrame({
        "BAX":  [0.0, 0.0, 5, 6, 7, 8, 9, 10, 11, 12],
        "BAK1": [0.0, 9.0, 5, 6, 7, 8, 9, 10, 11, 12],
    }, index=[f"S{i}" for i in range(10)])
    out = panels.expression_low_both(expr, ["BAX", "BAK1"], quantile=0.10)
    assert out["S0"]         # both low -> flagged
    assert not out["S1"]     # only BAX low -> not flagged (executioner step survives)


# ---------------- spatial routing (spatial.py) ----------------

def test_routing_categories_and_bypass():
    # engineer a clear bypass-required cell (high guardian, low executioner) vs sufficient
    n = 20
    rng = np.random.default_rng(0)
    guardian_hi = np.linspace(0, 10, n)          # BCL2 gradient
    exec_lvl = np.linspace(10, 0, n)             # BAX/BAK anti-correlated
    expr = pd.DataFrame({"BCL2": guardian_hi, "MCL1": guardian_hi,
                         "BAX": exec_lvl, "BAK1": exec_lvl},
                        index=[f"spot{i}" for i in range(n)])
    r = spatial.routing(expr)
    assert set(r["routing"].unique()) <= {"bypass-required", "venetoclax-sufficient", "low-signal"}
    # the top-guardian / bottom-executioner spot should be bypass-required
    assert r.iloc[-1]["routing"] == "bypass-required"
    # the bottom-guardian / top-executioner spot should be venetoclax-sufficient
    assert r.iloc[0]["routing"] == "venetoclax-sufficient"


def test_routing_with_stability_returns_scores():
    n = 30
    expr = pd.DataFrame(np.random.default_rng(1).random((n, 4)),
                        columns=["BCL2", "MCL1", "BAX", "BAK1"],
                        index=[f"s{i}" for i in range(n)])
    r = spatial.routing_with_stability(expr)
    assert "stability" in r.columns
    assert ((r["stability"] >= 0) & (r["stability"] <= 1)).all()


# ---------------- synthetic method validation (validation.py) ----------------

def test_synthetic_recovery_is_high():
    import validation
    from sklearn.metrics import roc_auc_score
    expr, coords, truth = validation.simulate_field(side=30, effect=2.0)
    r = spatial.routing(expr, coords)
    score = (r["guardian_dependence"] * (1 - r["executioner_availability"])).values
    auc = roc_auc_score(truth, score)
    assert auc > 0.75  # pipeline recovers a known ground-truth bypass region
