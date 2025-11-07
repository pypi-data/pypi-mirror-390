# Overlay_dx

[![PyPI version](https://badge.fury.io/py/overlay-dx.svg)](https://badge.fury.io/py/overlay-dx)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Visual and quantitative metric for evaluating time series forecasts**

Overlay_dx is a novel evaluation metric that combines visual interpretability with quantitative assessment. It measures the alignment between predicted and actual values across different tolerance thresholds, providing both intuitive visualization and a numerical score.

## Features

- **Visual interpretation** through overlay curves
- **Quantitative assessment** via area under curve (AUC) score
- **Less sensitive to outliers** than MSE/RMSE
- **Scikit-learn compatible** - works with cross_val_score, GridSearchCV, Pipeline
- **Easy to use** with minimal setup

## Installation

```bash
pip install overlay-dx
```

## Quick Start

```python
from overlay_dx import overlay_dx_score
import numpy as np

# Your predictions and actual values
y_true = np.array([1, 2, 3, 4, 5])
y_pred = np.array([1.1, 2.1, 2.9, 4.1, 5.1])

# Calculate overlay_dx score
score = overlay_dx_score(y_true, y_pred)
print(f"Overlay_dx score: {score:.3f}")
# Output: Overlay_dx score: 0.930
```

## Scikit-learn Integration

```python
from overlay_dx import make_overlay_dx_scorer
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestRegressor

# Create scorer
scorer = make_overlay_dx_scorer()

# Use with cross-validation
model = RandomForestRegressor()
scores = cross_val_score(model, X, y, scoring=scorer, cv=5)
print(f"CV scores: {scores.mean():.3f} (+/- {scores.std():.3f})")
```

## With GridSearchCV

```python
from overlay_dx import OVERLAY_DX_SCORER
from sklearn.model_selection import GridSearchCV

param_grid = {'n_estimators': [50, 100, 200]}
grid = GridSearchCV(
    RandomForestRegressor(),
    param_grid,
    scoring=OVERLAY_DX_SCORER,
    cv=5
)
grid.fit(X_train, y_train)
print(f"Best score: {grid.best_score_:.3f}")
```

## How It Works

Overlay_dx measures the percentage of predictions falling within tolerance intervals of varying sizes around actual values. It then computes the area under the resulting curve, normalized by the maximum possible area.

**Key advantages:**
- Intuitive visual interpretation
- Robust to outliers
- Captures performance across multiple tolerance levels
- Easy to explain to non-technical stakeholders

## Research Paper

Overlay_dx is based on peer-reviewed research published at OLA 2025:

**"Overlay_dx - Automating forecasting evaluation"**  
Long H. Ngo, Mohammed Amine Chamli, Jonathan Rivalan, and Thomas Jaillon  
4th International Conference on Optimization and Learning Algorithms (OLA 2025)

📄 [Conference](https://ola2025.sciencesconf.org/)

The paper demonstrates overlay_dx effectiveness across multiple public datasets (Beijing Air Quality, ETT, ELD) and compares it with traditional metrics (MAE, RMSE, MAPE, etc.).

## API Reference

### `overlay_dx_score(y_true, y_pred, max_percentage=100, min_percentage=0.1, step=0.1)`

Calculate overlay_dx score.

**Parameters:**
- `y_true`: array-like, actual values
- `y_pred`: array-like, predicted values
- `max_percentage`: float, maximum tolerance percentage (default: 100)
- `min_percentage`: float, minimum tolerance percentage (default: 0.1)
- `step`: float, step size for tolerance levels (default: 0.1)

**Returns:**
- `score`: float between 0 and 1, higher is better

### `make_overlay_dx_scorer(max_percentage=100, min_percentage=0.1, step=0.1)`

Create a scikit-learn scorer object.

**Returns:**
- `scorer`: callable compatible with sklearn model selection tools

### Pre-configured scorers

- `OVERLAY_DX_SCORER`: Default configuration
- `OVERLAY_DX_SCORER_FINE`: Fine-grained (step=0.01)
- `OVERLAY_DX_SCORER_COARSE`: Coarse-grained (step=1.0)

## Advanced Usage

### Custom Parameters

```python
from overlay_dx import make_overlay_dx_scorer

# Create scorer with custom tolerance range
scorer = make_overlay_dx_scorer(
    max_percentage=50,  # Only test up to 50% of range
    min_percentage=0.5,
    step=0.5
)
```

### Using the Evaluate Class

```python
from overlay_dx import Evaluate

evaluator = Evaluate(target_values=y_true, prediction=y_pred)

# Get various metrics
mae = evaluator.mae()
rmse = evaluator.rmse()
overlay_score = evaluator.overlay_dx_area_under_curve_metric(
    forecast=y_pred,
    max_percentage=100,
    min_percentage=0.1,
    step=0.1
)
```

## Requirements

- Python >= 3.8
- numpy >= 1.20.0
- scikit-learn >= 1.0.0
- matplotlib >= 3.3.0

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details.

## Citation

If you use overlay_dx in your research, please cite:

```bibtex
@inproceedings{ngo2025overlaydx,
  title={Overlay_dx - Automating forecasting evaluation},
  author={Ngo, Long H. and Chamli, Mohammed Amine and Rivalan, Jonathan and Jaillon, Thomas},
  booktitle={4th International Conference on Optimization and Learning Algorithms (OLA)},
  year={2025}
}
```

## Links

- **GitHub**: https://github.com/Smile-SA/overlay_dx
- **PyPI**: https://pypi.org/project/overlay-dx/
- **Documentation**: https://github.com/Smile-SA/overlay_dx#readme
- **Paper**: https://ola2025.sciencesconf.org/

## Authors

Developed by the R&D team at [Smile](https://www.smile.eu/).
