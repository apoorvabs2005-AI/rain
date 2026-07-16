import os
import urllib.request
import pandas as pd
import numpy as np
import joblib
import logging
from sklearn.model_selection import train_test_split

from utils.preprocessing import preprocess_data
from utils.model_utils import get_models_dict, evaluate_model

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Constants
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "dataset")
DATASET_PATH = os.path.join(DATASET_DIR, "rainfall.csv")
DATASET_URL = "https://raw.githubusercontent.com/devarsh512/Rainfall_Prediction_India_ML/master/Sub_Division_IMD_2017.csv"

MODELS_DIR = os.path.join(BASE_DIR, "models")

def download_dataset():
    """
    Downloads the rainfall dataset from the public repository if not already present.
    """
    if not os.path.exists(DATASET_DIR):
        os.makedirs(DATASET_DIR)
        logger.info(f"Created directory: {DATASET_DIR}")
        
    if not os.path.exists(DATASET_PATH):
        logger.info(f"Downloading dataset from {DATASET_URL}...")
        try:
            req = urllib.request.Request(DATASET_URL, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                with open(DATASET_PATH, 'wb') as f:
                    f.write(response.read())
            logger.info(f"Dataset successfully downloaded and saved to {DATASET_PATH}")
        except Exception as e:
            logger.error(f"Failed to download dataset: {e}")
            raise e
    else:
        logger.info(f"Dataset already exists at {DATASET_PATH}")

def main():
    # 1. Download data
    download_dataset()
    
    # 2. Load data
    logger.info("Loading dataset...")
    df = pd.read_csv(DATASET_PATH)
    logger.info(f"Dataset loaded successfully with shape: {df.shape}")
    
    # 3. Preprocess data
    logger.info("Starting preprocessing...")
    X, y, label_encoder, scaler = preprocess_data(df, is_training=True)
    logger.info(f"Preprocessing completed. Features shape: {X.shape}, Target shape: {y.shape}")
    
    # 4. Train-Test Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    logger.info(f"Split data into Train: {X_train.shape}, Test: {X_test.shape}")
    
    # 5. Initialize Models
    models = get_models_dict()
    logger.info(f"Initialized {len(models)} models for training.")
    
    results = []
    trained_model_objs = {}
    
    # 6. Train and evaluate
    for name, model in models.items():
        logger.info(f"Training and evaluating {name}...")
        try:
            metrics, y_pred = evaluate_model(model, X_train, X_test, y_train, y_test)
            metrics["Model"] = name
            results.append(metrics)
            trained_model_objs[name] = model
            logger.info(f"{name} evaluated: R2 = {metrics['r2']:.4f}, RMSE = {metrics['rmse']:.2f}")
        except Exception as e:
            logger.error(f"Error training {name}: {e}")
            
    # 7. Create Leaderboard
    leaderboard = pd.DataFrame(results)
    
    # Sort: Highest R2 and Lowest RMSE
    leaderboard = leaderboard.sort_values(by=["r2", "rmse"], ascending=[False, True]).reset_index(drop=True)
    leaderboard.index += 1  # 1-indexed ranks
    leaderboard.index.name = "Rank"
    leaderboard = leaderboard.reset_index()
    
    logger.info("\n--- Model Leaderboard ---")
    logger.info(f"\n{leaderboard.to_string()}")
    
    # 8. Save artifacts
    if not os.path.exists(MODELS_DIR):
        os.makedirs(MODELS_DIR)
        logger.info(f"Created directory: {MODELS_DIR}")
        
    # Save encoders
    joblib.dump(label_encoder, os.path.join(MODELS_DIR, "label_encoder.pkl"))
    joblib.dump(scaler, os.path.join(MODELS_DIR, "scaler.pkl"))
    logger.info("Saved Label Encoder and Scaler.")
    
    # Save best model
    best_model_name = leaderboard.loc[0, "Model"]
    best_model = trained_model_objs[best_model_name]
    
    joblib.dump(best_model, os.path.join(MODELS_DIR, "best_model.pkl"))
    logger.info(f"Saved the best performing model ({best_model_name}) to models/best_model.pkl")
    
    # Save leaderboard.csv
    leaderboard.to_csv(os.path.join(MODELS_DIR, "leaderboard.csv"), index=False)
    logger.info("Saved leaderboard.csv to models/")

if __name__ == "__main__":
    main()
