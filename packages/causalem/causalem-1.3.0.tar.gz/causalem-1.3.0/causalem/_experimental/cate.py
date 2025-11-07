"""
CATE (Conditional Average Treatment Effect) Estimation via Ensemble Matching.

This module provides class-based CATE estimation that complements the existing
functional API. It enables individual-level treatment effect prediction and
follows the fit/effect pattern common in CATE estimation libraries like EconML.

Current Support
---------------
- Binary treatment (two-arm)
- Continuous and binary outcomes (non-survival)

Future Extensions
-----------------
- Multi-arm treatment
- Survival outcomes
"""

from __future__ import annotations

from typing import Optional

import numpy as np
from sklearn.base import BaseEstimator, clone
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.model_selection import GroupKFold, KFold, cross_val_predict

from causalem import stochastic_match
from causalem.estimation.ensemble import clip_logit
from causalem.utils._weights import appearance_weights, fit_with_appearance_weights


class MatchingCATEEstimator:
    """
    Conditional Average Treatment Effect estimator using ensemble matching.

    This estimator learns heterogeneous treatment effects τ(x) = E[Y(1) - Y(0)|X=x]
    through a two-stage ensemble matching procedure:

    1. **Stage 1 (Iterations)**: Multiple iterations of propensity-score matching
       and outcome modeling with cross-fitting
    2. **Stage 2 (Meta-learning)**: Combines base predictions via a meta-learner
       (when do_stacking=True)

    After fitting, the estimator can predict individual treatment effects on
    training data or new observations.

    Parameters
    ----------
    niter : int, default=10
        Number of stage-1 iterations before meta-learning.
    matching_is_stochastic : bool, default=True
        Use stochastic matching when True, otherwise deterministic.
    matching_scale : float, default=1.0
        Temperature parameter for stochastic matching weights.
    matching_caliper : float or None, default=None
        Maximum allowable matching distance (in propensity score logit space).
    do_stacking : bool, default=True
        When False, bypass meta-learner and average effects across iterations.
    n_splits_propensity : int, default=5
        Number of folds for propensity score cross-fitting.
    n_splits_outcome : int, default=5
        Number of folds for outcome model cross-fitting.
    model_propensity : estimator or None, default=None
        Classifier for propensity scores. If None, uses LogisticRegression.
    model_outcome : estimator or list of estimators or None, default=None
        Base learner(s) for outcome prediction. Supports:
        - Single estimator: cloned niter times
        - List/tuple: must contain at least niter estimators
        - None: uses RandomForestRegressor (continuous) or RandomForestClassifier (binary)
    model_meta : estimator or None, default=None
        Meta-learner for stacking. If None, uses LinearRegression (continuous)
        or LogisticRegression (binary).
    outcome_type : {"continuous", "binary"} or None, default=None
        Type of outcome. If None, inferred from data.
    prob_clip_eps : float, default=1e-6
        Epsilon for probability clipping before taking logits.
    estimand : {"ATM", "ATT"}, default="ATM"
        Target estimand:
        - "ATM": Average Treatment Effect on Matched sample
        - "ATT": Average Treatment Effect on Treated (matched subset only)
    include_covariates_in_stacking : bool, default=False
        Include baseline covariates in meta-learner design matrix.
    random_state : int or None, default=None
        Seed for reproducibility.

    Attributes
    ----------
    n_features_in_ : int
        Number of features seen during fit.
    treatment_levels_ : ndarray
        Unique treatment levels (should be [0, 1] for binary).
    outcome_type_ : str
        Inferred or specified outcome type.
    propensity_models_ : list
        Fitted propensity score models (one per fold).
    outcome_models_ : list
        Fitted outcome models (one per iteration).
    meta_learner_ : estimator or None
        Fitted meta-learner (if do_stacking=True).
    matching_matrix_ : ndarray of shape (n, niter)
        Cluster IDs for each observation and iteration (-1 = unmatched).
    weights_ : ndarray of shape (n,)
        Appearance weights (# times each unit was matched).
    y_pred_ : ndarray of shape (n,)
        Factual outcome predictions on training data.
    y_pred_cf_ : ndarray of shape (n,)
        Counterfactual outcome predictions on training data.
    X_train_ : ndarray
        Training features (stored for reference).
    t_train_ : ndarray
        Training treatment assignments.
    treated_idx_ : ndarray
        Indices of treated units in training data.

    Examples
    --------
    >>> from causalem import load_data_lalonde
    >>> from causalem._experimental import MatchingCATEEstimator
    >>> X, t, y = load_data_lalonde(raw=False)
    >>> est = MatchingCATEEstimator(niter=5, random_state=42)
    >>> est.fit(X, t, y)
    >>> effects = est.effect()  # Individual effects on training data
    >>> ate = est.ate()  # Average treatment effect on matched sample
    >>> att = est.att()  # Average treatment effect on treated

    Notes
    -----
    - Currently only supports binary treatment and non-survival outcomes
    - For new data predictions, matching structure from training is not used
    - Multi-arm and survival support planned for future releases
    """

    def __init__(
        self,
        *,
        niter: int = 10,
        matching_is_stochastic: bool = True,
        matching_scale: float = 1.0,
        matching_caliper: Optional[float] = None,
        do_stacking: bool = True,
        n_splits_propensity: int = 5,
        n_splits_outcome: int = 5,
        model_propensity: Optional[BaseEstimator] = None,
        model_outcome=None,
        model_meta: Optional[BaseEstimator] = None,
        outcome_type: Optional[str] = None,
        prob_clip_eps: float = 1e-6,
        estimand: str = "ATM",
        include_covariates_in_stacking: bool = False,
        random_state: Optional[int] = None,
    ):
        self.niter = niter
        self.matching_is_stochastic = matching_is_stochastic
        self.matching_scale = matching_scale
        self.matching_caliper = matching_caliper
        self.do_stacking = do_stacking
        self.n_splits_propensity = n_splits_propensity
        self.n_splits_outcome = n_splits_outcome
        self.model_propensity = model_propensity
        self.model_outcome = model_outcome
        self.model_meta = model_meta
        self.outcome_type = outcome_type
        self.prob_clip_eps = prob_clip_eps
        self.estimand = estimand
        self.include_covariates_in_stacking = include_covariates_in_stacking
        self.random_state = random_state

        # Attributes set during fit() (type hints for mypy)
        self.n_features_in_: int
        self.treatment_levels_: np.ndarray
        self.outcome_type_: str
        self.rng_: np.random.Generator
        self.model_propensity_: BaseEstimator
        self.outcome_models_: list[BaseEstimator]
        self.model_meta_: Optional[BaseEstimator]
        self.matching_matrix_: np.ndarray
        self.weights_: np.ndarray
        self.y_pred_: np.ndarray
        self.y_pred_cf_: np.ndarray
        self.X_train_: np.ndarray
        self.t_train_: np.ndarray
        self.treated_idx_: np.ndarray

    def fit(
        self,
        X: np.ndarray,
        t: np.ndarray,
        y: np.ndarray,
        *,
        groups: Optional[np.ndarray] = None,
    ):
        """
        Fit the CATE model.

        Performs the complete ensemble matching pipeline:
        1. Cross-fitted propensity score estimation
        2. Stochastic/deterministic matching on propensity scores
        3. Cross-fitted outcome modeling on matched sets (niter iterations)
        4. Meta-learner training (if do_stacking=True)

        Parameters
        ----------
        X : ndarray of shape (n, p)
            Covariate matrix.
        t : ndarray of shape (n,)
            Binary treatment indicator (must be {0, 1}).
        y : ndarray of shape (n,)
            Outcome values.
        groups : ndarray of shape (n,) or None, default=None
            Group labels for GroupKFold cross-validation.

        Returns
        -------
        self : MatchingCATEEstimator
            Fitted estimator.

        Raises
        ------
        ValueError
            If treatment is not binary or outcome type is not supported.
        """
        self._validate_inputs(X, t, y)
        self._setup_rng()
        self._infer_outcome_type(y)
        self._setup_models()

        # Store training data
        self.n_features_in_ = X.shape[1]
        self.treatment_levels_ = np.unique(t)
        self.X_train_ = X
        self.t_train_ = t
        self.treated_idx_ = np.where(t == 1)[0]

        # Core fitting pipeline - run all iterations
        # Each iteration: propensity → matching → outcome fitting
        self._fit_all_iterations(X, t, y, groups)

        if self.do_stacking:
            self._fit_meta_learner(X, t, y, groups)
        else:
            self._aggregate_iterations(t, y)

        return self

    def effect(
        self, X: Optional[np.ndarray] = None, *, T0: int = 0, T1: int = 1
    ) -> np.ndarray:
        """
        Predict individual treatment effects τ(x) = E[Y|T=T1,X] - E[Y|T=T0,X].

        Parameters
        ----------
        X : ndarray of shape (m, p) or None, default=None
            Features to predict effects for. If None, uses training data with
            matching structure. If provided, predicts on new observations without
            using matching structure.
        T0 : int, default=0
            Reference treatment level.
        T1 : int, default=1
            Comparison treatment level.

        Returns
        -------
        effects : ndarray of shape (m,)
            Individual treatment effects for each observation.

        Raises
        ------
        ValueError
            If called before fit() or if treatment levels are invalid.
        """
        self._check_is_fitted()

        if X is None:
            return self._effect_training()
        else:
            return self._effect_new(X, T0, T1)

    def ate(self) -> float:
        """
        Compute Average Treatment Effect on matched sample.

        Returns
        -------
        ate : float
            Appearance-weighted average of individual treatment effects over all
            matched observations (when stacking), or simple average across iterations
            (when no stacking).
        """
        self._check_is_fitted()

        # If no stacking, return the pre-computed average
        if hasattr(self, "_te_no_stacking"):
            return self._te_no_stacking

        # Otherwise, use appearance-weighted average (stacking mode)
        effects = self._effect_training()
        matched_idx = np.where(self.weights_ > 0)[0]
        return float(
            np.average(effects[matched_idx], weights=self.weights_[matched_idx])
        )

    def att(self) -> float:
        """
        Compute Average Treatment Effect on Treated (matched subset).

        Returns
        -------
        att : float
            Appearance-weighted average of individual treatment effects over
            matched treated observations only.
        """
        self._check_is_fitted()
        effects = self._effect_training()
        matched_treated_idx = np.where((self.weights_ > 0) & (self.t_train_ == 1))[0]
        return float(
            np.average(
                effects[matched_treated_idx], weights=self.weights_[matched_treated_idx]
            )
        )

    # ------------------------------------------------------------------ #
    # Internal methods (to be implemented)
    # ------------------------------------------------------------------ #

    def _validate_inputs(self, X: np.ndarray, t: np.ndarray, y: np.ndarray):
        """Validate input data shapes and treatment levels."""
        if X.ndim != 2:
            raise ValueError(f"X must be 2D, got shape {X.shape}")
        if t.ndim != 1 or t.shape[0] != X.shape[0]:
            raise ValueError(f"t must be 1D with length {X.shape[0]}")
        if y.ndim != 1 or y.shape[0] != X.shape[0]:
            raise ValueError(f"y must be 1D with length {X.shape[0]}")

        treatment_levels = np.unique(t)
        if not np.array_equal(treatment_levels, [0, 1]):
            raise ValueError(
                f"Currently only binary treatment {{0, 1}} is supported, got {treatment_levels}"
            )

    def _setup_rng(self):
        """Initialize random number generator."""
        self.rng_ = np.random.default_rng(self.random_state)

    def _infer_outcome_type(self, y: np.ndarray):
        """Infer outcome type if not specified."""
        if self.outcome_type is None:
            if np.array_equal(np.unique(y), [0, 1]) or np.array_equal(
                np.unique(y), [0.0, 1.0]
            ):
                self.outcome_type_ = "binary"
            else:
                self.outcome_type_ = "continuous"
        else:
            allowed = {"continuous", "binary"}
            if self.outcome_type not in allowed:
                raise ValueError(
                    f"outcome_type must be one of {allowed}, got {self.outcome_type}"
                )
            self.outcome_type_ = self.outcome_type

    def _setup_models(self):
        """Set default models if not provided."""
        if self.model_propensity is None:
            self.model_propensity_ = LogisticRegression(solver="newton-cg")
        else:
            self.model_propensity_ = clone(self.model_propensity)

        if self.model_outcome is None:
            if self.outcome_type_ == "continuous":
                base_model = RandomForestRegressor(n_estimators=100)
            else:
                base_model = RandomForestClassifier(n_estimators=100)
            self.outcome_models_ = [clone(base_model) for _ in range(self.niter)]
        else:
            # Handle list, tuple, or single model
            if isinstance(self.model_outcome, (list, tuple)):
                if len(self.model_outcome) < self.niter:
                    raise ValueError(
                        f"model_outcome list must have at least {self.niter} models"
                    )
                self.outcome_models_ = [
                    clone(m) for m in self.model_outcome[: self.niter]
                ]
            else:
                self.outcome_models_ = [
                    clone(self.model_outcome) for _ in range(self.niter)
                ]

        if self.model_meta is None and self.do_stacking:
            if self.outcome_type_ == "continuous":
                self.model_meta_ = LinearRegression()
            else:
                self.model_meta_ = LogisticRegression(solver="newton-cg")
        else:
            self.model_meta_ = (
                clone(self.model_meta) if self.model_meta is not None else None
            )

    def _make_splitter(
        self, n_splits: int, shuffle: bool, groups: Optional[np.ndarray]
    ):
        """Create cross-validation splitter using self.rng_."""
        seed = int(self.rng_.integers(2**32))
        if groups is None:
            return KFold(n_splits=n_splits, shuffle=shuffle, random_state=seed)

        try:
            return GroupKFold(n_splits=n_splits, shuffle=shuffle, random_state=seed)
        except TypeError:  # older scikit-learn
            return GroupKFold(n_splits=n_splits)

    def _make_splitter_with_rng(
        self,
        n_splits: int,
        shuffle: bool,
        groups: Optional[np.ndarray],
        rng: np.random.Generator,
    ):
        """Create cross-validation splitter using provided rng."""
        seed = int(rng.integers(2**32))
        if groups is None:
            return KFold(n_splits=n_splits, shuffle=shuffle, random_state=seed)

        try:
            return GroupKFold(n_splits=n_splits, shuffle=shuffle, random_state=seed)
        except TypeError:  # older scikit-learn
            return GroupKFold(n_splits=n_splits)

    def _fit_all_iterations(
        self, X: np.ndarray, t: np.ndarray, y: np.ndarray, groups: Optional[np.ndarray]
    ):
        """Run all iterations: propensity → matching → outcome fitting."""
        cluster_list = []
        y_pred_list = []
        y_pred_cf_list = []

        # Prepare design matrices
        X_t = np.hstack((X, t.reshape(-1, 1)))
        X_t_cf = np.hstack((X, (1 - t).reshape(-1, 1)))

        for iter_idx in range(self.niter):
            # Each iteration gets its own RNG seed
            rng_iter = np.random.default_rng(int(self.rng_.integers(2**32)))

            # 1. Propensity fitting with cross-validation
            splitter_prop = self._make_splitter_with_rng(
                n_splits=self.n_splits_propensity,
                shuffle=True,
                groups=groups,
                rng=rng_iter,
            )

            oos_proba = cross_val_predict(
                clone(self.model_propensity_),
                X,
                t,
                cv=splitter_prop,
                method="predict_proba",
                groups=groups,
            )[:, 1]

            oos_scores = clip_logit(oos_proba, eps=self.prob_clip_eps)

            # 2. Matching
            cluster_ids = stochastic_match(
                treatment=t,
                score=oos_scores,
                scale=self.matching_scale,
                caliper=self.matching_caliper,
                nsmp=1 if self.matching_is_stochastic else 0,
                random_state=int(rng_iter.integers(2**32)),
            ).ravel()

            matched_idx = np.where(cluster_ids != -1)[0]
            cluster_list.append(cluster_ids)

            # 3. Outcome model fitting with cross-validation
            splitter_out = self._make_splitter_with_rng(
                n_splits=self.n_splits_outcome,
                shuffle=True,
                groups=groups,
                rng=rng_iter,
            )

            y_pred = np.full(X_t.shape[0], np.nan)
            y_pred_cf = np.full(X_t.shape[0], np.nan)

            for tr_idx, te_idx in splitter_out.split(X_t, groups=groups):
                matched_tr = np.intersect1d(matched_idx, tr_idx)
                if matched_tr.size == 0:
                    continue

                # Clone and fit model
                model = clone(self.outcome_models_[iter_idx])
                if "random_state" in model.get_params(deep=False):
                    model.set_params(random_state=int(rng_iter.integers(2**32)))

                model.fit(X_t[matched_tr], y[matched_tr])

                # Predict
                if self.outcome_type_ == "binary" and hasattr(model, "predict_proba"):
                    y_pred[te_idx] = model.predict_proba(X_t[te_idx])[:, 1]
                    y_pred_cf[te_idx] = model.predict_proba(X_t_cf[te_idx])[:, 1]
                else:
                    y_pred[te_idx] = model.predict(X_t[te_idx])
                    y_pred_cf[te_idx] = model.predict(X_t_cf[te_idx])

            y_pred_list.append(y_pred)
            y_pred_cf_list.append(y_pred_cf)

        # Store results
        self.matching_matrix_ = np.column_stack(cluster_list)
        self.weights_ = appearance_weights(self.matching_matrix_)
        self.y_pred_mat_ = np.column_stack(y_pred_list)
        self.y_pred_cf_mat_ = np.column_stack(y_pred_cf_list)

    def _fit_propensity(
        self, X: np.ndarray, t: np.ndarray, groups: Optional[np.ndarray]
    ):
        """Fit propensity score models with cross-fitting."""
        # Get out-of-sample propensity scores via cross-validation
        splitter_prop = self._make_splitter(
            n_splits=self.n_splits_propensity, shuffle=True, groups=groups
        )

        oos_proba = cross_val_predict(
            clone(self.model_propensity_),
            X,
            t,
            cv=splitter_prop,
            method="predict_proba",
            groups=groups,
        )[:, 1]

        # Convert to logit scale for matching
        self.propensity_scores_ = clip_logit(oos_proba, eps=self.prob_clip_eps)

    def _perform_matching(self, X: np.ndarray, t: np.ndarray):
        """Perform matching based on propensity scores (all iterations)."""
        # Perform niter matching draws using the propensity scores
        cluster_list = []

        for _ in range(self.niter):
            seed = int(self.rng_.integers(2**32))
            cluster_ids = stochastic_match(
                treatment=t,
                score=self.propensity_scores_,
                scale=self.matching_scale,
                caliper=self.matching_caliper,
                nsmp=1 if self.matching_is_stochastic else 0,
                random_state=seed,
            ).ravel()
            cluster_list.append(cluster_ids)

        # Store matching matrix (n, niter)
        self.matching_matrix_ = np.column_stack(cluster_list)

        # Compute appearance weights
        self.weights_ = appearance_weights(self.matching_matrix_)

    def _fit_outcome_models(
        self, X: np.ndarray, t: np.ndarray, y: np.ndarray, groups: Optional[np.ndarray]
    ):
        """Fit outcome models for each iteration on matched sets."""
        # Store predictions from each iteration
        y_pred_list = []
        y_pred_cf_list = []

        # Prepare design matrices
        X_t = np.hstack((X, t.reshape(-1, 1)))
        X_t_cf = np.hstack((X, (1 - t).reshape(-1, 1)))

        for iter_idx in range(self.niter):
            # Get matched units for this iteration
            cluster_ids = self.matching_matrix_[:, iter_idx]
            matched_idx = np.where(cluster_ids != -1)[0]

            # Cross-fitting splitter for outcome models
            splitter_out = self._make_splitter(
                n_splits=self.n_splits_outcome, shuffle=True, groups=groups
            )

            # Initialize predictions for this iteration
            y_pred = np.full(X_t.shape[0], np.nan)
            y_pred_cf = np.full(X_t.shape[0], np.nan)

            # Cross-fit outcome models
            for tr_idx, te_idx in splitter_out.split(X_t, groups=groups):
                matched_tr = np.intersect1d(matched_idx, tr_idx)
                if matched_tr.size == 0:
                    continue

                # Clone and fit model
                model = clone(self.outcome_models_[iter_idx])
                if "random_state" in model.get_params(deep=False):
                    model.set_params(random_state=int(self.rng_.integers(2**32)))

                model.fit(X_t[matched_tr], y[matched_tr])

                # Predict for test set
                if self.outcome_type_ == "binary" and hasattr(model, "predict_proba"):
                    y_pred[te_idx] = model.predict_proba(X_t[te_idx])[:, 1]
                    y_pred_cf[te_idx] = model.predict_proba(X_t_cf[te_idx])[:, 1]
                else:
                    y_pred[te_idx] = model.predict(X_t[te_idx])
                    y_pred_cf[te_idx] = model.predict(X_t_cf[te_idx])

            y_pred_list.append(y_pred)
            y_pred_cf_list.append(y_pred_cf)

        # Store as matrices (n, niter)
        self.y_pred_mat_ = np.column_stack(y_pred_list)
        self.y_pred_cf_mat_ = np.column_stack(y_pred_cf_list)

    def _fit_meta_learner(
        self, X: np.ndarray, t: np.ndarray, y: np.ndarray, groups: Optional[np.ndarray]
    ):
        """Fit meta-learner on stacked predictions with appearance weights."""
        # Ensure meta-learner is available
        assert (
            self.model_meta_ is not None
        ), "Meta-learner must be set when do_stacking=True"

        # Get matched union
        matched_union = np.where(self.weights_ > 0)[0]

        # Prepare prediction matrices
        y_pred_mat = self.y_pred_mat_.copy()
        y_pred_cf_mat = self.y_pred_cf_mat_.copy()

        # For binary outcomes, clip and logit the predictions
        if self.outcome_type_ == "binary":
            y_pred_mat = clip_logit(y_pred_mat, eps=self.prob_clip_eps)
            y_pred_cf_mat = clip_logit(y_pred_cf_mat, eps=self.prob_clip_eps)

        # Add covariates and treatment indicator if requested
        if self.include_covariates_in_stacking:
            y_pred_mat = np.hstack((y_pred_mat, X, t.reshape(-1, 1)))
            y_pred_cf_mat = np.hstack((y_pred_cf_mat, X, (1 - t).reshape(-1, 1)))
        else:
            y_pred_mat = np.hstack((y_pred_mat, t.reshape(-1, 1)))
            y_pred_cf_mat = np.hstack((y_pred_cf_mat, (1 - t).reshape(-1, 1)))

        # Cross-fit meta-learner on matched union
        splitter_meta = self._make_splitter(
            n_splits=self.n_splits_outcome, shuffle=True, groups=groups
        )

        # Initialize final predictions
        y_final = np.full(X.shape[0], np.nan)
        y_final_cf = np.full(X.shape[0], np.nan)

        for tr_idx, te_idx in splitter_meta.split(X, groups=groups):
            matched_tr = np.intersect1d(matched_union, tr_idx)
            if matched_tr.size == 0:
                raise ValueError(
                    "No matched units in training set. "
                    "Try increasing `matching_scale` or relaxing `matching_caliper`."
                )

            # Fit meta-learner with appearance weights
            fit_with_appearance_weights(
                self.model_meta_,
                y_pred_mat[matched_tr],
                y[matched_tr],
                sample_weight=self.weights_[matched_tr],
            )

            # Predict on test set
            if self.outcome_type_ == "binary" and hasattr(
                self.model_meta_, "predict_proba"
            ):
                y_final[te_idx] = self.model_meta_.predict_proba(y_pred_mat[te_idx])[
                    :, 1
                ]
                y_final_cf[te_idx] = self.model_meta_.predict_proba(
                    y_pred_cf_mat[te_idx]
                )[:, 1]
            else:
                y_final[te_idx] = self.model_meta_.predict(y_pred_mat[te_idx])
                y_final_cf[te_idx] = self.model_meta_.predict(y_pred_cf_mat[te_idx])

        # Store final predictions
        self.y_pred_ = y_final
        self.y_pred_cf_ = y_final_cf

    def _aggregate_iterations(self, t: np.ndarray, y: np.ndarray):
        """Aggregate effects across iterations when do_stacking=False."""
        # Compute TE for each iteration on its matched set, then average
        # This respects per-iteration matching (important when do_stacking=False)

        te_list = []
        for iter_idx in range(self.niter):
            cid = self.matching_matrix_[:, iter_idx]
            yp = self.y_pred_mat_[:, iter_idx]
            yp_cf = self.y_pred_cf_mat_[:, iter_idx]

            # Determine matched units for this iteration based on estimand
            if self.estimand == "ATT":
                matched_idx = np.where((cid != -1) & (t == 1))[0]
            elif self.estimand == "ATM":
                matched_idx = np.where(cid != -1)[0]
            else:
                raise ValueError(f"estimand='{self.estimand}' not supported")

            # Compute effect for this iteration
            yp_treat = np.where(t == 1, yp, yp_cf)[matched_idx]
            yp_ctrl = np.where(t == 1, yp_cf, yp)[matched_idx]
            te_iter = np.mean(yp_treat) - np.mean(yp_ctrl)
            te_list.append(te_iter)

        # Store the average effect (will be used by ate())
        # Also store averaged predictions for effect() method
        self._te_no_stacking = float(np.mean(te_list))
        self.y_pred_ = np.nanmean(self.y_pred_mat_, axis=1)
        self.y_pred_cf_ = np.nanmean(self.y_pred_cf_mat_, axis=1)

    def _effect_training(self) -> np.ndarray:
        """Compute individual effects on training data."""
        # Use stored predictions
        effects = np.where(
            self.t_train_ == 1,
            self.y_pred_ - self.y_pred_cf_,
            self.y_pred_cf_ - self.y_pred_,
        )
        return effects

    def _effect_new(self, X: np.ndarray, T0: int, T1: int) -> np.ndarray:
        """Compute individual effects on new data."""
        # TODO: Implement proper new data prediction
        # Challenge: base models are only fitted within CV folds during training
        # Options: (1) refit on all matched data, (2) use meta-learner if available,
        # (3) store all fold models
        # For now, raise NotImplementedError and focus on training data path
        raise NotImplementedError(
            "Prediction on new data not yet implemented. "
            "Use effect() without arguments to get effects on training data."
        )

    def _check_is_fitted(self):
        """Check if estimator has been fitted."""
        if not hasattr(self, "matching_matrix_"):
            raise ValueError("This MatchingCATEEstimator instance is not fitted yet.")
