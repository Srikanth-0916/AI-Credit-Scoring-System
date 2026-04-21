import pandas as pd
import numpy as np
import os

np.random.seed(42)
N = 2000

def generate_dataset():
    data = {}

    # Demographics
    data["age"] = np.random.randint(21, 60, N)
    data["monthly_income"] = np.random.randint(5000, 80000, N)
    data["employment_type"] = np.random.choice(["salaried", "self_employed", "gig_worker", "student"], N, p=[0.4, 0.25, 0.2, 0.15])

    # Alternate financial signals
    data["upi_txn_per_month"]       = np.random.randint(5, 150, N)
    data["avg_txn_amount"]          = np.random.randint(100, 5000, N)
    data["utility_bills_paid"]      = np.random.randint(0, 12, N)       # out of 12 months
    data["rent_payments_on_time"]   = np.random.randint(0, 12, N)
    data["mobile_recharge_regularity"] = np.random.uniform(0, 1, N)    # 0 = irregular, 1 = very regular

    # Behavioral features
    data["spending_variance"]       = np.random.uniform(0, 1, N)        # high = unstable spending
    data["income_stability_ratio"]  = np.random.uniform(0.3, 1.0, N)   # 1 = very stable
    data["savings_rate"]            = np.random.uniform(0, 0.5, N)      # proportion of income saved
    data["late_payments"]           = np.random.randint(0, 10, N)
    data["overdraft_count"]         = np.random.randint(0, 5, N)

    # Loan request details
    data["loan_amount_requested"]   = np.random.randint(5000, 500000, N)
    data["loan_tenure_months"]      = np.random.choice([6, 12, 24, 36, 48, 60], N)

    # Target: repaid = 1, defaulted = 0
    score = (
        0.25 * data["income_stability_ratio"] +
        0.20 * (data["utility_bills_paid"] / 12) +
        0.15 * (data["rent_payments_on_time"] / 12) +
        0.15 * data["savings_rate"] * 2 +
        0.10 * data["mobile_recharge_regularity"] +
        0.10 * (1 - data["spending_variance"]) +
        0.05 * np.clip(data["monthly_income"] / 80000, 0, 1) -
        0.10 * (data["late_payments"] / 10) -
        0.05 * (data["overdraft_count"] / 5)
    )
    score = np.clip(score, 0, 1)
    data["repaid"] = (score + np.random.normal(0, 0.1, N) > 0.5).astype(int)

    df = pd.DataFrame(data)

    os.makedirs("data", exist_ok=True)
    df.to_csv("data/credit_data.csv", index=False)
    print(f"✅ Dataset generated: {len(df)} rows saved to data/credit_data.csv")
    return df

if __name__ == "__main__":
    generate_dataset()
