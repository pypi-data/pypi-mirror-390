# CausalEM – Ensemble Matching for Causal Inference

> **CausalEM** is a toolbox for multi-arm treatment‑effect estimation and mediation analysis using stochastic matching and a stacked ensemble of heterogeneous ML models. It supports continuous, binary, and survival outcomes.

## Table of Contents

- [Key Features](#key-features)
- [API](#api)
- [Installation](#️-installation)
- [Package Vignette](#package-vignette)
- [Quick Start](#-quick-start)
  - [Two-arm Analysis](#two-arm-analysis)
  - [Multi-arm Analysis](#multi-arm-analysis)
  - [Confidence-Interval Calculation](#confidence-interval-calculation)
  - [Heterogeneous Ensemble](#heterogeneous-ensemble)
  - [Stacking vs No-Stacking](#stacking-vs-no-stacking)
  - [TE Estimation for Survival Outcomes](#te-estimation-for-survival-outcomes)
  - [Mediation Analysis](#mediation-analysis)
  - [CATE Estimation (Experimental)](#cate-estimation-experimental)
- [CausalEM in R](#causalem-in-r)
  - [Installation (R)](#installation-r)
  - [Quick Start (R)](#quick-start-r)
- [License](#license)
- [Release Notes](#release-notes)

---

## Key Features

| Feature | Impact |
|---------|--------|
| **Stochastic nearest-neighbor (NN) matching** | Larger effective sample size (ESS) and improved TE estimation accuracy compared to standard (deterministic) NN matching |
| **G-computation using two-staged, stacked ensemble of heterogeneous learners** | Generalization of standard G-computation framework to ensemble learning; cross-fitting of propensity-score and outcome models, similar to DoubleML |
| **Support for multi-arm treatments** | Improved multi-arm ESS via stochastic matching |
| **Mediation analysis** | Plug-in G-computation for interventional mediation effects (IDE/IIE) with binary treatment and binary/continuous mediators and outcomes, supporting bootstrap confidence intervals and optional stochastic matching |
| **Support for survival outcomes** | Use of data simulation from survival outcome models to implement stacked-ensemble for TE estimation in right-censored, time-to-event data |
| **Bootstrapped confidence interval (CI) estimation** | Honest estimation of CI by including entire (matching + TE estimation) pipeline in bootstrap loop |
| **Compatible with `scikit-learn`** | Maximum flexibility in using ML models by providing access to `scikit-learn` (and `scikit-survival` for survival) for propensity-score, outcome and meta-learner stages |
| **Full reproducibility of results** | Careful implementation of random number generation (RNG) seeding, including in `scikit-learn` models |
| **Available in Python and R** | Identical function-centric API in both languages using `reticulate`; combined with RNG management, leads to identical, reproducible results across platforms |

---

## API

| Function                 | Brief description                                         |
| ------------------------ | --------------------------------------------------------- |
| `estimate_te`           | Main pipeline – ensemble matching + meta‑learner          |
| `estimate_mediation`    | Mediation analysis with plug-in G-computation             |
| `MatchingCATEEstimator` | **[Experimental]** Individual-level treatment effect estimation (CATE) |
| `StochasticMatcher`      | 1:1 nearest‑neighbor matcher (deterministic ↔ stochastic) |
| `summarize_matching`     | Diagnostics: ESS, ASMD, variance ratios, overlap plots    |
| `load_data_lalonde`      | Standard Lalonde job‑training dataset (two-arm, continuous outcome) |
| `load_data_tof` | New simulated Tetralogy of Fallot (ToF) dataset (two-arm or three-arm, survival/binary/continuous outcome) |

---

## ⚙️ Installation <!--- install -->

```bash
pip install causalem
```

Optional dev extras:

```bash
pip install "causalem[dev]"
```

Minimum Python 3.9. Tested on macOS and Windows.

---

## Package Vignette

For a more detailed introduction to `CausalEM`, including the underlying math, see the _package vignette_ [insert link later], available on arXiv.

---

## 🚀 Quick Start <!--- quickstart -->

### Two-arm Analysis

Load the necessary packages:

```python
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

from causalem import (
  estimate_te,
  load_data_tof,
  stochastic_match,
  summarize_matching
)
```
Load the ToF data with two treatment levels and binarized outcome:
```python
X, t, y = load_data_tof(
  raw = False,
  treat_levels = ['PrP', 'SPS'],
  outcome_type="binary",
)
```
Stochastic matching using propensity scores:
```python
lr = LogisticRegression(solver="newton-cg", max_iter=1000)
lr.fit(X, t)
score = lr.predict_proba(X)[:, 1]
logit_score = np.log(score / (1 - score))

cluster = stochastic_match(
    treatment=t,
    score=logit_score,
    nsmp=10,
    scale=1.0,
    random_state=0,
)

diag = summarize_matching(
  cluster, X,
  treatment=t, plot=False
)
print("Combined Effective Sample Size (ESS):", diag.ess["combined"])
print("Absolute standardized mean difference (ASMD) by covariate:\n")
print(diag.summary)
```
TE estimation (includes stochastic matching as the first step, followed by outcome modeling):
```python
res = estimate_te(
    X,
    t,
    y,
    outcome_type="binary",
    niter=5,
    matching_scale=1.0,
    matching_is_stochastic=True,
    random_state_master=1,
)
print("Two-arm TE:", res["te"])
```

### Multi-arm Analysis

Load data for multi-arm analysis:
```python
df = load_data_tof(
  raw = True,
  outcome_type="binary",
)
t_all = df["treatment"].to_numpy()
X_all = df[["age", "zscore"]].to_numpy()
y_all = df["outcome"].to_numpy()
```
Constructing propensity scores using multinomial logistic regression:
```python
lr_multi = LogisticRegression(multi_class="multinomial", max_iter=1000)
lr_multi.fit(X_all, t_all)
proba = lr_multi.predict_proba(X_all)
ref = "PrP"
cols = [i for i, c in enumerate(lr_multi.classes_) if c != ref]
logit_multi = np.log(proba[:, cols] / (1 - proba[:, cols]))
```
Multi-arm stochastic matching:
```python
cluster_multi = stochastic_match(
    treatment=t_all,
    score=logit_multi,
    nsmp=5,
    scale=1.0,
    ref_group=ref,
    random_state=0,
)
diag_multi = summarize_matching(
    cluster_multi, X_all, treatment=t_all, ref_group=ref, plot=False
)
print("Multi-arm ESS per draw:\n", diag_multi.ess["per_draw"])  # dict of counts by group
```
Multi-arm TE estimation:
```python
res_multi = estimate_te(
    X_all,
    t_all,
    y_all,
    outcome_type="binary",
    ref_group=ref,
    niter=5,
    matching_scale=1.0,
    matching_is_stochastic=True,
    random_state_master=1,
)
print("Multi-arm pairwise effects:\n", res_multi["pairwise"])
```

### Confidence-Interval Calculation

Adding bootstrap CI to the two-arm analysis:
```python
res_boot = estimate_te(
    X,
    t,
    y,
    outcome_type="binary",
    niter=5,
    nboot=200,
    matching_scale=1.0,
    matching_is_stochastic=True,
    random_state_master=1,
    random_state_boot=7,
)
print("Bootstrap CI:", res_boot["ci"])
```

### Heterogeneous Ensemble

```python
learners = [
    LogisticRegression(max_iter=1000),
    RandomForestClassifier(n_estimators=200, max_depth=3),
]
res_ensemble = estimate_te(
    X,
    t,
    y,
    outcome_type="binary",
    model_outcome=learners,
    niter=len(learners),
    do_stacking=True,
    matching_scale=1.0,
    matching_is_stochastic=True,
    random_state_master=42,
)
print("Ensemble TE:", res_ensemble["te"])
```

### Stacking vs No-Stacking

```python
# No-stacking: average per-iteration effects without appearance weights
res_ns = estimate_te(
    X,
    t,
    y,
    outcome_type="binary",
    niter=5,
    do_stacking=False,
    random_state_master=0,
)

# Stacking: meta-learner fit with appearance weights over the matched union
res_stack = estimate_te(
    X,
    t,
    y,
    outcome_type="binary",
    niter=5,
    do_stacking=True,
    random_state_master=0,
)
```

### TE Estimation for Survival Outcomes
```python
X_surv, t_surv, y_surv = load_data_tof(
  raw=False
  , treat_levels = ['SPS', 'PrP']
)
res_surv = estimate_te(
    X_surv,
    t_surv,
    y_surv,
    outcome_type="survival",
    niter=5,
    matching_scale=1.0,
    matching_is_stochastic=True,
    random_state_master=0,
)
print("Survival HR:", res_surv["te"])
```

### Mediation Analysis

```python
# Load ToF data with mediation structure
from causalem.datasets import load_data_tof
from causalem.mediation import estimate_mediation

# Load ToF data: binary treatment (PrP vs SPS), continuous mediator (op_time), binary outcome
X, A, M, Y = load_data_tof(
    raw=False,
    treat_levels=['PrP', 'SPS'],  # Binary treatment comparison
    outcome_type="binary",        # Binary outcome for simpler interpretation
    include_mediator=True         # Include mediator variable (op_time)
)

# Estimate mediation effects
result = estimate_mediation(X, A, M, Y, random_state_master=42)

print("Total Effect (TE):", result["te"])
print("Interventional Direct Effect (IDE):", result["ide"])
print("Interventional Indirect Effect (IIE):", result["iie"])
print("Proportion Mediated:", result["prop_mediated"])
```

### CATE Estimation (Experimental)

**⚠️ Experimental Feature**: The CATE estimator API is under active development and may change.

Unlike `estimate_te()` which returns population-level averages, `MatchingCATEEstimator` predicts **individual-level treatment effects**:

```python
from causalem._experimental import MatchingCATEEstimator
from causalem import load_data_lalonde

X, t, y = load_data_lalonde(raw=False)

# Initialize and fit the CATE estimator
est = MatchingCATEEstimator(
    niter=10,
    matching_is_stochastic=True,
    matching_scale=1.0,
    do_stacking=True,
    random_state=42
)
est.fit(X, t, y)

# Get individual treatment effects
individual_effects = est.effect()
print(f"Individual effects range: [{individual_effects.min():.2f}, {individual_effects.max():.2f}]")

# Population summaries
print(f"ATE on matched: {est.ate():.2f}")
print(f"ATT on matched: {est.att():.2f}")

# Identify high-benefit subgroups
import numpy as np
high_benefit_idx = np.where(individual_effects > np.percentile(individual_effects, 75))[0]
print(f"High-benefit group size: {len(high_benefit_idx)}")
```

For more details, see `causalem/_experimental/README.md`.

---

## License

This project is licensed under the terms of the MIT License.

## Release Notes

### 1.3.0

**New Experimental Feature: CATE (Conditional Average Treatment Effect) Estimation**

- Added `MatchingCATEEstimator` class in `causalem._experimental` module for individual-level treatment effect prediction
- Provides scikit-learn style `fit()`/`effect()` API for learning and predicting heterogeneous treatment effects
- **Key capabilities**:
  - Individual-level treatment effect predictions (not just population averages)
  - Prediction on new/unseen data
  - ATM and ATT estimands supported
  - Stochastic and deterministic matching
  - Ensemble stacking with meta-learners
  - Compatible with heterogeneous base learners
- **Current scope** (binary treatment, non-survival outcomes):
  - ✓ Binary and continuous outcomes
  - ✓ Stochastic/deterministic matching
  - ✓ Stacking and no-stacking modes
  - ✓ ATM/ATT estimands
  - Future: Multi-arm treatment, survival outcomes, bootstrap CIs
- **Validation**: Comprehensive test suite verifying parity with `estimate_te()`
- **Documentation**: Detailed design documentation in `causalem/_experimental/README.md`
- **Status**: ⚠️ Experimental API - may change in future releases

**API Example:**
```python
from causalem._experimental import MatchingCATEEstimator

est = MatchingCATEEstimator(niter=10, do_stacking=True, random_state=42)
est.fit(X, t, y)

# Individual effects
effects = est.effect()

# Population summaries
ate = est.ate()
att = est.att()
```

### 1.2.0

**New Feature: Covariate Inclusion in Stacking Meta-Learner**

- Added `include_covariates_in_stacking` parameter to `estimate_te()` to enable including covariates in the meta-learner stage
- When `True`, covariates are included alongside base learner predictions in the meta-learner design matrix, allowing the meta-learner to learn non-linear combinations of predictions conditional on covariates
- Implemented across all pathways: binary, multi-arm, and survival outcomes
- For stacking mode with `do_stacking=True`, both base predictions and original covariates are passed to the meta-learner
- Defaults to `False` to preserve backward compatibility
- Warning issued if `include_covariates_in_stacking=True` but `do_stacking=False` (parameter has no effect without stacking)
- Comprehensive test coverage: 9 new tests covering all outcome types and edge cases

**Documentation Enhancement: Heterogeneous Ensembles**

- **Improved documentation** for the existing heterogeneous learner feature in `model_outcome` parameter
- Previously feature-complete but undocumented: `model_outcome` now clearly documents support for:
  - **List/tuple of estimators**: Mix different model types across iterations (e.g., Random Forest + Gradient Boosting + Linear models)
  - **Generator/iterator**: Dynamically yield different models for each iteration
  - **Single estimator**: Homogeneous ensemble (backward compatible)
- Added practical examples showing heterogeneous ensemble usage with lists and generators
- Documented benefits: improved robustness by combining models with different inductive biases
- **Comprehensive test suite** added: 22 tests (675 lines) in `tests/test_heterogeneous_learners.py` covering:
  - All input types (list, tuple, generator)
  - All outcome types (continuous, binary, survival)
  - Multi-arm treatments
  - Error handling (insufficient models, exhausted generators)
  - Integration with all features (bootstrap, stacking, covariates, ATT, stochastic matching)
  - Reproducibility and comparisons

**Bug Fixes:**
- Fixed multi-arm stacking to correctly use encoder categories when constructing counterfactual design matrices

**API Enhancements:**
```python
# Meta-learner uses only base predictions (default)
result = estimate_te(X, t, y, do_stacking=True, include_covariates_in_stacking=False)

# Meta-learner uses both base predictions and covariates
result = estimate_te(X, t, y, do_stacking=True, include_covariates_in_stacking=True)

# Heterogeneous ensemble with different model types
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
outcome_models = [
    RandomForestRegressor(n_estimators=100),
    GradientBoostingRegressor(n_estimators=100),
    LinearRegression()
]
result = estimate_te(X, t, y, model_outcome=outcome_models, niter=3)
```

### 1.1.0

**New Feature: Estimand Parameter (ATT vs ATM)**

- Added `estimand` parameter to `estimate_te()` and `estimate_te_multi()` functions
- Supports two estimands:
  - `'ATM'` (default): Average Treatment Effect on Matched sample - averages over all units appearing in matched sets (preserves backward compatibility)
  - `'ATT'`: Average Treatment Effect on Treated (common support) - averages over treated/ref_group units that were successfully matched
- Implemented across all pathways: binary, multi-arm, and survival outcomes
- For multi-arm with `estimand='ATT'`, `ref_group` parameter specifies which arm is the "treated" group
- ATT computes effects on matched treated units only (not all treated), following standard matching literature practice of estimating on the common support
- Comprehensive test coverage: 14 new tests covering all outcome types and pathways

**API Enhancement:**
```python
# Target effect on matched sample (default)
result = estimate_te(X, t, y, estimand='ATM')

# Target effect on treated population
result = estimate_te(X, t, y, estimand='ATT')
```

### 1.0.1

- Removed the R section of `README.md` since it has not been released yet.
- Added release notes for version 1.0.0.

### 1.0.0

- Removed `binarize_outcome` parameter from `load_data_lalonde` and `load_data_tof`.
- Absorbed `load_data_tof_with_mediator` into `load_data_tof`.

### 0.7.0
- Added mediation analysis functionality with `estimate_mediation` function for interventional mediation effects using plug-in G-computation.
- Supports binary treatment with binary/continuous mediators and continuous outcomes.
- Features bootstrap confidence intervals and optional integration with stochastic matching for improved robustness.
- Estimates total effect (TE), interventional direct effect (IDE), and interventional indirect effect (IIE).

### 0.6.2
- Exposed a new `n_mc` argument in estimate_te for specifying Monte‑Carlo draws per matched unit in survival analyses, replacing the previously fixed single draw.
- Clarified treatment‑effect estimands for stacking vs. no‑stacking modes, noting that stacked results are appearance‑weighted across the matched union.
- Documented appearance‑weighted meta‑learning and matched‑union survival contrasts.

### 0.6.1
- Corrected the version number in `pyproject.toml` file.

### 0.6.0
- Improved consistency of return data structure when `do_stacking=False` in multi-arm TE estimation.

### 0.5.4
- Added github action for publishing to PyPI

### 0.5.3
- First public release

### 0.5.1
- Edits to readme
- Added github action for publishing to (test) PyPI

### 0.5.0

- First test release
