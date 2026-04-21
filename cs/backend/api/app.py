import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid, json
from datetime import datetime

from config   import config
from database import init_db, get_session, ScoringRequest, Applicant
from model.predict import predict

app = Flask(__name__)
CORS(app, origins=config.CORS_ORIGINS)

# Init DB on startup
init_db()

# ── Helpers ────────────────────────────────────────────────────────────────

REQUIRED_FIELDS = [
    "applicant_name",
    "age", "monthly_income", "employment_type",
    "upi_txn_per_month", "avg_txn_amount",
    "utility_bills_paid", "rent_payments_on_time",
    "mobile_recharge_regularity", "spending_variance",
    "income_stability_ratio", "savings_rate",
    "late_payments", "overdraft_count",
    "loan_amount_requested", "loan_tenure_months",
]

def validate(payload):
    return [f for f in REQUIRED_FIELDS if f not in payload]

# ── Routes ─────────────────────────────────────────────────────────────────

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status":    "ok",
        "model":     "XGBoost v1.0",
        "database":  "SQLite",
        "timestamp": datetime.utcnow().isoformat()
    })


@app.route("/api/score", methods=["POST"])
def score():
    payload = request.get_json()
    if not payload:
        return jsonify({"error": "No JSON body provided"}), 400

    missing = validate(payload)
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400

    try:
        applicant_name = payload.pop("applicant_name")
        result = predict(payload)

        request_id = str(uuid.uuid4())[:8].upper()
        timestamp  = datetime.utcnow()

        # Persist to DB
        session = get_session()
        record = ScoringRequest(
            request_id            = request_id,
            applicant_name        = applicant_name,
            credit_score          = result["credit_score"],
            repayment_probability = result["repayment_probability"],
            risk_tier             = result["risk_tier"],
            eligible              = result["eligible"],
            eligibility_message   = result["eligibility_message"],
            top_factors           = json.dumps(result["top_factors"]),
            created_at            = timestamp,
            **{k: payload.get(k) for k in [
                "age", "monthly_income", "employment_type",
                "upi_txn_per_month", "avg_txn_amount",
                "utility_bills_paid", "rent_payments_on_time",
                "mobile_recharge_regularity", "spending_variance",
                "income_stability_ratio", "savings_rate",
                "late_payments", "overdraft_count",
                "loan_amount_requested", "loan_tenure_months",
            ]}
        )
        session.add(record)
        session.commit()
        session.close()

        return jsonify({
            "request_id":     request_id,
            "timestamp":      timestamp.isoformat(),
            "applicant_name": applicant_name,
            "loan_details": {
                "amount_requested": payload.get("loan_amount_requested"),
                "tenure_months":    payload.get("loan_tenure_months"),
            },
            **result
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/applicants", methods=["POST"])
def register_applicant():
    payload  = request.get_json() or {}
    missing  = [f for f in ["national_id", "full_name", "consent_given"] if f not in payload]
    if missing:
        return jsonify({"error": f"Missing: {missing}"}), 400

    session  = get_session()
    existing = session.query(Applicant).filter_by(national_id=payload["national_id"]).first()
    if existing:
        session.close()
        return jsonify({"error": "Applicant already registered", "id": existing.id}), 409

    applicant = Applicant(
        national_id   = payload["national_id"],
        full_name     = payload["full_name"],
        email         = payload.get("email"),
        phone         = payload.get("phone"),
        consent_given = payload["consent_given"],
    )
    session.add(applicant)
    session.commit()
    data = applicant.to_dict()
    session.close()
    return jsonify(data), 201


@app.route("/api/applicants/<national_id>", methods=["GET"])
def get_applicant(national_id):
    session   = get_session()
    applicant = session.query(Applicant).filter_by(national_id=national_id).first()
    session.close()
    if not applicant:
        return jsonify({"error": "Applicant not found"}), 404
    return jsonify(applicant.to_dict())


@app.route("/api/audit", methods=["GET"])
def audit():
    page   = int(request.args.get("page", 1))
    limit  = int(request.args.get("limit", 20))
    offset = (page - 1) * limit

    session = get_session()
    total   = session.query(ScoringRequest).count()
    records = (
        session.query(ScoringRequest)
        .order_by(ScoringRequest.created_at.desc())
        .offset(offset).limit(limit).all()
    )
    data = [r.to_dict() for r in records]
    session.close()
    return jsonify({"total": total, "page": page, "limit": limit, "records": data})


@app.route("/api/stats", methods=["GET"])
def stats():
    session = get_session()
    records = session.query(ScoringRequest).all()
    session.close()

    if not records:
        return jsonify({"message": "No scoring requests yet.", "total_applications": 0})

    scores         = [r.credit_score for r in records]
    tiers          = [r.risk_tier    for r in records]
    eligible_count = sum(1 for r in records if r.eligible is True)
    review_count   = sum(1 for r in records if r.eligible is None)
    rejected_count = sum(1 for r in records if r.eligible is False)
    tier_counts    = {}
    for t in tiers:
        tier_counts[t] = tier_counts.get(t, 0) + 1

    return jsonify({
        "total_applications": len(records),
        "average_score":      round(sum(scores) / len(scores)),
        "highest_score":      max(scores),
        "lowest_score":       min(scores),
        "eligible_count":     eligible_count,
        "review_count":       review_count,
        "rejected_count":     rejected_count,
        "tier_distribution":  tier_counts,
        "approval_rate":      round(eligible_count / len(records) * 100, 1),
    })


@app.route("/api/score/<request_id>", methods=["GET"])
def get_score(request_id):
    session = get_session()
    record  = session.query(ScoringRequest).filter_by(request_id=request_id).first()
    session.close()
    if not record:
        return jsonify({"error": "Request not found"}), 404
    data = record.to_dict()
    data["top_factors"] = json.loads(record.top_factors or "[]")
    return jsonify(data)


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Method not allowed"}), 405


if __name__ == "__main__":
    print(f"🚀 Starting AI Credit Scoring API on http://localhost:{config.PORT}")
    app.run(debug=config.DEBUG, port=config.PORT)
