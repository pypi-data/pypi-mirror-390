"""
Tests for sklearn-compatible overlay_dx functions.
Run with: pytest test_overlay_dx_sklearn.py
"""

import numpy as np
import pytest
from sklearn.model_selection import cross_val_score, GridSearchCV
from sklearn.linear_model import Ridge, LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import make_scorer


# Import from metrics.py after adding the sklearn extension
from overlay_dx import (
    overlay_dx_score, 
    make_overlay_dx_scorer, 
    OVERLAY_DX_SCORER,
    OVERLAY_DX_SCORER_FINE,      
    OVERLAY_DX_SCORER_COARSE     
)


class TestOverlayDxScore:
    """Test overlay_dx_score function"""
    
    def test_perfect_prediction(self):
        """Score should be close to 1.0 for perfect predictions"""
        y_true = np.array([1, 2, 3, 4, 5])
        y_pred = np.array([1, 2, 3, 4, 5])
        
        score = overlay_dx_score(y_true, y_pred)
        assert score > 0.99, f"Expected score > 0.99, got {score}"
    
    def test_poor_prediction(self):
        """Score should be lower for poor predictions"""
        y_true = np.array([1, 2, 3, 4, 5])
        y_pred = np.array([5, 4, 3, 2, 1])
        
        score = overlay_dx_score(y_true, y_pred)
        assert score < 0.8, f"Expected score < 0.8 for poor predictions, got {score}"
    
    def test_score_range(self):
        """Score should always be between 0 and 1"""
        np.random.seed(42)
        y_true = np.random.randn(100)
        y_pred = y_true + np.random.randn(100) * 0.5
        
        score = overlay_dx_score(y_true, y_pred)
        assert 0 <= score <= 1, f"Score {score} outside valid range [0, 1]"
    
    def test_input_validation(self):
        """Should handle input validation properly"""
        y_true = np.array([1, 2, 3, 4, 5])
        y_pred = np.array([1, 2, 3])
        
        with pytest.raises(ValueError):
            overlay_dx_score(y_true, y_pred)
    
    def test_custom_parameters(self):
        """Should work with custom max_percentage, min_percentage, step"""
        y_true = np.array([1, 2, 3, 4, 5])
        y_pred = np.array([1.1, 2.2, 2.9, 4.1, 5.2])
        
        score1 = overlay_dx_score(y_true, y_pred, max_percentage=100, min_percentage=0.1, step=0.1)
        score2 = overlay_dx_score(y_true, y_pred, max_percentage=50, min_percentage=0.1, step=0.5)
        
        assert isinstance(score1, float)
        assert isinstance(score2, float)
        assert 0 <= score1 <= 1
        assert 0 <= score2 <= 1


class TestMakeOverlayDxScorer:
    """Test make_overlay_dx_scorer function"""
    
    def test_scorer_creation(self):
        """Should create a valid sklearn scorer"""
        scorer = make_overlay_dx_scorer()
        assert callable(scorer)
    
    def test_scorer_with_estimator(self):
        """Scorer should work with sklearn estimators"""
        np.random.seed(42)
        X = np.random.randn(50, 3)
        y = X[:, 0] * 2 + X[:, 1] * 3 + np.random.randn(50) * 0.1
        
        model = Ridge()
        model.fit(X, y)
        
        scorer = make_overlay_dx_scorer()
        score = scorer(model, X, y)
        
        assert isinstance(score, (int, float))
        assert score > 0
    
    def test_custom_parameters(self):
        """Should create scorers with custom parameters"""
        scorer_fine = make_overlay_dx_scorer(max_percentage=100, min_percentage=0.01, step=0.01)
        scorer_coarse = make_overlay_dx_scorer(max_percentage=100, min_percentage=1.0, step=1.0)
        
        assert callable(scorer_fine)
        assert callable(scorer_coarse)


class TestSklearnIntegration:
    """Test integration with sklearn tools"""
    
    def test_cross_val_score(self):
        """Should work with cross_val_score"""
        np.random.seed(42)
        X = np.random.randn(100, 5)
        y = X[:, 0] * 2 + X[:, 1] * 3 + np.random.randn(100) * 0.5
        
        model = Ridge()
        scorer = make_overlay_dx_scorer()
        
        scores = cross_val_score(model, X, y, cv=3, scoring=scorer)
        
        assert len(scores) == 3
        assert all(isinstance(s, (int, float)) for s in scores)
        assert all(s > 0 for s in scores)
    
    def test_grid_search_cv(self):
        """Should work with GridSearchCV"""
        np.random.seed(42)
        X = np.random.randn(100, 5)
        y = X[:, 0] * 2 + X[:, 1] * 3 + np.random.randn(100) * 0.5
        
        param_grid = {'alpha': [0.1, 1.0, 10.0]}
        scorer = make_overlay_dx_scorer()
        
        grid_search = GridSearchCV(
            Ridge(),
            param_grid,
            scoring=scorer,
            cv=3
        )
        
        grid_search.fit(X, y)
        
        assert hasattr(grid_search, 'best_score_')
        assert hasattr(grid_search, 'best_params_')
        assert grid_search.best_score_ > 0
    
    def test_multiple_models_comparison(self):
        """Should allow comparing different models"""
        np.random.seed(42)
        X = np.random.randn(100, 5)
        y = X[:, 0] * 2 + X[:, 1] * 3 + np.random.randn(100) * 0.5
        
        models = {
            'Ridge': Ridge(),
            'LinearRegression': LinearRegression()
        }
        
        scorer = make_overlay_dx_scorer()
        results = {}
        
        for name, model in models.items():
            scores = cross_val_score(model, X, y, cv=3, scoring=scorer)
            results[name] = scores.mean()
        
        assert len(results) == 2
        assert all(score > 0 for score in results.values())


class TestPreConfiguredScorers:
    """Test pre-configured scorer constants"""
    
    def test_default_scorer(self):
        """OVERLAY_DX_SCORER should work"""
        np.random.seed(42)
        X = np.random.randn(50, 3)
        y = X[:, 0] * 2 + np.random.randn(50) * 0.1
        
        model = Ridge()
        scores = cross_val_score(model, X, y, cv=3, scoring=OVERLAY_DX_SCORER)
        
        assert len(scores) == 3
        assert all(s > 0 for s in scores)
    
    def test_fine_scorer(self):
        """OVERLAY_DX_SCORER_FINE should work"""
        np.random.seed(42)
        X = np.random.randn(50, 3)
        y = X[:, 0] * 2 + np.random.randn(50) * 0.1
        
        model = Ridge()
        scores = cross_val_score(model, X, y, cv=3, scoring=OVERLAY_DX_SCORER_FINE)
        
        assert len(scores) == 3
        assert all(s > 0 for s in scores)
    
    def test_coarse_scorer(self):
        """OVERLAY_DX_SCORER_COARSE should work"""
        np.random.seed(42)
        X = np.random.randn(50, 3)
        y = X[:, 0] * 2 + np.random.randn(50) * 0.1
        
        model = Ridge()
        scores = cross_val_score(model, X, y, cv=3, scoring=OVERLAY_DX_SCORER_COARSE)
        
        assert len(scores) == 3
        assert all(s > 0 for s in scores)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])