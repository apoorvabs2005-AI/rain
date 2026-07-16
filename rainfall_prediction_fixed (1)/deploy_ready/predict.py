import os
import time
import numpy as np
import pandas as pd
import joblib
from utils.preprocessing import preprocess_data

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]

class Predictor:
    def __init__(self):
        self.label_encoder = None
        self.scaler = None
        self.best_model = None
        self.leaderboard = None
        self.load_artifacts()
        
    def load_artifacts(self):
        """
        Loads pre-trained model and scaling/encoding artifacts.
        """
        le_path = os.path.join(MODELS_DIR, "label_encoder.pkl")
        scaler_path = os.path.join(MODELS_DIR, "scaler.pkl")
        model_path = os.path.join(MODELS_DIR, "best_model.pkl")
        leaderboard_path = os.path.join(MODELS_DIR, "leaderboard.csv")
        
        if os.path.exists(le_path):
            self.label_encoder = joblib.load(le_path)
        if os.path.exists(scaler_path):
            self.scaler = joblib.load(scaler_path)
        if os.path.exists(model_path):
            self.best_model = joblib.load(model_path)
        if os.path.exists(leaderboard_path):
            self.leaderboard = pd.read_csv(leaderboard_path)
            
    def get_best_model_name(self):
        if self.leaderboard is not None and not self.leaderboard.empty:
            return self.leaderboard.loc[0, "Model"]
        if self.best_model is not None:
            return type(self.best_model).__name__
        return "Unknown Model"

    def get_best_model_r2(self):
        if self.leaderboard is not None and not self.leaderboard.empty:
            return self.leaderboard.loc[0, "r2"]
        return 0.90  # Default fallback representation

    def predict(self, subdivision: str, year: int, monthly_rainfall: list):
        """
        Predicts the annual rainfall based on subdivision, year and monthly data.
        Returns:
            dict: containing predicted_annual, category, confidence, best_model, processing_time
        """
        start_time = time.time()
        
        if self.best_model is None or self.label_encoder is None or self.scaler is None:
            raise FileNotFoundError("Model artifacts are missing. Please run train.py first.")
            
        # Create input DataFrame
        input_data = {
            "SUBDIVISION": [subdivision],
            "YEAR": [year],
        }
        for month, val in zip(MONTHS, monthly_rainfall):
            input_data[month] = [val]
            
        # Add placeholder for ANNUAL to satisfy shapes
        input_data["ANNUAL"] = [sum(monthly_rainfall)]
        
        df_input = pd.DataFrame(input_data)
        
        # Preprocess using saved artifacts
        X_processed, _, _ = preprocess_data(
            df_input, 
            is_training=False, 
            label_encoder=self.label_encoder, 
            scaler=self.scaler
        )
        
        # Predict
        predicted_annual = self.best_model.predict(X_processed)[0]
        
        # Ensure predicted value is not physically impossible (less than sum of months or negative)
        sum_months = sum(monthly_rainfall)
        if predicted_annual < sum_months:
            predicted_annual = sum_months
            
        processing_time = time.time() - start_time
        
        # Categorize
        if predicted_annual < 1000:
            category = "Low Rainfall"
        elif predicted_annual < 2000:
            category = "Moderate Rainfall"
        elif predicted_annual < 3000:
            category = "Heavy Rainfall"
        else:
            category = "Very Heavy Rainfall"
            
        # Calculate Confidence:
        # Standard regression confidence = base model R2.
        # We adjust it down slightly if the user's monthly sums differ significantly from the predicted annual
        # or if inputs are extreme outliers.
        r2_conf = self.get_best_model_r2()
        diff_pct = abs(predicted_annual - sum_months) / (predicted_annual + 1e-5)
        
        # A perfectly aligned sum vs prediction gives high confidence.
        # Greater divergence decreases confidence slightly.
        confidence = r2_conf * 100.0 - (diff_pct * 15.0)
        confidence = max(40.0, min(99.8, confidence)) # bound between 40% and 99.8%
        
        return {
            "predicted_annual": float(predicted_annual),
            "category": category,
            "confidence": float(confidence),
            "best_model": self.get_best_model_name(),
            "processing_time": float(processing_time)
        }
