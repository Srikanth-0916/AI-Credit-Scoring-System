"""
Run with:  pytest tests/test_api.py -v
Make sure the model is trained before running.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import json
from api.app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c

# ── Sample payload ─────────────────────────────────────────────────────────
VALID_PAYLOAD = {
    "applicant_name":             "Test User",
    "age":                        30,
    "monthly_income":             40000,
    "employment_type":            "salaried",
    "upi_txn_per_month":          50,
    "avg_txn_amount":             900,
    "utility_bills_paid":         11,
    "rent_payments_on_time":      10,
    "mobile_recharge_regularity": 0.9,
    "spending_variance":          0.2,
    "income_stability_ratio":     0.85,
    "savings_rate":               0.2,
    "late_payments":              0,
    "overdraft_count":            0,
    "loan_amount_requested":      100000,
    "loan_tenure_months":         24,
}

# ── Health check ───────────────────────────────────────────────────────────
def test_health(client):
    res  = client.get("/api/health")
    data = res.get_json()
    assert res.status_code == 200
    assert data["status"] == "ok"

# ── Score endpoint ─────────────────────────────────────────────────────────
def test_score_valid(client):
    res  = client.post("/api/score", json=VALID_PAYLOAD)
    data = res.get_json()
    assert res.status_code == 200
    assert "credit_score" in data
    assert 300 <= data["credit_score"] <= 850
    assert "risk_tier" in data
    assert len(data["top_factors"]) > 0

def test_score_missing_field(client):
    payload = VALID_PAYLOAD.copy()
    del payload["monthly_income"]
    res  = client.post("/api/score", json=payload)
    data = res.get_json()
    assert res.status_code == 400
    assert "error" in data

def test_score_no_body(client):
    res = client.post("/api/score", data="", content_type="application/json")
    assert res.status_code == 400

def test_score_returns_shap(client):
    res  = client.post("/api/score", json=VALID_PAYLOAD)
    data = res.get_json()
    assert res.status_code == 200
    factors = data["top_factors"]
    assert isinstance(factors, list)
    for f in factors:
        assert "feature" in f
        assert "impact"  in f
        assert "direction" in f
        assert f["direction"] in ["positive", "negative"]

# ── Audit & stats ──────────────────────────────────────────────────────────
def test_audit(client):
    # Score first to populate audit
    client.post("/api/score", json=VALID_PAYLOAD)
    res  = client.get("/api/audit")
    data = res.get_json()
    assert res.status_code == 200
    assert "records" in data
    assert isinstance(data["records"], list)

def test_stats(client):
    client.post("/api/score", json=VALID_PAYLOAD)
    res  = client.get("/api/stats")
    data = res.get_json()
    assert res.status_code == 200
    assert "total_applications" in data
    assert data["total_applications"] >= 1

# ── Score tiers ────────────────────────────────────────────────────────────
def test_high_score_applicant(client):
    payload = VALID_PAYLOAD.copy()
    payload.update({
        "income_stability_ratio":     1.0,
        "utility_bills_paid":         12,
        "rent_payments_on_time":      12,
        "savings_rate":               0.4,
        "late_payments":              0,
        "overdraft_count":            0,
        "mobile_recharge_regularity": 1.0,
        "spending_variance":          0.0,
    })
    res  = client.post("/api/score", json=payload)
    data = res.get_json()
    assert res.status_code == 200
    assert data["credit_score"] >= 650  # Expect decent score

def test_low_score_applicant(client):
    payload = VALID_PAYLOAD.copy()
    payload.update({
        "income_stability_ratio":     0.3,
        "utility_bills_paid":         2,
        "rent_payments_on_time":      1,
        "savings_rate":               0.0,
        "late_payments":              9,
        "overdraft_count":            4,
        "mobile_recharge_regularity": 0.1,
        "spending_variance":          0.9,
    })
    res  = client.post("/api/score", json=payload)
    data = res.get_json()
    assert res.status_code == 200
    assert data["credit_score"] < 650  # Expect lower score

# ── Applicant registration ─────────────────────────────────────────────────
def test_register_applicant(client):
    res  = client.post("/api/applicants", json={
        "national_id":   "TEST123456",
        "full_name":     "Test Applicant",
        "email":         "test@example.com",
        "consent_given": True
    })
    assert res.status_code in [201, 409]  # 409 if already exists

def test_get_applicant_not_found(client):
    res = client.get("/api/applicants/NONEXISTENT999")
    assert res.status_code == 404

# ── Error handling ─────────────────────────────────────────────────────────
def test_404(client):
    res = client.get("/api/doesnotexist")
    assert res.status_code == 404
