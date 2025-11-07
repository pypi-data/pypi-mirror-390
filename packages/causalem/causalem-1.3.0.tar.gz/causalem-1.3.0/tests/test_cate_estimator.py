"""
Tests for experimental CATE estimator.

These tests ensure the MatchingCATEEstimator produces results consistent with
the existing estimate_te() function, while also testing CATE-specific functionality.
"""

import numpy as np
import pytest
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression

from causalem import estimate_te, load_data_lalonde

# Mark all tests in this module as experimental
pytestmark = pytest.mark.experimental


# ------------------------------------------------------------------ #
# Basic instantiation and validation
# ------------------------------------------------------------------ #


def test_cate_estimator_imports():
    """Test that the experimental CATE estimator can be imported."""
    from causalem._experimental import MatchingCATEEstimator

    assert MatchingCATEEstimator is not None


def test_cate_estimator_init():
    """Test CATE estimator initialization with various parameters."""
    from causalem._experimental import MatchingCATEEstimator

    # Default initialization
    est = MatchingCATEEstimator()
    assert est.niter == 10
    assert est.matching_is_stochastic is True
    assert est.do_stacking is True

    # Custom initialization
    est = MatchingCATEEstimator(
        niter=5,
        matching_is_stochastic=False,
        do_stacking=False,
        random_state=42,
    )
    assert est.niter == 5
    assert est.matching_is_stochastic is False
    assert est.do_stacking is False
    assert est.random_state == 42


def test_cate_estimator_validates_binary_treatment():
    """Test that non-binary treatment raises an error."""
    from causalem._experimental import MatchingCATEEstimator

    X, t, y = load_data_lalonde(raw=False)

    # Multi-level treatment should fail
    t_multi = np.repeat([0, 1, 2], len(t) // 3 + 1)[: len(t)]

    est = MatchingCATEEstimator(random_state=42)

    with pytest.raises(ValueError, match="binary treatment"):
        est.fit(X, t_multi, y)


def test_cate_estimator_not_fitted_error():
    """Test that methods raise error when called before fit."""
    from causalem._experimental import MatchingCATEEstimator

    est = MatchingCATEEstimator(random_state=42)

    with pytest.raises(ValueError, match="not fitted"):
        est.effect()

    with pytest.raises(ValueError, match="not fitted"):
        est.ate()

    with pytest.raises(ValueError, match="not fitted"):
        est.att()


# ------------------------------------------------------------------ #
# Validation against estimate_te() - CRITICAL TESTS
# ------------------------------------------------------------------ #


def test_cate_ate_matches_estimate_te_continuous():
    """
    CRITICAL: Verify CATE.ate() produces same result as estimate_te()['te'].

    This test ensures the new class-based API is numerically equivalent to
    the existing functional API for continuous outcomes.
    """
    from causalem._experimental import MatchingCATEEstimator

    X, t, y = load_data_lalonde(raw=False)

    # Function API
    result_func = estimate_te(
        X,
        t,
        y,
        outcome_type="continuous",
        model_outcome=RandomForestRegressor(n_estimators=20),
        niter=3,
        n_splits_propensity=3,
        n_splits_outcome=3,
        matching_is_stochastic=False,
        do_stacking=True,
        random_state_master=42,
    )

    # Class API
    est = MatchingCATEEstimator(
        outcome_type="continuous",
        model_outcome=RandomForestRegressor(n_estimators=20),
        niter=3,
        n_splits_propensity=3,
        n_splits_outcome=3,
        matching_is_stochastic=False,
        do_stacking=True,
        random_state=42,
    )
    est.fit(X, t, y)

    # Results should match within numerical tolerance
    assert np.isclose(est.ate(), result_func["te"], rtol=1e-5, atol=1e-8)


def test_cate_ate_matches_estimate_te_binary():
    """Verify CATE.ate() matches estimate_te() for binary outcomes."""
    from causalem._experimental import MatchingCATEEstimator

    X, t, y = load_data_lalonde(raw=False)
    y_bin = (y > 3700).astype(int)

    # Function API
    result_func = estimate_te(
        X,
        t,
        y_bin,
        outcome_type="binary",
        model_outcome=RandomForestClassifier(n_estimators=20),
        niter=3,
        n_splits_propensity=3,
        n_splits_outcome=3,
        matching_is_stochastic=False,
        do_stacking=True,
        random_state_master=42,
    )

    # Class API
    est = MatchingCATEEstimator(
        outcome_type="binary",
        model_outcome=RandomForestClassifier(n_estimators=20),
        niter=3,
        n_splits_propensity=3,
        n_splits_outcome=3,
        matching_is_stochastic=False,
        do_stacking=True,
        random_state=42,
    )
    est.fit(X, t, y_bin)

    assert np.isclose(est.ate(), result_func["te"], rtol=1e-5, atol=1e-8)


def test_cate_att_matches_estimate_te():
    """Verify CATE.att() matches estimate_te() with estimand='ATT'."""
    from causalem._experimental import MatchingCATEEstimator

    X, t, y = load_data_lalonde(raw=False)

    # Function API with ATT
    result_func = estimate_te(
        X,
        t,
        y,
        outcome_type="continuous",
        niter=3,
        n_splits_propensity=3,
        n_splits_outcome=3,
        matching_is_stochastic=False,
        estimand="ATT",
        random_state_master=42,
    )

    # Class API with ATT
    est = MatchingCATEEstimator(
        outcome_type="continuous",
        niter=3,
        n_splits_propensity=3,
        n_splits_outcome=3,
        matching_is_stochastic=False,
        estimand="ATT",
        random_state=42,
    )
    est.fit(X, t, y)

    assert np.isclose(est.att(), result_func["te"], rtol=1e-5, atol=1e-8)


def test_cate_no_stacking_matches_estimate_te():
    """Verify CATE matches estimate_te() when do_stacking=False."""
    from causalem._experimental import MatchingCATEEstimator

    X, t, y = load_data_lalonde(raw=False)

    # Function API without stacking
    result_func = estimate_te(
        X,
        t,
        y,
        outcome_type="continuous",
        niter=3,
        n_splits_propensity=3,
        n_splits_outcome=3,
        matching_is_stochastic=False,
        do_stacking=False,
        random_state_master=42,
    )

    # Class API without stacking
    est = MatchingCATEEstimator(
        outcome_type="continuous",
        niter=3,
        n_splits_propensity=3,
        n_splits_outcome=3,
        matching_is_stochastic=False,
        do_stacking=False,
        random_state=42,
    )
    est.fit(X, t, y)

    assert np.isclose(est.ate(), result_func["te"], rtol=1e-5, atol=1e-8)


def test_cate_stochastic_matching_matches_estimate_te():
    """Verify CATE matches estimate_te() with stochastic matching."""
    from causalem._experimental import MatchingCATEEstimator

    X, t, y = load_data_lalonde(raw=False)

    # Function API with stochastic matching
    result_func = estimate_te(
        X,
        t,
        y,
        outcome_type="continuous",
        niter=3,
        n_splits_propensity=3,
        n_splits_outcome=3,
        matching_is_stochastic=True,
        matching_scale=1.0,
        do_stacking=True,
        random_state_master=42,
    )

    # Class API with stochastic matching
    est = MatchingCATEEstimator(
        outcome_type="continuous",
        niter=3,
        n_splits_propensity=3,
        n_splits_outcome=3,
        matching_is_stochastic=True,
        matching_scale=1.0,
        do_stacking=True,
        random_state=42,
    )
    est.fit(X, t, y)

    assert np.isclose(est.ate(), result_func["te"], rtol=1e-5, atol=1e-8)


# ------------------------------------------------------------------ #
# CATE-specific functionality tests
# ------------------------------------------------------------------ #


def test_cate_effect_returns_individual_effects():
    """Test that effect() returns individual-level predictions."""
    from causalem._experimental import MatchingCATEEstimator

    X, t, y = load_data_lalonde(raw=False)

    est = MatchingCATEEstimator(niter=3, random_state=42)
    est.fit(X, t, y)

    effects = est.effect()

    # Should return array of same length as training data
    assert effects.shape == (X.shape[0],)
    assert np.all(np.isfinite(effects))

    # Effects should show heterogeneity (not all identical)
    assert np.std(effects) > 0


@pytest.mark.skip(reason="Implementation not yet complete")
def test_cate_effect_on_new_data():
    """Test that effect(X_new) works on new observations."""
    from causalem._experimental import MatchingCATEEstimator

    X, t, y = load_data_lalonde(raw=False)

    # Split data
    n_train = int(0.7 * len(X))
    X_train, X_test = X[:n_train], X[n_train:]
    t_train, y_train = t[:n_train], y[:n_train]

    est = MatchingCATEEstimator(niter=3, random_state=42)
    est.fit(X_train, t_train, y_train)

    # Predict on test data
    effects_test = est.effect(X_test)

    assert effects_test.shape == (X_test.shape[0],)
    assert np.all(np.isfinite(effects_test))


def test_cate_reproducibility():
    """Test that same random state gives identical results."""
    from causalem._experimental import MatchingCATEEstimator

    X, t, y = load_data_lalonde(raw=False)

    est1 = MatchingCATEEstimator(niter=3, random_state=42)
    est1.fit(X, t, y)
    effects1 = est1.effect()
    ate1 = est1.ate()

    est2 = MatchingCATEEstimator(niter=3, random_state=42)
    est2.fit(X, t, y)
    effects2 = est2.effect()
    ate2 = est2.ate()

    # Should be bit-identical
    assert np.array_equal(effects1, effects2)
    assert ate1 == ate2


@pytest.mark.skip(reason="Implementation not yet complete")
def test_cate_heterogeneous_learners():
    """Test CATE with heterogeneous base learners."""
    from causalem._experimental import MatchingCATEEstimator

    X, t, y = load_data_lalonde(raw=False)

    learners = [
        RandomForestRegressor(n_estimators=20, max_depth=3),
        RandomForestRegressor(n_estimators=20, max_depth=5),
        LinearRegression(),
    ]

    est = MatchingCATEEstimator(
        model_outcome=learners, niter=3, do_stacking=True, random_state=42
    )
    est.fit(X, t, y)

    effects = est.effect()
    assert effects.shape == (X.shape[0],)
    assert np.all(np.isfinite(effects))


@pytest.mark.skip(reason="Implementation not yet complete")
def test_cate_with_covariates_in_stacking():
    """Test CATE with include_covariates_in_stacking=True."""
    from causalem._experimental import MatchingCATEEstimator

    X, t, y = load_data_lalonde(raw=False)

    est = MatchingCATEEstimator(
        niter=3,
        do_stacking=True,
        include_covariates_in_stacking=True,
        random_state=42,
    )
    est.fit(X, t, y)

    ate = est.ate()
    assert np.isfinite(ate)


# ------------------------------------------------------------------ #
# Edge cases and error handling
# ------------------------------------------------------------------ #


@pytest.mark.skip(reason="Implementation not yet complete")
def test_cate_with_caliper():
    """Test CATE with matching caliper."""
    from causalem._experimental import MatchingCATEEstimator

    X, t, y = load_data_lalonde(raw=False)

    est = MatchingCATEEstimator(
        niter=3,
        matching_caliper=0.1,
        random_state=42,
    )
    est.fit(X, t, y)

    # Some units may be unmatched
    assert hasattr(est, "weights_")
    assert np.any(est.weights_ == 0)  # Some unmatched

    # ATE should only use matched units
    ate = est.ate()
    assert np.isfinite(ate)


@pytest.mark.skip(reason="Implementation not yet complete")
def test_cate_with_groups():
    """Test CATE with GroupKFold via groups parameter."""
    from causalem._experimental import MatchingCATEEstimator

    X, t, y = load_data_lalonde(raw=False)

    # Create synthetic group labels
    groups = np.repeat(np.arange(10), len(X) // 10 + 1)[: len(X)]

    est = MatchingCATEEstimator(niter=3, n_splits_propensity=5, random_state=42)
    est.fit(X, t, y, groups=groups)

    ate = est.ate()
    assert np.isfinite(ate)


# ------------------------------------------------------------------ #
# Future multi-arm and survival tests (placeholder)
# ------------------------------------------------------------------ #


@pytest.mark.skip(reason="Multi-arm support not yet implemented")
def test_cate_multi_arm():
    """Test CATE with multi-arm treatment (future)."""
    pass


@pytest.mark.skip(reason="Survival support not yet implemented")
def test_cate_survival():
    """Test CATE with survival outcomes (future)."""
    pass
