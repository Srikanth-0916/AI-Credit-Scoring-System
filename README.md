# AI-based Credit Scoring System
### Team Blind | Full Stack Implementation

---

## 📁 Project Structure

```
credit-scoring/
├── backend/
│   ├── data/
│   │   └── generate_data.py       ← Synthetic dataset generator
│   ├── model/
│   │   └── train.py               ← XGBoost + SHAP training script
│   ├── api/
│   │   └── app.py                 ← Flask REST API
│   └── requirements.txt
└── frontend/
    ├── public/
    │   └── index.html
    ├── src/
    │   ├── App.jsx                 ← React Dashboard
    │   └── index.js
    └── package.json
```

---

## ⚙️ Setup & Run (Step by Step)

### Step 1 — Backend Setup

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Generate synthetic training data
python data/generate_data.py

# Train the XGBoost model (saves model + SHAP explainer)
cd model
python train.py
cd ..

# Start Flask API
python api/app.py
# → Running on http://localhost:5000
```

### Step 2 — Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start React app
npm start
# → Running on http://localhost:3000
```

---

## 🌐 API Endpoints

| Method | Endpoint       | Description                     |
|--------|----------------|---------------------------------|
| GET    | /api/health    | Check if API is running         |
| POST   | /api/score     | Score an applicant              |
| GET    | /api/audit     | View last 50 scoring requests   |
| GET    | /api/stats     | Dashboard summary statistics    |

### Sample POST /api/score Request

```json
{
    "applicant_name": "Priya Sharma",
    "age": 28,
    "monthly_income": 35000,
    "employment_type": "salaried",
    "upi_txn_per_month": 60,
    "avg_txn_amount": 900,
    "utility_bills_paid": 11,
    "rent_payments_on_time": 10,
    "mobile_recharge_regularity": 0.9,
    "spending_variance": 0.2,
    "income_stability_ratio": 0.85,
    "savings_rate": 0.2,
    "late_payments": 0,
    "overdraft_count": 0,
    "loan_amount_requested": 100000,
    "loan_tenure_months": 24
}
```

### Sample Response

```json
{
    "request_id": "A1B2C3D4",
    "applicant_name": "Priya Sharma",
    "credit_score": 742,
    "repayment_probability": 0.8123,
    "risk_tier": "Moderate Risk",
    "eligible": true,
    "eligibility_message": "Eligible for loan",
    "top_factors": [
        { "feature": "Income Stability Ratio", "impact": 0.21, "direction": "positive" },
        { "feature": "Utility Bills Paid",     "impact": 0.18, "direction": "positive" },
        { "feature": "Late Payments",           "impact": -0.09, "direction": "negative" }
    ]
}
```

---

## 📊 Features Used by the Model

| Feature | Type | Description |
|---|---|---|
| age | Demographic | Applicant age |
| monthly_income | Financial | Monthly earnings |
| employment_type | Categorical | salaried / gig / self_employed / student |
| upi_txn_per_month | Behavioral | Digital payment frequency |
| avg_txn_amount | Behavioral | Average transaction value |
| utility_bills_paid | Alternate | Out of 12 months |
| rent_payments_on_time | Alternate | Out of 12 months |
| mobile_recharge_regularity | Behavioral | 0 (irregular) → 1 (very regular) |
| spending_variance | Behavioral | 0 (stable) → 1 (volatile) |
| income_stability_ratio | Behavioral | 0 (unstable) → 1 (stable) |
| savings_rate | Financial | Fraction of income saved |
| late_payments | Risk | Count of late payments |
| overdraft_count | Risk | Count of overdrafts |
| loan_amount_requested | Loan | Amount in ₹ |
| loan_tenure_months | Loan | 6 / 12 / 24 / 36 / 48 / 60 |

---

## 🧠 Credit Score Tiers

| Score Range | Risk Tier | Eligibility |
|---|---|---|
| 750 – 850 | Low Risk | ✅ Eligible |
| 650 – 749 | Moderate Risk | ✅ Eligible |
| 550 – 649 | High Risk | ⚠️ Manual Review |
| 300 – 549 | Very High Risk | ❌ Not Eligible |
