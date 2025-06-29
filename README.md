# MLB Betskies Dashboard

A production-grade MLB predictions dashboard with daily-automated model/data updates, live odds, advanced stats, and CI/CD.

---

## 🚀 Deploy/Run on Replit

1. **Fork** or **import** this repository to your own GitHub account.
2. Go to [Replit](https://replit.com/) and create a new Repl:
   - Click "Import from GitHub"
   - Paste your repository URL
3. Replit will auto-install from `requirements.txt` and run using `.replit` (which uses gunicorn for production).
   - Your app will be served at `https://<your-repl-name>.<your-username>.repl.co`
4. If you update data/model, either:
   - Wait for the GitHub Actions workflow to run (see below), OR
   - Run `python scripts/automate_data_pipeline.py` in the Replit shell to refresh manually.

---

## 🛠️ Local Development

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```
- App will be at [http://localhost:8050](http://localhost:8050)

---

## 🔄 Automated Data/Model Refresh (GitHub Actions)

- The included workflow `.github/workflows/refresh-data-and-model.yml` runs daily (8am UTC) or on demand.
- It will:
  - Fetch latest data, retrain the model, generate predictions.
  - Commit and push any updated data/model files back to your repo.
- **No secrets required** unless you need API keys for data fetching (see below).

---

## 🏗️ Production Server

- **Replit**: Uses Gunicorn (see `.replit` and `wsgi.py`).
- **Other Platforms**: Use the included `Procfile` for Heroku/Render/etc.

---

## 📊 Usage

- The dashboard supports:
  - Filtering by date and team
  - Viewing win probabilities, picks, weather, live odds
  - Advanced stats for pitchers/teams/players in detail panel

---

## 🔄 CI/CD Pipeline

- GitHub Actions job to refresh and push latest data/model (see above).
- (Optional) You can add more jobs for testing, linting, or deployment.

---

## 📁 Directory Structure

```
app.py                  # Main Dash app
wsgi.py                 # WSGI entrypoint for production servers
scripts/                # Data fetch, prep, feature engineering, model scripts
data/                   # Data and model files (autoupdated)
.github/workflows/      # GitHub Actions workflows
requirements.txt        # Python dependencies
Procfile                # For Heroku/production
.replit, replit.nix     # Replit configuration
README.md               # You are here!
```

---

## 🔑 API Keys & Secrets

- If your data fetch scripts require API keys:
  - Add them as GitHub repo secrets or as Replit secrets (`.env` or Replit Secrets tab).
  - Reference them in your scripts using `os.environ`.

---

## 🧪 Testing

- Add any unit tests under `tests/` and extend the GitHub Actions workflow as needed.

---

## 🙋 FAQ

**Q: Why use Gunicorn instead of Dash's dev server?**  
A: Gunicorn is a production WSGI server, more stable and scalable.

**Q: Can I update data/model manually on Replit?**  
A: Yes, open the shell and run `python scripts/automate_data_pipeline.py`.

**Q: How do I add more features?**  
A: Fork the repo, push changes, and Replit will auto-reload. For advanced features, edit `app.py` or scripts as needed.

---

MIT License