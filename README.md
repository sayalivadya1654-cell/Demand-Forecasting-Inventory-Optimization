# 📦 Demand Forecasting & Inventory Optimization

> **An end-to-end Machine Learning solution for demand prediction and data-driven inventory optimization.**

## 🎯 What It Does

This project uses historical sales and inventory data to forecast future product demand and support better inventory planning.

It combines **data analysis, feature engineering, machine learning, SQL analytics, and inventory optimization** to help reduce overstocking and stockout risks.

### Key Capabilities

✅ **Demand Forecasting** — Predict future product demand using historical sales patterns

✅ **Data Analysis** — Identify trends, seasonality, product behavior, and demand patterns

✅ **Feature Engineering** — Create meaningful features for improved model performance

✅ **Machine Learning** — Train and evaluate predictive models for demand forecasting

✅ **Inventory Optimization** — Generate data-driven inventory and replenishment insights

✅ **SQL Analytics** — Perform business-oriented sales and inventory analysis (see `sql/`)

✅ **Interactive Dashboard** — Provide forecasting and inventory insights through Streamlit, with light/dark theme support

---

## 🛠️ Tech Stack

**Programming & Analysis**

![Python](https://img.shields.io/badge/Python-3776AB?logo=python\&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?logo=pandas\&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?logo=numpy\&logoColor=white)

**Machine Learning**

![Scikit-learn](https://img.shields.io/badge/Scikit--learn-F7931E?logo=scikit-learn\&logoColor=white)

**Visualization**

![Matplotlib](https://img.shields.io/badge/Matplotlib-11557C)
![Seaborn](https://img.shields.io/badge/Seaborn-4C72B0)

**Database & Development**

![SQL](https://img.shields.io/badge/SQL-CC2927)
![Jupyter](https://img.shields.io/badge/Jupyter-F37626?logo=jupyter\&logoColor=white)
![VS Code](https://img.shields.io/badge/VS%20Code-007ACC?logo=visual-studio-code\&logoColor=white)

**Deployment & Version Control**

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit\&logoColor=white)
![Git](https://img.shields.io/badge/Git-F05032?logo=git\&logoColor=white)
![GitHub](https://img.shields.io/badge/GitHub-181717?logo=github\&logoColor=white)

---

## 📊 Machine Learning

The forecasting component focuses on predicting future demand from historical sales and engineered features (lag values, rolling averages, price/discount features, calendar features, etc.).

### Models Trained

Two candidate models were trained and compared on a **time-based 80/20 train/test split** (the last 20% of dates, held out and never seen during training):

| Model | MAE | RMSE | R² |
|---|---|---|---|
| Linear Regression | 11.89 | 19.74 | 0.825 |
| **Random Forest (selected)** | **5.77** | **9.62** | **0.958** |

**Random Forest was selected as the final model** and is the one powering the live dashboard (`models/demand_forecasting_model.pkl`).

| Metric | Purpose |
| ------------ | ----------------------------------------------------- |
| **MAE** | Average absolute prediction error, in units of demand |
| **RMSE** | Penalizes larger prediction errors more heavily |
| **R² Score** | Share of demand variation the model explains (0.958 = ~96%) |


---

## 📦 Inventory Optimization

The predicted demand can be used to support inventory planning decisions such as:

* 📈 Expected future demand
* 📦 Recommended inventory levels
* 🔄 Replenishment planning
* ⚠️ Stockout risk identification
* 📉 Overstock reduction

Inventory recommendations use a standard reorder-point model: `Reorder Point = (Average Daily Demand × Lead Time) + Safety Stock`, with lead time and safety stock configurable directly in the dashboard.

The objective is to balance **product availability and inventory cost** using predictive analytics.

---

## 🚀 Quick Start

### Prerequisites

* Python **3.10+**
* pip
* Git
* VS Code or another Python IDE

### Installation

Clone the repository:

```bash
git clone https://github.com/sayalivadya1654-cell/Demand-Forecasting-Inventory-Optimization.git
cd Demand-Forecasting-Inventory-Optimization
```

Create a virtual environment:

**Windows**

```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux**

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## ▶️ Usage

### 1. Run the Analysis & Train the Model

Open the project in **VS Code or Jupyter Notebook** and run the notebooks in order:

1. `01_data_exploration.ipynb`
2. `02_data_cleaning.ipynb`
3. `03_eda.ipynb`
4. `04_feature_engineering.ipynb`
5. `05_model_training.ipynb`
6. `06_model_evaluation.ipynb` — trains and compares Linear Regression vs. Random Forest, then saves the winning model to `models/demand_forecasting_model.pkl`

### 2. Run the Dashboard

Once the model file exists:

```bash
streamlit run app/app.py
```

The application provides an interactive interface for demand forecasting and inventory-related analysis, with a light/dark mode toggle in the sidebar.

---

## 📈 Business Value

This solution is designed to help businesses:

* Improve demand planning
* Make better inventory decisions
* Reduce excess inventory
* Minimize stockout risk
* Improve replenishment planning
* Use historical data for predictive decision-making

---

## 📁 Data

The project uses historical sales and inventory data for analysis and forecasting.

The dataset is processed through data cleaning and feature engineering before being used for machine learning.

Processed datasets are included for reproducibility where applicable.

---

## 🔮 Future Enhancements

* Real-time sales and inventory integration
* Advanced time-series forecasting
* Automated model retraining
* Real-time inventory alerts
* Cloud deployment (Streamlit Community Cloud)
* Automated replenishment recommendations

---

## 👩‍💻 Author

### Sayali Vaidya

**B.Tech — Information Technology | Data Science & Machine Learning**

[![GitHub](https://img.shields.io/badge/GitHub-Sayali%20Vaidya-181717?logo=github\&logoColor=white)](https://github.com/sayalivadya1654-cell)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Sayali%20Vaidya-0A66C2?logo=linkedin\&logoColor=white)](https://www.linkedin.com/in/sayali-vaidya-369a6b279)

---

⭐ **If you find this project useful, consider giving it a star.**
