"""
Master automation script for MLB Betskies: 
- Updates all data (schedule, stats, weather, etc.)
- Retrains the model with the latest data
- Generates daily predictions

Recommended to run this once daily via cron, GitHub Actions, or other schedulers.
"""

import os
import subprocess
import datetime

def run_script(script_path, args=[]):
    cmd = ["python", script_path] + args
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print("Return code:", result.returncode)
    if result.stdout:
        print("STDOUT:\n", result.stdout)
    if result.stderr:
        print("STDERR:\n", result.stderr)
    if result.returncode != 0:
        raise RuntimeError(f"Script {script_path} failed.")

def main():
    today = datetime.date.today()
    # 1. Update all data (fresh fetch, clean, and prep)
    run_script("scripts/fetch_all_data.py", ["--year", str(today.year), "--historic_seasons", str(today.year-2), str(today.year-1), "--skip_weather"])
    run_script("scripts/data_prep.py")
    # 2. Retrain the model with the latest data
    run_script("scripts/feature_engineering_advanced.py")
    run_script("scripts/train_xgb_model.py")
    # 3. Fetch weather for today's and upcoming games
    run_script("scripts/fetch_all_data.py", ["--year", str(today.year), "--skip_weather", "False"])
    # 4. Generate predictions for today/upcoming games
    run_script("scripts/predict_upcoming.py")
    print("MLB Betskies pipeline completed.")

if __name__ == "__main__":
    main()