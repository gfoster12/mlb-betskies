"""
Standalone script to retrain the model using the most recent data.
Run after data update/cleaning and feature engineering.
"""

import subprocess

def main():
    # Step 1: Feature engineering (advanced)
    subprocess.run(["python", "scripts/feature_engineering_advanced.py"], check=True)
    # Step 2: Model training
    subprocess.run(["python", "scripts/train_xgb_model.py"], check=True)
    print("Model retrained and saved.")

if __name__ == "__main__":
    main()