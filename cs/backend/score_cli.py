"""
Command-line scoring tool.

Usage:
    python score_cli.py                         # Interactive prompts
    python score_cli.py --file sample.json      # Score from JSON file
    python score_cli.py --demo                  # Run with demo applicant
"""
import argparse, json, sys, os
sys.path.insert(0, os.path.dirname(__file__))

from model.predict import predict

DEMO = {
    "age": 28, "monthly_income": 35000, "employment_type": "salaried",
    "upi_txn_per_month": 55, "avg_txn_amount": 900,
    "utility_bills_paid": 11, "rent_payments_on_time": 10,
    "mobile_recharge_regularity": 0.88, "spending_variance": 0.22,
    "income_stability_ratio": 0.83, "savings_rate": 0.17,
    "late_payments": 1, "overdraft_count": 0,
    "loan_amount_requested": 100000, "loan_tenure_months": 24,
}

def print_result(name, result):
    score  = result["credit_score"]
    tier   = result["risk_tier"]
    proba  = result["repayment_probability"]
    msg    = result["eligibility_message"]
    status = "✅" if result["eligible"] is True else ("⚠️" if result["eligible"] is None else "❌")

    print("\n" + "="*52)
    print(f"  CREDIT SCORE REPORT — {name}")
    print("="*52)
    print(f"  Credit Score        : {score}  /  850")
    print(f"  Risk Tier           : {tier}")
    print(f"  Repayment Prob.     : {proba * 100:.1f}%")
    print(f"  Eligibility         : {status}  {msg}")
    print("\n  TOP INFLUENCING FACTORS:")
    for i, f in enumerate(result["top_factors"], 1):
        arrow = "▲" if f["direction"] == "positive" else "▼"
        print(f"    {i}. {arrow} {f['feature']}  (impact: {f['impact']:+.4f})")
    print("="*52 + "\n")

def interactive():
    print("\n── AI Credit Scoring CLI ──\n")
    name = input("Applicant Name: ").strip() or "Unknown"
    data = {}
    fields = [
        ("age", int), ("monthly_income", float),
        ("employment_type", str),  # salaried | self_employed | gig_worker | student
        ("upi_txn_per_month", int), ("avg_txn_amount", float),
        ("utility_bills_paid", int), ("rent_payments_on_time", int),
        ("mobile_recharge_regularity", float), ("spending_variance", float),
        ("income_stability_ratio", float), ("savings_rate", float),
        ("late_payments", int), ("overdraft_count", int),
        ("loan_amount_requested", float), ("loan_tenure_months", int),
    ]
    for key, cast in fields:
        while True:
            try:
                val = input(f"  {key.replace('_', ' ').title()}: ")
                data[key] = cast(val)
                break
            except ValueError:
                print(f"  ⚠ Please enter a valid {cast.__name__}")

    result = predict(data)
    print_result(name, result)

def main():
    parser = argparse.ArgumentParser(description="AI Credit Scoring CLI")
    parser.add_argument("--file", help="Path to JSON input file")
    parser.add_argument("--demo", action="store_true", help="Run with demo data")
    args = parser.parse_args()

    if args.demo:
        result = predict(DEMO)
        print_result("Demo Applicant", result)
    elif args.file:
        with open(args.file) as f:
            payload = json.load(f)
        name = payload.pop("applicant_name", "Unknown")
        result = predict(payload)
        print_result(name, result)
    else:
        interactive()

if __name__ == "__main__":
    main()
