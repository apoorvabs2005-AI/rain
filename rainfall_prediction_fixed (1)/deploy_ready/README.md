# AI-Based Rainfall Prediction Dashboard (Real-Time Weather Experience)

A production-ready, commercial-grade single-page web application that predicts annual precipitation levels across various meteorological subdivisions of India. The platform uses a pre-trained Gradient Boosting Machine Learning model working entirely in the background, offering an elegant weather app interface similar to Google Weather and Apple Weather.

---

## 🌟 Key Features
- **Header Section**: Simulated weather app status bar showing dynmic date, current subdivision, and simulated light theme toggle.
- **Dynamic Predictions**: Slider inputs for all 12 calendar months to predict the annual rainfall total in millimeters, categorize the rainfall intensity (Low, Moderate, Heavy, Very Heavy), and output a simulated prediction confidence rate.
- **AI Weather Summary**: A natural-language summary that translates prediction outcomes and crops suitability without technical machine learning jargon.
- **Prediction Insights**: Highlight weather cards identifying the wettest month, driest month, monthly averages, and seasonal precipitation trends.
- **Plotly Visualizations**: Tab-based interactive charts including:
  - Monthly Rainfall Bar Chart
  - Monthly Rainfall Line Chart
  - Monthly Rainfall Area Chart
  - Annual Rainfall Gauge Meter
  - Historical Density Distribution (marking the predicted value position)
- **Recent Predictions History**: Captures prediction trials in Streamlit session memory, supports downloads as a CSV file, and offers a cache-clear button.

---

## 🛠️ Technology Stack
- **Backend Core**: Python 3.10
- **Web Interface**: Streamlit
- **ML Engine**: Scikit-learn (Gradient Boosting Regressor)
- **Data Visualizations**: Plotly / Plotly Express
- **Math & Preprocessing**: Pandas, NumPy, Joblib

---

## ⚙️ How to Run Locally

### 1. Prerequisites
Ensure you have Python 3.10+ installed.

### 2. Install Dependencies
Navigate into the project directory and install required Python packages:
```bash
pip install -r requirements.txt
```

### 3. Start the Server
Launch the local Streamlit server:
```bash
streamlit run app.py
```

Streamlit will start and display the local hosting address (usually `http://localhost:8501`). Open this address in your preferred browser.

---

## 📂 Project Structure
```
rainfall_prediction/
├── app.py                  # Main single-page web app entry point
├── train.py                # Standalone model training & downloader script
├── predict.py              # Backend inference module loading saved best models
├── dataset/
│   └── rainfall.csv        # Historical subdivision observations (1901-2017)
├── models/
│   ├── best_model.pkl      # Pre-trained Gradient Boosting model weights
│   ├── label_encoder.pkl   # Fit label encoder object
│   ├── scaler.pkl          # Fit standard scaler object
│   └── leaderboard.csv     # Scored evaluation comparison database
├── utils/
│   ├── preprocessing.py    # Features IQR outlier capping, scaling, and feature engineering
│   ├── visualization.py    # Standard layout formatting and Plotly generators
│   └── helper.py           # Custom weather gradients and CSS animation frames
├── requirements.txt        # Specified python library requirements
├── README.md               # User guide documentation
├── .gitignore              # Ignored builds and local cache exclusions
└── LICENSE                 # Standard software license agreement
```
