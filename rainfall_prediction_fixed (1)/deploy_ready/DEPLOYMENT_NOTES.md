# Deployment Notes

## What was wrong

1. **`.gitignore` was excluding your model files and dataset.**
   The original `.gitignore` had:
   ```
   models/best_model.pkl
   models/label_encoder.pkl
   models/scaler.pkl
   dataset/rainfall.csv
   ```
   These lines told Git to never commit the very files the app depends on.
   When Streamlit Cloud cloned your repo, those files simply weren't there,
   which cascaded into the crash you saw. This has been removed.

2. **Relative file paths broke on Streamlit Cloud.**
   Streamlit Community Cloud always runs your app with the working directory
   set to the **repository root**, not the folder your `app.py` lives in.
   Your code used `os.path.join("dataset", "rainfall.csv")` and
   `MODELS_DIR = "models"`, which only worked locally. Every path is now
   built from `os.path.dirname(os.path.abspath(__file__))`, so it resolves
   correctly no matter where Streamlit runs the script from.

3. **Deeply nested folder structure.**
   Your original zip was `rainfall/rainfall_prediction/app.py` — three
   levels deep once cloned. This is very easy to point Streamlit Cloud's
   "Main file path" at incorrectly, which produces the endless
   "Main module does not exist" log you saw. This package is flattened so
   `app.py` sits at the repo root.

4. **Loading failures were silent.** `load_historical_data()` and the model
   loader now raise a visible `st.error(...)` in the app itself instead of
   quietly returning `None`, so if anything is still misconfigured you'll
   see the real reason instead of a Streamlit Cloud "redacted" message.

5. Removed `__pycache__/` and `catboost_info/` (local training logs) — not
   needed for deployment and just adds bloat/noise to the repo.

## How to deploy this folder

1. Push the **contents of this folder** to the root of a GitHub repo (don't
   nest it inside another folder).
2. On [share.streamlit.io](https://share.streamlit.io), create a new app:
   - Repository: your repo
   - Branch: main (or whichever you used)
   - **Main file path: `app.py`** (not `rainfall_prediction/app.py`)
3. In "Advanced settings" during deploy, explicitly set the Python version
   (e.g. 3.12). Streamlit Cloud has had bugs where `runtime.txt` is ignored
   and it silently uses a newer Python than your dependencies support, so
   don't rely on `runtime.txt` alone — set it in the UI too.
4. Deploy. If you still see an error, click "Manage app" → logs, which will
   show the *actual* uncaught exception (not the redacted version).

## Files kept out of git on purpose (see `.gitignore`)
`__pycache__/`, `catboost_info/` (regenerated locally each time you train),
OS/editor cruft. Your model artifacts and dataset are now correctly tracked.
