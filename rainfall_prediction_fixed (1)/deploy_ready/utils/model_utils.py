import time
import numpy as np
import pandas as pd
import logging
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import (
    RandomForestRegressor,
    ExtraTreesRegressor,
    GradientBoostingRegressor,
    AdaBoostRegressor,
)
from sklearn.svm import SVR

# Optional imports wrapper for gradient boosters, though we require them
try:
    from xgboost import XGBRegressor
except ImportError:
    XGBRegressor = None
    logging.warning("XGBoost is not installed.")

try:
    from lightgbm import LGBMRegressor
except ImportError:
    LGBMRegressor = None
    logging.warning("LightGBM is not installed.")

try:
    from catboost import CatBoostRegressor
except ImportError:
    CatBoostRegressor = None
    logging.warning("CatBoost is not installed.")

logger = logging.getLogger(__name__)

def get_models_dict():
    """
    Returns a dictionary of the 10 models to be trained.
    """
    models = {
        "Linear Regression": LinearRegression(),
        "Decision Tree Regressor": DecisionTreeRegressor(random_state=42, max_depth=8),
        "Random Forest Regressor": RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10),
        "Extra Trees Regressor": ExtraTreesRegressor(n_estimators=100, random_state=42, max_depth=10),
        "Gradient Boosting Regressor": GradientBoostingRegressor(n_estimators=100, random_state=42, max_depth=4),
        "AdaBoost Regressor": AdaBoostRegressor(n_estimators=50, random_state=42),
        "Support Vector Regressor": SVR(kernel="rbf", C=100.0, epsilon=0.1),
    }
    
    if XGBRegressor is not None:
        models["XGBoost Regressor"] = XGBRegressor(n_estimators=100, max_depth=5, random_state=42, verbosity=0)
    else:
        logger.warning("Skipping XGBoost Regressor - library not imported.")
        
    if LGBMRegressor is not None:
        models["LightGBM Regressor"] = LGBMRegressor(n_estimators=100, max_depth=5, random_state=42, verbose=-1)
    else:
        logger.warning("Skipping LightGBM Regressor - library not imported.")
        
    if CatBoostRegressor is not None:
        models["CatBoost Regressor"] = CatBoostRegressor(n_estimators=100, depth=5, random_seed=42, verbose=0)
    else:
        logger.warning("Skipping CatBoost Regressor - library not imported.")
        
    return models

def evaluate_model(model, X_train, X_test, y_train, y_test):
    """
    Trains and evaluates a model, measuring training and prediction times.
    """
    metrics = {}
    
    # Train
    start_time = time.time()
    model.fit(X_train, y_train)
    metrics["training_time"] = time.time() - start_time
    
    # Predict
    start_time = time.time()
    y_pred = model.predict(X_test)
    metrics["prediction_time"] = time.time() - start_time
    
    # Metrics
    metrics["mae"] = mean_absolute_error(y_test, y_pred)
    metrics["mse"] = mean_squared_error(y_test, y_pred)
    metrics["rmse"] = np.sqrt(metrics["mse"])
    metrics["r2"] = r2_score(y_test, y_pred)
    
    return metrics, y_pred
