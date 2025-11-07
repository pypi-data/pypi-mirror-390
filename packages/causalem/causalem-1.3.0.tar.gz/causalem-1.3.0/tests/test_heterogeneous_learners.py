"""
Tests for heterogeneous learner support in estimate_te.

This module tests the ability to provide lists, tuples, or generators of
different estimators for the model_outcome parameter, creating heterogeneous
ensembles where each iteration uses a different base learner.
"""

import numpy as np
import pytest
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sksurv.ensemble import RandomSurvivalForest
from sksurv.linear_model import CoxPHSurvivalAnalysis

from causalem import estimate_te, load_data_lalonde, load_data_tof
from causalem.estimation.ensemble import estimate_te_multi

# -------------------------------------------------------------------
# Shared test configuration
# -------------------------------------------------------------------
KW_COMMON = dict(
    niter=1,
    n_splits_propensity=3,
    n_splits_outcome=3,
    matching_is_stochastic=False,
    matching_scale=1.0,
    matching_caliper=None,
)


# -------------------------------------------------------------------
# Basic functionality tests
# -------------------------------------------------------------------
class TestBasicHeterogeneousSupport:
    """Test basic heterogeneous learner input types."""

    def test_single_model_backward_compatibility(self):
        """Test that single models still work (backward compatibility)."""
        X, t, y = load_data_lalonde(raw=False)

        result = estimate_te(
            X,
            t,
            y,
            outcome_type="continuous",
            model_outcome=RandomForestRegressor(n_estimators=10),
            random_state_master=42,
            **KW_COMMON,
        )

        assert "te" in result
        assert np.isfinite(result["te"])
        assert "matching" in result
        assert result["matching"].shape == (X.shape[0], 1)

    def test_list_input(self):
        """Test that list input works."""
        X, t, y = load_data_lalonde(raw=False)

        outcome_models = [
            RandomForestRegressor(n_estimators=10, max_depth=3),
            RandomForestRegressor(n_estimators=10, max_depth=5),
            LinearRegression(),
        ]

        result = estimate_te(
            X,
            t,
            y,
            outcome_type="continuous",
            model_outcome=outcome_models,
            niter=3,
            random_state_master=42,
            n_splits_propensity=3,
            n_splits_outcome=3,
            matching_is_stochastic=False,
        )

        assert "te" in result
        assert np.isfinite(result["te"])
        assert result["matching"].shape == (X.shape[0], 3)

    def test_tuple_input(self):
        """Test that tuple input works (not just list)."""
        X, t, y = load_data_lalonde(raw=False)

        outcome_models = (
            RandomForestRegressor(n_estimators=10),
            LinearRegression(),
        )

        result = estimate_te(
            X,
            t,
            y,
            outcome_type="continuous",
            model_outcome=outcome_models,
            niter=2,
            random_state_master=42,
            n_splits_propensity=3,
            n_splits_outcome=3,
            matching_is_stochastic=False,
        )

        assert "te" in result
        assert np.isfinite(result["te"])
        assert result["matching"].shape == (X.shape[0], 2)

    def test_generator_input(self):
        """Test generator/iterator input for models."""
        X, t, y = load_data_lalonde(raw=False)

        def outcome_generator():
            yield RandomForestRegressor(n_estimators=10, max_depth=3)
            yield RandomForestRegressor(n_estimators=10, max_depth=5)
            yield LinearRegression()

        result = estimate_te(
            X,
            t,
            y,
            outcome_type="continuous",
            model_outcome=outcome_generator(),
            niter=3,
            random_state_master=42,
            n_splits_propensity=3,
            n_splits_outcome=3,
            matching_is_stochastic=False,
        )

        assert "te" in result
        assert np.isfinite(result["te"])
        assert result["matching"].shape == (X.shape[0], 3)


# -------------------------------------------------------------------
# Tests across outcome types
# -------------------------------------------------------------------
class TestHeterogeneousAcrossOutcomeTypes:
    """Test heterogeneous learners with different outcome types."""

    def test_continuous_outcome(self):
        """Test list of models with continuous outcome."""
        X, t, y = load_data_lalonde(raw=False)

        outcome_models = [
            RandomForestRegressor(n_estimators=10, max_depth=3),
            RandomForestRegressor(n_estimators=10, max_depth=5),
            LinearRegression(),
        ]

        result = estimate_te(
            X,
            t,
            y,
            outcome_type="continuous",
            model_outcome=outcome_models,
            niter=3,
            random_state_master=42,
            n_splits_propensity=3,
            n_splits_outcome=3,
            matching_is_stochastic=False,
        )

        assert "te" in result
        assert np.isfinite(result["te"])

    def test_binary_outcome(self):
        """Test list of models with binary outcome."""
        X, t, y = load_data_lalonde(raw=False)
        y_bin = (y > 3700).astype(int)

        outcome_models = [
            RandomForestClassifier(n_estimators=10, max_depth=3),
            RandomForestClassifier(n_estimators=10, max_depth=5),
            LogisticRegression(max_iter=500),
        ]

        result = estimate_te(
            X,
            t,
            y_bin,
            outcome_type="binary",
            model_outcome=outcome_models,
            niter=3,
            random_state_master=42,
            n_splits_propensity=3,
            n_splits_outcome=3,
            matching_is_stochastic=False,
        )

        assert "te" in result
        assert np.isfinite(result["te"])
        assert -1.0 <= result["te"] <= 1.0

    def test_survival_outcome(self):
        """Test list of models with survival outcome."""
        X, t, y = load_data_tof(raw=False, treat_levels=["PrP", "SPS"])

        outcome_models = [
            RandomSurvivalForest(n_estimators=50, max_depth=3, n_jobs=1),
            RandomSurvivalForest(n_estimators=50, max_depth=5, n_jobs=1),
            CoxPHSurvivalAnalysis(),
        ]

        result = estimate_te(
            X,
            t,
            y,
            outcome_type="survival",
            model_outcome=outcome_models,
            niter=3,
            random_state_master=42,
            n_splits_propensity=3,
            n_splits_outcome=3,
            matching_is_stochastic=False,
        )

        assert "te" in result
        assert np.isfinite(result["te"])
        assert result["te"] > 0  # HR should be positive


# -------------------------------------------------------------------
# Multi-arm treatment tests
# -------------------------------------------------------------------
class TestHeterogeneousMultiArm:
    """Test heterogeneous learners with multi-arm treatments."""

    def test_multi_arm_binary_outcome(self):
        """Test list of models with multi-arm treatment (binary outcome)."""
        df = load_data_tof(raw=True, outcome_type="binary")
        X = df[["age", "zscore"]].to_numpy()
        t = df["treatment"].to_numpy()  # 3 levels: PrP, SPS, RVOTd
        y = df["outcome"].to_numpy()

        outcome_models = [
            RandomForestClassifier(n_estimators=10, max_depth=3),
            RandomForestClassifier(n_estimators=10, max_depth=5),
        ]

        result = estimate_te(
            X,
            t,
            y,
            outcome_type="binary",
            model_outcome=outcome_models,
            ref_group="PrP",
            niter=2,
            random_state_master=42,
            n_splits_propensity=3,
            n_splits_outcome=3,
            matching_is_stochastic=False,
        )

        assert "per_treatment" in result
        assert "pairwise" in result
        assert result["pairwise"].shape[0] == 3  # 3 pairwise comparisons
        assert np.all(np.isfinite(result["pairwise"]["te"]))

    @pytest.mark.xfail(
        reason="Cox meta-learner can have numerical instability on some platforms",
        strict=False,
    )
    def test_multi_arm_survival_outcome(self):
        """Test list of models with multi-arm treatment (survival outcome).

        Note: This test uses Cox proportional hazards as the meta-learner (default),
        which can encounter LAPACK numerical errors on some platforms (especially Linux)
        when the survival predictions are not sufficiently smooth. Marked as xfail
        to acknowledge this known issue without blocking CI.
        """
        df = load_data_tof(raw=True)
        X = df[["age", "zscore"]].to_numpy()
        t = df["treatment"].to_numpy()
        y = df[["time", "status"]].to_numpy()

        outcome_models = [
            RandomSurvivalForest(n_estimators=50, max_depth=3, n_jobs=1),
            RandomSurvivalForest(n_estimators=50, max_depth=5, n_jobs=1),
        ]

        result = estimate_te_multi(
            X,
            t,
            y,
            outcome_type="survival",
            model_outcome=outcome_models,
            ref_group="PrP",
            niter=2,
            random_state_master=42,
            n_splits_propensity=3,
            n_splits_outcome=3,
            matching_is_stochastic=False,
        )

        assert "pairwise" in result
        assert result["pairwise"].shape[0] == 3
        assert np.all(result["pairwise"]["te"] > 0)  # HRs positive


# -------------------------------------------------------------------
# Error handling tests
# -------------------------------------------------------------------
class TestHeterogeneousErrorHandling:
    """Test error handling for heterogeneous learners."""

    def test_insufficient_models_in_list(self):
        """Test error when list has insufficient models for niter."""
        X, t, y = load_data_lalonde(raw=False)

        outcome_models = [RandomForestRegressor(n_estimators=10)]  # Only 1 model

        with pytest.raises(ValueError, match="model_outcome.*shorter than niter"):
            estimate_te(
                X,
                t,
                y,
                outcome_type="continuous",
                model_outcome=outcome_models,
                niter=3,  # Need 3 models
                random_state_master=42,
                n_splits_propensity=3,
                n_splits_outcome=3,
                matching_is_stochastic=False,
            )

    def test_generator_exhaustion(self):
        """Test error when generator yields fewer models than niter."""
        X, t, y = load_data_lalonde(raw=False)

        def outcome_generator():
            yield RandomForestRegressor(n_estimators=10)
            # Only yields 1 model

        with pytest.raises(
            ValueError, match="Generator.*yielded fewer than niter estimators"
        ):
            estimate_te(
                X,
                t,
                y,
                outcome_type="continuous",
                model_outcome=outcome_generator(),
                niter=3,  # Need 3 models
                random_state_master=42,
                n_splits_propensity=3,
                n_splits_outcome=3,
                matching_is_stochastic=False,
            )

    def test_empty_list_error(self):
        """Test error when empty list is provided."""
        X, t, y = load_data_lalonde(raw=False)

        with pytest.raises(ValueError, match="model_outcome.*shorter than niter"):
            estimate_te(
                X,
                t,
                y,
                outcome_type="continuous",
                model_outcome=[],  # Empty list
                niter=1,
                random_state_master=42,
                n_splits_propensity=3,
                n_splits_outcome=3,
                matching_is_stochastic=False,
            )


# -------------------------------------------------------------------
# Reproducibility tests
# -------------------------------------------------------------------
class TestHeterogeneousReproducibility:
    """Test reproducibility with heterogeneous learners."""

    def test_reproducibility_with_same_seed(self):
        """Test that results are reproducible with same random state."""
        X, t, y = load_data_lalonde(raw=False)

        outcome_models = [
            RandomForestRegressor(n_estimators=10, max_depth=3),
            RandomForestRegressor(n_estimators=10, max_depth=5),
        ]

        result1 = estimate_te(
            X,
            t,
            y,
            outcome_type="continuous",
            model_outcome=outcome_models,
            niter=2,
            random_state_master=123,
            n_splits_propensity=3,
            n_splits_outcome=3,
            matching_is_stochastic=False,
        )

        result2 = estimate_te(
            X,
            t,
            y,
            outcome_type="continuous",
            model_outcome=outcome_models,
            niter=2,
            random_state_master=123,
            n_splits_propensity=3,
            n_splits_outcome=3,
            matching_is_stochastic=False,
        )

        assert result1["te"] == result2["te"]
        assert np.array_equal(result1["matching"], result2["matching"])

    def test_different_results_with_different_seed(self):
        """Test that results differ with different random states."""
        X, t, y = load_data_lalonde(raw=False)

        outcome_models = [
            RandomForestRegressor(n_estimators=10, max_depth=3),
            RandomForestRegressor(n_estimators=10, max_depth=5),
        ]

        result1 = estimate_te(
            X,
            t,
            y,
            outcome_type="continuous",
            model_outcome=outcome_models,
            niter=2,
            random_state_master=42,
            n_splits_propensity=3,
            n_splits_outcome=3,
            matching_is_stochastic=False,
        )

        result2 = estimate_te(
            X,
            t,
            y,
            outcome_type="continuous",
            model_outcome=outcome_models,
            niter=2,
            random_state_master=999,
            n_splits_propensity=3,
            n_splits_outcome=3,
            matching_is_stochastic=False,
        )

        # Different seeds should yield different results
        assert result1["te"] != result2["te"]


# -------------------------------------------------------------------
# Integration with other features
# -------------------------------------------------------------------
class TestHeterogeneousIntegration:
    """Test heterogeneous learners with other estimate_te features."""

    def test_with_bootstrap_ci(self):
        """Test list models with bootstrap confidence intervals."""
        X, t, y = load_data_lalonde(raw=False)

        outcome_models = [
            RandomForestRegressor(n_estimators=10),
            LinearRegression(),
        ]

        result = estimate_te(
            X,
            t,
            y,
            outcome_type="continuous",
            model_outcome=outcome_models,
            niter=2,
            nboot=5,
            random_state_master=42,
            random_state_boot=99,
            n_jobs=1,
            n_splits_propensity=3,
            n_splits_outcome=3,
            matching_is_stochastic=False,
        )

        assert "te" in result
        assert "ci" in result
        assert "boot" in result
        assert len(result["boot"]) == 5
        assert result["ci"][0] <= result["te"] <= result["ci"][1]

    def test_with_stacking_enabled(self):
        """Test list models with do_stacking=True (meta-learner)."""
        X, t, y = load_data_lalonde(raw=False)

        outcome_models = [
            RandomForestRegressor(n_estimators=10, max_depth=3),
            RandomForestRegressor(n_estimators=10, max_depth=5),
            LinearRegression(),
        ]

        result = estimate_te(
            X,
            t,
            y,
            outcome_type="continuous",
            model_outcome=outcome_models,
            niter=3,
            do_stacking=True,
            random_state_master=42,
            n_splits_propensity=3,
            n_splits_outcome=3,
            matching_is_stochastic=False,
        )

        assert "te" in result
        assert np.isfinite(result["te"])

    def test_with_stacking_disabled(self):
        """Test list models with do_stacking=False (simple averaging)."""
        X, t, y = load_data_lalonde(raw=False)

        outcome_models = [
            RandomForestRegressor(n_estimators=10, max_depth=3),
            RandomForestRegressor(n_estimators=10, max_depth=5),
        ]

        result = estimate_te(
            X,
            t,
            y,
            outcome_type="continuous",
            model_outcome=outcome_models,
            niter=2,
            do_stacking=False,
            random_state_master=42,
            n_splits_propensity=3,
            n_splits_outcome=3,
            matching_is_stochastic=False,
        )

        assert "te" in result
        assert np.isfinite(result["te"])

    def test_with_covariates_in_stacking(self):
        """Test list models with include_covariates_in_stacking=True."""
        X, t, y = load_data_lalonde(raw=False)

        outcome_models = [
            RandomForestRegressor(n_estimators=10, max_depth=3),
            RandomForestRegressor(n_estimators=10, max_depth=5),
            LinearRegression(),
        ]

        result = estimate_te(
            X,
            t,
            y,
            outcome_type="continuous",
            model_outcome=outcome_models,
            niter=3,
            include_covariates_in_stacking=True,
            random_state_master=42,
            n_splits_propensity=3,
            n_splits_outcome=3,
            matching_is_stochastic=False,
        )

        assert "te" in result
        assert np.isfinite(result["te"])

    def test_with_att_estimand(self):
        """Test heterogeneous learners with estimand='ATT'."""
        X, t, y = load_data_lalonde(raw=False)

        outcome_models = [
            RandomForestRegressor(n_estimators=10, max_depth=3),
            RandomForestRegressor(n_estimators=10, max_depth=5),
        ]

        result = estimate_te(
            X,
            t,
            y,
            outcome_type="continuous",
            model_outcome=outcome_models,
            niter=2,
            estimand="ATT",
            random_state_master=42,
            n_splits_propensity=3,
            n_splits_outcome=3,
            matching_is_stochastic=False,
        )

        assert "te" in result
        assert np.isfinite(result["te"])

    def test_with_stochastic_matching(self):
        """Test heterogeneous learners with stochastic matching."""
        X, t, y = load_data_lalonde(raw=False)

        outcome_models = [
            RandomForestRegressor(n_estimators=10, max_depth=3),
            RandomForestRegressor(n_estimators=10, max_depth=5),
        ]

        result = estimate_te(
            X,
            t,
            y,
            outcome_type="continuous",
            model_outcome=outcome_models,
            niter=2,
            matching_is_stochastic=True,
            matching_scale=1.0,
            random_state_master=42,
            n_splits_propensity=3,
            n_splits_outcome=3,
        )

        assert "te" in result
        assert np.isfinite(result["te"])


# -------------------------------------------------------------------
# Comparison tests
# -------------------------------------------------------------------
class TestHeterogeneousVsHomogeneous:
    """Compare heterogeneous vs homogeneous ensembles."""

    def test_heterogeneous_differs_from_homogeneous(self):
        """Test that heterogeneous ensemble differs from homogeneous."""
        X, t, y = load_data_lalonde(raw=False)

        # Homogeneous: Same model repeated
        result_homogeneous = estimate_te(
            X,
            t,
            y,
            outcome_type="continuous",
            model_outcome=RandomForestRegressor(n_estimators=10, max_depth=3),
            niter=3,
            random_state_master=42,
            n_splits_propensity=3,
            n_splits_outcome=3,
            matching_is_stochastic=False,
        )

        # Heterogeneous: Different models
        outcome_models = [
            RandomForestRegressor(n_estimators=10, max_depth=3),
            RandomForestRegressor(n_estimators=10, max_depth=5),
            LinearRegression(),
        ]

        result_heterogeneous = estimate_te(
            X,
            t,
            y,
            outcome_type="continuous",
            model_outcome=outcome_models,
            niter=3,
            random_state_master=42,
            n_splits_propensity=3,
            n_splits_outcome=3,
            matching_is_stochastic=False,
        )

        # Results should be different (sanity check)
        # Same seed but different models should yield different results
        assert result_homogeneous["te"] != result_heterogeneous["te"]

    def test_list_of_same_model_matches_single_model(self):
        """Test that list of identical models behaves like single model."""
        X, t, y = load_data_lalonde(raw=False)

        # Single model (cloned niter times internally)
        result_single = estimate_te(
            X,
            t,
            y,
            outcome_type="continuous",
            model_outcome=RandomForestRegressor(n_estimators=10, max_depth=5),
            niter=3,
            random_state_master=42,
            n_splits_propensity=3,
            n_splits_outcome=3,
            matching_is_stochastic=False,
        )

        # List of same models
        outcome_models = [
            RandomForestRegressor(n_estimators=10, max_depth=5),
            RandomForestRegressor(n_estimators=10, max_depth=5),
            RandomForestRegressor(n_estimators=10, max_depth=5),
        ]

        result_list = estimate_te(
            X,
            t,
            y,
            outcome_type="continuous",
            model_outcome=outcome_models,
            niter=3,
            random_state_master=42,
            n_splits_propensity=3,
            n_splits_outcome=3,
            matching_is_stochastic=False,
        )

        # Should produce identical results
        assert result_single["te"] == result_list["te"]
        assert np.array_equal(result_single["matching"], result_list["matching"])
