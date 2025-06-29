"""
Script to generate predictions for today's and upcoming MLB games.
Assumes data and model are fresh.
"""

import datetime
import subprocess

def main():
    today = datetime.date.today()
    # Fetch latest games and weather
    subprocess.run(["python", "scripts/fetch_all_data.py", "--year", str(today.year), "--skip_weather", "False"], check=True)
    # Clean/prep new data
    subprocess.run(["python", "scripts/data_prep.py"], check=True)
    # (Assumes model is already trained and feature engineering is up to date)
    # Generate predictions for today/upcoming
    subprocess.run(["python", "scripts/predict_upcoming.py"], check=True)
    print("Predictions for today/upcoming games generated.")

if __name__ == "__main__":
    main()