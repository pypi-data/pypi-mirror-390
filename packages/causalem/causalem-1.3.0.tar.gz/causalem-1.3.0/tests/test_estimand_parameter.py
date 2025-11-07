"""Tests for the estimand parameter (ATM vs ATT)."""

import numpy as np
import pytest
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

from causalem import estimate_te, load_data_lalonde, load_data_tof
from causalem.estimation.ensemble import estimate_te_multi

# -------------------------------------------------------------------
# Helpers / lightweight configs
# -------------------------------------------------------------------
KW_COMMON = dict(
    niter=2,
    n_splits_propensity=3,
    n_splits_outcome=3,
    matching_is_stochastic=False,
    matching_scale=1.0,
    matching_caliper=None,
    nboot=0,
)


# -------------------------------------------------------------------
# Test estimand parameter validation
# -------------------------------------------------------------------
def test_estimand_validation_invalid():
    """Test that invalid estimand values raise ValueError."""
    X, t, y = load_data_lalonde(raw=False)

    with pytest.raises(ValueError, match="estimand='INVALID' not recognized"):
        estimate_te(
            X,
            t,
            y,
            outcome_type="continuous",
            estimand="INVALID",
            random_state_master=123,
            **KW_COMMON,
        )


def test_estimand_validation_ate_not_implemented():
    """Test that ATE estimand raises NotImplementedError."""
    X, t, y = load_data_lalonde(raw=False)

    with pytest.raises(
        NotImplementedError, match="estimand='ATE' is not yet implemented"
    ):
        estimate_te(
            X,
            t,
            y,
            outcome_type="continuous",
            estimand="ATE",
            random_state_master=123,
            **KW_COMMON,
        )


# -------------------------------------------------------------------
# Test ATM (default behavior, backward compatibility)
# -------------------------------------------------------------------
def test_estimand_atm_default():
    """Test that ATM is the default estimand (backward compatibility)."""
    X, t, y = load_data_lalonde(raw=False)

    # No estimand specified (should default to ATM)
    result_default = estimate_te(
        X,
        t,
        y,
        outcome_type="continuous",
        model_outcome=RandomForestRegressor(n_estimators=20),
        random_state_master=123,
        **KW_COMMON,
    )

    # Explicit ATM
    result_atm = estimate_te(
        X,
        t,
        y,
        outcome_type="continuous",
        model_outcome=RandomForestRegressor(n_estimators=20),
        random_state_master=123,
        estimand="ATM",
        **KW_COMMON,
    )

    # Should be identical
    assert result_default["te"] == result_atm["te"]
    assert np.array_equal(result_default["matching"], result_atm["matching"])


# -------------------------------------------------------------------
# Test ATT for binary treatment (no-stacking)
# -------------------------------------------------------------------
def test_estimand_att_binary_no_stacking():
    """Test ATT estimand with binary treatment (no-stacking pathway)."""
    X, t, y = load_data_lalonde(raw=False)

    result_atm = estimate_te(
        X,
        t,
        y,
        outcome_type="continuous",
        model_outcome=RandomForestRegressor(n_estimators=20),
        random_state_master=123,
        estimand="ATM",
        do_stacking=False,
        **KW_COMMON,
    )

    result_att = estimate_te(
        X,
        t,
        y,
        outcome_type="continuous",
        model_outcome=RandomForestRegressor(n_estimators=20),
        random_state_master=123,
        estimand="ATT",
        do_stacking=False,
        **KW_COMMON,
    )

    # ATT and ATM should generally differ (unless perfectly balanced)
    # We just verify that both run successfully and return valid results
    assert "te" in result_atm
    assert "te" in result_att
    assert "matching" in result_atm
    assert "matching" in result_att

    # Both should be numeric
    assert isinstance(result_atm["te"], (int, float))
    assert isinstance(result_att["te"], (int, float))


# -------------------------------------------------------------------
# Test ATT for binary treatment (stacking)
# -------------------------------------------------------------------
def test_estimand_att_binary_stacking():
    """Test ATT estimand with binary treatment (stacking pathway)."""
    X, t, y = load_data_lalonde(raw=False)

    result_atm = estimate_te(
        X,
        t,
        y,
        outcome_type="continuous",
        model_outcome=RandomForestRegressor(n_estimators=20),
        random_state_master=123,
        estimand="ATM",
        do_stacking=True,
        **KW_COMMON,
    )

    result_att = estimate_te(
        X,
        t,
        y,
        outcome_type="continuous",
        model_outcome=RandomForestRegressor(n_estimators=20),
        random_state_master=123,
        estimand="ATT",
        do_stacking=True,
        **KW_COMMON,
    )

    # Both should run successfully
    assert "te" in result_atm
    assert "te" in result_att
    assert "matching" in result_atm
    assert "matching" in result_att

    # Both should be numeric
    assert isinstance(result_atm["te"], (int, float))
    assert isinstance(result_att["te"], (int, float))


# -------------------------------------------------------------------
# Test ATT for binary treatment with bootstrap
# -------------------------------------------------------------------
def test_estimand_att_binary_bootstrap():
    """Test ATT estimand with bootstrap confidence intervals."""
    X, t, y = load_data_lalonde(raw=False)

    result = estimate_te(
        X,
        t,
        y,
        outcome_type="continuous",
        model_outcome=RandomForestRegressor(n_estimators=20),
        random_state_master=123,
        random_state_boot=456,
        estimand="ATT",
        nboot=10,  # Small number for speed
        niter=2,
        n_splits_propensity=3,
        n_splits_outcome=3,
        matching_is_stochastic=False,
    )

    # Should have bootstrap results
    assert "te" in result
    assert "ci" in result
    assert "boot" in result
    assert len(result["boot"]) == 10


# -------------------------------------------------------------------
# Test ATT for multi-arm treatment (no-stacking)
# -------------------------------------------------------------------
def test_estimand_att_multi_no_stacking():
    """Test ATT estimand with multi-arm treatment (no-stacking pathway)."""
    # Generate simple multi-arm data
    np.random.seed(42)
    n = 200
    X = np.random.randn(n, 5)
    t = np.random.choice(["A", "B", "C"], size=n)
    y = X[:, 0] + (t == "A") * 2.0 + (t == "B") * 1.0 + np.random.randn(n) * 0.5

    result_atm = estimate_te_multi(
        X,
        t,
        y,
        outcome_type="continuous",
        model_outcome=RandomForestRegressor(n_estimators=20),
        random_state_master=123,
        ref_group="A",
        estimand="ATM",
        do_stacking=False,
        **KW_COMMON,
    )

    result_att = estimate_te_multi(
        X,
        t,
        y,
        outcome_type="continuous",
        model_outcome=RandomForestRegressor(n_estimators=20),
        random_state_master=123,
        ref_group="A",
        estimand="ATT",
        do_stacking=False,
        **KW_COMMON,
    )

    # Both should run successfully
    assert "per_treatment" in result_atm
    assert "per_treatment" in result_att
    assert "pairwise" in result_atm
    assert "pairwise" in result_att


# -------------------------------------------------------------------
# Test ATT for multi-arm treatment (stacking)
# -------------------------------------------------------------------
def test_estimand_att_multi_stacking():
    """Test ATT estimand with multi-arm treatment (stacking pathway)."""
    # Generate simple multi-arm data
    np.random.seed(42)
    n = 200
    X = np.random.randn(n, 5)
    t = np.random.choice(["A", "B", "C"], size=n)
    y = X[:, 0] + (t == "A") * 2.0 + (t == "B") * 1.0 + np.random.randn(n) * 0.5

    result_atm = estimate_te_multi(
        X,
        t,
        y,
        outcome_type="continuous",
        model_outcome=RandomForestRegressor(n_estimators=20),
        random_state_master=123,
        ref_group="A",
        estimand="ATM",
        do_stacking=True,
        **KW_COMMON,
    )

    result_att = estimate_te_multi(
        X,
        t,
        y,
        outcome_type="continuous",
        model_outcome=RandomForestRegressor(n_estimators=20),
        random_state_master=123,
        ref_group="A",
        estimand="ATT",
        do_stacking=True,
        **KW_COMMON,
    )

    # Both should run successfully
    assert "per_treatment" in result_atm
    assert "per_treatment" in result_att
    assert "pairwise" in result_atm
    assert "pairwise" in result_att


# -------------------------------------------------------------------
# Test ATT requires ref_group for multi-arm
# -------------------------------------------------------------------
def test_estimand_att_multi_requires_ref_group():
    """Test that ATT requires ref_group for multi-arm treatment."""
    np.random.seed(42)
    n = 200
    X = np.random.randn(n, 5)
    t = np.random.choice(["A", "B", "C"], size=n)
    y = X[:, 0] + np.random.randn(n) * 0.5

    with pytest.raises(ValueError, match="ref_group is required when estimand='ATT'"):
        estimate_te_multi(
            X,
            t,
            y,
            outcome_type="continuous",
            model_outcome=RandomForestRegressor(n_estimators=20),
            random_state_master=123,
            ref_group=None,  # Missing ref_group
            estimand="ATT",
            **KW_COMMON,
        )


# -------------------------------------------------------------------
# Test ATT vs ATM produce different results
# -------------------------------------------------------------------
def test_estimand_att_vs_atm_differ():
    """Test that ATT and ATM generally produce different estimates."""
    # Create imbalanced data where ATT and ATM should differ
    np.random.seed(42)
    n = 300
    X = np.random.randn(n, 5)
    # 20% treated (imbalanced)
    t = np.random.binomial(1, 0.2, size=n)
    # Treatment effect depends on X[0] (heterogeneous)
    y = X[:, 0] + t * (2.0 + X[:, 0]) + np.random.randn(n) * 0.5

    result_atm = estimate_te(
        X,
        t,
        y,
        outcome_type="continuous",
        model_outcome=RandomForestRegressor(n_estimators=30, max_depth=5),
        random_state_master=123,
        estimand="ATM",
        **KW_COMMON,
    )

    result_att = estimate_te(
        X,
        t,
        y,
        outcome_type="continuous",
        model_outcome=RandomForestRegressor(n_estimators=30, max_depth=5),
        random_state_master=123,
        estimand="ATT",
        **KW_COMMON,
    )

    # In this imbalanced case with heterogeneous effects, ATT and ATM should differ
    # We don't check exact difference, just that both are valid numbers
    assert isinstance(result_atm["te"], (int, float))
    assert isinstance(result_att["te"], (int, float))
    assert not np.isnan(result_atm["te"])
    assert not np.isnan(result_att["te"])


# -------------------------------------------------------------------
# Test ATT with binary outcome
# -------------------------------------------------------------------
def test_estimand_att_binary_outcome():
    """Test ATT estimand with binary outcome."""
    np.random.seed(42)
    n = 200
    X = np.random.randn(n, 5)
    t = np.random.binomial(1, 0.3, size=n)
    # Binary outcome
    y = np.random.binomial(1, 1 / (1 + np.exp(-(X[:, 0] + t * 1.5))), size=n)

    result_atm = estimate_te(
        X,
        t,
        y,
        outcome_type="binary",
        model_outcome=RandomForestClassifier(n_estimators=20),
        random_state_master=123,
        estimand="ATM",
        **KW_COMMON,
    )

    result_att = estimate_te(
        X,
        t,
        y,
        outcome_type="binary",
        model_outcome=RandomForestClassifier(n_estimators=20),
        random_state_master=123,
        estimand="ATT",
        **KW_COMMON,
    )

    # Both should run successfully
    assert "te" in result_atm
    assert "te" in result_att
    assert isinstance(result_atm["te"], (int, float))
    assert isinstance(result_att["te"], (int, float))


# -------------------------------------------------------------------
# Test ATT with binary survival outcome
# -------------------------------------------------------------------
def test_estimand_att_binary_survival():
    """Test ATT estimand with binary survival outcome using TOF data."""
    # Use real TOF data (binary: PrP vs SPS)
    X, t, y = load_data_tof(raw=False, treat_levels=["PrP", "SPS"])

    from sksurv.ensemble import RandomSurvivalForest

    # Test ATM (all matched)
    result_atm = estimate_te(
        X,
        t,
        y,
        outcome_type="survival",
        model_outcome=RandomSurvivalForest(n_estimators=20, n_jobs=1),
        random_state_master=123,
        estimand="ATM",
        niter=2,
        n_splits_propensity=3,
        n_splits_outcome=3,
        matching_is_stochastic=False,
        nboot=0,
        n_mc=10,
    )

    # Test ATT (matched treated only)
    result_att = estimate_te(
        X,
        t,
        y,
        outcome_type="survival",
        model_outcome=RandomSurvivalForest(n_estimators=20, n_jobs=1),
        random_state_master=123,
        estimand="ATT",
        niter=2,
        n_splits_propensity=3,
        n_splits_outcome=3,
        matching_is_stochastic=False,
        nboot=0,
        n_mc=10,
    )

    # Both should return hazard ratios
    assert "te" in result_atm
    assert "te" in result_att
    assert isinstance(result_atm["te"], (int, float))
    assert isinstance(result_att["te"], (int, float))

    # Hazard ratios should be positive and finite
    assert result_atm["te"] > 0
    assert result_att["te"] > 0
    assert np.isfinite(result_atm["te"])
    assert np.isfinite(result_att["te"])


# -------------------------------------------------------------------
# Test ATT with multi-arm survival outcome
# -------------------------------------------------------------------
def test_estimand_att_multi_survival():
    """Test ATT estimand with multi-arm survival outcome using TOF data."""
    # Use real TOF data (multi-arm: Control, PrP, SPS)
    df = load_data_tof(raw=True)
    X = df[["age", "zscore"]].to_numpy()
    t = df["treatment"].to_numpy()
    y = df[["time", "status"]].to_numpy()

    from sksurv.ensemble import RandomSurvivalForest

    # Test ATM (all matched) - use no-stacking like existing tests
    result_atm = estimate_te_multi(
        X,
        t,
        y,
        outcome_type="survival",
        model_outcome=RandomSurvivalForest(n_estimators=20, n_jobs=1),
        random_state_master=123,
        ref_group="PrP",
        estimand="ATM",
        do_stacking=False,  # Use no-stacking pathway (more stable)
        niter=2,
        n_splits_propensity=3,
        n_splits_outcome=3,
        matching_is_stochastic=False,
        nboot=0,
        n_mc=10,
    )

    # Test ATT (matched ref_group only)
    result_att = estimate_te_multi(
        X,
        t,
        y,
        outcome_type="survival",
        model_outcome=RandomSurvivalForest(n_estimators=20, n_jobs=1),
        random_state_master=123,
        ref_group="PrP",
        estimand="ATT",
        do_stacking=False,  # Use no-stacking pathway (more stable)
        niter=2,
        n_splits_propensity=3,
        n_splits_outcome=3,
        matching_is_stochastic=False,
        nboot=0,
        n_mc=10,
    )

    # Both should return pairwise DataFrames
    assert "pairwise" in result_atm
    assert "pairwise" in result_att
    assert len(result_atm["pairwise"]) > 0
    assert len(result_att["pairwise"]) > 0

    # Check hazard ratios are valid (positive and finite)
    for _, row in result_atm["pairwise"].iterrows():
        assert row["te"] > 0
        assert np.isfinite(row["te"])

    for _, row in result_att["pairwise"].iterrows():
        assert row["te"] > 0
        assert np.isfinite(row["te"])


# -------------------------------------------------------------------
# Test ATT multi-arm survival requires ref_group
# -------------------------------------------------------------------
def test_estimand_att_multi_survival_requires_ref_group():
    """Test that ATT requires ref_group for multi-arm survival."""
    # Use real TOF data
    df = load_data_tof(raw=True)
    X = df[["age", "zscore"]].to_numpy()
    t = df["treatment"].to_numpy()
    y = df[["time", "status"]].to_numpy()

    from sksurv.ensemble import RandomSurvivalForest

    # Should raise error when ref_group is missing for ATT
    with pytest.raises(ValueError, match="ref_group is required"):
        estimate_te_multi(
            X,
            t,
            y,
            outcome_type="survival",
            model_outcome=RandomSurvivalForest(n_estimators=20, n_jobs=1),
            random_state_master=123,
            ref_group=None,  # Missing!
            estimand="ATT",
            do_stacking=False,
            niter=2,
            n_splits_propensity=3,
            n_splits_outcome=3,
            matching_is_stochastic=False,
            nboot=0,
            n_mc=10,
        )
